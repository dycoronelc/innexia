from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
import os
import logging
from datetime import datetime, timedelta
import httpx

from ..core.auth import get_current_user
from ..database import get_db
from ..models.user import User
from ..models.business_model_canvas import BusinessModelCanvas
from ..models.project import Project
from ..models.activity import ProjectActivity
from ..schemas.business_model_canvas import BusinessModelCanvasCreate
from ..schemas.activity import ProjectActivityCreate
from ..config import settings
from ..services.guardrails_service import guardrails_service
from ..services.reasoning_service import reasoning_service, ReasoningContext
from ..services.workflow_service import workflow_service
try:
    from ..services.openai_service import openai_client
    import openai
except ImportError:
    # Fallback si no se puede importar el servicio
    openai_client = None
    openai = None

# Configurar logger
logger = logging.getLogger(__name__)

def validate_openai_client():
    """Valida que el cliente de OpenAI esté disponible"""
    if not openai_client:
        raise HTTPException(status_code=500, detail="Servicio de OpenAI no disponible")

router = APIRouter()

# ============================================================================
# SCHEMAS PARA EL CHATBOT
# ============================================================================

class GenerateBMCRequest(BaseModel):
    business_idea: str
    provider: str = "openai"
    project_id: Optional[int] = None
    use_high_quality: bool = False  # Para usar modelo balanceado
    use_gpt4: bool = False  # Para usar GPT-4 explícitamente (más lento)
    generate_activities: bool = True  # Para generar actividades automáticamente

class AnalyzeProjectRequest(BaseModel):
    project_id: int
    analysis_type: str = "general"

class ActivityRecommendationsRequest(BaseModel):
    activity_description: str
    project_context: str

class CreateActivitiesRequest(BaseModel):
    project_id: int
    activities: list

class EnhancedChatRequest(BaseModel):
    message: str
    project_id: Optional[int] = None
    use_guardrails: bool = True
    use_reasoning: bool = True
    use_workflows: bool = True
    workflow_type: Optional[str] = None  # 'bmc_analysis', 'activity_recommendations', 'business_idea_validation'

# ============================================================================
# CONFIGURACIÓN DE IA
# ============================================================================

# Configuración para diferentes proveedores de IA
AI_PROVIDERS = {
    "openai": {
        "api_key_env": "OPENAI_API_KEY",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-3.5-turbo",  # Modelo más rápido para respuestas más rápidas
        "fast_model": "gpt-3.5-turbo",  # Modelo rápido para respuestas inmediatas
        "quality_model": "gpt-4",  # Modelo de alta calidad para análisis complejos
        "balanced_model": "gpt-3.5-turbo-16k"  # Modelo balanceado entre velocidad y calidad
    },
    "claude": {
        "api_key_env": "CLAUDE_API_KEY", 
        "base_url": "https://api.anthropic.com/v1",
        "model": "claude-3-haiku-20240307",  # Modelo más rápido de Claude
        "fast_model": "claude-3-haiku-20240307",
        "quality_model": "claude-3-sonnet-20240229",
        "balanced_model": "claude-3-haiku-20240307"  # Claude Haiku es bastante balanceado
    }
}

# ============================================================================
# FUNCIONES DE IA
# ============================================================================

async def generate_bmc_with_ai(business_idea: str, provider: str = "openai", use_high_quality: bool = False, use_gpt4: bool = False, generate_activities: bool = True) -> dict:
    """
    Genera un Business Model Canvas usando IA y opcionalmente actividades recomendadas
    """
    try:
        # Obtener configuración del proveedor
        if provider not in AI_PROVIDERS:
            raise HTTPException(status_code=400, detail="Proveedor de IA no soportado")
        
        config = AI_PROVIDERS[provider]
        api_key = settings.OPENAI_API_KEY if provider == "openai" else settings.CLAUDE_API_KEY
        
        if not api_key or api_key == "sk-proj-your-openai-api-key-here":
            print("API key no configurada, usando respuesta de fallback")
            return generate_fallback_response(generate_activities)
        
        # Elegir modelo según la calidad requerida
        if use_gpt4:
            # Usar GPT-4 explícitamente (más lento pero mejor calidad)
            model_to_use = config["quality_model"]
        elif use_high_quality:
            # Usar modelo balanceado para evitar timeouts
            model_to_use = config["balanced_model"]
        else:
            # Usar modelo rápido
            model_to_use = config["fast_model"]
        
        # Llamada a la IA según el proveedor
        if provider == "openai":
            return await call_openai_api(business_idea, api_key, config, model_to_use, use_high_quality, generate_activities)
        elif provider == "claude":
            return await call_claude_api(business_idea, api_key, config, model_to_use, use_high_quality, generate_activities)
        else:
            raise HTTPException(status_code=400, detail="Proveedor no implementado")
            
    except Exception as e:
        print(f"Error generando BMC con IA: {e}")
        raise HTTPException(status_code=500, detail="Error al generar BMC con IA")

async def call_openai_api(business_idea: str, api_key: str, config: dict, model: str, use_high_quality: bool, generate_activities: bool = True) -> dict:
    """
    Llama a la API de OpenAI con configuración optimizada para velocidad y fallback automático
    """
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Configuración según la calidad requerida
    if use_high_quality:
        max_tokens = 1500  # Aumentar para contenido más detallado
        temperature = 0.7  # Más creativo para mejor calidad
        timeout = 25.0     # Timeout más largo para GPT-4
        system_prompt = """Eres un experto consultor en Business Model Canvas con amplia experiencia en emprendimiento e innovación. 
        
        Tu tarea es analizar ideas de negocio y generar Business Model Canvas específicos, detallados y realistas. 
        
        IMPORTANTE:
        - Analiza cuidadosamente la industria y modelo de negocio
        - Genera contenido específico y relevante, NO genérico
        - Usa nombres reales de empresas, tecnologías, procesos y conceptos del sector
        - Basa cada elemento en la realidad del negocio propuesto
        - Responde ÚNICAMENTE con JSON válido"""
    else:
        max_tokens = 1200  # Aumentar para contenido más específico
        temperature = 0.6  # Más creativo pero controlado
        timeout = 15.0     # Timeout moderado
        system_prompt = """Eres un experto en Business Model Canvas especializado en emprendimiento. 
        
        Genera contenido específico y relevante para cada idea de negocio. 
        
        REGLAS:
        - Analiza la industria y modelo de negocio
        - Crea elementos específicos, no genéricos
        - Usa nombres reales y conceptos del sector
        - Responde ÚNICAMENTE con JSON válido"""
    
    # Configuración especial para GPT-4 con timeout más corto
    if model == "gpt-4":
        timeout = 25.0  # Reducir timeout para GPT-4
        max_tokens = 1000  # Reducir tokens para GPT-4
    
    # Acortar la idea de negocio si es muy larga
    if len(business_idea) > 500:
        business_idea = business_idea[:500] + "..."
    
    # Generar prompt específico y detallado
    if generate_activities:
        optimized_prompt = f"""
        Analiza la siguiente idea de negocio y genera un Business Model Canvas específico y detallado:

        IDEA DE NEGOCIO: {business_idea}

        INSTRUCCIONES:
        1. Analiza la idea de negocio cuidadosamente
        2. Genera contenido específico para cada sección del BMC
        3. Usa nombres reales y específicos, no genéricos
        4. Basa cada elemento en la industria y modelo de negocio identificado
        5. Incluye 2-3 elementos específicos por sección

        Responde ÚNICAMENTE con este JSON:
        {{
            "bmc": {{
                "key_partners": ["socio específico 1", "socio específico 2"],
                "key_activities": ["actividad específica 1", "actividad específica 2"],
                "key_resources": ["recurso específico 1", "recurso específico 2"],
                "value_propositions": ["propuesta de valor específica 1", "propuesta de valor específica 2"],
                "customer_relationships": ["tipo de relación específica 1", "tipo de relación específica 2"],
                "channels": ["canal específico 1", "canal específico 2"],
                "customer_segments": ["segmento específico 1", "segmento específico 2"],
                "cost_structure": ["costo específico 1", "costo específico 2"],
                "revenue_streams": ["fuente de ingreso específica 1", "fuente de ingreso específica 2"]
            }},
            "recommended_activities": [
                {{
                    "title": "Actividad específica para este negocio",
                    "description": "Descripción detallada de la actividad",
                    "priority": "high",
                    "estimated_duration_days": 7
                }}
            ]
        }}
        """
    else:
        optimized_prompt = f"""
        Analiza la siguiente idea de negocio y genera un Business Model Canvas específico y detallado:

        IDEA DE NEGOCIO: {business_idea}

        INSTRUCCIONES:
        1. Analiza la idea de negocio cuidadosamente
        2. Genera contenido específico para cada sección del BMC
        3. Usa nombres reales y específicos, no genéricos
        4. Basa cada elemento en la industria y modelo de negocio identificado
        5. Incluye 2-3 elementos específicos por sección

        Responde ÚNICAMENTE con este JSON:
        {{
            "key_partners": ["socio específico 1", "socio específico 2"],
            "key_activities": ["actividad específica 1", "actividad específica 2"],
            "key_resources": ["recurso específico 1", "recurso específico 2"],
            "value_propositions": ["propuesta de valor específica 1", "propuesta de valor específica 2"],
            "customer_relationships": ["tipo de relación específica 1", "tipo de relación específica 2"],
            "channels": ["canal específico 1", "canal específico 2"],
            "customer_segments": ["segmento específico 1", "segmento específico 2"],
            "cost_structure": ["costo específico 1", "costo específico 2"],
            "revenue_streams": ["fuente de ingreso específica 1", "fuente de ingreso específica 2"]
        }}
        """
    
    data = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": optimized_prompt
            }
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Extraer JSON del response
                try:
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    json_str = content[start:end]
                    parsed_data = json.loads(json_str)
                    
                    if generate_activities:
                        return {
                            "bmc": parsed_data.get("bmc", parsed_data),
                            "recommended_activities": parsed_data.get("recommended_activities", []),
                            "message": f"BMC generado exitosamente usando {model}"
                        }
                    else:
                        return {
                            "bmc": parsed_data,
                            "message": f"BMC generado exitosamente usando {model}"
                        }
                        
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"Error parseando JSON: {e}")
                    return await call_openai_api_fallback(business_idea, api_key, generate_activities)
            else:
                print(f"Error en OpenAI API: {response.status_code}")
                return await call_openai_api_fallback(business_idea, api_key, generate_activities)
                
    except httpx.TimeoutException:
        print(f"Timeout con {model}, usando fallback")
        return await call_openai_api_fallback(business_idea, api_key, generate_activities)
    except Exception as e:
        print(f"Error en OpenAI API: {e}")
        return await call_openai_api_fallback(business_idea, api_key, generate_activities)

