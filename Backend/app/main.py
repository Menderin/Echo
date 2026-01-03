import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from app.api.models import Program, SourceCreate, SourceUpdate, SourceResponse
from app.services.scraper import scrape, ScraperError
from app.db import models, crud, database
from app.api import logs as logs_api

# Crear las tablas en la base de datos al iniciar
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Radio Autonoma API",
    description="API para gestionar descargas y transmisiones de radio",
    version="1.0.0"
)

# Registrar router de logs
app.include_router(logs_api.router)

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
            try:
                crud.create_log(db=db, level="INFO", message=f"Episodio ya existe: {existing_episode.title}", details=None, source="scrape")
            except Exception:
                pass
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
                try:
                    crud.create_log(db=db, level="INFO", message=f"Episodio re-descargado y actualizado: {existing_episode.title}", details=None, source="scrape")
                except Exception:
                    pass
            else:
                # Si es nuevo, creamos uno nuevo
                new_episode = crud.create_episode(
                    db=db,
                    title=program.id,
                    url=program.url,
                    source=program.source,  # youtube, stream, etc.
                    file_path=result["file_path"]
                )
                print(f"💾 Guardado en DB: ID {new_episode.id}")
                try:
                    crud.create_log(db=db, level="INFO", message=f"Episodio descargado: {new_episode.title}", details=None, source="scrape")
                except Exception:
                    pass

        return {
            "status": "success",
            "data": result
        }
        
    except ScraperError as e:
        try:
            crud.create_log(db=db, level="ERROR", message=str(e), details=None, source="scrape")
        except Exception:
            pass
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error crítico: {e}")
        try:
            crud.create_log(db=db, level="ERROR", message=str(e), details=None, source="scrape")
        except Exception:
            pass
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
    try:
        crud.create_log(db=db, level="INFO", message=f"Episodio eliminado: {episode.title}", details=None, source="delete")
    except Exception:
        pass
    
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
                # Normalizar path para consistencia (barras inclinadas y relativo)
                full_path = full_path.replace("\\", "/")
                
                # Asegurar que la ruta sea relativa (sin /app/ al inicio)
                if full_path.startswith("/app/"):
                    full_path = full_path[5:]  # Remover "/app/"
                
                # Verificar si ya existe en BD
                existing = crud.get_episode_by_file_path(db, full_path)
                if not existing:
                    try:
                        # Crear registro
                        # Usamos el nombre del archivo (sin extensión) como ID/Título
                        file_id = os.path.splitext(file)[0]
                        
                        # Intentar determinar el source original
                        # Buscar si existe otro registro con el mismo título (podría ser descarga previa)
                        potential_source = "local"
                        
                        # Buscar en la BD por título similar
                        all_episodes = crud.get_episodes(db, skip=0, limit=1000)
                        for ep in all_episodes:
                            if ep.title and ep.title.strip() == file_id.strip():
                                # Si encontramos un match por título, usar su source
                                potential_source = ep.source
                                break
                        
                        crud.create_episode(
                            db=db,
                            title=file_id,
                            url=f"local://{file_id}",  # URL ficticia para locales
                            source=potential_source,  # Detectado o "local"
                            file_path=full_path
                        )
                        added_count += 1
                        print(f"➕ Archivo importado: {file} (source: {potential_source})")
                    except Exception as e:
                        print(f"❌ Error importando {file}: {e}")
                        errors.append(f"{file}: {str(e)}")
                        try:
                            crud.create_log(db=db, level="ERROR", message=f"Error importando {file}", details=str(e), source="sync")
                        except Exception:
                            pass

    return {
        "status": "success", 
        "message": f"Sincronización completada. {added_count} archivos nuevos añadidos.",
        "added": added_count,
        "errors": errors
    }

@app.post("/cleanup")
async def cleanup_orphaned_records(db: Session = Depends(database.get_db)):
    """
    1. Normaliza todas las rutas de archivo (remueve /app/ si existe)
    2. Elimina de la BD los registros de episodios cuyos archivos físicos no existen
    3. Elimina duplicados basados en file_path
    """
    all_episodes = crud.get_episodes(db, skip=0, limit=10000)
    deleted_count = 0
    normalized_count = 0
    duplicates_removed = 0
    errors = []
    
    # 1. Normalizar rutas y eliminar huérfanos
    for episode in all_episodes:
        # Normalizar path si tiene /app/
        if episode.file_path and episode.file_path.startswith("/app/"):
            new_path = episode.file_path[5:]  # Remover "/app/"
            episode.file_path = new_path
            db.commit()
            normalized_count += 1
            print(f"🔄 Ruta normalizada: {new_path}")
        
        # Verificar si el archivo existe
        if episode.file_path and not os.path.exists(episode.file_path):
            try:
                crud.delete_episode(db, episode.id)
                deleted_count += 1
                print(f"🧹 Registro huérfano eliminado: {episode.title} (ID: {episode.id})")
            except Exception as e:
                print(f"❌ Error eliminando registro {episode.id}: {e}")
                errors.append(f"{episode.title}: {str(e)}")
                try:
                    crud.create_log(db=db, level="ERROR", message=f"Error eliminando registro {episode.id}", details=str(e), source="cleanup")
                except Exception:
                    pass
    
    # 2. Eliminar duplicados (mismo file_path)
    # Recargar episodios después de normalización
    all_episodes = crud.get_episodes(db, skip=0, limit=10000)
    seen_paths = {}
    for episode in all_episodes:
        if episode.file_path in seen_paths:
            # Es un duplicado, eliminar este
            try:
                crud.delete_episode(db, episode.id)
                duplicates_removed += 1
                print(f"🗑️ Duplicado eliminado: {episode.title} (ID: {episode.id})")
            except Exception as e:
                print(f"❌ Error eliminando duplicado {episode.id}: {e}")
                errors.append(f"{episode.title}: {str(e)}")
                try:
                    crud.create_log(db=db, level="ERROR", message=f"Error eliminando registro {episode.id}", details=str(e), source="cleanup")
                except Exception:
                    pass
        else:
            seen_paths[episode.file_path] = episode.id

    return {
        "status": "success",
        "message": f"Limpieza completada. {normalized_count} rutas normalizadas, {deleted_count} registros huérfanos eliminados, {duplicates_removed} duplicados eliminados.",
        "normalized": normalized_count,
        "deleted": deleted_count,
        "duplicates_removed": duplicates_removed,
        "errors": errors
    }

