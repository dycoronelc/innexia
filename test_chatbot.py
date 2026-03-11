#!/usr/bin/env python3
"""
Script de prueba para el ChatBot con IA
Verifica que las APIs funcionen correctamente con OpenAI
"""

import requests
import json
import os
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
CHATBOT_BMC_URL = f"{BASE_URL}/api/chatbot/generate-bmc"
CHATBOT_ANALYSIS_URL = f"{BASE_URL}/api/chatbot/analyze-project"
CHATBOT_RECOMMENDATIONS_URL = f"{BASE_URL}/api/chatbot/activity-recommendations"

def login():
    """Iniciar sesión y obtener token"""
    print("🔐 Iniciando sesión...")
    
    login_data = {
        "username": "admin@innexia.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(LOGIN_URL, data=login_data)
        response.raise_for_status()
        
        data = response.json()
        if "access_token" in data:
            print("✅ Login exitoso")
            return data["access_token"]
        else:
            print("❌ Error en login: No se recibió token")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en login: {e}")
        return None

def test_generate_bmc(token):
    """Probar generación de BMC"""
    print("\n🤖 Probando generación de BMC...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "business_idea": "Una plataforma de e-learning para enseñar programación a niños de 8-12 años usando juegos y proyectos interactivos",
        "provider": "openai"
    }
    
    try:
        response = requests.post(CHATBOT_BMC_URL, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        print("✅ BMC generado exitosamente")
        print(f"📊 Mensaje: {result.get('message', 'N/A')}")
        
        if 'bmc' in result:
            bmc = result['bmc']
            print("📋 Business Model Canvas generado:")
            for key, values in bmc.items():
                print(f"  • {key.replace('_', ' ').title()}: {len(values)} elementos")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error generando BMC: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Respuesta: {e.response.text}")
        return False

def test_project_analysis(token):
    """Probar análisis de proyecto"""
    print("\n📊 Probando análisis de proyecto...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "project_id": 1,
        "analysis_type": "general"
    }
    
    try:
        response = requests.post(CHATBOT_ANALYSIS_URL, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Análisis de proyecto exitoso")
        print(f"📊 Mensaje: {result.get('message', 'N/A')}")
        
        if 'analysis' in result:
            analysis = result['analysis']
            print("📋 Análisis generado:")
            for key, values in analysis.items():
                if isinstance(values, list):
                    print(f"  • {key.title()}: {len(values)} elementos")
                else:
                    print(f"  • {key.title()}: {values}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error analizando proyecto: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Respuesta: {e.response.text}")
        return False

def test_activity_recommendations(token):
    """Probar recomendaciones de actividades"""
    print("\n💡 Probando recomendaciones de actividades...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "activity_description": "Desarrollar el diseño de la interfaz de usuario para la aplicación móvil",
        "project_context": "Proyecto de desarrollo de app de e-learning"
    }
    
    try:
        response = requests.post(CHATBOT_RECOMMENDATIONS_URL, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Recomendaciones generadas exitosamente")
        print(f"📊 Mensaje: {result.get('message', 'N/A')}")
        
        if 'recommendations' in result:
            recommendations = result['recommendations']
            print("📋 Recomendaciones generadas:")
            for key, values in recommendations.items():
                if isinstance(values, list):
                    print(f"  • {key.replace('_', ' ').title()}: {len(values)} sugerencias")
                else:
                    print(f"  • {key.replace('_', ' ').title()}: {values}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error generando recomendaciones: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Respuesta: {e.response.text}")
        return False

def main():
    """Función principal"""
    print("🧪 INICIANDO PRUEBAS DEL CHATBOT CON IA")
    print("=" * 50)
    print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Backend URL: {BASE_URL}")
    print("=" * 50)
    
    # Verificar que el backend esté corriendo
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print("✅ Backend está corriendo")
    except requests.exceptions.RequestException:
        print("❌ Backend no está corriendo. Por favor, inicia el servidor backend.")
        return
    
    # Login
    token = login()
    if not token:
        print("❌ No se pudo obtener token. Abortando pruebas.")
        return
    
    # Ejecutar pruebas
    tests = [
        ("Generación de BMC", test_generate_bmc),
        ("Análisis de Proyecto", test_project_analysis),
        ("Recomendaciones de Actividades", test_activity_recommendations)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        success = test_func(token)
        results.append((test_name, success))
    
    # Resumen
    print("\n" + "="*50)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASÓ" if success else "❌ FALLÓ"
        print(f"{status} - {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{len(results)} pruebas pasaron")
    
    if passed == len(results):
        print("🎉 ¡Todas las pruebas pasaron! El ChatBot está funcionando correctamente.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")

if __name__ == "__main__":
    main()

