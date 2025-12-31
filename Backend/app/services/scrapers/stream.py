import subprocess
from .base import BaseScraper, ScraperError

class StreamScraper(BaseScraper):
    def download(self, url: str, output_path: str, **kwargs):
        # Duración por defecto 60 min si no se especifica
        duration_minutes = kwargs.get("duration_minutes", 60)
        
        command = [
            "ffmpeg",
            "-y",
            "-i", url,
            "-t", str(duration_minutes * 60),
            "-vn",
            "-acodec", "libmp3lame",
            output_path
        ]

        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0:
                raise ScraperError(f"Stream capture failed: {result.stderr}")
        except Exception as e:
            raise ScraperError(f"Error executing ffmpeg: {str(e)}")