async def call_openai_api_fallback(business_idea: str, api_key: str, generate_activities: bool = True) -> dict:
    """
    Fallback automático a GPT-3.5-turbo-16k para casos de timeout o error
    """
    print("Usando fallback a GPT-3.5-turbo-16k")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Prompt más simple para el fallback
    if generate_activities:
        fallback_prompt = f"""
        Genera BMC y actividades para: {business_idea[:300]}
        
        JSON:
        {{
            "bmc": {{
                "key_partners": ["socio1", "socio2"],
                "key_activities": ["actividad1", "actividad2"],
                "key_resources": ["recurso1", "recurso2"],
                "value_propositions": ["propuesta1", "propuesta2"],
                "customer_relationships": ["relacion1", "relacion2"],
                "channels": ["canal1", "canal2"],
                "customer_segments": ["segmento1", "segmento2"],
                "cost_structure": ["costo1", "costo2"],
                "revenue_streams": ["ingreso1", "ingreso2"]
            }},
            "recommended_activities": [
                {{
                    "title": "Actividad",
                    "description": "Descripción",
                    "priority": "high",
                    "estimated_duration_days": 7
                }}
            ]
        }}
        """
    else:
        fallback_prompt = f"""
        Genera BMC para: {business_idea[:300]}
        
        JSON:
        {{
            "key_partners": ["socio1", "socio2"],
            "key_activities": ["actividad1", "actividad2"],
            "key_resources": ["recurso1", "recurso2"],
            "value_propositions": ["propuesta1", "propuesta2"],
            "customer_relationships": ["relacion1", "relacion2"],
            "channels": ["canal1", "canal2"],
            "customer_segments": ["segmento1", "segmento2"],
            "cost_structure": ["costo1", "costo2"],
            "revenue_streams": ["ingreso1", "ingreso2"]
        }}
        """
    
    data = {
        "model": "gpt-3.5-turbo-16k",
        "messages": [
            {
                "role": "system",
                "content": "Eres un experto en Business Model Canvas. Responde SOLO con JSON válido."
            },
            {
                "role": "user",
                "content": fallback_prompt
            }
        ],
        "max_tokens": 800,
        "temperature": 0.2
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=15.0
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                try:
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    json_str = content[start:end]
                    parsed_data = json.loads(json_str)
                    
                    if generate_activities:
                        return {
                            "bmc": parsed_data.get("bmc", parsed_data),
                            "recommended_activities": parsed_data.get("recommended_activities", []),
                            "message": "BMC generado exitosamente usando modelo alternativo (GPT-4 no disponible)"
                        }
                    else:
                        return {
                            "bmc": parsed_data,
                            "message": "BMC generado exitosamente usando modelo alternativo (GPT-4 no disponible)"
                        }
                        
                except (json.JSONDecodeError, ValueError):
                    return generate_fallback_response(generate_activities)
            else:
                return generate_fallback_response(generate_activities)
                
    except Exception as e:
        print(f"Error en fallback: {e}")
        return generate_fallback_response(generate_activities)

async def call_claude_api(business_idea: str, api_key: str, config: dict, model: str, use_high_quality: bool, generate_activities: bool = True) -> dict:
    """
    Llama a la API de Claude con configuración optimizada para velocidad
    """
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    
    # Configuración según la calidad requerida
    if use_high_quality:
        max_tokens = 1500  # Reducir de 2000 a 1500
        temperature = 0.5  # Reducir de 0.7 a 0.5
        timeout = 25.0     # Reducir de 30 a 25 segundos
    else:
        max_tokens = 1000
        temperature = 0.3
        timeout = 15.0
    
    # Generar prompt según si se incluyen actividades o no
    if generate_activities:
        optimized_prompt = f"""
        Analiza esta idea de negocio y genera un Business Model Canvas con actividades.
        
        IDEA: {business_idea}
        
        Responde SOLO con JSON válido:
        {{
            "bmc": {{
                "key_partners": ["socio1", "socio2"],
                "key_activities": ["actividad1", "actividad2"],
                "key_resources": ["recurso1", "recurso2"],
                "value_propositions": ["propuesta1", "propuesta2"],
                "customer_relationships": ["relacion1", "relacion2"],
                "channels": ["canal1", "canal2"],
                "customer_segments": ["segmento1", "segmento2"],
                "cost_structure": ["costo1", "costo2"],
                "revenue_streams": ["ingreso1", "ingreso2"]
            }},
            "recommended_activities": [
                {{"title": "Actividad 1", "description": "Descripción", "priority": "high", "estimated_duration_days": 7}}
            ]
        }}
        """
    else:
        optimized_prompt = f"""
        Genera un Business Model Canvas para: {business_idea}
        
        Responde SOLO con JSON válido en esta estructura:
        {{
            "key_partners": ["socio1", "socio2"],
            "key_activities": ["actividad1", "actividad2"],
            "key_resources": ["recurso1", "recurso2"],
            "value_propositions": ["propuesta1", "propuesta2"],
            "customer_relationships": ["relacion1", "relacion2"],
            "channels": ["canal1", "canal2"],
            "customer_segments": ["segmento1", "segmento2"],
            "cost_structure": ["costo1", "costo2"],
            "revenue_streams": ["ingreso1", "ingreso2"]
        }}
        """
    
    data = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "user",
                "content": optimized_prompt
            }
        ],
        "temperature": temperature,
        "top_p": 0.9
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{config['base_url']}/messages",
                headers=headers,
                json=data,
                timeout=timeout
            )
            
            if response.status_code != 200:
                print(f"Error en Claude API: {response.status_code} - {response.text}")
                return generate_fallback_bmc(generate_activities)
            
            result = response.json()
            content = result["content"][0]["text"]
            
            # Intentar parsear JSON
            try:
                ai_response = json.loads(content)
                # Si incluye actividades, devolver la estructura completa
                if generate_activities and "bmc" in ai_response:
                    return ai_response
                # Si no incluye actividades o es formato legacy, normalizar
                elif generate_activities:
                    return {
                        "bmc": ai_response,
                        "recommended_activities": []
                    }
                else:
                    return ai_response
            except json.JSONDecodeError:
                print(f"Error parseando JSON de Claude: {content}")
                return generate_fallback_bmc(generate_activities)
                
    except httpx.TimeoutException:
        print("Timeout en Claude API - usando fallback")
        return generate_fallback_bmc(generate_activities)
    except Exception as e:
        print(f"Error llamando Claude API: {e}")
        return generate_fallback_bmc(generate_activities)

def generate_fallback_bmc(generate_activities: bool = True) -> dict:
    """
    Genera un BMC básico como fallback específico para delivery de comida saludable
    """
    basic_bmc = {
        "key_partners": [
            "Restaurantes de comida saludable",
            "Proveedores de ingredientes orgánicos", 
            "Servicios de delivery locales",
            "Influencers de salud y fitness",
            "Gimnasios y centros de bienestar"
        ],
        "key_activities": [
            "Desarrollo de plataforma móvil",
            "Gestión de restaurantes asociados",
            "Control de calidad de alimentos",
            "Marketing digital y redes sociales",
            "Logística de delivery optimizada"
        ],
        "key_resources": [
            "Equipo de desarrollo tecnológico",
            "Red de restaurantes asociados",
            "Sistema de gestión de pedidos",
            "Fleet de delivery",
            "Base de datos de clientes"
        ],
        "value_propositions": [
            "Comida saludable a domicilio",
            "Opciones nutritivas y balanceadas",
            "Entrega rápida y confiable",
            "Precios accesibles",
            "Transparencia nutricional"
        ],
        "customer_relationships": [
            "Atención al cliente personalizada",
            "Programa de fidelización",
            "Comunidad de usuarios saludables",
            "Soporte nutricional",
            "Feedback continuo"
        ],
        "channels": [
            "App móvil iOS/Android",
            "Website responsive",
            "Redes sociales (Instagram, Facebook)",
            "Marketing de influencers",
            "Partnerships con gimnasios"
        ],
        "customer_segments": [
            "Profesionales ocupados conscientes de la salud",
            "Personas en dietas específicas",
            "Familias que buscan opciones saludables",
            "Deportistas y atletas",
            "Personas con restricciones alimentarias"
        ],
        "cost_structure": [
            "Desarrollo y mantenimiento de plataforma",
            "Costos de marketing y adquisición",
            "Operaciones de delivery",
            "Comisiones a restaurantes",
            "Personal y administración"
        ],
        "revenue_streams": [
            "Comisiones por pedido (15-20%)",
            "Tarifas de delivery",
            "Suscripciones premium",
            "Publicidad de restaurantes",
            "Servicios nutricionales adicionales"
        ]
    }
    
    if generate_activities:
        return {
            "bmc": basic_bmc,
            "recommended_activities": [
                {
                    "title": "Investigación de Mercado",
                    "description": "Realizar análisis de mercado y competencia",
                    "priority": "high",
                    "estimated_duration_days": 14
                },
                {
                    "title": "Definir Propuesta de Valor",
                    "description": "Clarificar y refinar la propuesta de valor del producto/servicio",
                    "priority": "high",
                    "estimated_duration_days": 7
                },
                {
                    "title": "Crear Plan de Marketing",
                    "description": "Desarrollar estrategia de marketing y comunicación",
                    "priority": "medium",
                    "estimated_duration_days": 10
                },
                {
                    "title": "Establecer Canales de Distribución",
                    "description": "Identificar y configurar canales de venta",
                    "priority": "medium",
                    "estimated_duration_days": 15
                },
                {
                    "title": "Validar Modelo de Negocio",
                    "description": "Probar el modelo con clientes potenciales",
                    "priority": "high",
                    "estimated_duration_days": 21
                }
            ]
        }
    else:
        return basic_bmc

def generate_fallback_response(generate_activities: bool = True) -> dict:
    """
    Respuesta de fallback cuando todo falla
    """
    fallback_bmc = {
        "key_partners": ["Socios estratégicos", "Proveedores tecnológicos", "Instituciones de salud"],
        "key_activities": ["Desarrollo de software", "Análisis de datos", "Gestión de usuarios"],
        "key_resources": ["Equipo de desarrollo", "Infraestructura tecnológica", "Base de datos médica"],
        "value_propositions": ["Mejora de calidad de vida", "Análisis personalizado", "Recomendaciones inteligentes"],
        "customer_relationships": ["Soporte personalizado", "Comunidad activa", "Seguimiento continuo"],
        "channels": ["App móvil", "Plataforma web", "Redes sociales"],
        "customer_segments": ["Personas conscientes de su salud", "Usuarios de fitness", "Pacientes crónicos"],
        "cost_structure": ["Desarrollo de software", "Infraestructura", "Marketing", "Soporte"],
        "revenue_streams": ["Suscripciones premium", "Consultas personalizadas", "Análisis avanzados"]
    }
    
    if generate_activities:
        fallback_activities = [
            {
                "title": "Investigación de Mercado",
                "description": "Analizar competencia y necesidades del mercado de apps de salud",
                "priority": "high",
                "estimated_duration_days": 14
            },
            {
                "title": "Desarrollo de MVP",
                "description": "Crear versión mínima viable de la aplicación",
                "priority": "high",
                "estimated_duration_days": 30
            },
            {
                "title": "Integración con APIs de Salud",
                "description": "Conectar con APIs para análisis de resultados médicos",
                "priority": "high",
                "estimated_duration_days": 21
            },
            {
                "title": "Estrategia de Marketing",
                "description": "Definir estrategia de posicionamiento en el mercado de salud",
                "priority": "medium",
                "estimated_duration_days": 14
            },
            {
                "title": "Pruebas de Usabilidad",
                "description": "Realizar pruebas con usuarios reales",
                "priority": "medium",
                "estimated_duration_days": 10
            }
        ]
        
        return {
            "bmc": fallback_bmc,
            "recommended_activities": fallback_activities,
            "message": "BMC generado usando datos de respaldo (error en API)"
        }
    else:
        return {
            "bmc": fallback_bmc,
            "message": "BMC generado usando datos de respaldo (error en API)"
        }

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