# ===== DESCARGA AUTOMATICA DE TODAS LAS FUENTES =====

@app.post("/download-all-sources")
async def download_all_sources(db: Session = Depends(database.get_db)):
    """
    Descarga el ultimo episodio de todas las fuentes activas.
    Util para automatizacion programada (cron jobs).
    """
    # Obtener todas las fuentes activas
    sources = crud.get_sources(db, skip=0, limit=1000)
    active_sources = [s for s in sources if s.active]
    
    if not active_sources:
        return {
            "status": "success",
            "message": "No hay fuentes activas para descargar",
            "downloaded": 0,
            "skipped": 0,
            "errors": []
        }
    
    results = {
        "downloaded": 0,
        "skipped": 0,
        "errors": []
    }
    
    print(f"\n{'='*60}")
    print(f"INICIANDO DESCARGA AUTOMATICA DE {len(active_sources)} FUENTES")
    print(f"{'='*60}\n")
    
    for source in active_sources:
        try:
            print(f"\nProcesando: {source.name}")
            print(f"   Tipo: {source.source_type}")
            print(f"   URL: {source.url}")
            
            # Verificar si ya existe en BD
            existing = crud.get_episode_by_url(db, url=source.url)
            
            if existing and existing.file_path and os.path.exists(existing.file_path):
                print(f"   Ya existe, saltando...")
                results["skipped"] += 1
                continue
            
            # Preparar datos para scrape
            program_data = {
                "id": source.name.lower().replace(" ", "_"),
                "source": source.source_type,
                "url": source.url
            }
            
            # Ejecutar descarga
            result = scrape(program_data)
            
            if result["status"] == "downloaded":
                # Guardar en BD usando el titulo real del episodio
                episode_title = result.get("title") or source.name  # Fallback a source.name si no hay titulo
                new_episode = crud.create_episode(
                    db=db,
                    title=episode_title,
                    url=source.url,
                    source=source.source_type,
                    file_path=result["file_path"]
                )
                print(f"   Descargado exitosamente: {result['file_path']}")
                results["downloaded"] += 1
            else:
                print(f"   Saltado (no se descargo)")
                results["skipped"] += 1
                
        except Exception as e:
            error_msg = f"{source.name}: {str(e)}"
            print(f"   Error: {error_msg}")
            results["errors"].append(error_msg)
    
    print(f"\n{'='*60}")
    print(f"RESUMEN:")
    print(f"   Descargados: {results['downloaded']}")
    print(f"   Saltados: {results['skipped']}")
    print(f"   Errores: {len(results['errors'])}")
    print(f"{'='*60}\n")
    
    return {
        "status": "success",
        "message": f"Proceso completado. {results['downloaded']} fuentes descargadas, {results['skipped']} saltadas, {len(results['errors'])} errores.",
        "downloaded": results["downloaded"],
        "skipped": results["skipped"],
        "errors": results["errors"]
    }


# ===== ENDPOINTS PARA GESTION DE FUENTES =====

@app.post("/sources", response_model=SourceResponse, status_code=201)
async def create_source(source: SourceCreate, db: Session = Depends(database.get_db)):
    """Crea una nueva fuente de contenido"""
    try:
        source_data = source.model_dump()
        new_source = crud.create_source(db, source_data)
        return new_source
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando fuente: {str(e)}")


@app.get("/sources", response_model=List[SourceResponse])
async def read_sources(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    """Obtiene la lista de fuentes de contenido"""
    sources = crud.get_sources(db, skip=skip, limit=limit)
    return sources


@app.get("/sources/{source_id}", response_model=SourceResponse)
async def read_source(source_id: int, db: Session = Depends(database.get_db)):
    """Obtiene una fuente especifica por ID"""
    source = crud.get_source(db, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Fuente no encontrada")
    return source


@app.put("/sources/{source_id}", response_model=SourceResponse)
async def update_source(source_id: int, source: SourceUpdate, db: Session = Depends(database.get_db)):
    """Actualiza una fuente existente"""
    source_data = source.model_dump(exclude_unset=True)
    updated_source = crud.update_source(db, source_id, source_data)
    
    if not updated_source:
        raise HTTPException(status_code=404, detail="Fuente no encontrada")
    
    return updated_source


@app.delete("/sources/{source_id}")
async def delete_source(source_id: int, db: Session = Depends(database.get_db)):
    """Elimina una fuente de contenido"""
    deleted_source = crud.delete_source(db, source_id)
    
    if not deleted_source:
        raise HTTPException(status_code=404, detail="Fuente no encontrada")
    
    return {"status": "success", "message": f"Fuente {source_id} eliminada exitosamente"}
