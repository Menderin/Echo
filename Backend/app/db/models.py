from sqlalchemy import Column, Integer, String, DateTime
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
