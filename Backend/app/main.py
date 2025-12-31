import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.api.models import Program
from app.services.scraper import scrape, ScraperError
from app.db import models, crud, database

# Crear las tablas en la base de datos al iniciar
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Radio Autonoma API",
    description="API para gestionar descargas y transmisiones de radio",
    version="1.0.0"
)

# Configurar CORS para permitir que el Frontend hable con el Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, cambia esto por la URL real del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "online", "message": "Radio Autonoma Backend is running"}

@app.post("/scrape")
async def run_scraper(program: Program, db: Session = Depends(database.get_db)):
    """
    Inicia la descarga de un programa.
    Verifica primero si ya existe en la base de datos Y en el disco.
    """
    # 1. Verificar si ya existe en BD
    existing_episode = crud.get_episode_by_url(db, url=program.url)
    
    if existing_episode:
        # 1.1 Verificar si el archivo realmente existe en disco
        if existing_episode.file_path and os.path.exists(existing_episode.file_path):
            print(f"⚠️ Episodio ya existe y archivo encontrado: {existing_episode.title}")
            return {
                "status": "skipped",
                "message": "El episodio ya fue descargado anteriormente",
                "data": {
                    "id": existing_episode.id,
                    "title": existing_episode.title,
                    "file_path": existing_episode.file_path
                }
            }
        else:
            print(f"⚠️ Registro encontrado en BD pero archivo NO existe. Re-descargando: {program.id}")
            # Si no existe el archivo, continuamos con la descarga (saltamos el return)

    try:
        # 2. Procedemos a descargar
        program_dict = program.dict()
        print(f"📥 Iniciando descarga: {program.id}")
        
        result = scrape(program_dict)
        
        # 3. Guardar o Actualizar en Base de Datos
        if result["status"] == "downloaded":
            if existing_episode:
                # Si ya existía el registro (pero no el archivo), actualizamos la ruta
                existing_episode.file_path = result["file_path"]
                # Podríamos actualizar otros campos si fuera necesario
                db.commit()
                db.refresh(existing_episode)
                print(f"🔄 Registro actualizado en DB: ID {existing_episode.id}")
            else:
                # Si es nuevo, creamos uno nuevo
                new_episode = crud.create_episode(
                    db=db,
                    title=program.id,
                    url=program.url,
                    source=program.source,
                    file_path=result["file_path"]
                )
                print(f"💾 Guardado en DB: ID {new_episode.id}")

        return {
            "status": "success",
            "data": result
        }
        
    except ScraperError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error crítico: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.get("/episodes")
async def read_episodes(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    """Obtiene la lista de episodios descargados"""
    episodes = crud.get_episodes(db, skip=skip, limit=limit)
    return episodes

@app.delete("/episodes/{episode_id}")
async def delete_episode(episode_id: int, db: Session = Depends(database.get_db)):
    """Elimina un episodio de la base de datos y del disco"""
    episode = crud.get_episode(db, episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episodio no encontrado")
    
    # 1. Eliminar archivo físico
    if episode.file_path and os.path.exists(episode.file_path):
        try:
            os.remove(episode.file_path)
            print(f"🗑️ Archivo eliminado: {episode.file_path}")
        except Exception as e:
            print(f"⚠️ Error al eliminar archivo: {e}")
            # No lanzamos error para permitir que se borre de la BD aunque falle el borrado de archivo
    
    # 2. Eliminar de la BD
    crud.delete_episode(db, episode_id)
    
    return {"status": "success", "message": f"Episodio {episode_id} eliminado"}

@app.post("/sync")
async def sync_files(db: Session = Depends(database.get_db)):
    """
    Escanea la carpeta de datos y añade a la BD los archivos que no estén registrados.
    Útil para importar descargas antiguas o manuales.
    """
    base_path = "data/raw"
    added_count = 0
    errors = []

    if not os.path.exists(base_path):
        return {"status": "error", "message": "No se encontró la carpeta de datos"}

    # Recorrer recursivamente
    for root_dir, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".mp3"):
                full_path = os.path.join(root_dir, file)
                # Normalizar path para consistencia (barras inclinadas)
                full_path = full_path.replace("\\", "/")
                
                # Verificar si ya existe en BD
                if not crud.get_episode_by_file_path(db, full_path):
                    try:
                        # Crear registro
                        # Usamos el nombre del archivo (sin extensión) como ID/Título
                        file_id = os.path.splitext(file)[0]
                        
                        crud.create_episode(
                            db=db,
                            title=file_id,
                            url=f"local://{file_id}", # URL ficticia para locales
                            source="local_scan",
                            file_path=full_path
                        )
                        added_count += 1
                        print(f"➕ Archivo importado: {file}")
                    except Exception as e:
                        print(f"❌ Error importando {file}: {e}")
                        errors.append(f"{file}: {str(e)}")

    return {
        "status": "success", 
        "message": f"Sincronización completada. {added_count} archivos nuevos añadidos.",
        "added": added_count,
        "errors": errors
    }

@app.post("/cleanup")
async def cleanup_orphaned_records(db: Session = Depends(database.get_db)):
    """
    Elimina de la BD los registros de episodios cuyos archivos físicos no existen.
    Útil para limpiar la base de datos después de borrar archivos manualmente.
    """
    all_episodes = crud.get_episodes(db, skip=0, limit=10000)
    deleted_count = 0
    errors = []

    for episode in all_episodes:
        # Verificar si el archivo existe
        if episode.file_path and not os.path.exists(episode.file_path):
            try:
                crud.delete_episode(db, episode.id)
                deleted_count += 1
                print(f"🧹 Registro huérfano eliminado: {episode.title} (ID: {episode.id})")
            except Exception as e:
                print(f"❌ Error eliminando registro {episode.id}: {e}")
                errors.append(f"{episode.title}: {str(e)}")

    return {
        "status": "success",
        "message": f"Limpieza completada. {deleted_count} registros huérfanos eliminados.",
        "deleted": deleted_count,
        "errors": errors
    }