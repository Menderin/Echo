radio-automation-system/
│
├── 📂 backend/                 # Todo lo relacionado con Python
│   ├── 📂 app/
│   │   ├── 📂 api/             # Endpoints para el Dashboard (FastAPI)
│   │   │   ├── routes.py       # Ej: /status, /force-download
│   │   │   └── models.py       # Modelos Pydantic para la API
│   │   │
│   │   ├── 📂 core/            # Configuraciones generales
│   │   │   └── config.py       # Variables de entorno, rutas de carpetas
│   │   │
│   │   ├── 📂 db/              # Base de datos
│   │   │   ├── database.py     # Conexión SQLite
│   │   │   └── crud.py         # Funciones para leer/escribir logs
│   │   │
│   │   ├── 📂 services/        # LA LÓGICA PRINCIPAL (Aquí ocurre la magia)
│   │   │   ├── 📜 scheduler.py # APScheduler (Orquesta cuándo ejecutar qué)
│   │   │   ├── 📜 scraper.py   # Lógica de yt-dlp y requests (Descargas)
│   │   │   ├── 📜 editor.py    # Lógica de pydub (Recortes y normalización)
│   │   │   └── 📜 drive.py     # Lógica de subida a la nube
│   │   │
│   │   └── main.py             # Punto de entrada (Inicia FastAPI + Scheduler)
│   │
│   ├── 📂 tests/               # Tests unitarios (importante para validar recortes)
│   ├── requirements.txt        # Dependencias (yt-dlp, pydub, fastapi, etc.)
│   └── Dockerfile              # Para contenerizar el backend
│
├── 📂 frontend/                # Todo lo relacionado con el Dashboard
│   ├── 📂 src/
│   │   ├── 📂 components/      # Tablas, botones, alertas
│   │   ├── 📂 services/        # Llamadas a tu API de Python (fetch/axios)
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile              # Para contenerizar el frontend (nginx/node)
│
├── 📂 data/                    # (IGNORAR EN GIT) Almacenamiento local temporal
│   ├── 📂 raw/                 # Descargas crudas (antes de editar)
│   ├── 📂 processed/           # Audios editados listos para Antofagasta
│   └── 📜 radio.db             # Archivo SQLite
│
├── 📜 schedule_config.yaml     # CRÍTICO: La configuración de los programas
├── 📜 docker-compose.yml       # Orquestación de Backend + Frontend
├── 📜 .gitignore               # Importante: ignorar carpeta /data y venv
└── 📜 README.md                # Documentación de cómo instalarw