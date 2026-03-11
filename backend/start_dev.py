#!/usr/bin/env python3
"""
Script de inicio para desarrollo - Configura la base de datos y ejecuta el servidor
"""
import subprocess
import sys
import os
import time

def run_command(command, description):
    """Ejecutar un comando y mostrar el resultado"""
    print(f"\n🔧 {description}...")
    print(f"📝 Comando: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado exitosamente")
        if result.stdout:
            print(f"📤 Salida: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        if e.stderr:
            print(f"📥 Error: {e.stderr}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando entorno de desarrollo para Innexia BMC...")
    print("=" * 60)
    
    # Verificar que estemos en el directorio correcto
    if not os.path.exists("app"):
        print("❌ Error: Este script debe ejecutarse desde el directorio 'backend'")
        print("💡 Ejecuta: cd backend && python start_dev.py")
        return False
    
    # Paso 1: Instalar dependencias
    print("\n📦 PASO 1: Instalando dependencias...")
    if not run_command("pip install -r requirements.txt", "Instalación de dependencias"):
        print("❌ No se pudieron instalar las dependencias")
        return False
    
    # Paso 2: Configurar base de datos
    print("\n🗄️ PASO 2: Configurando base de datos...")
    if not run_command("python setup_database.py", "Configuración de base de datos"):
        print("❌ No se pudo configurar la base de datos")
        print("💡 Verifica que MySQL esté ejecutándose y las credenciales sean correctas")
        return False
    
    # Paso 3: Inicializar base de datos
    print("\n📝 PASO 3: Inicializando base de datos...")
    if not run_command("python init_db.py", "Inicialización de base de datos"):
        print("❌ No se pudo inicializar la base de datos")
        return False
    
    # Paso 4: Ejecutar migraciones (si existen)
    if os.path.exists("alembic.ini"):
        print("\n🔄 PASO 4: Ejecutando migraciones...")
        if not run_command("alembic upgrade head", "Ejecución de migraciones"):
            print("⚠️ Las migraciones fallaron, pero continuando...")
    
    # Paso 5: Iniciar servidor
    print("\n🌐 PASO 5: Iniciando servidor de desarrollo...")
    print("🎯 El servidor estará disponible en: http://localhost:8000")
    print("📚 Documentación de la API: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")
    print("\n⏹️ Para detener el servidor, presiona Ctrl+C")
    print("=" * 60)
    
    # Ejecutar el servidor
    try:
        run_command("python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload", "Servidor de desarrollo")
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
        return True
    except Exception as e:
        print(f"❌ Error al ejecutar el servidor: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 ¡Entorno de desarrollo configurado exitosamente!")
        print("📱 Ahora puedes ejecutar el frontend con: npm run dev")
    else:
        print("\n💥 Error en la configuración del entorno de desarrollo")
        sys.exit(1)

