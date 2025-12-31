from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base

class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)  # nombreEpisodio
    station_name = Column(String, index=True) # radioEmisora (Por ahora texto, luego FK)
    duration = Column(String, nullable=True) # duración
    url = Column(String, unique=True, index=True) # link (Unique para evitar duplicados)
    file_path = Column(String) # Donde se guardó el archivo
    created_at = Column(DateTime(timezone=True), server_default=func.now())
