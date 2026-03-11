#!/usr/bin/env python3
"""
Script de prueba para verificar la estructura del sistema de agentes OpenAI
"""

import os
import sys

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Prueba que todas las importaciones funcionen correctamente"""
    print("🧪 Probando importaciones...")
    
    try:
        from app.services.agents_service import agents_service, IntentDetectionResult, BMCResult
        print("✅ Importaciones exitosas")
        return True
    except Exception as e:
        print(f"❌ Error en importaciones: {e}")
        return False

def test_agent_initialization():
    """Prueba que los agentes se inicialicen correctamente"""
    print("\n🧪 Probando inicialización de agentes...")
    
    try:
        from app.services.agents_service import agents_service
        
        # Verificar que los agentes estén inicializados
        agents = agents_service.agents
        expected_agents = ['intent_detector', 'bmc_generator', 'business_plan_generator', 'marketing_plan_generator', 'project_manager']
        
        for agent_name in expected_agents:
            if agent_name in agents:
                print(f"✅ Agente '{agent_name}' inicializado correctamente")
            else:
                print(f"❌ Agente '{agent_name}' no encontrado")
                return False
        
        print("✅ Todos los agentes inicializados correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en inicialización: {e}")
        return False

def test_session_management():
    """Prueba que el sistema de sesiones funcione"""
    print("\n🧪 Probando sistema de sesiones...")
    
    try:
        from app.services.agents_service import agents_service
        
        # Verificar que el directorio de sesiones exista
        sessions_dir = agents_service.sessions_dir
        if os.path.exists(sessions_dir):
            print(f"✅ Directorio de sesiones existe: {sessions_dir}")
        else:
            print(f"❌ Directorio de sesiones no existe: {sessions_dir}")
            return False
        
        # Probar creación de sesión
        session = agents_service.get_session("test_session")
        print("✅ Sesión creada exitosamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en sistema de sesiones: {e}")
        return False

def test_api_endpoints():
    """Prueba que los endpoints de la API estén configurados"""
    print("\n🧪 Probando endpoints de API...")
    
    try:
        from app.api.agents import router
        
        # Verificar que el router esté configurado
        if router:
            print("✅ Router de agentes configurado correctamente")
            
            # Verificar que las rutas estén definidas
            routes = [route.path for route in router.routes]
            expected_routes = [
                "/detect-intent",
                "/generate-bmc", 
                "/generate-business-plan",
                "/generate-marketing-plan",
                "/analyze-project"
            ]
            
            for route in expected_routes:
                if any(route in r for r in routes):
                    print(f"✅ Ruta '{route}' encontrada")
                else:
                    print(f"❌ Ruta '{route}' no encontrada")
                    return False
            
            return True
        else:
            print("❌ Router no configurado")
            return False
            
    except Exception as e:
        print(f"❌ Error en endpoints de API: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("🚀 Iniciando pruebas de estructura del sistema de agentes...")
    print("=" * 70)
    
    tests = [
        test_imports,
        test_agent_initialization,
        test_session_management,
        test_api_endpoints
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 70)
    print(f"📊 Resultados: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("✅ Todas las pruebas de estructura pasaron exitosamente!")
        print("\n🎯 El sistema de agentes está listo para usar con una API key válida")
    else:
        print("❌ Algunas pruebas fallaron. Revisar los errores arriba.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

