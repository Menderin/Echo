from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from datetime import datetime
import pytz
from .database import Base

# Zona horaria de Chile
CHILE_TZ = pytz.timezone('America/Santiago')

class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)  # nombreEpisodio
    source = Column(String, index=True) # youtube, stream, local, etc.
    duration = Column(String, nullable=True) # duración
    url = Column(String, unique=True, index=True) # link (Unique para evitar duplicados)
    file_path = Column(String) # Donde se guardó el archivo
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(CHILE_TZ))


class Source(Base):
    """Modelo para gestionar fuentes de contenido (radios, canales YouTube, etc.)"""
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)  # "Radio Japón", "Noticias Telemundo"
    source_type = Column(String)  # "youtube", "stream"
    url = Column(String)  # URL principal o identificador
    description = Column(String, nullable=True)  # Descripción opcional
    schedule_time = Column(String, nullable=True)  # "07:00", "15:00" (para referencia)
    duration_minutes = Column(Integer, nullable=True)  # Duración esperada en minutos
    active = Column(Boolean, default=True)  # Si está activa o no
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(CHILE_TZ))
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=lambda: datetime.now(CHILE_TZ))


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String, index=True)  # INFO, WARN, ERROR
    message = Column(String, index=True)
    details = Column(Text, nullable=True)
    source = Column(String, index=True, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(CHILE_TZ))