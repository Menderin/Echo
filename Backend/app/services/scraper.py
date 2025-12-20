import os
import subprocess
from datetime import datetime
from typing import Dict


RAW_DIR = os.path.abspath("data/raw")


class ScraperError(Exception):
    pass


def ensure_raw_dir():
    if not os.path.exists(RAW_DIR):
        os.makedirs(RAW_DIR, exist_ok=True)


def generate_filename(program_id: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    return f"{program_id}_{timestamp}.mp3"


def download_youtube(url: str, output_path: str):
    command = [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "--audio-quality", "192K",
        "-o", output_path,
        url
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        raise ScraperError(f"YouTube download failed: {result.stderr}")


def download_stream(url: str, output_path: str, duration_minutes: int = 60):
    command = [
        "ffmpeg",
        "-y",
        "-i", url,
        "-t", str(duration_minutes * 60),
        "-vn",
        "-acodec", "libmp3lame",
        output_path
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        raise ScraperError(f"Stream capture failed: {result.stderr}")


def scrape(program: Dict) -> Dict:
    """
    Descarga el audio de un programa y lo guarda en /data/raw
    """

    ensure_raw_dir()

    program_id = program["id"]
    source = program["source"]
    url = program["url"]

    filename = generate_filename(program_id)
    output_path = os.path.join(RAW_DIR, filename)

    if source == "youtube":
        download_youtube(url, output_path)

    elif source == "stream":
        # duración por defecto: 60 min (puede venir luego desde YAML)
        download_stream(url, output_path)

    elif source == "local":
        # No se descarga nada
        return {
            "program_id": program_id,
            "source": source,
            "file_path": None,
            "status": "skipped"
        }

    else:
        raise ScraperError(f"Fuente no soportada: {source}")

    return {
        "program_id": program_id,
        "source": source,
        "file_path": output_path,
        "status": "downloaded"
    }
