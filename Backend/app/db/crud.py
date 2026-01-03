from sqlalchemy.orm import Session
from . import models

def get_episode_by_url(db: Session, url: str):
    """Busca si ya existe un episodio con esa URL"""
    return db.query(models.Episode).filter(models.Episode.url == url).first()

def get_episode_by_file_path(db: Session, file_path: str):
    """Busca si ya existe un episodio con ese path de archivo"""
    return db.query(models.Episode).filter(models.Episode.file_path == file_path).first()


def get_episode(db: Session, episode_id: int):
    """Busca un episodio por su ID"""
    return db.query(models.Episode).filter(models.Episode.id == episode_id).first()

def get_episodes(db: Session, skip: int = 0, limit: int = 100):
    """Obtiene una lista de episodios ordenados por fecha de creación descendente"""
    return db.query(models.Episode).order_by(models.Episode.created_at.desc()).offset(skip).limit(limit).all()

def create_episode(db: Session, title: str, url: str, source: str, file_path: str):
    """Guarda un nuevo episodio en la base de datos"""
    db_episode = models.Episode(
        title=title,
        url=url,
        source=source,  # youtube, stream, local, etc.
        file_path=file_path
    )
    db.add(db_episode)
    db.commit()
    db.refresh(db_episode)
    return db_episode

def delete_episode(db: Session, episode_id: int):
    """Elimina un episodio de la base de datos"""
    db_episode = get_episode(db, episode_id)
    if db_episode:
        db.delete(db_episode)
        db.commit()
    return db_episode


# ===== FUNCIONES CRUD PARA SOURCES =====

def create_source(db: Session, source_data: dict):
    """Crea una nueva fuente de contenido"""
    db_source = models.Source(**source_data)
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


def get_sources(db: Session, skip: int = 0, limit: int = 100):
    """Obtiene lista de fuentes ordenadas por fecha de creación"""
    return db.query(models.Source).order_by(models.Source.created_at.desc()).offset(skip).limit(limit).all()


def get_source(db: Session, source_id: int):
    """Busca una fuente por su ID"""
    return db.query(models.Source).filter(models.Source.id == source_id).first()


def update_source(db: Session, source_id: int, source_data: dict):
    """Actualiza una fuente existente"""
    db_source = get_source(db, source_id)
    if db_source:
        for key, value in source_data.items():
            if value is not None:  # Solo actualizar campos no-None
                setattr(db_source, key, value)
        db.commit()
        db.refresh(db_source)
    return db_source


def delete_source(db: Session, source_id: int):
    """Elimina una fuente de la base de datos"""
    db_source = get_source(db, source_id)
    if db_source:
        db.delete(db_source)
        db.commit()
    return db_source

def create_log(db: Session, level: str, message: str, details: str = None, source: str = None):
    """Guarda un evento de log en la base de datos"""
    db_log = models.Log(
        level=level,
        message=message,
        details=details,
        source=source
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_logs(db: Session, skip: int = 0, limit: int = 50, level: str = None, start_date=None, end_date=None, q: str = None):
    """Obtiene logs con filtros simples: nivel, rango de fecha y búsqueda en mensaje/detalles"""
    query = db.query(models.Log)

    if level:
        query = query.filter(models.Log.level == level)

    if start_date:
        query = query.filter(models.Log.timestamp >= start_date)

    if end_date:
        query = query.filter(models.Log.timestamp <= end_date)

    if q:
        like_q = f"%{q}%"
        query = query.filter((models.Log.message.ilike(like_q)) | (models.Log.details.ilike(like_q)))

    total = query.count()
    items = query.order_by(models.Log.timestamp.desc()).offset(skip).limit(limit).all()
    return {"items": items, "total": total, "skip": skip, "limit": limit}