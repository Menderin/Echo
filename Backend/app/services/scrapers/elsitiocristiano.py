import requests
import re
from bs4 import BeautifulSoup
from .base import BaseScraper, ScraperError

class ElSitioCristianoScraper(BaseScraper):
    """
    Scraper para El Sitio Cristiano (elsitiocristiano.com)
    Obtiene automáticamente el último episodio de un programa mediante web scraping
    
    Estrategia:
    1. Parsear la página principal del programa para obtener el link del último episodio
    2. Acceder a la página del episodio y extraer la URL del MP3 del JavaScript
    3. Descargar el MP3 directamente
    """
    
    def download(self, url: str, output_path: str, **kwargs):
        """
        Descarga el último episodio de un programa de El Sitio Cristiano
        
        Args:
            url: URL de la página principal del programa
                 Ej: https://www.elsitiocristiano.com/ministries/el-amor-que-vale/?gawc=true
            output_path: Ruta donde guardar el archivo MP3
        """
        try:
            # Asegurar que estamos en la pagina de archivos (/listen/)
            if not url.endswith('/listen/') and not url.endswith('/listen'):
                url = url.rstrip('/') + '/listen/'
            
            # ===== PASO 1: Obtener el link del ultimo episodio =====
            print(f"Obteniendo lista de episodios de: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar links de episodios - patron especifico: /listen/titulo-12345.html
            episode_links = soup.find_all('a', href=re.compile(r'/listen/[^/]+-\d+\.html$'))
            
            if not episode_links:
                # Fallback: buscar cualquier link .html en /listen/
                episode_links = soup.find_all('a', href=re.compile(r'/listen/[^/]+\.html$'))
            
            if not episode_links:
                raise ScraperError("No se encontraron episodios en la pagina")
            
            # Tomar el primer link (episodio mas reciente)
            first_episode = episode_links[0]
            episode_url = first_episode.get('href')
            
            # Asegurar que sea URL completa
            if not episode_url.startswith('http'):
                episode_url = 'https://www.elsitiocristiano.com' + episode_url
            
            # Obtener titulo del episodio (separar de la fecha si viene pegada)
            raw_title = first_episode.get_text(strip=True)
            # El titulo viene con formato: "Nombre del Episodioenero 2, 2026"
            # Necesitamos separar solo el titulo
            # Buscamos patrones de fecha comunes y los removemos
            import re as regex_module
            # Patron para detectar meses en español seguidos de dia y año
            date_pattern = r'(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+\d{1,2},\s+\d{4}'
            episode_title = regex_module.sub(date_pattern, '', raw_title, flags=regex_module.IGNORECASE).strip()
            
            print(f"Ultimo episodio encontrado: {episode_title}")
            print(f"URL del episodio: {episode_url}")
            
            # ===== PASO 2: Extraer la URL del MP3 del JavaScript embebido =====
            print(f"📄 Obteniendo URL del MP3...")
            episode_response = requests.get(episode_url, timeout=30)
            episode_response.raise_for_status()
            
            # Buscar fileUrl en el JavaScript: fileUrl: 'https://...'
            pattern = r"fileUrl:\s*['\"]([^'\"]+)['\"]"
            match = re.search(pattern, episode_response.text)
            
            if not match:
                raise ScraperError("No se encontró la URL del MP3 en la página del episodio")
            
            mp3_url = match.group(1)
            print(f"✅ URL del MP3 encontrada")
            print(f"🔗 {mp3_url}")
            
            # ===== PASO 3: Descargar el archivo MP3 =====
            print(f"📥 Descargando MP3...")
            mp3_response = requests.get(mp3_url, stream=True, timeout=120)
            mp3_response.raise_for_status()
            
            # Obtener tamaño total si está disponible
            total_size = int(mp3_response.headers.get('content-length', 0))
            downloaded = 0
            
            # Descargar en chunks y mostrar progreso
            with open(output_path, 'wb') as f:
                for chunk in mp3_response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Mostrar progreso cada 1MB
                        if total_size > 0 and downloaded % (1024 * 1024) < 8192:
                            mb_downloaded = downloaded / (1024 * 1024)
                            mb_total = total_size / (1024 * 1024)
                            percentage = (downloaded / total_size) * 100
                            print(f"  Progreso: {mb_downloaded:.1f}/{mb_total:.1f} MB ({percentage:.1f}%)")
            
            print(f"✅ Descarga completada: {output_path}")
            print(f"📊 Tamaño total: {downloaded / (1024 * 1024):.1f} MB")
            
            # Retornar el titulo del episodio para guardar en BD
            return {"title": episode_title}
            
        except requests.RequestException as e:
            raise ScraperError(f"Error en la petición HTTP: {str(e)}")
        except Exception as e:
            raise ScraperError(f"Error descargando desde El Sitio Cristiano: {str(e)}")
