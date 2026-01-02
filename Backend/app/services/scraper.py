import os
from datetime import datetime
import pytz
from typing import Dict
from .scrapers.factory import ScraperFactory
from .scrapers.base import ScraperError

RAW_DIR = os.path.abspath("data/raw")

# Zona horaria de Chile
CHILE_TZ = pytz.timezone('America/Santiago')

def get_todays_dir() -> str:
    """
    Genera y crea la ruta del directorio para hoy: data/raw/YYYY/MM/DD
    Usa la zona horaria de Chile (America/Santiago)
    """
    now = datetime.now(CHILE_TZ)
    # Construimos la ruta: data/raw/2023/10/27
    todays_path = os.path.join(RAW_DIR, now.strftime("%Y"), now.strftime("%m"), now.strftime("%d"))
    
    if not os.path.exists(todays_path):
        os.makedirs(todays_path, exist_ok=True)
        
    return todays_path

def generate_filename(program_id: str) -> str:
    return f"{program_id}.mp3"

def scrape(program: Dict) -> Dict:
    """
    Descarga el audio de un programa y lo guarda en /data/raw/YYYY/MM/DD
    """
    program_id = program["id"]
    source = program["source"]
    url = program["url"]

    # Caso especial para local (no requiere descarga)
    if source == "local":
        return {
            "program_id": program_id,
            "source": source,
            "file_path": None,
            "status": "skipped"
        }

    try:
        # 1. Obtener el scraper adecuado usando la Factory
        scraper = ScraperFactory.get_scraper(source)
        
        # 2. Preparar rutas (Ahora con carpetas por fecha)
        output_dir = get_todays_dir()
        filename = generate_filename(program_id)
        output_path = os.path.join(output_dir, filename)
        
        # Normalizar path para consistencia (relativo, sin /app/)
        output_path = output_path.replace("\\", "/")
        if output_path.startswith("/app/"):
            output_path = output_path[5:]  # Remover "/app/"

        # 3. Ejecutar descarga
        scraper.download(url, output_path)

        return {
            "program_id": program_id,
            "source": source,
            "file_path": output_path,
            "status": "downloaded"
        }

    except ScraperError as e:
        raise e
    except Exception as e:
        raise ScraperError(f"Error inesperado en scrape: {str(e)}")
