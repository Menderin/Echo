import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from app.api.models import Program, SourceCreate, SourceUpdate, SourceResponse
from app.services.scraper import scrape, ScraperError
from app.db import models, crud, database
from app.api import logs as logs_api
from app.api import routes

# Crear las tablas en la base de datos al iniciar
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Radio Autonoma API",
    description="API para gestionar descargas y transmisiones de radio",
    version="1.0.0"
)

# Registrar routers
app.include_router(logs_api.router)
app.include_router(routes.router)

# Configurar CORS para permitir que el Frontend hable con el Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, cambia esto por la URL real del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
