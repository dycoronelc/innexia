"""
Configuración de logging para suprimir warnings específicos
"""
import logging
import warnings
import os

def configure_logging():
    """Configurar logging y suprimir warnings específicos"""
    
    # Suprimir warnings de bcrypt/passlib compatibility
    warnings.filterwarnings("ignore", message=".*bcrypt.*", category=UserWarning)
    warnings.filterwarnings("ignore", message=".*passlib.*", category=UserWarning)
    
    # Configurar logging básico
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Suprimir logs específicos de bcrypt
    bcrypt_logger = logging.getLogger('bcrypt')
    bcrypt_logger.setLevel(logging.ERROR)
    
    passlib_logger = logging.getLogger('passlib')
    passlib_logger.setLevel(logging.ERROR)
    
    # Suprimir logs de SQLAlchemy que no son críticos
    sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
    sqlalchemy_logger.setLevel(logging.WARNING)
    
    sqlalchemy_pool_logger = logging.getLogger('sqlalchemy.pool')
    sqlalchemy_pool_logger.setLevel(logging.WARNING)

# Configurar logging al importar el módulo
configure_logging()

