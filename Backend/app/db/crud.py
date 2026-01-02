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

