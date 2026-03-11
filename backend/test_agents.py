#!/usr/bin/env python3
"""
Script de prueba para el sistema de agentes OpenAI
"""

import asyncio
import os
import sys
import json

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.agents_service import agents_service

async def test_intent_detection():
    """Prueba la detección de intenciones"""
    print("🧪 Probando detección de intenciones...")
    
    test_messages = [
        "Quiero crear un Business Model Canvas para mi startup de bienestar",
        "Necesito un plan de negocio para mi restaurante",
        "Ayúdame a crear una estrategia de marketing",
        "¿Cómo está mi proyecto actual?",
        "Hola, ¿cómo estás?"
    ]
    
    for message in test_messages:
        try:
            print(f"\n📝 Mensaje: '{message}'")
            
            context = {
                "recent_messages": [],
                "current_project": None,
                "user_profile": {"role": "emprendedor", "preferences": []}
            }
            
            result = await agents_service.detect_intent(message, context)
            
            print(f"🎯 Intención detectada: {result.get('intent', 'N/A')}")
            print(f"📊 Confianza: {result.get('confidence', 0)}")
            print(f"💭 Acción sugerida: {result.get('suggestedAction', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

async def test_bmc_generation():
    """Prueba la generación de BMC"""
    print("\n🧪 Probando generación de BMC...")
    
    business_idea = "Plataforma de bienestar integral que conecta usuarios con profesionales de la salud mental y física"
    
    try:
        print(f"💡 Idea de negocio: '{business_idea}'")
        
        result = await agents_service.generate_bmc(business_idea, use_high_quality=True)
        
        print("✅ BMC generado exitosamente!")
        print(f"📋 Elementos generados:")
        
        bmc = result.get('bmc', {})
        for key, value in bmc.items():
            if isinstance(value, list):
                print(f"  • {key}: {len(value)} elementos")
            else:
                print(f"  • {key}: {value}")
                
        activities = result.get('recommended_activities', [])
        print(f"🎯 Actividades recomendadas: {len(activities)}")
        
    except Exception as e:
        print(f"❌ Error generando BMC: {e}")

async def main():
    """Función principal de prueba"""
    print("🚀 Iniciando pruebas del sistema de agentes OpenAI...")
    print("=" * 60)
    
    # Verificar que la API key esté configurada
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Advertencia: OPENAI_API_KEY no está configurada")
        print("   Configura la variable de entorno para usar los agentes")
        return
    
    try:
        # Probar detección de intenciones
        await test_intent_detection()
        
        # Probar generación de BMC
        await test_bmc_generation()
        
        print("\n" + "=" * 60)
        print("✅ Pruebas completadas exitosamente!")
        
    except Exception as e:
        print(f"\n❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

