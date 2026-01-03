from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Program(BaseModel):
    id: str
    source: str  # youtube, stream, local
    url: str
    schedule_time: Optional[str] = None  # Para uso futuro (cronograma)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "morning_show",
                "source": "youtube",
                "url": "https://youtube.com/..."
            }
        }


# ===== MODELOS PARA GESTIÓN DE FUENTES =====

class SourceBase(BaseModel):
    """Modelo base para fuentes de contenido"""
    name: str
    source_type: str  # "youtube", "stream"
    url: str
    description: Optional[str] = None
    schedule_time: Optional[str] = None  # "07:00", "15:00"
    duration_minutes: Optional[int] = 60
    active: bool = True


class SourceCreate(SourceBase):
    """Modelo para crear una nueva fuente"""
    pass


class SourceUpdate(BaseModel):
    """Modelo para actualizar una fuente (todos los campos opcionales)"""
    name: Optional[str] = None
    source_type: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    schedule_time: Optional[str] = None
    duration_minutes: Optional[int] = None
    active: Optional[bool] = None


class SourceResponse(SourceBase):
    """Modelo de respuesta con campos adicionales de BD"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
