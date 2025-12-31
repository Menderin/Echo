from fastapi import FastAPI, HTTPException, Depends
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

@app.get("/")
async def root():
    return {"status": "online", "message": "Radio Autonoma Backend is running"}

@app.post("/scrape")
async def run_scraper(program: Program, db: Session = Depends(database.get_db)):
    """
    Inicia la descarga de un programa.
    Verifica primero si ya existe en la base de datos.
    """
    # 1. Verificar si ya existe
    existing_episode = crud.get_episode_by_url(db, url=program.url)
    if existing_episode:
        print(f"⚠️ Episodio ya existe: {existing_episode.title}")
        return {
            "status": "skipped",
            "message": "El episodio ya fue descargado anteriormente",
            "data": {
                "id": existing_episode.id,
                "title": existing_episode.title,
                "file_path": existing_episode.file_path
            }
        }

    try:
        # 2. Si no existe, procedemos a descargar
        program_dict = program.dict()
        print(f"📥 Iniciando descarga: {program.id}")
        
        result = scrape(program_dict)
        
        # 3. Guardar en Base de Datos
        if result["status"] == "downloaded":
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