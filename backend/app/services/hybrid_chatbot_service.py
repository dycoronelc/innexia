"""
Servicio híbrido que integra el sistema de agentes OpenAI con el chatbot existente
"""

from typing import Dict, Any, Optional
import logging
from .agents_service import agents_service

logger = logging.getLogger(__name__)

class HybridChatbotService:
    """Servicio híbrido que combina agentes especializados con el sistema existente"""
    
    def __init__(self):
        self.agents_service = agents_service
        self.use_agents = True  # Flag para habilitar/deshabilitar agentes
    
    async def detect_intent_with_agents(self, message: str, conversation_context: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta intención usando agentes especializados"""
        try:
            if self.use_agents:
                result = await self.agents_service.detect_intent(message, conversation_context)
                return result
            else:
                # Fallback al sistema anterior
                return await self._fallback_intent_detection(message)
        except Exception as e:
            logger.warning(f"Error en detección con agentes, usando fallback: {e}")
            return await self._fallback_intent_detection(message)
    
    async def generate_bmc_with_agents(self, business_idea: str, use_high_quality: bool = False) -> Dict[str, Any]:
        """Genera BMC usando agentes especializados"""
        try:
            if self.use_agents:
                return await self.agents_service.generate_bmc(business_idea, use_high_quality)
            else:
                # Fallback al sistema anterior
                return await self._fallback_bmc_generation(business_idea, use_high_quality)
        except Exception as e:
            logger.warning(f"Error generando BMC con agentes, usando fallback: {e}")
            return await self._fallback_bmc_generation(business_idea, use_high_quality)
    
    async def generate_business_plan_with_agents(self, business_idea: str) -> Dict[str, Any]:
        """Genera plan de negocio usando agentes especializados"""
        try:
            if self.use_agents:
                return await self.agents_service.generate_business_plan(business_idea)
            else:
                # Fallback al sistema anterior
                return await self._fallback_business_plan_generation(business_idea)
        except Exception as e:
            logger.warning(f"Error generando plan de negocio con agentes, usando fallback: {e}")
            return await self._fallback_business_plan_generation(business_idea)
    
    async def generate_marketing_plan_with_agents(self, business_idea: str) -> Dict[str, Any]:
        """Genera plan de marketing usando agentes especializados"""
        try:
            if self.use_agents:
                return await self.agents_service.generate_marketing_plan(business_idea)
            else:
                # Fallback al sistema anterior
                return await self._fallback_marketing_plan_generation(business_idea)
        except Exception as e:
            logger.warning(f"Error generando plan de marketing con agentes, usando fallback: {e}")
            return await self._fallback_marketing_plan_generation(business_idea)
    
    async def _fallback_intent_detection(self, message: str) -> Dict[str, Any]:
        """Fallback para detección de intenciones usando el sistema anterior"""
        lower_message = message.lower()
        
        if any(phrase in lower_message for phrase in ['bmc', 'business model canvas', 'modelo de negocio']):
            return {
                "intent": "bmc_generation",
                "confidence": 0.8,
                "extractedContext": message,
                "suggestedAction": "Generar Business Model Canvas",
                "reasoning": "Detectado usando fallback"
            }
        elif any(phrase in lower_message for phrase in ['plan de negocio', 'business plan']):
            return {
                "intent": "business_plan",
                "confidence": 0.8,
                "extractedContext": message,
                "suggestedAction": "Generar plan de negocio",
                "reasoning": "Detectado usando fallback"
            }
        elif any(phrase in lower_message for phrase in ['plan de marketing', 'estrategia de marketing']):
            return {
                "intent": "marketing_plan",
                "confidence": 0.8,
                "extractedContext": message,
                "suggestedAction": "Generar plan de marketing",
                "reasoning": "Detectado usando fallback"
            }
        else:
            return {
                "intent": "general_conversation",
                "confidence": 0.5,
                "extractedContext": message,
                "suggestedAction": "Conversación general",
                "reasoning": "Fallback por defecto"
            }
    
    async def _fallback_bmc_generation(self, business_idea: str, use_high_quality: bool = False) -> Dict[str, Any]:
        """Fallback para generación de BMC usando el sistema anterior"""
        # Aquí iría la lógica del sistema anterior
        # Por ahora retornamos un BMC genérico
        return {
            "bmc": {
                "key_partners": ["Socio estratégico 1", "Proveedor clave"],
                "key_activities": ["Desarrollo de producto", "Marketing"],
                "key_resources": ["Equipo técnico", "Tecnología"],
                "value_propositions": ["Valor único 1", "Beneficio clave"],
                "customer_relationships": ["Relación directa", "Soporte personalizado"],
                "channels": ["Canal online", "Distribución directa"],
                "customer_segments": ["Segmento objetivo 1", "Mercado secundario"],
                "cost_structure": ["Costo de desarrollo", "Costo operativo"],
                "revenue_streams": ["Venta directa", "Suscripciones"]
            },
            "recommended_activities": [
                {
                    "title": "Actividad recomendada",
                    "description": "Descripción de la actividad",
                    "priority": "high",
                    "estimated_duration_days": 7
                }
            ]
        }
    
    async def _fallback_business_plan_generation(self, business_idea: str) -> Dict[str, Any]:
        """Fallback para generación de plan de negocio"""
        return {
            "executive_summary": f"Plan de negocio para: {business_idea}",
            "business_description": "Descripción del negocio",
            "market_analysis": "Análisis de mercado",
            "marketing_strategy": "Estrategia de marketing",
            "financial_projections": "Proyecciones financieras"
        }
    
    async def _fallback_marketing_plan_generation(self, business_idea: str) -> Dict[str, Any]:
        """Fallback para generación de plan de marketing"""
        return {
            "target_market": "Mercado objetivo",
            "positioning": "Posicionamiento",
            "marketing_channels": ["Canal 1", "Canal 2"],
            "budget": "Presupuesto estimado",
            "metrics": "Métricas de éxito"
        }
    
    def enable_agents(self):
        """Habilita el uso de agentes especializados"""
        self.use_agents = True
        logger.info("Agentes especializados habilitados")
    
    def disable_agents(self):
        """Deshabilita el uso de agentes especializados"""
        self.use_agents = False
        logger.info("Agentes especializados deshabilitados, usando sistema anterior")

# Instancia global del servicio híbrido
hybrid_chatbot_service = HybridChatbotService()
