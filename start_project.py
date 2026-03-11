#!/usr/bin/env python3
"""
Script de inicio completo para Innexia Business Model Canvas
Configura y ejecuta tanto backend como frontend
"""
import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def print_header():
    """Imprimir encabezado del proyecto"""
    print("🚀" + "="*60)
    print("🎯 INNEXIA BUSINESS MODEL CANVAS")
    print("📱 PWA + Backend + Frontend Completo")
    print("="*60 + "🚀")
    print()

def check_requirements():
    """Verificar requisitos del sistema"""
    print("🔍 Verificando requisitos del sistema...")
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("❌ Se requiere Python 3.8 o superior")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    
    # Verificar Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()} detectado")
        else:
            print("❌ Node.js no está instalado")
            return False
    except FileNotFoundError:
        print("❌ Node.js no está instalado")
        return False
    
    # Verificar npm
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm {result.stdout.strip()} detectado")
        else:
            print("❌ npm no está disponible")
            return False
    except FileNotFoundError:
        print("❌ npm no está disponible")
        return False
    
    # Verificar MySQL
    try:
        result = subprocess.run(['mysql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ MySQL detectado")
        else:
            print("❌ MySQL no está disponible")
            return False
    except FileNotFoundError:
        print("❌ MySQL no está disponible")
        return False
    
    print("✅ Todos los requisitos están satisfechos")
    return True

def setup_backend():
    """Configurar y ejecutar el backend"""
    print("\n🔧 Configurando Backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Directorio 'backend' no encontrado")
        return False
    
    os.chdir(backend_dir)
    
    # Instalar dependencias
    print("📦 Instalando dependencias de Python...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencias instaladas")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False
    
    # Configurar base de datos
    print("🗄️ Configurando base de datos...")
    try:
        subprocess.run([sys.executable, "setup_database.py"], check=True, capture_output=True)
        print("✅ Base de datos configurada")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error configurando base de datos: {e}")
        return False
    
    # Inicializar base de datos
    print("📝 Inicializando base de datos...")
    try:
        subprocess.run([sys.executable, "init_db.py"], check=True, capture_output=True)
        print("✅ Base de datos inicializada")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error inicializando base de datos: {e}")
        return False
    
    os.chdir("..")
    return True

def setup_frontend():
    """Configurar el frontend"""
    print("\n🎨 Configurando Frontend...")
    
    # Verificar si existe package.json
    if not Path("package.json").exists():
        print("❌ package.json no encontrado")
        return False
    
    # Instalar dependencias
    print("📦 Instalando dependencias de Node.js...")
    try:
        subprocess.run(['npm', 'install'], check=True, capture_output=True)
        print("✅ Dependencias instaladas")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False
    
    return True

def start_backend():
    """Iniciar el backend en segundo plano"""
    print("\n🌐 Iniciando Backend...")
    
    backend_dir = Path("backend")
    os.chdir(backend_dir)
    
    try:
        # Iniciar servidor en segundo plano
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "app.main:app",
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Esperar un poco para que el servidor inicie
        time.sleep(3)
        
        # Verificar si el servidor está funcionando
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend iniciado exitosamente en http://localhost:8000")
                print("📚 Documentación: http://localhost:8000/docs")
                os.chdir("..")
                return process
            else:
                print("❌ Backend no responde correctamente")
                process.terminate()
                os.chdir("..")
                return None
        except ImportError:
            print("⚠️ requests no disponible, asumiendo que el backend está funcionando")
            os.chdir("..")
            return process
        except Exception as e:
            print(f"❌ Error verificando backend: {e}")
            process.terminate()
            os.chdir("..")
            return None
            
    except Exception as e:
        print(f"❌ Error iniciando backend: {e}")
        os.chdir("..")
        return None

def start_frontend():
    """Iniciar el frontend"""
    print("\n📱 Iniciando Frontend...")
    
    try:
        # Iniciar servidor de desarrollo
        subprocess.run(['npm', 'run', 'dev'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error iniciando frontend: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Frontend detenido por el usuario")
        return True
    
    return True

def open_browsers():
    """Abrir navegadores con las URLs del proyecto"""
    print("\n🌐 Abriendo navegadores...")
    
    urls = [
        "http://localhost:8000/docs",  # API Docs
        "http://localhost:3000",       # Frontend
    ]
    
    for url in urls:
        try:
            webbrowser.open(url)
            print(f"✅ Abierto: {url}")
        except Exception as e:
            print(f"⚠️ No se pudo abrir: {url}")

def main():
    """Función principal"""
    print_header()
    
    # Verificar requisitos
    if not check_requirements():
        print("\n💥 Requisitos no satisfechos. Por favor, instala los componentes faltantes.")
        return False
    
    # Configurar backend
    if not setup_backend():
        print("\n💥 Error configurando backend")
        return False
    
    # Configurar frontend
    if not setup_frontend():
        print("\n💥 Error configurando frontend")
        return False
    
    # Iniciar backend
    backend_process = start_backend()
    if not backend_process:
        print("\n💥 Error iniciando backend")
        return False
    
    # Esperar un poco más para que el backend esté completamente listo
    time.sleep(2)
    
    # Abrir navegadores
    open_browsers()
    
    print("\n🎉 ¡Proyecto iniciado exitosamente!")
    print("="*60)
    print("📱 Frontend: http://localhost:3000")
    print("🔧 Backend: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔍 Health: http://localhost:8000/health")
    print("\n⏹️ Para detener todo, presiona Ctrl+C")
    print("="*60)
    
    try:
        # Iniciar frontend (esto bloqueará hasta que se detenga)
        start_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servicios...")
    
    # Limpiar procesos
    if backend_process:
        print("🛑 Deteniendo backend...")
        backend_process.terminate()
        backend_process.wait()
    
    print("\n👋 ¡Hasta luego!")
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)


