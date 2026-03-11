import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Settings:
    # Configuración de la base de datos
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "bmc")
    DB_ECHO = os.getenv("DB_ECHO", "false").lower() == "true"

    # Configuración de seguridad
    SECRET_KEY = os.getenv("SECRET_KEY", "tu-clave-secreta-aqui-cambiar-en-produccion")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # Configuración del servidor
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"

    # Configuración de archivos
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))
    ALLOWED_EXTENSIONS = [".pdf", ".jpg", ".jpeg", ".png", ".docx", ".doc", ".xlsx", ".xls", ".txt"]

    # Configuración de CORS (en producción: CORS_ORIGINS = https://frontend-xxx.up.railway.app sin comillas)
    _cors_env = os.getenv("CORS_ORIGINS", "").strip().strip('"').strip("'")
    if _cors_env:
        # Separar por coma y quitar espacios/comillas de cada origen
        CORS_ORIGINS = [
            x.strip().strip('"').strip("'")
            for x in _cors_env.split(",")
            if x.strip()
        ]
    else:
        CORS_ORIGINS = [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:5173",
        ]

    # Configuración de la aplicación
    APP_NAME = os.getenv("APP_NAME", "Innexia BMC Backend")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    
    # Configuración de IA
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# Crear instancia de settings
settings = Settings()

# Crear directorio de uploads si no existe
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
