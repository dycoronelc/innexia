from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Configuración de la base de datos - SQLite para desarrollo, MySQL para producción
import os

# Verificar si MySQL está disponible, si no usar SQLite
try:
    import pymysql
    # Intentar conectar a MySQL
    connection = pymysql.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME
    )
    connection.close()
    # Si llegamos aquí, MySQL está disponible
    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    print("Usando MySQL como base de datos")
except Exception as e:
    # MySQL no está disponible, usar SQLite
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    print(f"MySQL no disponible ({e}), usando SQLite temporalmente")

# Crear el motor de la base de datos
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # Configuración específica para SQLite
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.DB_ECHO
    )
else:
    # Configuración para MySQL
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=settings.DB_ECHO
    )

# Crear la sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para los modelos
Base = declarative_base()

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para crear todas las tablas
def create_tables():
    Base.metadata.create_all(bind=engine)

# Función para eliminar todas las tablas (solo para desarrollo)
def drop_tables():
    Base.metadata.drop_all(bind=engine)
