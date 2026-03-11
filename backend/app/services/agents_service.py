"""
Servicio de Agentes OpenAI para detección de intenciones y generación de contenido
"""
import json
import logging
from typing import Dict, Any, List, Optional
from agents import Agent, Runner, SQLiteSession, AgentOutputSchema
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class IntentDetectionResult(BaseModel):
    intent: str
    confidence: float
    extractedContext: str
    suggestedAction: str
    reasoning: str

class BMCData(BaseModel):
    key_partners: List[str]
    key_activities: List[str]
    key_resources: List[str]
    value_propositions: List[str]
    customer_relationships: List[str]
    channels: List[str]
    customer_segments: List[str]
    cost_structure: List[str]
    revenue_streams: List[str]

class RecommendedActivity(BaseModel):
    title: str
    description: str
    priority: str
    estimated_duration_days: int

class BMCResult(BaseModel):
    bmc: BMCData
    recommended_activities: List[RecommendedActivity]

class AgentsService:
    def __init__(self):
        self.agents = self._initialize_agents()
        self.session = self._get_session()
    
    def _initialize_agents(self) -> Dict[str, Agent]:
        """Inicializa los agentes especializados"""
        return {
            'intent_detector': Agent(
                name="IntentDetector",
                model="gpt-3.5-turbo",
                instructions="""
                Eres un experto en análisis de intenciones de usuarios especializado en emprendimiento e innovación.
                Tu tarea es analizar mensajes de usuarios y determinar su intención principal.
                
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
                
                Analiza el mensaje y contexto cuidadosamente. Responde ÚNICAMENTE con JSON válido:
                {
                    "intent": "intención_detectada",
                    "confidence": 0.95,
                    "extractedContext": "contexto_extraído_del_mensaje",
                    "suggestedAction": "acción_específica_sugerida",
                    "reasoning": "breve_explicación_del_razonamiento"
                }
                """
            ),
            'bmc_generator': Agent(
                name="BMCGenerator",
                model="gpt-3.5-turbo",
                instructions="""
                Eres un experto en Business Model Canvas especializado en emprendimiento e innovación.
                Tu tarea es generar un BMC específico y detallado basado en la idea de negocio proporcionada.
                
                INSTRUCCIONES:
                1. Analiza la idea de negocio cuidadosamente
                2. Genera contenido específico para cada sección del BMC
                3. Usa nombres reales y específicos, no genéricos
                4. Basa cada elemento en la industria y modelo de negocio identificado
                5. Incluye 2-3 elementos específicos por sección
                6. Genera actividades recomendadas específicas para el negocio
                
                Responde ÚNICAMENTE con JSON válido:
                {
                    "bmc": {
                        "key_partners": ["socio específico 1", "socio específico 2"],
                        "key_activities": ["actividad específica 1", "actividad específica 2"],
                        "key_resources": ["recurso específico 1", "recurso específico 2"],
                        "value_propositions": ["propuesta de valor específica 1", "propuesta de valor específica 2"],
                        "customer_relationships": ["tipo de relación específica 1", "tipo de relación específica 2"],
                        "channels": ["canal específico 1", "canal específico 2"],
                        "customer_segments": ["segmento específico 1", "segmento específico 2"],
                        "cost_structure": ["costo específico 1", "costo específico 2"],
                        "revenue_streams": ["fuente de ingreso específica 1", "fuente de ingreso específica 2"]
                    },
                    "recommended_activities": [
                        {
                            "title": "Actividad específica para este negocio",
                            "description": "Descripción detallada de la actividad",
                            "priority": "high",
                            "estimated_duration_days": 7
                        }
                    ]
                }
                """
            )
        }
    
    def _get_session(self) -> SQLiteSession:
        """Obtiene o crea una sesión SQLite para persistencia"""
        try:
            return SQLiteSession("agents_sessions.db")
        except Exception as e:
            logger.warning(f"Error creando sesión SQLite: {e}")
            # Fallback a sesión en memoria
            return SQLiteSession(":memory:")
    
    async def detect_intent(self, message: str, conversation_context: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta la intención del usuario usando agentes OpenAI"""
        try:
            context_message = f"""
            CONTEXTO DE CONVERSACIÓN:
            Mensajes recientes: {conversation_context.get('recent_messages', [])}
            Proyecto actual: {conversation_context.get('current_project', 'Ninguno')}
            Perfil usuario: {conversation_context.get('user_profile', 'No disponible')}
            
            MENSAJE DEL USUARIO: "{message}"
            """
            
            result = await Runner.run(
                self.agents['intent_detector'],
                context_message
            )
            
            try:
                # Parsear JSON del resultado
                if isinstance(result.final_output, str):
                    parsed_result = json.loads(result.final_output)
                    return parsed_result
                else:
                    return result.final_output
            except json.JSONDecodeError as e:
                logger.error(f"Error parseando JSON: {e}")
                # Si no se puede parsear, devolver resultado por defecto
                return {
                    "intent": "general_conversation",
                    "confidence": 0.5,
                    "extractedContext": message,
                    "suggestedAction": "Conversación general",
                    "reasoning": "No se pudo parsear la respuesta del agente"
                }
                
        except Exception as e:
            logger.error(f"Error en detección de intenciones: {e}")
            return {
                "intent": "general_conversation",
                "confidence": 0.5,
                "extractedContext": message,
                "suggestedAction": "Conversación general",
                "reasoning": f"Error en detección: {str(e)}"
            }
    
    async def generate_bmc(self, business_idea: str, use_high_quality: bool = True) -> Dict[str, Any]:
        """Genera un Business Model Canvas usando agentes OpenAI"""
        try:
            prompt = f"""
            Analiza la siguiente idea de negocio y genera un Business Model Canvas específico y detallado:

            IDEA DE NEGOCIO: {business_idea}

            INSTRUCCIONES:
            1. Analiza la idea de negocio cuidadosamente
            2. Genera contenido específico para cada sección del BMC
            3. Usa nombres reales y específicos, no genéricos
            4. Basa cada elemento en la industria y modelo de negocio identificado
            5. Incluye 2-3 elementos específicos por sección
            6. Genera actividades recomendadas específicas para el negocio
            """
            
            result = await Runner.run(
                self.agents['bmc_generator'],
                prompt
            )
            
            try:
                # Parsear JSON del resultado
                if isinstance(result.final_output, str):
                    return json.loads(result.final_output)
                else:
                    return result.final_output
            except json.JSONDecodeError:
                # Si no se puede parsear, devolver BMC genérico
                return {
                    "bmc": {
                        "key_partners": ["Proveedores especializados", "Socios tecnológicos"],
                        "key_activities": ["Desarrollo de producto", "Marketing digital"],
                        "key_resources": ["Equipo especializado", "Tecnología"],
                        "value_propositions": ["Solución innovadora", "Calidad superior"],
                        "customer_relationships": ["Atención personalizada", "Soporte continuo"],
                        "channels": ["Plataforma web", "Redes sociales"],
                        "customer_segments": ["Mercado objetivo", "Segmento secundario"],
                        "cost_structure": ["Desarrollo", "Marketing"],
                        "revenue_streams": ["Ventas directas", "Suscripciones"]
                    },
                    "recommended_activities": [
                        {
                            "title": "Validación de mercado",
                            "description": "Realizar investigación de mercado para validar la demanda",
                            "priority": "high",
                            "estimated_duration_days": 14
                        }
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error generando BMC: {e}")
            return {
                "bmc": {
                    "key_partners": ["Proveedores", "Socios"],
                    "key_activities": ["Actividad 1", "Actividad 2"],
                    "key_resources": ["Recurso 1", "Recurso 2"],
                    "value_propositions": ["Propuesta 1", "Propuesta 2"],
                    "customer_relationships": ["Relación 1", "Relación 2"],
                    "channels": ["Canal 1", "Canal 2"],
                    "customer_segments": ["Segmento 1", "Segmento 2"],
                    "cost_structure": ["Costo 1", "Costo 2"],
                    "revenue_streams": ["Ingreso 1", "Ingreso 2"]
                },
                "recommended_activities": []
            }
    
    async def generate_business_plan(self, business_idea: str) -> Dict[str, Any]:
        """Genera un plan de negocio usando agentes OpenAI"""
        try:
            # Por ahora, devolver un plan básico
            # TODO: Implementar agente especializado en planes de negocio
            return {
                "business_plan": {
                    "executive_summary": f"Plan de negocio para: {business_idea}",
                    "market_analysis": "Análisis de mercado detallado",
                    "financial_projections": "Proyecciones financieras"
                }
            }
        except Exception as e:
            logger.error(f"Error generando plan de negocio: {e}")
            return {"error": str(e)}
    
    async def generate_marketing_plan(self, business_idea: str) -> Dict[str, Any]:
        """Genera un plan de marketing usando agentes OpenAI"""
        try:
            # Por ahora, devolver un plan básico
            # TODO: Implementar agente especializado en planes de marketing
            return {
                "marketing_plan": {
                    "target_audience": f"Audiencia objetivo para: {business_idea}",
                    "marketing_strategies": "Estrategias de marketing",
                    "budget_allocation": "Asignación de presupuesto"
                }
            }
        except Exception as e:
            logger.error(f"Error generando plan de marketing: {e}")
            return {"error": str(e)}

# Instancia global del servicio
agents_service = AgentsService()
