from abc import ABC, abstractmethod

class ScraperError(Exception):
    pass

class BaseScraper(ABC):
    @abstractmethod
    def download(self, url: str, output_path: str, **kwargs):
        """
        Descarga contenido desde la URL dada y lo guarda en output_path.
        Debe lanzar ScraperError en caso de fallo.
        """
        pass
