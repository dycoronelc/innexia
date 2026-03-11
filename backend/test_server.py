#!/usr/bin/env python3
"""
Script simple para probar el servidor
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔍 Importando configuración...")
    from app.config import settings
    print(f"✅ Configuración cargada - DB_HOST: {settings.DB_HOST}")
    
    print("🔍 Importando aplicación...")
    from app.main import app
    print("✅ Aplicación importada exitosamente")
    
    print("🔍 Verificando endpoints...")
    routes = [route.path for route in app.routes]
    print(f"✅ Rutas disponibles: {len(routes)}")
    
    print("🔍 Iniciando servidor de prueba...")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)




