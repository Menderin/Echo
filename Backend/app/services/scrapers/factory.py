from .base import BaseScraper, ScraperError
from .youtube import YoutubeScraper
from .stream import StreamScraper

class ScraperFactory:
    @staticmethod
    def get_scraper(source: str) -> BaseScraper:
        if source == "youtube":
            return YoutubeScraper()
        elif source == "stream":
            return StreamScraper()
        else:
            raise ScraperError(f"Fuente no soportada: {source}")
