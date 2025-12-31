import subprocess
import os
from .base import BaseScraper, ScraperError

class YoutubeScraper(BaseScraper):
    def download(self, url: str, output_path: str, **kwargs):
        # Separar el directorio y el nombre del archivo
        output_dir = os.path.dirname(output_path)
        output_filename = os.path.basename(output_path)
        
        # yt-dlp usa templates para el nombre del archivo
        # Usamos %(ext)s para que automáticamente use la extensión correcta
        output_template = os.path.join(output_dir, output_filename)
        
        command = [
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "192K",
            "-o", output_template,
            "--no-playlist",  # Evitar descargar playlists completas
            url
        ]

        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0:
                raise ScraperError(f"YouTube download failed: {result.stderr}")
        except Exception as e:
            raise ScraperError(f"Error executing yt-dlp: {str(e)}")
