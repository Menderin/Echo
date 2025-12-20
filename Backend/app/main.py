import sys
from pathlib import Path
from app.services.scraper import scrape

test_program = {
    "id": "test_youtube_short",
    "source": "youtube",
    "url": "https://www.youtube.com/watch?v=9bZkp7q19f0"  # Gangnam Style - conocido y corto
}

print("🔧 Probando scraper de radio...")
print(f"📥 Programa: {test_program['id']}")
print(f"🌐 URL: {test_program['url']}")

try:
    result = scrape(test_program)
    print(f"✅ ÉXITO: {result}")
except Exception as e:
    print(f"❌ ERROR durante la descarga: {e}")
    print("\n⚠️ Verifica que tengas instalado:")
    print("   1. ffmpeg - https://ffmpeg.org/download.html")
    print("   2. yt-dlp - Ya lo tienes según pip")