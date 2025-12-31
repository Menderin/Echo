from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Creamos la carpeta data si no existe (aunque Docker ya lo hace)
os.makedirs("data", exist_ok=True)

# URL de conexión a SQLite. El archivo se guardará en /app/data/radio.db
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/radio.db"

# connect_args={"check_same_thread": False} es necesario solo para SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependencia para obtener la sesión de DB en cada petición
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
