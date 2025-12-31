import subprocess
from .base import BaseScraper, ScraperError

class YoutubeScraper(BaseScraper):
    def download(self, url: str, output_path: str, **kwargs):
        command = [
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "192K",
            "-o", output_path,
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