async def create_recommended_activities(recommended_activities: list, project_id: int, user_id: int, db: Session) -> list:
    """
    Crea actividades recomendadas en la base de datos
    """
    created_activities = []
    
    try:
        print(f"Iniciando creación de {len(recommended_activities)} actividades para proyecto {project_id}")
        
        for i, activity_data in enumerate(recommended_activities):
            print(f"Procesando actividad {i+1}: {activity_data}")
            # Calcular fechas de inicio y fin
            start_date = datetime.now() + timedelta(days=i * 2)  # Espaciar actividades cada 2 días
            duration_days = activity_data.get("estimated_duration_days", 7)
            due_date = start_date + timedelta(days=duration_days)
            
            # Crear la actividad
            try:
                activity = ProjectActivity(
                    title=activity_data.get("title", f"Actividad {i+1}"),
                    description=activity_data.get("description", ""),
                    status="todo",  # Todas las actividades generadas empiezan en "Por Hacer"
                    priority=activity_data.get("priority", "medium"),
                    project_id=project_id,
                    start_date=start_date,
                    due_date=due_date
                )
                
                print(f"Actividad creada en memoria: {activity.title}")
                db.add(activity)
                db.flush()  # Para obtener el ID sin hacer commit
                print(f"Actividad guardada con ID: {activity.id}")
                
            except Exception as e:
                print(f"Error creando actividad {i+1}: {e}")
                raise e
            
            # Asignar el usuario actual a la actividad (opcional)
            # assignee = ActivityAssignee(
            #     activity_id=activity.id,
            #     user_id=user_id
            # )
            # db.add(assignee)
            
            created_activities.append({
                "id": activity.id,
                "title": activity.title,
                "description": activity.description,
                "status": activity.status,
                "priority": activity.priority,
                "start_date": activity.start_date.isoformat(),
                "due_date": activity.due_date.isoformat()
            })
        
        db.commit()
        print(f"Creadas {len(created_activities)} actividades para el proyecto {project_id}")
        
    except Exception as e:
        db.rollback()
        print(f"Error creando actividades: {e}")
        raise e
    
    return created_activities

# ============================================================================
# ENDPOINTS DEL CHATBOT
# ============================================================================

