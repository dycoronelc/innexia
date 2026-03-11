#!/usr/bin/env python3
"""
Script de prueba para verificar que la API esté funcionando correctamente
"""
import requests
import json
import time
import sys

# Configuración
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

def test_health_check():
    """Probar el endpoint de health check"""
    print("🔍 Probando health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check exitoso")
            print(f"📊 Respuesta: {response.json()}")
            return True
        else:
            print(f"❌ Health check falló: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor")
        print("💡 Verifica que el servidor esté ejecutándose en http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_root_endpoint():
    """Probar el endpoint raíz"""
    print("\n🏠 Probando endpoint raíz...")
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("✅ Endpoint raíz exitoso")
            print(f"📊 Respuesta: {response.json()}")
            return True
        else:
            print(f"❌ Endpoint raíz falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_docs_endpoint():
    """Probar el endpoint de documentación"""
    print("\n📚 Probando endpoint de documentación...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ Documentación accesible")
            print(f"🌐 URL: {BASE_URL}/docs")
            return True
        else:
            print(f"❌ Documentación no accesible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_auth_endpoints():
    """Probar endpoints de autenticación"""
    print("\n🔐 Probando endpoints de autenticación...")
    
    # Probar registro de usuario
    print("  📝 Probando registro de usuario...")
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Usuario de Prueba",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{API_URL}/auth/register", json=register_data)
        if response.status_code in [200, 201, 422]:  # 422 es válido si el usuario ya existe
            print("✅ Endpoint de registro accesible")
            if response.status_code == 422:
                print("ℹ️ Usuario ya existe (esto es normal)")
            else:
                print(f"📊 Respuesta: {response.json()}")
        else:
            print(f"❌ Endpoint de registro falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en registro: {e}")
        return False
    
    # Probar login
    print("  🔑 Probando login...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{API_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            print("✅ Login exitoso")
            token_data = response.json()
            print(f"🎫 Token obtenido: {token_data.get('access_token', 'No disponible')[:20]}...")
            return token_data.get('access_token')
        else:
            print(f"❌ Login falló: {response.status_code}")
            print(f"📊 Respuesta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return None

def test_protected_endpoints(token):
    """Probar endpoints protegidos con el token"""
    if not token:
        print("\n⚠️ No se puede probar endpoints protegidos sin token")
        return False
    
    print(f"\n🔒 Probando endpoints protegidos...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Probar obtener usuarios
    print("  👥 Probando obtener usuarios...")
    try:
        response = requests.get(f"{API_URL}/users/", headers=headers)
        if response.status_code == 200:
            print("✅ Endpoint de usuarios accesible")
            users = response.json()
            print(f"📊 Usuarios encontrados: {len(users)}")
        else:
            print(f"❌ Endpoint de usuarios falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Probar obtener proyectos
    print("  📁 Probando obtener proyectos...")
    try:
        response = requests.get(f"{API_URL}/projects/", headers=headers)
        if response.status_code == 200:
            print("✅ Endpoint de proyectos accesible")
            projects = response.json()
            print(f"📊 Proyectos encontrados: {len(projects)}")
        else:
            print(f"❌ Endpoint de proyectos falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def main():
    """Función principal"""
    print("🧪 Iniciando pruebas de la API de Innexia BMC...")
    print("=" * 60)
    
    # Esperar un poco para que el servidor esté listo
    print("⏳ Esperando que el servidor esté listo...")
    time.sleep(2)
    
    # Ejecutar pruebas
    tests = [
        ("Health Check", test_health_check),
        ("Endpoint Raíz", test_root_endpoint),
        ("Documentación", test_docs_endpoint),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} falló")
    
    # Probar autenticación
    print("\n🔐 Probando sistema de autenticación...")
    token = test_auth_endpoints()
    if token:
        passed += 1
        total += 1
        
        # Probar endpoints protegidos
        if test_protected_endpoints(token):
            passed += 1
            total += 1
        else:
            print("❌ Endpoints protegidos fallaron")
    else:
        print("❌ Sistema de autenticación falló")
        total += 1
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print(f"✅ Exitosas: {passed}")
    print(f"❌ Fallidas: {total - passed}")
    print(f"📈 Porcentaje: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ¡Todas las pruebas pasaron! La API está funcionando correctamente.")
        print("📱 Ahora puedes integrar el frontend con el backend.")
    else:
        print(f"\n⚠️ {total - passed} prueba(s) fallaron. Revisa los errores arriba.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


