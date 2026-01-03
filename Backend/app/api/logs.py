from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db import crud
from app.db import database

router = APIRouter()


@router.get("/logs")
async def list_logs(skip: int = 0, limit: int = 50, level: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, q: Optional[str] = None, db: Session = Depends(database.get_db)):
    """Listado de logs con paginación y filtros básicos.

    - `level`: INFO, WARN, ERROR
    - `start_date` / `end_date`: ISO8601 strings
    - `q`: búsqueda en mensaje / detalles
    """
    sd = None
    ed = None
    try:
        if start_date:
            sd = datetime.fromisoformat(start_date)
        if end_date:
            ed = datetime.fromisoformat(end_date)
    except Exception:
        raise HTTPException(status_code=400, detail="start_date/end_date deben estar en formato ISO8601")

    result = crud.get_logs(db=db, skip=skip, limit=limit, level=level, start_date=sd, end_date=ed, q=q)

    # Serializar objetos SQLAlchemy a dicts simples
    items = []
    for it in result["items"]:
        items.append({
            "id": it.id,
            "level": it.level,
            "message": it.message,
            "details": it.details,
            "source": it.source,
            "timestamp": it.timestamp.isoformat() if it.timestamp else None
        })

    return {"items": items, "total": result["total"], "skip": result["skip"], "limit": result["limit"]}


@router.post("/logs")
async def create_log_endpoint(level: str, message: str, details: Optional[str] = None, source: Optional[str] = None, db: Session = Depends(database.get_db)):
    """Endpoint simple para crear logs (útil para pruebas o registro manual)."""
    log = crud.create_log(db=db, level=level, message=message, details=details, source=source)
    return {"status": "success", "id": log.id}