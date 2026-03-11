#!/usr/bin/env python3
"""
Script para probar la API del sistema multiempresas
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Probar health check"""
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
    except Exception as e:
        print(f"❌ Error en health check: {e}")
        return False

def test_root_endpoint():
    """Probar endpoint raíz"""
    print("\n🏠 Probando endpoint raíz...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Endpoint raíz exitoso")
            print(f"📊 Respuesta: {response.json()}")
            return True
        else:
            print(f"❌ Endpoint raíz falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en endpoint raíz: {e}")
        return False

def test_documentation():
    """Probar acceso a documentación"""
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
        print(f"❌ Error accediendo a documentación: {e}")
        return False

def test_company_endpoints():
    """Probar endpoints de empresa"""
    print("\n🏢 Probando endpoints de empresa...")
    
    # Obtener todas las empresas (requiere super admin)
    print("  📋 Probando obtener empresas...")
    try:
        response = requests.get(f"{BASE_URL}/api/company/")
        if response.status_code in [401, 403]:  # No autorizado o prohibido (esperado sin token)
            print("   ✅ Endpoint protegido correctamente")
            return True
        else:
            print(f"   ❌ Endpoint no protegido: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error probando empresas: {e}")
        return False

def test_auth_endpoints():
    """Probar endpoints de autenticación"""
    print("\n🔐 Probando endpoints de autenticación...")
    
    # Probar login con usuario Innexia
    print("  🔑 Probando login con usuario Innexia...")
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print("   ✅ Login exitoso")
            print(f"   🎫 Token obtenido: {token_data['access_token'][:50]}...")
            
            # Probar obtener información de la empresa
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            company_response = requests.get(f"{BASE_URL}/api/company/me", headers=headers)
            if company_response.status_code == 200:
                company_data = company_response.json()
                print("   ✅ Información de empresa obtenida")
                print(f"   🏢 Empresa: {company_data['name']} ({company_data['slug']})")
                print(f"   🎨 Colores: {company_data['primary_color']} / {company_data['secondary_color']}")
                return True
            else:
                print(f"   ❌ Error obteniendo empresa: {company_response.status_code}")
                return False
        else:
            print(f"   ❌ Login falló: {response.status_code}")
            print(f"   📝 Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error en login: {e}")
        return False

def test_multi_company_isolation():
    """Probar aislamiento entre empresas"""
    print("\n🔒 Probando aislamiento entre empresas...")
    
    # Login con usuario Innexia
    print("  🔑 Login con usuario Innexia...")
    try:
        innexia_login = {
            "username": "admin",
            "password": "admin123"
        }
        innexia_response = requests.post(f"{BASE_URL}/api/auth/login", data=innexia_login)
        if innexia_response.status_code != 200:
            print("   ❌ Login Innexia falló")
            return False
        
        innexia_token = innexia_response.json()["access_token"]
        innexia_headers = {"Authorization": f"Bearer {innexia_token}"}
        print("   ✅ Login Innexia exitoso")
        
        # Login con usuario TechCorp
        print("  🔑 Login con usuario TechCorp...")
        techcorp_login = {
            "username": "techcorp_admin",
            "password": "admin123"
        }
        techcorp_response = requests.post(f"{BASE_URL}/api/auth/login", data=techcorp_login)
        if techcorp_response.status_code != 200:
            print("   ❌ Login TechCorp falló")
            return False
        
        techcorp_token = techcorp_response.json()["access_token"]
        techcorp_headers = {"Authorization": f"Bearer {techcorp_token}"}
        print("   ✅ Login TechCorp exitoso")
        
        # Obtener información de empresa de cada usuario
        print("  🏢 Obteniendo información de empresas...")
        
        innexia_company = requests.get(f"{BASE_URL}/api/company/me", headers=innexia_headers)
        techcorp_company = requests.get(f"{BASE_URL}/api/company/me", headers=techcorp_headers)
        
        if innexia_company.status_code == 200 and techcorp_company.status_code == 200:
            innexia_data = innexia_company.json()
            techcorp_data = techcorp_company.json()
            
            print(f"   🏢 Innexia: {innexia_data['name']} - {innexia_data['primary_color']}")
            print(f"   🏢 TechCorp: {techcorp_data['name']} - {techcorp_data['primary_color']}")
            
            # Verificar que son empresas diferentes
            if innexia_data['id'] != techcorp_data['id']:
                print("   ✅ Aislamiento entre empresas confirmado")
                return True
            else:
                print("   ❌ Error: Usuarios acceden a la misma empresa")
                return False
        else:
            print("   ❌ Error obteniendo información de empresas")
            return False
            
    except Exception as e:
        print(f"   ❌ Error probando aislamiento: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas del sistema multiempresas...")
    print("=" * 60)
    
    tests = [
        test_health_check,
        test_root_endpoint,
        test_documentation,
        test_company_endpoints,
        test_auth_endpoints,
        test_multi_company_isolation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Error ejecutando prueba: {e}")
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS MULTIEMPRESAS")
    print(f"✅ Exitosas: {passed}")
    print(f"❌ Fallidas: {total - passed}")
    print(f"📈 Porcentaje: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ¡Todas las pruebas pasaron! El sistema multiempresas está funcionando correctamente.")
    else:
        print(f"\n⚠️ {total - passed} prueba(s) fallaron. Revisa los errores arriba.")
    
    print("\n🔗 Documentación de la API:")
    print(f"   📚 Swagger UI: {BASE_URL}/docs")
    print(f"   📖 ReDoc: {BASE_URL}/redoc")

if __name__ == "__main__":
    main()
