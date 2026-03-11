# Script de Testing del Sistema InnovAI
# Fecha: 2025-01-09
# Objetivo: Probar funcionalidades principales del sistema

import requests
import json
import time

# Configuración
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_authentication():
    """Probar autenticación del sistema"""
    print("🔐 Testing: Autenticación")
    
    # Datos de login
    login_data = {
        "username": "admin",
        "password": "admin123", 
        "company_id": 1
    }
    
    try:
        # Login
        response = requests.post(f"{BASE_URL}/api/auth/login-company", json=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print(f"✅ Login exitoso - Token obtenido: {access_token[:20]}...")
            
            # Verificar token
            headers = {"Authorization": f"Bearer {access_token}"}
            me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
            
            if me_response.status_code == 200:
                user_data = me_response.json()
                print(f"✅ Token válido - Usuario: {user_data.get('username', 'N/A')}")
                return access_token
            else:
                print(f"❌ Token inválido - Status: {me_response.status_code}")
                return None
        else:
            print(f"❌ Login fallido - Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error en autenticación: {e}")
        return None

def test_guided_interview(token):
    """Probar entrevista guiada"""
    print("\n🎯 Testing: Entrevista Guiada")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Iniciar entrevista
        start_response = requests.post(f"{BASE_URL}/api/business-interview/start", headers=headers)
        
        if start_response.status_code == 200:
            interview_data = start_response.json()
            print(f"✅ Entrevista iniciada - Progreso: {interview_data.get('progress_percentage', 0)}%")
            
            # Verificar estructura de respuesta
            required_fields = ['current_question', 'progress_percentage', 'completed_fields', 'remaining_fields', 'is_complete']
            for field in required_fields:
                if field in interview_data:
                    print(f"  ✅ Campo '{field}' presente")
                else:
                    print(f"  ❌ Campo '{field}' faltante")
            
            return interview_data
        else:
            print(f"❌ Error iniciando entrevista - Status: {start_response.status_code}")
            print(f"Response: {start_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error en entrevista guiada: {e}")
        return None

def test_project_creation(token):
    """Probar creación de proyectos"""
    print("\n📁 Testing: Creación de Proyectos")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Datos del proyecto de prueba
        project_data = {
            "name": "Proyecto de Prueba - Testing",
            "description": "Proyecto creado para testing del sistema",
            "category": "Nuevo",
            "tags": ["testing", "prueba"],
            "location": "Sin ubicación",
            "status": "active"
        }
        
        # Crear proyecto
        create_response = requests.post(f"{BASE_URL}/api/projects/", json=project_data, headers=headers)
        
        if create_response.status_code in [200, 201]:
            project = create_response.json()
            print(f"✅ Proyecto creado - ID: {project.get('id')}, Nombre: {project.get('name')}")
            
            # Verificar que se puede obtener
            get_response = requests.get(f"{BASE_URL}/api/projects/{project.get('id')}", headers=headers)
            
            if get_response.status_code == 200:
                retrieved_project = get_response.json()
                print(f"✅ Proyecto recuperado - Verificación exitosa")
                return project.get('id')
            else:
                print(f"❌ Error recuperando proyecto - Status: {get_response.status_code}")
                return None
        else:
            print(f"❌ Error creando proyecto - Status: {create_response.status_code}")
            print(f"Response: {create_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error en creación de proyectos: {e}")
        return None

def test_bmc_generation(token, project_id):
    """Probar generación de BMC"""
    print("\n📊 Testing: Generación de BMC")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Datos para BMC
        bmc_data = {
            "business_idea": "Una plataforma de delivery de comida saludable para oficinas con opciones personalizadas según preferencias dietéticas",
            "project_id": project_id,
            "provider": "openai",
            "use_high_quality": True,
            "use_gpt4": False,
            "generate_activities": True
        }
        
        # Generar BMC
        bmc_response = requests.post(f"{BASE_URL}/api/chatbot/generate-bmc", json=bmc_data, headers=headers)
        
        if bmc_response.status_code == 200:
            bmc_result = bmc_response.json()
            print(f"✅ BMC generado exitosamente")
            
            # Verificar estructura del BMC
            if 'data' in bmc_result and 'bmc' in bmc_result['data']:
                bmc = bmc_result['data']['bmc']
                bmc_fields = ['key_partners', 'key_activities', 'key_resources', 'value_propositions', 
                             'customer_relationships', 'channels', 'customer_segments', 'cost_structure', 'revenue_streams']
                
                for field in bmc_fields:
                    if field in bmc and len(bmc[field]) > 0:
                        print(f"  ✅ Campo '{field}' generado con {len(bmc[field])} elementos")
                    else:
                        print(f"  ⚠️ Campo '{field}' vacío o faltante")
                
                # Verificar actividades generadas
                if 'created_activities' in bmc_result['data']:
                    activities_count = bmc_result['data']['created_activities']
                    print(f"  ✅ Actividades creadas: {activities_count}")
                
                return True
            else:
                print(f"❌ Estructura de BMC incorrecta")
                return False
        else:
            print(f"❌ Error generando BMC - Status: {bmc_response.status_code}")
            print(f"Response: {bmc_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en generación de BMC: {e}")
        return False

def test_main_apis(token):
    """Probar APIs principales"""
    print("\n🌐 Testing: APIs Principales")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    apis_to_test = [
        ("/api/projects/", "GET", "Lista de proyectos"),
        ("/api/activities/", "GET", "Lista de actividades"),
        ("/api/masters/categories", "GET", "Categorías"),
        ("/api/masters/tags", "GET", "Etiquetas"),
        ("/api/users/", "GET", "Lista de usuarios"),
    ]
    
    success_count = 0
    
    for endpoint, method, description in apis_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", headers=headers)
            
            if response.status_code == 200:
                print(f"  ✅ {description} - Status: {response.status_code}")
                success_count += 1
            else:
                print(f"  ❌ {description} - Status: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {description} - Error: {e}")
    
    print(f"\n📊 APIs probadas: {success_count}/{len(apis_to_test)} exitosas")
    return success_count == len(apis_to_test)

def main():
    """Función principal de testing"""
    print("🚀 Iniciando Testing del Sistema InnovAI")
    print("=" * 50)
    
    # Test 1: Autenticación
    token = test_authentication()
    if not token:
        print("\n❌ Testing detenido - No se pudo autenticar")
        return
    
    # Test 2: Entrevista Guiada
    interview_data = test_guided_interview(token)
    
    # Test 3: Creación de Proyectos
    project_id = test_project_creation(token)
    
    # Test 4: Generación de BMC (solo si tenemos un proyecto)
    bmc_success = False
    if project_id:
        bmc_success = test_bmc_generation(token, project_id)
    
    # Test 5: APIs Principales
    apis_success = test_main_apis(token)
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE TESTING")
    print("=" * 50)
    print(f"🔐 Autenticación: {'✅ EXITOSO' if token else '❌ FALLIDO'}")
    print(f"🎯 Entrevista Guiada: {'✅ EXITOSO' if interview_data else '❌ FALLIDO'}")
    print(f"📁 Creación de Proyectos: {'✅ EXITOSO' if project_id else '❌ FALLIDO'}")
    print(f"📊 Generación de BMC: {'✅ EXITOSO' if bmc_success else '❌ FALLIDO'}")
    print(f"🌐 APIs Principales: {'✅ EXITOSO' if apis_success else '❌ FALLIDO'}")
    
    # Estado general
    total_tests = 5
    passed_tests = sum([bool(token), bool(interview_data), bool(project_id), bmc_success, apis_success])
    
    print(f"\n🎯 RESULTADO GENERAL: {passed_tests}/{total_tests} tests exitosos")
    
    if passed_tests == total_tests:
        print("🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
    elif passed_tests >= 3:
        print("✅ Sistema mayormente funcional - Algunas funcionalidades necesitan atención")
    else:
        print("⚠️ Sistema con problemas significativos - Revisar configuración")

if __name__ == "__main__":
    main()