@router.post("/generate-bmc")
async def generate_business_model_canvas(
    request: GenerateBMCRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Genera un Business Model Canvas automáticamente usando IA
    """
    try:
        print(f"Generando BMC para proyecto {request.project_id} con idea: {request.business_idea[:100]}...")
        
        # Generar BMC con IA (incluyendo actividades si está habilitado)
        ai_response = await generate_bmc_with_ai(
            request.business_idea, 
            request.provider, 
            request.use_high_quality, 
            request.use_gpt4, 
            request.generate_activities
        )
        
        print(f"Respuesta de IA recibida: {type(ai_response)}")
        print(f"Claves en respuesta: {list(ai_response.keys()) if isinstance(ai_response, dict) else 'No es dict'}")
        
        # Extraer BMC y actividades de la respuesta
        if "bmc" in ai_response:
            bmc_data = ai_response["bmc"]
            recommended_activities = ai_response.get("recommended_activities", [])
        else:
            bmc_data = ai_response
            recommended_activities = []
        
        # Si se especifica un proyecto, crear el BMC en la base de datos
        if request.project_id:
            # Verificar que el proyecto existe y pertenece al usuario
            project = db.query(Project).filter(
                Project.id == request.project_id,
                Project.company_id == current_user.company_id
            ).first()
            
            if not project:
                raise HTTPException(status_code=404, detail="Proyecto no encontrado")
            
            # Crear BMC en la base de datos
            print(f"Creando BMC para proyecto {request.project_id}")
            print(f"Datos del BMC: {bmc_data}")
            
            bmc_create = BusinessModelCanvasCreate(
                project_id=request.project_id,
                key_partners=bmc_data["key_partners"],
                key_activities=bmc_data["key_activities"],
                key_resources=bmc_data["key_resources"],
                value_propositions=bmc_data["value_propositions"],
                customer_relationships=bmc_data["customer_relationships"],
                channels=bmc_data["channels"],
                customer_segments=bmc_data["customer_segments"],
                cost_structure=bmc_data["cost_structure"],
                revenue_streams=bmc_data["revenue_streams"]
            )
            
            print(f"BMC create object: {bmc_create}")
            bmc = BusinessModelCanvas(**bmc_create.dict())
            print(f"BMC object created: {bmc}")
            db.add(bmc)
            db.commit()
            db.refresh(bmc)
            print(f"BMC guardado con ID: {bmc.id}")
            
            # Crear actividades recomendadas si están disponibles
            created_activities = []
            if request.generate_activities and recommended_activities:
                created_activities = await create_recommended_activities(
                    recommended_activities, 
                    request.project_id, 
                    current_user.id, 
                    db
                )
            
            return {
                "message": "Business Model Canvas generado y guardado exitosamente",
                "bmc": bmc_data,
                "saved_bmc_id": bmc.id,
                "created_activities": len(created_activities),
                "activities": created_activities if created_activities else None
            }
        
        # Si no se especifica proyecto, crear un proyecto temporal
        # No se especificó proyecto, creando proyecto temporal
        
        # Crear proyecto temporal
        project_name = request.business_idea[:50] + "..." if len(request.business_idea) > 50 else request.business_idea
        
        # Obtener el status "Activo" por defecto
        from ..models.status import Status
        active_status = db.query(Status).filter(Status.name == "Activo").first()
        if not active_status:
            raise HTTPException(status_code=500, detail="No se encontró el status 'Activo' en la base de datos")
        
        temp_project = Project(
            name=project_name,
            description=f"Proyecto temporal generado automáticamente: {request.business_idea}",
            owner_id=current_user.id,
            company_id=current_user.company_id,
            status_id=active_status.id
        )
        db.add(temp_project)
        db.commit()
        db.refresh(temp_project)
        # Proyecto temporal creado
        
        # Crear BMC en el proyecto temporal
        bmc_create = BusinessModelCanvasCreate(
            project_id=temp_project.id,
            key_partners=bmc_data["key_partners"],
            key_activities=bmc_data["key_activities"],
            key_resources=bmc_data["key_resources"],
            value_propositions=bmc_data["value_propositions"],
            customer_relationships=bmc_data["customer_relationships"],
            channels=bmc_data["channels"],
            customer_segments=bmc_data["customer_segments"],
            cost_structure=bmc_data["cost_structure"],
            revenue_streams=bmc_data["revenue_streams"]
        )
        
        bmc = BusinessModelCanvas(**bmc_create.dict())
        db.add(bmc)
        db.commit()
        db.refresh(bmc)
        # BMC guardado en proyecto temporal
        
        # Crear actividades recomendadas si están disponibles
        created_activities = []
        if request.generate_activities and recommended_activities:
            created_activities = await create_recommended_activities(
                recommended_activities, 
                temp_project.id, 
                current_user.id, 
                db
            )
        
        return {
            "message": "Business Model Canvas generado y guardado exitosamente",
            "bmc": bmc_data,
            "saved_bmc_id": bmc.id,
            "temp_project_id": temp_project.id,
            "temp_project_name": temp_project.name,
            "created_activities": len(created_activities),
            "activities": created_activities if created_activities else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en generate_bmc: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/analyze-project/{project_id}")
async def analyze_project_with_ai(
    project_id: int,
    analysis_type: str = "general",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analiza un proyecto usando IA y proporciona recomendaciones
    """
    try:
        # Verificar que el proyecto existe y pertenece al usuario
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.company_id == current_user.company_id
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        
        # Generar análisis según el tipo
        if analysis_type == "general":
            analysis = await generate_project_analysis(project, db)
        elif analysis_type == "activities":
            analysis = await generate_activities_analysis(project, db)
        elif analysis_type == "timeline":
            analysis = await generate_timeline_analysis(project, db)
        elif analysis_type == "risks":
            analysis = await generate_risks_analysis(project, db)
        else:
            raise HTTPException(status_code=400, detail="Tipo de análisis no válido")
        
        return {
            "message": f"Análisis de proyecto generado exitosamente",
            "analysis": analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en analyze_project: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/activity-recommendations")
async def get_activity_recommendations(
    request: ActivityRecommendationsRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Proporciona recomendaciones para una actividad específica
    """
    try:
        recommendations = await generate_activity_recommendations(
            request.activity_description, 
            request.project_context
        )
        
        return {
            "message": "Recomendaciones generadas exitosamente",
            "recommendations": recommendations
        }
        
    except Exception as e:
        print(f"Error en activity_recommendations: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/create-activities")
async def create_activities_for_project(
    request: CreateActivitiesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crea actividades para un proyecto específico
    """
    try:
        print(f"Recibida solicitud para crear actividades para proyecto {request.project_id}")
        print(f"Actividades recibidas: {request.activities}")
        
        # Verificar que el proyecto existe y pertenece al usuario
        project = db.query(Project).filter(
            Project.id == request.project_id,
            Project.company_id == current_user.company_id
        ).first()
        
        if not project:
            print(f"Proyecto {request.project_id} no encontrado para usuario {current_user.id}")
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        
        print(f"Proyecto encontrado: {project.name}")
        
        # Crear las actividades
        print("Iniciando creación de actividades...")
        created_activities = await create_recommended_activities(
            request.activities,
            request.project_id,
            current_user.id,
            db
        )
        
        print(f"Actividades creadas exitosamente: {len(created_activities)}")
        
        return {
            "message": f"Actividades creadas exitosamente para el proyecto {project.name}",
            "created_activities": len(created_activities),
            "activities": created_activities
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en create_activities: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/test-create-activities")
async def test_create_activities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint de prueba para crear actividades
    """
    try:
        # Crear un proyecto de prueba si no existe
        test_project = db.query(Project).filter(
            Project.name == "Proyecto de Prueba",
            Project.company_id == current_user.company_id
        ).first()
        
        if not test_project:
            test_project = Project(
                name="Proyecto de Prueba",
                description="Proyecto para probar creación de actividades",
                category="Test",
                status="active",
                company_id=current_user.company_id
            )
            db.add(test_project)
            db.commit()
            db.refresh(test_project)
        
        # Actividades de prueba
        test_activities = [
            {
                "title": "Actividad de Prueba 1",
                "description": "Descripción de prueba",
                "priority": "high",
                "estimated_duration_days": 7
            },
            {
                "title": "Actividad de Prueba 2", 
                "description": "Otra descripción de prueba",
                "priority": "medium",
                "estimated_duration_days": 5
            }
        ]
        
        print(f"Probando creación de actividades para proyecto {test_project.id}")
        created_activities = await create_recommended_activities(
            test_activities,
            test_project.id,
            current_user.id,
            db
        )
        
        return {
            "message": "Prueba exitosa",
            "created_activities": len(created_activities),
            "activities": created_activities
        }
        
    except Exception as e:
        print(f"Error en test_create_activities: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error en prueba: {str(e)}")

@router.post("/test-simple-activity")
async def test_simple_activity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint de prueba simple para crear una actividad
    """
    try:
        # Buscar cualquier proyecto del usuario
        project = db.query(Project).filter(
            Project.company_id == current_user.company_id
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="No hay proyectos disponibles")
        
        print(f"Creando actividad simple para proyecto {project.id}")
        
        # Crear una actividad simple
        from datetime import datetime, timedelta
        
        activity = ProjectActivity(
            title="Actividad de Prueba Simple",
            description="Esta es una actividad de prueba",
            status="todo",
            priority="medium",
            project_id=project.id,
            start_date=datetime.now(),
            due_date=datetime.now() + timedelta(days=7)
        )
        
        db.add(activity)
        db.commit()
        db.refresh(activity)
        
        print(f"Actividad creada exitosamente con ID: {activity.id}")
        
        return {
            "message": "Actividad de prueba creada exitosamente",
            "activity_id": activity.id,
            "title": activity.title
        }
        
    except Exception as e:
        print(f"Error en test_simple_activity: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error en prueba simple: {str(e)}")

# ============================================================================
# FUNCIONES DE ANÁLISIS
# ============================================================================

async def generate_project_analysis(project: Project, db: Session) -> dict:
    """
    Genera análisis general del proyecto
    """
    # TODO: Implementar análisis con IA
    return {
        "strengths": ["Buena planificación", "Equipo competente"],
        "weaknesses": ["Falta de recursos", "Timeline ajustado"],
        "opportunities": ["Mercado en crecimiento", "Nuevas tecnologías"],
        "threats": ["Competencia fuerte", "Cambios regulatorios"],
        "recommendations": ["Aumentar recursos", "Mejorar comunicación"]
    }

async def generate_activities_analysis(project: Project, db: Session) -> dict:
    """
    Genera análisis de actividades del proyecto
    """
    # TODO: Implementar análisis con IA
    return {
        "completed_activities": 5,
        "in_progress_activities": 3,
        "pending_activities": 2,
        "bottlenecks": ["Actividad A", "Actividad B"],
        "recommendations": ["Reasignar recursos", "Priorizar actividades"]
    }

async def generate_timeline_analysis(project: Project, db: Session) -> dict:
    """
    Genera análisis de timeline del proyecto
    """
    # TODO: Implementar análisis con IA
    return {
        "progress_percentage": 65,
        "days_ahead": 5,
        "days_behind": 0,
        "critical_path": ["Actividad 1", "Actividad 2"],
        "recommendations": ["Acelerar actividades críticas", "Optimizar recursos"]
    }

async def generate_risks_analysis(project: Project, db: Session) -> dict:
    """
    Genera análisis de riesgos del proyecto
    """
    # TODO: Implementar análisis con IA
    return {
        "high_risks": ["Riesgo técnico", "Riesgo de recursos"],
        "medium_risks": ["Riesgo de timeline", "Riesgo de calidad"],
        "low_risks": ["Riesgo menor"],
        "mitigation_strategies": ["Plan de contingencia", "Monitoreo continuo"]
    }

async def generate_activity_recommendations(activity_description: str, project_context: str) -> dict:
    """
    Genera recomendaciones para una actividad específica basadas en el BMC del proyecto
    """
    try:
        # Extraer project_id del contexto si está disponible
        project_id = None
        if "ID:" in project_context:
            try:
                project_id = int(project_context.split("ID:")[1].split(")")[0].strip())
            except:
                pass
        
        # Si tenemos project_id, intentar obtener información del BMC
        bmc_info = ""
        if project_id:
            try:
                from ..models.business_model_canvas import BusinessModelCanvas
                from ..database import get_db
                
                # Obtener sesión de base de datos
                db = next(get_db())
                bmc = db.query(BusinessModelCanvas).filter(BusinessModelCanvas.project_id == project_id).first()
                
                if bmc:
                    bmc_info = f"""
INFORMACIÓN DEL BUSINESS MODEL CANVAS:
- Socios Clave: {bmc.key_partners or 'No especificado'}
- Actividades Clave: {bmc.key_activities or 'No especificado'}
- Recursos Clave: {bmc.key_resources or 'No especificado'}
- Propuesta de Valor: {bmc.value_propositions or 'No especificado'}
- Relaciones con Clientes: {bmc.customer_relationships or 'No especificado'}
- Canales: {bmc.channels or 'No especificado'}
- Segmentos de Clientes: {bmc.customer_segments or 'No especificado'}
- Estructura de Costos: {bmc.cost_structure or 'No especificado'}
- Fuentes de Ingresos: {bmc.revenue_streams or 'No especificado'}
"""
            except Exception as e:
                print(f"Error obteniendo BMC: {e}")
        
        # Construir prompt para IA
        prompt = f"""
Basándote en la siguiente información del proyecto y su Business Model Canvas, proporciona recomendaciones específicas para la actividad solicitada.

CONTEXTO DEL PROYECTO:
{project_context}

{bmc_info}

ACTIVIDAD SOLICITADA:
{activity_description}

Por favor, proporciona recomendaciones específicas y prácticas basadas en la información del BMC. Si no hay suficiente información en el BMC, sugiere qué información adicional sería útil.

Formato de respuesta en JSON:
{{
    "best_practices": ["práctica 1", "práctica 2"],
    "tools": ["herramienta específica 1", "herramienta específica 2"],
    "resources": ["recurso específico 1", "recurso específico 2"],
    "timeline_suggestions": ["sugerencia 1", "sugerencia 2"],
    "risk_mitigation": ["mitigación 1", "mitigación 2"]
}}

Si no puedes proporcionar recomendaciones específicas basadas en el BMC, usa valores genéricos como "Información insuficiente en BMC" para indicar que se necesita más información.
"""

        # Usar IA para generar recomendaciones
        if settings.OPENAI_API_KEY:
            try:
                # Usar la nueva API de OpenAI v1.0+
                from openai import OpenAI
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Eres un consultor de negocios experto que proporciona recomendaciones prácticas basadas en Business Model Canvas."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                
                # Parsear respuesta JSON
                ai_response = response.choices[0].message.content.strip()
                try:
                    import json
                    recommendations = json.loads(ai_response)
                    return recommendations
                except json.JSONDecodeError:
                    # Si no es JSON válido, usar respuesta estructurada
                    pass
            except Exception as e:
                print(f"Error con OpenAI: {e}")
        
        # Fallback: recomendaciones básicas basadas en el contexto
        if bmc_info:
            return {
                "best_practices": [
                    "Alinea las actividades con tus socios clave identificados en el BMC",
                    "Asegúrate de que las actividades apoyen tu propuesta de valor principal",
                    "Considera los recursos clave disponibles según tu BMC"
                ],
                "tools": ["Herramientas específicas no disponibles - completar BMC"],
                "resources": ["Recursos específicos no disponibles - completar BMC"],
                "timeline_suggestions": [
                    "Prioriza actividades que generen valor según tu BMC",
                    "Establece hitos basados en tus fuentes de ingresos"
                ],
                "risk_mitigation": [
                    "Monitorea los riesgos relacionados con tu estructura de costos",
                    "Mantén flexibilidad en las relaciones con clientes"
                ]
            }
        else:
            # Recomendaciones completamente genéricas
            return {
                "best_practices": ["Planificar detalladamente", "Comunicar claramente"],
                "tools": ["Herramienta A", "Herramienta B"],
                "resources": ["Recurso 1", "Recurso 2"],
                "timeline_suggestions": ["Dividir en subtareas", "Establecer hitos"],
                "risk_mitigation": ["Identificar riesgos temprano", "Tener plan B"]
            }
            
    except Exception as e:
        print(f"Error generando recomendaciones: {e}")
        # Fallback en caso de error
        return {
            "best_practices": ["Planificar detalladamente", "Comunicar claramente"],
            "tools": ["Herramienta A", "Herramienta B"],
            "resources": ["Recurso 1", "Recurso 2"],
            "timeline_suggestions": ["Dividir en subtareas", "Establecer hitos"],
            "risk_mitigation": ["Identificar riesgos temprano", "Tener plan B"]
        }

@router.post("/generate-business-plan", response_model=dict)
async def generate_business_plan(
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Genera un plan de negocio completo usando IA
    """
    try:
        # Extraer datos del request
        business_idea = request.get("business_idea", "")
        project_id = request.get("project_id")
        use_gpt4 = request.get("use_gpt4", False)
        
        if not business_idea:
            raise HTTPException(status_code=400, detail="business_idea es requerido")
        
        # Determinar el modelo a usar
        model = "gpt-4" if use_gpt4 else "gpt-3.5-turbo-16k"
        
        # Prompt especializado para plan de negocio
        prompt = f"""
        Genera un plan de negocio completo y profesional para la siguiente idea de negocio: "{business_idea}"
        
        El plan debe incluir:
        
        1. RESUMEN EJECUTIVO (2-3 párrafos)
        2. DESCRIPCIÓN DE LA EMPRESA (1-2 párrafos)
        3. ANÁLISIS DE MERCADO:
           - Tamaño del mercado
           - Mercado objetivo
           - Tendencias del mercado
           - Análisis de competencia
           - Posicionamiento en el mercado
        4. ESTRUCTURA ORGANIZACIONAL:
           - Estructura organizacional
           - Equipo de gestión
           - Estructura legal
           - Personal clave
        5. LÍNEA DE PRODUCTOS/SERVICIOS:
           - Descripción detallada
           - Características y beneficios
           - Ciclo de vida del producto
           - Propiedad intelectual
        6. ESTRATEGIA DE MARKETING Y VENTAS:
           - Estrategia de marketing
           - Estrategia de ventas
           - Estrategia de precios
           - Canales de distribución
           - Estrategia promocional
        7. REQUISITOS DE FINANCIAMIENTO:
           - Financiamiento actual
           - Necesidades de financiamiento
           - Uso de fondos
           - Fuentes de financiamiento
           - Cronograma
        8. PROYECCIONES FINANCIERAS (3 años):
           - Proyecciones de ingresos
           - Proyecciones de costos
           - Estado de resultados
           - Flujo de caja
           - Análisis de punto de equilibrio
        9. APÉNDICES
        
        Responde en formato JSON con la siguiente estructura:
        {{
            "executive_summary": "texto del resumen ejecutivo",
            "company_description": "descripción de la empresa",
            "market_analysis": {{
                "market_size": "descripción del tamaño del mercado",
                "target_market": "descripción del mercado objetivo",
                "market_trends": ["tendencia 1", "tendencia 2", "tendencia 3"],
                "competitive_analysis": {{
                    "direct_competitors": [
                        {{
                            "name": "nombre del competidor",
                            "strengths": ["fortaleza 1", "fortaleza 2"],
                            "weaknesses": ["debilidad 1", "debilidad 2"],
                            "market_share": "porcentaje del mercado",
                            "pricing_strategy": "estrategia de precios"
                        }}
                    ],
                    "indirect_competitors": [...],
                    "competitive_advantages": ["ventaja 1", "ventaja 2"],
                    "market_gaps": ["gap 1", "gap 2"]
                }},
                "market_positioning": "posicionamiento en el mercado"
            }},
            "organization_management": {{
                "organizational_structure": "descripción de la estructura",
                "management_team": [
                    {{
                        "name": "nombre",
                        "position": "cargo",
                        "experience": "experiencia",
                        "responsibilities": ["responsabilidad 1", "responsabilidad 2"]
                    }}
                ],
                "legal_structure": "estructura legal",
                "key_personnel": ["persona 1", "persona 2"]
            }},
            "service_product_line": {{
                "description": "descripción del producto/servicio",
                "features": ["característica 1", "característica 2"],
                "benefits": ["beneficio 1", "beneficio 2"],
                "lifecycle": "ciclo de vida",
                "intellectual_property": ["propiedad 1", "propiedad 2"]
            }},
            "marketing_sales": {{
                "marketing_strategy": "estrategia de marketing",
                "sales_strategy": "estrategia de ventas",
                "pricing_strategy": "estrategia de precios",
                "distribution_channels": ["canal 1", "canal 2"],
                "promotional_strategy": ["estrategia 1", "estrategia 2"]
            }},
            "funding_requirements": {{
                "current_funding": "financiamiento actual",
                "funding_needs": "necesidades de financiamiento",
                "use_of_funds": ["uso 1", "uso 2"],
                "funding_sources": ["fuente 1", "fuente 2"],
                "timeline": "cronograma"
            }},
            "financial_projections": {{
                "revenue_projections": [
                    {{
                        "year": 1,
                        "revenue": 100000,
                        "growth_rate": 0.15,
                        "revenue_streams": [
                            {{
                                "name": "stream 1",
                                "amount": 60000,
                                "percentage": 0.6
                            }}
                        ]
                    }}
                ],
                "cost_projections": [
                    {{
                        "year": 1,
                        "total_costs": 80000,
                        "fixed_costs": 40000,
                        "variable_costs": 40000,
                        "cost_breakdown": [
                            {{
                                "category": "categoría",
                                "amount": 20000,
                                "percentage": 0.25
                            }}
                        ]
                    }}
                ],
                "profit_loss": [
                    {{
                        "year": 1,
                        "revenue": 100000,
                        "costs": 80000,
                        "gross_profit": 20000,
                        "operating_expenses": 15000,
                        "net_profit": 5000,
                        "profit_margin": 0.05
                    }}
                ],
                "cash_flow": [
                    {{
                        "year": 1,
                        "operating_cash_flow": 5000,
                        "investing_cash_flow": -10000,
                        "financing_cash_flow": 5000,
                        "net_cash_flow": 0,
                        "ending_cash_balance": 5000
                    }}
                ],
                "break_even_analysis": "análisis de punto de equilibrio"
            }},
            "appendix": "contenido del apéndice"
        }}
        
        Asegúrate de que todos los campos estén completos y sean realistas para la idea de negocio.
        """
        
        # Verificar que openai_client esté disponible

        
        validate_openai_client()

        
        

        
        # Llamar a OpenAI
        response = await openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Eres un experto consultor de negocios especializado en crear planes de negocio profesionales y completos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000 if model == "gpt-4" else 8000
        )
        
        # Extraer y parsear la respuesta
        content = response.choices[0].message.content
        business_plan = json.loads(content)
        
        # Guardar en la base de datos si hay project_id
        document_url = None
        if project_id:
            try:
                # Generar PDF usando el servicio de PDF
                from ..services.pdf_generation_service import PDFGenerationService, DocumentRequest, DocumentType
                
                pdf_service = PDFGenerationService()
                
                # Crear solicitud de documento PDF
                doc_request = DocumentRequest(
                    document_type=DocumentType.BUSINESS_PLAN,
                    title="Plan de Negocio",
                    content=business_plan,
                    project_name=f"Proyecto: {business_idea[:50]}",
                    company_name="InnovAI",
                    author=f"Usuario: {current_user.email}"
                )
                
                # Generar PDF
                pdf_content = pdf_service.generate_document(doc_request)
                
                # Crear nombre de archivo único para PDF
                import uuid
                filename = f"plan_negocio_{project_id}_{uuid.uuid4().hex[:8]}.pdf"
                
                # Crear directorio del proyecto si no existe
                project_dir = os.path.join(settings.UPLOAD_DIR, str(project_id))
                os.makedirs(project_dir, exist_ok=True)
                
                # Guardar archivo PDF
                file_path = os.path.join(project_dir, filename)
                with open(file_path, 'wb') as f:
                    f.write(pdf_content)
                
                # Crear registro en base de datos
                from ..models.document import ProjectDocument
                db_document = ProjectDocument(
                    filename=filename,
                    original_filename=f"Plan de Negocio - {business_idea[:50]}.pdf",
                    file_path=file_path,
                    file_type='.pdf',
                    file_size=len(pdf_content),
                    description=f"Plan de negocio profesional generado automáticamente para: {business_idea}",
                    project_id=project_id,
                    uploader_id=current_user.id
                )
                
                db.add(db_document)
                db.commit()
                db.refresh(db_document)
                
                # Generar URL de descarga
                document_url = f"/api/documents/{db_document.id}/download"
                
                logger.info(f"Plan de negocio PDF guardado como documento ID: {db_document.id}")
                
            except Exception as e:
                logger.error(f"Error guardando plan de negocio PDF: {str(e)}")
                # Continuar sin fallar si hay error guardando
        
        return {
            "status": "success",
            "message": "Plan de negocio generado exitosamente",
            "business_plan": business_plan,
            "document_url": document_url,
            "document_id": db_document.id if project_id and 'db_document' in locals() else None
        }
        
    except Exception as e:
        logger.error(f"Error generando plan de negocio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generando plan de negocio: {str(e)}")

@router.post("/generate-marketing-plan", response_model=dict)
async def generate_marketing_plan(
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Genera un plan de marketing estratégico usando IA
    """
    try:
        # Extraer datos del request
        business_idea = request.get("business_idea", "")
        project_id = request.get("project_id")
        use_gpt4 = request.get("use_gpt4", False)
        
        if not business_idea:
            raise HTTPException(status_code=400, detail="business_idea es requerido")
        
        # Determinar el modelo a usar
        model = "gpt-4" if use_gpt4 else "gpt-3.5-turbo-16k"
        
        # Prompt especializado para plan de marketing
        prompt = f"""
        Genera un plan de marketing estratégico completo para la siguiente idea de negocio: "{business_idea}"
        
        El plan debe incluir:
        
        1. RESUMEN DEL MERCADO (1-2 párrafos)
        2. AUDIENCIA OBJETIVO:
           - Audiencia primaria (descripción, tamaño, características, puntos de dolor, motivaciones)
           - Audiencia secundaria (descripción, tamaño, características, puntos de dolor, motivaciones)
           - Demografía (rango de edad, género, nivel de ingresos, educación, ubicación, ocupación)
           - Psicografía (valores, intereses, estilo de vida)
           - Patrones de comportamiento (frecuencia de compra, canales preferidos, etc.)
        3. OBJETIVOS DE MARKETING (3-5 objetivos específicos y medibles)
        4. ESTRATEGIAS DE MARKETING (por canal):
           - Canal digital (enfoque, tácticas, presupuesto, resultados esperados)
           - Canal tradicional (enfoque, tácticas, presupuesto, resultados esperados)
           - Otros canales relevantes
        5. PLAN DE PRESUPUESTO:
           - Presupuesto total
           - Asignación por canal (porcentaje, monto, justificación)
           - Asignación por timeline (período, porcentaje, monto, actividades)
        6. TIMELINE DE IMPLEMENTACIÓN (cronograma detallado)
        7. KPIs Y MÉTRICAS (indicadores clave de rendimiento)
        
        Responde en formato JSON con la siguiente estructura:
        {{
            "market_overview": "resumen del mercado",
            "target_audience": {{
                "primary": {{
                    "description": "descripción de la audiencia primaria",
                    "size": "tamaño estimado",
                    "characteristics": ["característica 1", "característica 2"],
                    "pain_points": ["punto de dolor 1", "punto de dolor 2"],
                    "motivations": ["motivación 1", "motivación 2"]
                }},
                "secondary": {{
                    "description": "descripción de la audiencia secundaria",
                    "size": "tamaño estimado",
                    "characteristics": ["característica 1", "característica 2"],
                    "pain_points": ["punto de dolor 1", "punto de dolor 2"],
                    "motivations": ["motivación 1", "motivación 2"]
                }},
                "demographics": {{
                    "age_range": "rango de edad",
                    "gender": "género",
                    "income_level": "nivel de ingresos",
                    "education": "educación",
                    "location": "ubicación",
                    "occupation": ["ocupación 1", "ocupación 2"]
                }},
                "psychographics": ["valor 1", "valor 2"],
                "behavior_patterns": ["patrón 1", "patrón 2"]
            }},
            "marketing_objectives": ["objetivo 1", "objetivo 2", "objetivo 3"],
            "marketing_strategies": [
                {{
                    "channel": "nombre del canal",
                    "approach": "enfoque estratégico",
                    "tactics": ["táctica 1", "táctica 2"],
                    "budget": 10000,
                    "expected_results": ["resultado 1", "resultado 2"]
                }}
            ],
            "budget_allocation": {{
                "total_budget": 50000,
                "channel_allocation": [
                    {{
                        "channel": "canal",
                        "percentage": 0.4,
                        "amount": 20000,
                        "rationale": "justificación de la asignación"
                    }}
                ],
                "timeline_allocation": [
                    {{
                        "period": "Q1 2024",
                        "percentage": 0.25,
                        "amount": 12500,
                        "activities": ["actividad 1", "actividad 2"]
                    }}
                ]
            }},
            "timeline": "cronograma detallado de implementación",
            "kpis": ["KPI 1", "KPI 2", "KPI 3"]
        }}
        
        Asegúrate de que todos los campos estén completos y sean realistas para la idea de negocio.
        """
        
        # Verificar que openai_client esté disponible

        
        validate_openai_client()

        
        

        
        # Llamar a OpenAI
        response = await openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Eres un experto consultor de marketing especializado en crear planes de marketing estratégicos y efectivos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000 if model == "gpt-4" else 8000
        )
        
        # Extraer y parsear la respuesta
        content = response.choices[0].message.content
        marketing_plan = json.loads(content)
        
        # Generar PDF y guardar documento si hay project_id
        document_url = None
        document_id = None
        if project_id:
            try:
                from ..services.pdf_generation_service import PDFGenerationService, DocumentRequest, DocumentType
                from ..models.document import ProjectDocument
                import uuid
                
                pdf_service = PDFGenerationService()
                doc_request = DocumentRequest(
                    document_type=DocumentType.MARKETING_PLAN,
                    title="Plan de Marketing",
                    content=marketing_plan,
                    project_name=f"Proyecto: {business_idea[:50]}",
                    company_name="InnovAI",
                    author=f"Usuario: {current_user.email}"
                )
                
                pdf_content = pdf_service.generate_document(doc_request)
                
                # Crear nombre único para el archivo
                filename = f"plan_marketing_{project_id}_{uuid.uuid4().hex[:8]}.pdf"
                project_dir = os.path.join(settings.UPLOAD_DIR, str(project_id))
                os.makedirs(project_dir, exist_ok=True)
                file_path = os.path.join(project_dir, filename)
                
                # Guardar archivo PDF
                with open(file_path, 'wb') as f:
                    f.write(pdf_content)
                
                # Crear registro en base de datos
                db_document = ProjectDocument(
                    filename=filename,
                    original_filename=f"Plan de Marketing - {business_idea[:50]}.pdf",
                    file_path=file_path,
                    file_type='.pdf',
                    file_size=len(pdf_content),
                    description=f"Plan de marketing profesional generado automáticamente para: {business_idea}",
                    project_id=project_id,
                    uploader_id=current_user.id
                )
                
                db.add(db_document)
                db.commit()
                db.refresh(db_document)
                
                document_url = f"/api/documents/{db_document.id}/download"
                document_id = db_document.id
                
                logger.info(f"Plan de marketing PDF guardado como documento ID: {db_document.id}")
                
            except Exception as e:
                logger.error(f"Error guardando plan de marketing PDF: {str(e)}")
        
        return {
            "status": "success",
            "message": "Plan de marketing generado exitosamente",
            "marketing_plan": marketing_plan,
            "document_url": document_url,
            "document_id": document_id
        }
        
    except Exception as e:
        logger.error(f"Error generando plan de marketing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generando plan de marketing: {str(e)}")

@router.post("/generate-market-research", response_model=dict)
async def generate_market_research(
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Genera un análisis de mercado detallado usando IA
    """
    try:
        # Extraer datos del request
        business_idea = request.get("business_idea", "")
        project_id = request.get("project_id")
        use_gpt4 = request.get("use_gpt4", False)
        
        if not business_idea:
            raise HTTPException(status_code=400, detail="business_idea es requerido")
        
        # Determinar el modelo a usar
        model = "gpt-4" if use_gpt4 else "gpt-3.5-turbo-16k"
        
        # Prompt especializado para análisis de mercado
        prompt = f"""
        Genera un análisis de mercado detallado y profundo para la siguiente idea de negocio: "{business_idea}"
        
        El análisis debe incluir:
        
        1. RESUMEN EJECUTIVO (2-3 párrafos)
        2. OBJETIVOS DE LA INVESTIGACIÓN (3-5 objetivos específicos)
        3. METODOLOGÍA (enfoque de investigación)
        4. VISIÓN GENERAL DEL MERCADO:
           - Tamaño del mercado
           - Crecimiento del mercado
           - Segmentos del mercado (nombre, tamaño, tasa de crecimiento, características, necesidades)
           - Impulsores clave del mercado
           - Desafíos del mercado
        5. INSIGHTS DEL CLIENTE:
           - Viaje del cliente (etapa, puntos de contacto, emociones, necesidades, oportunidades)
           - Puntos de dolor identificados
           - Preferencias del cliente
           - Comportamiento de compra
           - Factores de satisfacción
        6. PAISAJE COMPETITIVO:
           - Participación de mercado (empresa, porcentaje, tendencia)
           - Posiciones competitivas (empresa, posición, fortalezas, debilidades, estrategias)
           - Ventajas competitivas
           - Amenazas identificadas
        7. OPORTUNIDADES DE MERCADO (3-5 oportunidades)
        8. RECOMENDACIONES (3-5 recomendaciones estratégicas)
        9. APÉNDICES (fuentes de datos, metodología detallada)
        
        Responde en formato JSON con la siguiente estructura:
        {{
            "executive_summary": "resumen ejecutivo",
            "research_objectives": ["objetivo 1", "objetivo 2", "objetivo 3"],
            "methodology": "metodología de investigación",
            "market_overview": {{
                "market_size": "tamaño del mercado",
                "market_growth": "crecimiento del mercado",
                "market_segments": [
                    {{
                        "name": "nombre del segmento",
                        "size": "tamaño del segmento",
                        "growth_rate": "tasa de crecimiento",
                        "characteristics": ["característica 1", "característica 2"],
                        "needs": ["necesidad 1", "necesidad 2"]
                    }}
                ],
                "key_drivers": ["impulsor 1", "impulsor 2"],
                "challenges": ["desafío 1", "desafío 2"]
            }},
            "customer_insights": {{
                "customer_journey": [
                    {{
                        "stage": "etapa del viaje",
                        "touchpoints": ["punto de contacto 1", "punto de contacto 2"],
                        "emotions": ["emoción 1", "emoción 2"],
                        "needs": ["necesidad 1", "necesidad 2"],
                        "opportunities": ["oportunidad 1", "oportunidad 2"]
                    }}
                ],
                "pain_points": ["punto de dolor 1", "punto de dolor 2"],
                "preferences": ["preferencia 1", "preferencia 2"],
                "buying_behavior": ["comportamiento 1", "comportamiento 2"],
                "satisfaction_factors": ["factor 1", "factor 2"]
            }},
            "competitive_landscape": {{
                "market_share": [
                    {{
                        "company": "nombre de la empresa",
                        "percentage": 25.5,
                        "trend": "increasing"
                    }}
                ],
                "competitive_positions": [
                    {{
                        "company": "nombre de la empresa",
                        "position": "líder del mercado",
                        "strengths": ["fortaleza 1", "fortaleza 2"],
                        "weaknesses": ["debilidad 1", "debilidad 2"],
                        "strategies": ["estrategia 1", "estrategia 2"]
                    }}
                ],
                "competitive_advantages": ["ventaja 1", "ventaja 2"],
                "threats": ["amenaza 1", "amenaza 2"]
            }},
            "market_opportunities": ["oportunidad 1", "oportunidad 2", "oportunidad 3"],
            "recommendations": ["recomendación 1", "recomendación 2", "recomendación 3"],
            "appendices": ["apéndice 1", "apéndice 2"]
        }}
        
        Asegúrate de que todos los campos estén completos y sean realistas para la idea de negocio.
        """
        
        # Verificar que openai_client esté disponible

        
        validate_openai_client()

        
        

        
        # Llamar a OpenAI
        response = await openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Eres un experto investigador de mercado especializado en análisis profundo de mercados y comportamiento del cliente."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000 if model == "gpt-4" else 8000
        )
        
        # Extraer y parsear la respuesta
        content = response.choices[0].message.content
        market_research = json.loads(content)
        
        # Generar PDF y guardar documento si hay project_id
        document_url = None
        document_id = None
        if project_id:
            try:
                from ..services.pdf_generation_service import PDFGenerationService, DocumentRequest, DocumentType
                from ..models.document import ProjectDocument
                import uuid
                
                pdf_service = PDFGenerationService()
                doc_request = DocumentRequest(
                    document_type=DocumentType.MARKET_RESEARCH,
                    title="Investigación de Mercado",
                    content=market_research,
                    project_name=f"Proyecto: {business_idea[:50]}",
                    company_name="InnovAI",
                    author=f"Usuario: {current_user.email}"
                )
                
                pdf_content = pdf_service.generate_document(doc_request)
                
                # Crear nombre único para el archivo
                filename = f"investigacion_mercado_{project_id}_{uuid.uuid4().hex[:8]}.pdf"
                project_dir = os.path.join(settings.UPLOAD_DIR, str(project_id))
                os.makedirs(project_dir, exist_ok=True)
                file_path = os.path.join(project_dir, filename)
                
                # Guardar archivo PDF
                with open(file_path, 'wb') as f:
                    f.write(pdf_content)
                
                # Crear registro en base de datos
                db_document = ProjectDocument(
                    filename=filename,
                    original_filename=f"Investigación de Mercado - {business_idea[:50]}.pdf",
                    file_path=file_path,
                    file_type='.pdf',
                    file_size=len(pdf_content),
                    description=f"Investigación de mercado profesional generada automáticamente para: {business_idea}",
                    project_id=project_id,
                    uploader_id=current_user.id
                )
                
                db.add(db_document)
                db.commit()
                db.refresh(db_document)
                
                document_url = f"/api/documents/{db_document.id}/download"
                document_id = db_document.id
                
                logger.info(f"Investigación de mercado PDF guardada como documento ID: {db_document.id}")
                
            except Exception as e:
                logger.error(f"Error guardando investigación de mercado PDF: {str(e)}")
        
        return {
            "status": "success",
            "message": "Análisis de mercado generado exitosamente",
            "market_research": market_research,
            "document_url": document_url,
            "document_id": document_id
        }
        
    except Exception as e:
        logger.error(f"Error generando análisis de mercado: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generando análisis de mercado: {str(e)}")

@router.post("/generate-business-model-alternatives", response_model=dict)
async def generate_business_model_alternatives(
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Genera análisis de modelos de negocio alternativos usando IA
    """
    try:
        # Extraer datos del request
        business_idea = request.get("business_idea", "")
        project_id = request.get("project_id")
        use_gpt4 = request.get("use_gpt4", False)
        
        if not business_idea:
            raise HTTPException(status_code=400, detail="business_idea es requerido")
        
        # Determinar el modelo a usar
        model = "gpt-4" if use_gpt4 else "gpt-3.5-turbo-16k"
        
        # Prompt especializado para modelos de negocio alternativos
        prompt = f"""
        Genera un análisis completo de modelos de negocio alternativos para la siguiente idea de negocio: "{business_idea}"
        
        El análisis debe incluir:
        
        1. RESUMEN EJECUTIVO (2-3 párrafos)
        2. ANÁLISIS DEL MODELO ACTUAL:
           - Descripción del modelo de negocio actual
           - Fortalezas del modelo actual
           - Debilidades del modelo actual
        3. MODELOS DE NEGOCIO ALTERNATIVOS (3-5 modelos diferentes):
           - Nombre del modelo
           - Descripción detallada
           - Características principales
           - Ventajas específicas
           - Desventajas y limitaciones
           - Casos de uso apropiados
        4. ANÁLISIS COMPARATIVO:
           - Criterios de evaluación
           - Matriz comparativa detallada
           - Análisis de viabilidad
        5. RECOMENDACIONES DE IMPLEMENTACIÓN:
           - Modelo recomendado
           - Justificación de la recomendación
           - Consideraciones especiales
        6. PLAN DE TRANSICIÓN:
           - Fases de implementación
           - Recursos necesarios
           - Riesgos y mitigaciones
        7. MÉTRICAS DE ÉXITO:
           - KPIs principales
           - Métricas de seguimiento
           - Cronograma de evaluación
        
        Responde en formato JSON con la siguiente estructura:
        {{
            "executive_summary": "resumen ejecutivo",
            "current_model": {{
                "description": "descripción del modelo actual",
                "strengths": ["fortaleza 1", "fortaleza 2"],
                "weaknesses": ["debilidad 1", "debilidad 2"]
            }},
            "alternatives": [
                {{
                    "name": "nombre del modelo alternativo",
                    "description": "descripción detallada",
                    "key_features": ["característica 1", "característica 2"],
                    "advantages": ["ventaja 1", "ventaja 2"],
                    "disadvantages": ["desventaja 1", "desventaja 2"],
                    "use_cases": ["caso de uso 1", "caso de uso 2"]
                }}
            ],
            "comparison": {{
                "evaluation_criteria": ["criterio 1", "criterio 2"],
                "comparative_matrix": "matriz comparativa detallada"
            }},
            "implementation_recommendations": {{
                "recommended_model": "modelo recomendado",
                "justification": "justificación de la recomendación",
                "special_considerations": ["consideración 1", "consideración 2"]
            }},
            "transition_plan": {{
                "implementation_phases": [
                    {{
                        "name": "nombre de la fase",
                        "duration": "duración estimada",
                        "activities": "actividades principales"
                    }}
                ],
                "required_resources": ["recurso 1", "recurso 2"],
                "risks_mitigations": ["riesgo 1", "riesgo 2"]
            }},
            "success_metrics": {{
                "primary_kpis": ["KPI 1", "KPI 2"],
                "tracking_metrics": ["métrica 1", "métrica 2"],
                "evaluation_timeline": "cronograma de evaluación"
            }}
        }}
        
        Asegúrate de que todos los campos estén completos y sean realistas para la idea de negocio.
        """
        
        # Verificar que openai_client esté disponible
        validate_openai_client()
        
        # Llamar a OpenAI
        response = await openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Eres un experto consultor de modelos de negocio especializado en análisis estratégico y diseño de modelos de negocio innovadores."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000 if model == "gpt-4" else 8000
        )
        
        # Extraer y parsear la respuesta
        content = response.choices[0].message.content
        business_model_alternatives = json.loads(content)
        
        # Generar PDF y guardar documento si hay project_id
        document_url = None
        document_id = None
        if project_id:
            try:
                from ..services.pdf_generation_service import PDFGenerationService, DocumentRequest, DocumentType
                from ..models.document import ProjectDocument
                import uuid
                
                pdf_service = PDFGenerationService()
                doc_request = DocumentRequest(
                    document_type=DocumentType.BUSINESS_MODEL_ALTERNATIVES,
                    title="Modelos de Negocio Alternativos",
                    content=business_model_alternatives,
                    project_name=f"Proyecto: {business_idea[:50]}",
                    company_name="InnovAI",
                    author=f"Usuario: {current_user.email}"
                )
                
                pdf_content = pdf_service.generate_document(doc_request)
                
                # Crear nombre único para el archivo
                filename = f"modelos_negocio_{project_id}_{uuid.uuid4().hex[:8]}.pdf"
                project_dir = os.path.join(settings.UPLOAD_DIR, str(project_id))
                os.makedirs(project_dir, exist_ok=True)
                file_path = os.path.join(project_dir, filename)
                
                # Guardar archivo PDF
                with open(file_path, 'wb') as f:
                    f.write(pdf_content)
                
                # Crear registro en base de datos
                db_document = ProjectDocument(
                    filename=filename,
                    original_filename=f"Modelos de Negocio Alternativos - {business_idea[:50]}.pdf",
                    file_path=file_path,
                    file_type='.pdf',
                    file_size=len(pdf_content),
                    description=f"Análisis de modelos de negocio alternativos generado automáticamente para: {business_idea}",
                    project_id=project_id,
                    uploader_id=current_user.id
                )
                
                db.add(db_document)
                db.commit()
                db.refresh(db_document)
                
                document_url = f"/api/documents/{db_document.id}/download"
                document_id = db_document.id
                
                logger.info(f"Modelos de negocio alternativos PDF guardados como documento ID: {db_document.id}")
                
            except Exception as e:
                logger.error(f"Error guardando modelos de negocio alternativos PDF: {str(e)}")
        
        return {
            "status": "success",
            "message": "Análisis de modelos de negocio alternativos generado exitosamente",
            "business_model_alternatives": business_model_alternatives,
            "document_url": document_url,
            "document_id": document_id
        }
        
    except Exception as e:
        logger.error(f"Error generando modelos de negocio alternativos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generando modelos de negocio alternativos: {str(e)}")

@router.post("/generate-complete-project", response_model=dict)
async def generate_complete_project(
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Genera un proyecto completo con BMC, plan de negocio, marketing y análisis de mercado
    """
    try:
        # Extraer datos del request
        business_idea = request.get("business_idea", "")
        use_gpt4 = request.get("use_gpt4", False)
        
        if not business_idea:
            raise HTTPException(status_code=400, detail="business_idea es requerido")
        
        # Determinar el modelo a usar
        model = "gpt-4" if use_gpt4 else "gpt-3.5-turbo-16k"
        
        # 1. Generar BMC
        bmc_response = await generate_bmc_with_ai(business_idea, "openai", False, use_gpt4, True)
        
        # 2. Generar plan de negocio
        business_plan_response = await generate_business_plan_internal(business_idea, current_user.id, None, use_gpt4)
        
        # 3. Generar plan de marketing
        marketing_plan_response = await generate_marketing_plan_internal(business_idea, current_user.id, None, use_gpt4)
        
        # 4. Generar análisis de mercado
        market_research_response = await generate_market_research_internal(business_idea, current_user.id, None, use_gpt4)
        
        # 5. Crear proyecto en la base de datos
        project_name = business_idea[:50] + "..." if len(business_idea) > 50 else business_idea
        project = Project(
            name=project_name,
            description=f"Proyecto generado automáticamente con IA: {business_idea}",
            category="Generado por IA",
            tags=["IA", "Generado automáticamente"],
            location="Sin ubicación",
            status="active",
            created_by=current_user.id
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        # 6. Crear actividades basadas en el BMC
        activities = []
        if bmc_response.get("recommended_activities"):
            for i, rec_activity in enumerate(bmc_response["recommended_activities"][:5]):  # Máximo 5 actividades
                activity = ProjectActivity(
                    title=rec_activity["title"],
                    description=rec_activity["description"],
                    status="pending",
                    priority=rec_activity["priority"],
                    start_date=datetime.now(),
                    due_date=datetime.now() + timedelta(days=rec_activity["estimated_duration_days"]),
                    project_id=project.id,
                    created_by=current_user.id
                )
                db.add(activity)
                activities.append(activity)
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Proyecto completo generado exitosamente",
            "project_id": project.id,
            "project_name": project.name,
            "bmc": bmc_response.get("bmc", {}),
            "business_plan": business_plan_response.get("business_plan", {}),
            "marketing_plan": marketing_plan_response.get("marketing_plan", {}),
            "market_research": market_research_response.get("market_research", {}),
            "activities": [
                {
                    "id": act.id,
                    "title": act.title,
                    "description": act.description,
                    "status": act.status,
                    "priority": act.priority,
                    "start_date": act.start_date.isoformat(),
                    "due_date": act.due_date.isoformat()
                } for act in activities
            ],
            "documents": {
                "business_plan_url": None,
                "marketing_plan_url": None,
                "market_research_url": None
            }
        }
        
    except Exception as e:
        logger.error(f"Error generando proyecto completo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generando proyecto completo: {str(e)}")

# Funciones auxiliares para generar documentos individuales
async def generate_business_plan_internal(business_idea: str, user_id: int, project_id: Optional[int], use_gpt4: bool):
    """Función auxiliar para generar plan de negocio"""
    try:
        # Determinar el modelo a usar
        model = "gpt-4" if use_gpt4 else "gpt-3.5-turbo-16k"
        
        # Prompt especializado para plan de negocio
        prompt = f"""
        Genera un plan de negocio completo y profesional para la siguiente idea de negocio: "{business_idea}"
        
        El plan debe incluir:
        
        1. RESUMEN EJECUTIVO (2-3 párrafos)
        2. DESCRIPCIÓN DE LA EMPRESA (1-2 párrafos)
        3. ANÁLISIS DE MERCADO:
           - Tamaño del mercado
           - Mercado objetivo
           - Tendencias del mercado
           - Análisis de competencia
           - Posicionamiento en el mercado
        4. ESTRUCTURA ORGANIZACIONAL:
           - Estructura organizacional
           - Equipo de gestión
           - Estructura legal
           - Personal clave
        5. LÍNEA DE PRODUCTOS/SERVICIOS:
           - Descripción detallada
           - Características y beneficios
           - Ciclo de vida del producto
           - Propiedad intelectual
        6. ESTRATEGIA DE MARKETING Y VENTAS:
           - Estrategia de marketing
           - Estrategia de ventas
           - Estrategia de precios
           - Canales de distribución
           - Estrategia promocional
        7. REQUISITOS DE FINANCIAMIENTO:
           - Financiamiento actual
           - Necesidades de financiamiento
           - Uso de fondos
           - Fuentes de financiamiento
           - Cronograma
        8. PROYECCIONES FINANCIERAS (3 años):
           - Proyecciones de ingresos
           - Proyecciones de costos
           - Estado de resultados
           - Flujo de caja
           - Análisis de punto de equilibrio
        9. APÉNDICES
        
        Responde en formato JSON con la estructura completa del plan de negocio.
        """
        
        # Verificar que openai_client esté disponible

        
        validate_openai_client()

        
        

        
        # Llamar a OpenAI
        response = await openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Eres un experto consultor de negocios especializado en crear planes de negocio profesionales y completos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000 if model == "gpt-4" else 8000
        )
        
        # Extraer y parsear la respuesta
        content = response.choices[0].message.content
        business_plan = json.loads(content)
        
        return {
            "status": "success",
            "message": "Plan de negocio generado exitosamente",
            "business_plan": business_plan
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generando plan de negocio: {str(e)}",
            "business_plan": {}
        }

async def generate_marketing_plan_internal(business_idea: str, user_id: int, project_id: Optional[int], use_gpt4: bool):
    """Función auxiliar para generar plan de marketing"""
    try:
        # Determinar el modelo a usar
        model = "gpt-4" if use_gpt4 else "gpt-3.5-turbo-16k"
        
        # Prompt especializado para plan de marketing
        prompt = f"""
        Genera un plan de marketing estratégico completo para la siguiente idea de negocio: "{business_idea}"
        
        El plan debe incluir:
        
        1. RESUMEN DEL MERCADO (1-2 párrafos)
        2. AUDIENCIA OBJETIVO:
           - Audiencia primaria (descripción, tamaño, características, puntos de dolor, motivaciones)
           - Audiencia secundaria (descripción, tamaño, características, puntos de dolor, motivaciones)
           - Demografía (rango de edad, género, nivel de ingresos, educación, ubicación, ocupación)
           - Psicografía (valores, intereses, estilo de vida)
           - Patrones de comportamiento (frecuencia de compra, canales preferidos, etc.)
        3. OBJETIVOS DE MARKETING (3-5 objetivos específicos y medibles)
        4. ESTRATEGIAS DE MARKETING (por canal):
           - Canal digital (enfoque, tácticas, presupuesto, resultados esperados)
           - Canal tradicional (enfoque, tácticas, presupuesto, resultados esperados)
           - Otros canales relevantes
        5. PLAN DE PRESUPUESTO:
           - Presupuesto total
           - Asignación por canal (porcentaje, monto, justificación)
           - Asignación por timeline (período, porcentaje, monto, actividades)
        6. TIMELINE DE IMPLEMENTACIÓN (cronograma detallado)
        7. KPIs Y MÉTRICAS (indicadores clave de rendimiento)
        
        Responde en formato JSON con la estructura completa del plan de marketing.
        """
        
        # Verificar que openai_client esté disponible

        
        validate_openai_client()

        
        

        
        # Llamar a OpenAI
        response = await openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Eres un experto consultor de marketing especializado en crear planes de marketing estratégicos y efectivos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000 if model == "gpt-4" else 8000
        )
        
        # Extraer y parsear la respuesta
        content = response.choices[0].message.content
        marketing_plan = json.loads(content)
        
        return {
            "status": "success",
            "message": "Plan de marketing generado exitosamente",
            "marketing_plan": marketing_plan
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generando plan de marketing: {str(e)}",
            "marketing_plan": {}
        }

async def generate_market_research_internal(business_idea: str, user_id: int, project_id: Optional[int], use_gpt4: bool):
    """Función auxiliar para generar análisis de mercado"""
    try:
        # Determinar el modelo a usar
        model = "gpt-4" if use_gpt4 else "gpt-3.5-turbo-16k"
        
        # Prompt especializado para análisis de mercado
        prompt = f"""
        Genera un análisis de mercado detallado y profundo para la siguiente idea de negocio: "{business_idea}"
        
        El análisis debe incluir:
        
        1. RESUMEN EJECUTIVO (2-3 párrafos)
        2. OBJETIVOS DE LA INVESTIGACIÓN (3-5 objetivos específicos)
        3. METODOLOGÍA (enfoque de investigación)
        4. VISIÓN GENERAL DEL MERCADO:
           - Tamaño del mercado
           - Crecimiento del mercado
           - Segmentos del mercado (nombre, tamaño, tasa de crecimiento, características, necesidades)
           - Impulsores clave del mercado
           - Desafíos del mercado
        5. INSIGHTS DEL CLIENTE:
           - Viaje del cliente (etapa, puntos de contacto, emociones, necesidades, oportunidades)
           - Puntos de dolor identificados
           - Preferencias del cliente
           - Comportamiento de compra
           - Factores de satisfacción
        6. PAISAJE COMPETITIVO:
           - Participación de mercado (empresa, porcentaje, tendencia)
           - Posiciones competitivas (empresa, posición, fortalezas, debilidades, estrategias)
           - Ventajas competitivas
           - Amenazas identificadas
        7. OPORTUNIDADES DE MERCADO (3-5 oportunidades)
        8. RECOMENDACIONES (3-5 recomendaciones estratégicas)
        9. APÉNDICES (fuentes de datos, metodología detallada)
        
        Responde en formato JSON con la estructura completa del análisis de mercado.
        """
        
        # Verificar que openai_client esté disponible

        
        validate_openai_client()

        
        

        
        # Llamar a OpenAI
        response = await openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Eres un experto investigador de mercado especializado en análisis profundo de mercados y comportamiento del cliente."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000 if model == "gpt-4" else 8000
        )
        
        # Extraer y parsear la respuesta
        content = response.choices[0].message.content
        market_research = json.loads(content)
        
        return {
            "status": "success",
            "message": "Análisis de mercado generado exitosamente",
            "market_research": market_research
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generando análisis de mercado: {str(e)}",
            "market_research": {}
        }

# Esquemas para detección de intenciones
class ConversationMessage(BaseModel):
    text: str
    sender: str
    timestamp: str

class ProjectContext(BaseModel):
    id: str
    name: str
    description: str

class UserProfile(BaseModel):
    role: str
    preferences: List[str]

class ConversationContext(BaseModel):
    recent_messages: List[ConversationMessage]
    current_project: Optional[ProjectContext] = None
    user_profile: Optional[UserProfile] = None

class IntentDetectionRequest(BaseModel):
    message: str
    conversation_context: ConversationContext
    prompt: Optional[str] = None

@router.post("/detect-intent")
async def detect_intent(
    request: IntentDetectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Detectar la intención del usuario usando IA
    """
    try:
        validate_openai_client()
        
        # Construir el prompt para detección de intenciones
        prompt = request.prompt or f"""
Eres un asistente especializado en emprendimiento e innovación que ayuda a detectar la intención de los usuarios.

ANALIZA el mensaje del usuario y determina su INTENCIÓN PRINCIPAL:

INTENCIONES DISPONIBLES:
- bmc_generation: Solicita Business Model Canvas, modelo de negocio, BMC
- business_plan: Solicita plan de negocio, business plan, plan empresarial  
- marketing_plan: Solicita plan de marketing, estrategia de marketing
- market_research: Solicita investigación de mercado, análisis de mercado
- project_analysis: Solicita análisis de proyecto, estado del proyecto
- activity_recommendations: Solicita recomendaciones, mejoras, optimización
- guided_conversation: Solicita conversación guiada, preguntas paso a paso
- business_interview: Solicita entrevista de negocio, cuestionario empresarial
- complete_project_generation: Solicita crear proyecto completo
- general_conversation: Conversación general, preguntas generales

CONTEXTO DE CONVERSACIÓN:
Mensajes recientes: {[msg.text for msg in request.conversation_context.recent_messages]}
Proyecto actual: {request.conversation_context.current_project.name if request.conversation_context.current_project else 'Ninguno'}
Perfil usuario: {request.conversation_context.user_profile.role if request.conversation_context.user_profile else 'No disponible'}

MENSAJE DEL USUARIO: "{request.message}"

Responde ÚNICAMENTE en formato JSON válido:
{{
  "intent": "intención_detectada",
  "confidence": 0.95,
  "extractedContext": "contexto_extraído_del_mensaje_y_conversación",
  "suggestedAction": "acción_específica_sugerida",
  "reasoning": "breve_explicación_del_razonamiento"
}}
"""

        # Llamar a OpenAI para detectar la intención
        response = await openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un experto en análisis de intenciones de usuarios especializado en emprendimiento e innovación. Responde ÚNICAMENTE en formato JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        # Extraer y parsear la respuesta
        content = response.choices[0].message.content
        
        try:
            intent_result = json.loads(content)
            
            # Validar que la respuesta tenga la estructura esperada
            if not all(key in intent_result for key in ['intent', 'confidence', 'extractedContext', 'suggestedAction']):
                raise ValueError("Respuesta de OpenAI no tiene la estructura esperada")
            
            return {
                "status": "success",
                "message": "Intención detectada exitosamente",
                "data": intent_result
            }
            
        except json.JSONDecodeError as e:
            # Si no se puede parsear JSON, usar detección de fallback
            logger.warning(f"Error parseando respuesta de OpenAI: {e}")
            return {
                "status": "success",
                "message": "Intención detectada usando fallback",
                "data": {
                    "intent": "general_conversation",
                    "confidence": 0.6,
                    "extractedContext": request.message,
                    "suggestedAction": "Iniciar conversación general",
                    "reasoning": "Fallback por error de parsing"
                }
            }
        
    except Exception as e:
        logger.error(f"Error en detección de intención: {str(e)}")
        return {
            "status": "error",
            "message": f"Error detectando intención: {str(e)}",
            "data": {
                "intent": "general_conversation",
                "confidence": 0.5,
                "extractedContext": request.message,
                "suggestedAction": "Conversación general",
                "reasoning": "Error en detección"
            }
        }

# ============================================================================
# NUEVO ENDPOINT CON AGENTKIT INTEGRATION
# ============================================================================

@router.post("/enhanced-chat")
async def enhanced_chat(
    request: EnhancedChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint mejorado que integra Guardrails, Reasoning y Workflows del AgentKit
    """
    try:
        logger.info(f"Procesando chat mejorado para usuario {current_user.id}")
        
        # PASO 1: Guardrails - Validar entrada
        guardrails_result = None
        if request.use_guardrails:
            guardrails_result = guardrails_service.validate_input(request.message)
            
            if not guardrails_result['should_proceed']:
                return {
                    "status": "blocked",
                    "message": guardrails_result['overall_message'],
                    "reason": "guardrails_failed",
                    "details": guardrails_result['checks'],
                    "suggestions": [
                        "Reformula tu pregunta enfocándote en emprendimiento y creación de negocios",
                        "Evita incluir información personal como emails o teléfonos",
                        "Mantén el foco en temas relacionados con tu proyecto empresarial"
                    ]
                }
        
        # PASO 2: Obtener contexto del proyecto si está disponible
        project_context = None
        bmc_data = None
        
        if request.project_id:
            project = db.query(Project).filter(
                Project.id == request.project_id,
                Project.user_id == current_user.id
            ).first()
            
            if project:
                project_context = {
                    "project_name": project.name,
                    "project_description": project.description,
                    "project_category": project.category,
                    "project_status": project.status
                }
                
                # Obtener BMC si existe
                bmc = db.query(BusinessModelCanvas).filter(
                    BusinessModelCanvas.project_id == request.project_id
                ).first()
                
                if bmc:
                    bmc_data = {
                        "key_partners": bmc.key_partners or [],
                        "key_activities": bmc.key_activities or [],
                        "key_resources": bmc.key_resources or [],
                        "value_propositions": bmc.value_propositions or [],
                        "customer_relationships": bmc.customer_relationships or [],
                        "channels": bmc.channels or [],
                        "customer_segments": bmc.customer_segments or [],
                        "cost_structure": bmc.cost_structure or [],
                        "revenue_streams": bmc.revenue_streams or []
                    }
        
        # PASO 3: Reasoning - Analizar y procesar con reasoning avanzado
        reasoning_result = None
        if request.use_reasoning:
            reasoning_context = ReasoningContext(
                user_query=request.message,
                project_context=project_context,
                bmc_data=bmc_data,
                conversation_history=[],  # En una implementación real, cargaríamos el historial
                user_profile={
                    "user_id": current_user.id,
                    "experience_level": "intermediate"  # Podría venir del perfil del usuario
                }
            )
            
            reasoning_result = reasoning_service.process_reasoning(reasoning_context)
        
        # PASO 4: Workflows - Ejecutar workflow específico si se especifica
        workflow_result = None
        if request.use_workflows and request.workflow_type:
            workflow_context = {
                "user_query": request.message,
                "project_context": project_context,
                "bmc_data": bmc_data,
                "user_id": current_user.id
            }
            
            try:
                workflow_result = await workflow_service.execute_workflow(
                    request.workflow_type, 
                    workflow_context
                )
            except Exception as e:
                logger.error(f"Error ejecutando workflow {request.workflow_type}: {e}")
                workflow_result = {"error": str(e)}
        
        # PASO 5: Generar respuesta final con OpenAI
        final_prompt = _build_enhanced_prompt(
            request.message, 
            project_context, 
            bmc_data,
            reasoning_result,
            workflow_result,
            guardrails_result
        )
        
        # Usar OpenAI para generar respuesta final
        if openai_client:
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "Eres un consultor experto en emprendimiento y creación de negocios. Proporciona consejos prácticos, específicos y accionables basados en el contexto del usuario y el análisis realizado."
                        },
                        {
                            "role": "user",
                            "content": final_prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                
                ai_response = response.choices[0].message.content
            except Exception as e:
                logger.error(f"Error con OpenAI: {e}")
                ai_response = _generate_fallback_response(request.message, reasoning_result, workflow_result)
        else:
            ai_response = _generate_fallback_response(request.message, reasoning_result, workflow_result)
        
        # PASO 6: Preparar respuesta final
        response_data = {
            "status": "success",
            "message": "Chat procesado exitosamente",
            "data": {
                "response": ai_response,
                "enhancements": {
                    "guardrails": {
                        "applied": request.use_guardrails,
                        "result": guardrails_result['overall_result'] if guardrails_result else None,
                        "warnings": guardrails_result.get('warnings', []) if guardrails_result else []
                    },
                    "reasoning": {
                        "applied": request.use_reasoning,
                        "confidence": reasoning_result['final_response']['confidence_score'] if reasoning_result else None,
                        "key_insights": reasoning_result['final_response']['key_insights'][:3] if reasoning_result else []
                    },
                    "workflow": {
                        "applied": request.use_workflows,
                        "type": request.workflow_type,
                        "status": workflow_result['status'] if workflow_result else None
                    }
                }
            }
        }
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error en chat mejorado: {str(e)}")
        return {
            "status": "error",
            "message": f"Error procesando chat: {str(e)}",
            "data": {
                "response": "Lo siento, hubo un error procesando tu consulta. Por favor intenta de nuevo.",
                "fallback": True
            }
        }

def _build_enhanced_prompt(message: str, project_context: dict, bmc_data: dict, 
                          reasoning_result: dict, workflow_result: dict, guardrails_result: dict) -> str:
    """Construye un prompt mejorado basado en todos los análisis realizados"""
    
    prompt_parts = [f"Consulta del usuario: {message}\n"]
    
    # Agregar contexto del proyecto
    if project_context:
        prompt_parts.append(f"Contexto del proyecto: {project_context.get('project_name', 'Sin nombre')}")
        prompt_parts.append(f"Descripción: {project_context.get('project_description', 'Sin descripción')}")
    
    # Agregar datos del BMC
    if bmc_data:
        prompt_parts.append("\nDatos del Business Model Canvas:")
        for key, value in bmc_data.items():
            if value and len(value) > 0:
                prompt_parts.append(f"- {key}: {', '.join(value[:3])}")
    
    # Agregar insights del reasoning
    if reasoning_result and reasoning_result.get('final_response'):
        final_resp = reasoning_result['final_response']
        prompt_parts.append(f"\nInsights clave identificados:")
        for insight in final_resp.get('key_insights', [])[:3]:
            prompt_parts.append(f"- {insight}")
        
        prompt_parts.append(f"\nRecomendaciones generadas:")
        for rec in final_resp.get('recommendations', [])[:3]:
            prompt_parts.append(f"- {rec}")
    
    # Agregar resultados del workflow
    if workflow_result and workflow_result.get('results'):
        prompt_parts.append(f"\nResultados del workflow:")
        for step_id, result in workflow_result['results'].items():
            if isinstance(result, dict) and result.get('message'):
                prompt_parts.append(f"- {result['message']}")
    
    # Agregar advertencias de guardrails
    if guardrails_result and guardrails_result.get('warnings'):
        prompt_parts.append(f"\nAdvertencias de seguridad:")
        for warning in guardrails_result['warnings']:
            prompt_parts.append(f"- {warning}")
    
    prompt_parts.append(f"\nPor favor, proporciona una respuesta útil, específica y accionable basada en toda esta información.")
    
    return "\n".join(prompt_parts)

def _generate_fallback_response(message: str, reasoning_result: dict, workflow_result: dict) -> str:
    """Genera una respuesta de fallback cuando OpenAI no está disponible"""
    
    fallback_responses = [
        "Basándome en tu consulta, te recomiendo enfocarte en desarrollar claramente tu propuesta de valor y identificar tus segmentos de clientes objetivo.",
        "Para mejorar tu negocio, considera completar tu Business Model Canvas con información más específica sobre tus canales de distribución y socios clave.",
        "Te sugiero validar tu idea de negocio mediante investigación de mercado y pruebas con clientes potenciales antes de hacer grandes inversiones."
    ]
    
    # Si tenemos reasoning, usar esas recomendaciones
    if reasoning_result and reasoning_result.get('final_response'):
        recommendations = reasoning_result['final_response'].get('recommendations', [])
        if recommendations:
            return f"Basándome en el análisis de tu situación, te recomiendo: {recommendations[0]}. Además, considera {recommendations[1] if len(recommendations) > 1 else 'validar tu propuesta de valor con clientes potenciales'}."
    
    # Si tenemos workflow, usar esos resultados
    if workflow_result and workflow_result.get('results'):
        return "He procesado tu consulta y generado recomendaciones específicas. Te sugiero revisar los resultados del análisis para obtener pasos concretos a seguir."
    
    # Respuesta genérica
    return fallback_responses[0]

# Endpoint para obtener workflows disponibles
@router.get("/workflows")
async def get_available_workflows(current_user: User = Depends(get_current_user)):
    """Obtiene la lista de workflows disponibles"""
    try:
        workflows = workflow_service.list_workflows()
        return {
            "status": "success",
            "data": workflows
        }
    except Exception as e:
        logger.error(f"Error obteniendo workflows: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

# Endpoint para obtener información de un workflow específico
@router.get("/workflows/{workflow_id}")
async def get_workflow_info(workflow_id: str, current_user: User = Depends(get_current_user)):
    """Obtiene información detallada de un workflow específico"""
    try:
        workflow_info = workflow_service.get_workflow_info(workflow_id)
        return {
            "status": "success",
            "data": workflow_info
        }
    except Exception as e:
        logger.error(f"Error obteniendo información del workflow {workflow_id}: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
