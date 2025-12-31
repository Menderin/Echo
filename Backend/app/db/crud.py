from sqlalchemy.orm import Session
from . import models

def get_episode_by_url(db: Session, url: str):
    """Busca si ya existe un episodio con esa URL"""
    return db.query(models.Episode).filter(models.Episode.url == url).first()

def create_episode(db: Session, title: str, url: str, source: str, file_path: str):
    """Guarda un nuevo episodio en la base de datos"""
    db_episode = models.Episode(
        title=title,
        url=url,
        station_name=source, # Usamos 'source' como nombre de emisora por ahora
        file_path=file_path
    )
    db.add(db_episode)
    db.commit()
    db.refresh(db_episode)
    return db_episode
