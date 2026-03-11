"""
Configuración inicial de la aplicación
"""
import warnings
import logging
import os

# Configurar warnings ANTES de importar cualquier módulo que use bcrypt
warnings.filterwarnings("ignore", message=".*bcrypt.*", category=UserWarning)
warnings.filterwarnings("ignore", message=".*passlib.*", category=UserWarning)
warnings.filterwarnings("ignore", message=".*trapped.*", category=UserWarning)

# Configurar logging para suprimir logs innecesarios
logging.getLogger('bcrypt').setLevel(logging.ERROR)
logging.getLogger('passlib').setLevel(logging.ERROR)

print("Configuracion de warnings aplicada")