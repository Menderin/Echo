import os
from datetime import datetime
import pytz
from typing import Dict
from .scrapers.factory import ScraperFactory
from .scrapers.base import ScraperError

# Determinar ruta de datos según entorno
# En Docker (/app) data está mapeado en /app/data
# En local (Backend/) data está en ../data
if os.path.exists("/.dockerenv"):
    RAW_DIR = os.path.abspath("data/raw")
else:
    # Subir 4 niveles: services -> app -> Backend -> Radio-Autonoma (Raíz)
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")

# Zona horaria de Chile
CHILE_TZ = pytz.timezone('America/Santiago')

def get_todays_dir(source_name: str) -> str:
    """
    Genera y crea la ruta del directorio para hoy: data/raw/SOURCE/YYYY/MM/DD
    Usa la zona horaria de Chile (America/Santiago)
    """
    now = datetime.now(CHILE_TZ)
    # Construimos la ruta: data/raw/youtube/2023/10/27
    todays_path = os.path.join(RAW_DIR, source_name, now.strftime("%Y"), now.strftime("%m"), now.strftime("%d"))
    
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
        
        # 2. Preparar rutas (Ahora con carpetas por fuente y fecha)
        output_dir = get_todays_dir(source)
        filename = generate_filename(program_id)
        output_path = os.path.join(output_dir, filename)
        
        # Normalizar path para consistencia (relativo, sin /app/)
        output_path = output_path.replace("\\", "/")
        if output_path.startswith("/app/"):
            output_path = output_path[5:]  # Remover "/app/"

        # 3. Ejecutar descarga
        scraper_result = scraper.download(url, output_path)
        
        # Obtener título del episodio si el scraper lo retorna
        episode_title = None
        if scraper_result and isinstance(scraper_result, dict):
            episode_title = scraper_result.get("title")

        return {
            "program_id": program_id,
            "source": source,
            "file_path": output_path,
            "title": episode_title,  # Titulo real del episodio
            "status": "downloaded"
        }

    except ScraperError as e:
        raise e
    except Exception as e:
        raise ScraperError(f"Error inesperado en scrape: {str(e)}")
