import os
from datetime import datetime
from typing import Dict
from .scrapers.factory import ScraperFactory
from .scrapers.base import ScraperError

RAW_DIR = os.path.abspath("data/raw")

def ensure_raw_dir():
    if not os.path.exists(RAW_DIR):
        os.makedirs(RAW_DIR, exist_ok=True)

def generate_filename(program_id: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    return f"{program_id}_{timestamp}.mp3"

def scrape(program: Dict) -> Dict:
    """
    Descarga el audio de un programa y lo guarda en /data/raw
    """
    ensure_raw_dir()

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
        
        # 2. Preparar rutas
        filename = generate_filename(program_id)
        output_path = os.path.join(RAW_DIR, filename)

        # 3. Ejecutar descarga
        # Podemos pasar parámetros extra si vienen en el dict 'program'
        scraper.download(url, output_path)

        return {
            "program_id": program_id,
            "source": source,
            "file_path": output_path,
            "status": "downloaded"
        }

    except ScraperError as e:
        # Re-lanzamos para que lo maneje el main.py
        raise e
    except Exception as e:
        raise ScraperError(f"Error inesperado en scrape: {str(e)}")
