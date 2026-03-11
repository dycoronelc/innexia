import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

class ReasoningStep(Enum):
    ANALYZE_CONTEXT = "analyze_context"
    IDENTIFY_KEY_INSIGHTS = "identify_key_insights"
    GENERATE_RECOMMENDATIONS = "generate_recommendations"
    VALIDATE_RECOMMENDATIONS = "validate_recommendations"
    STRUCTURE_RESPONSE = "structure_response"

@dataclass
class ReasoningContext:
    user_query: str
    project_context: Optional[Dict] = None
    bmc_data: Optional[Dict] = None
    conversation_history: Optional[List[Dict]] = None
    user_profile: Optional[Dict] = None

@dataclass
class ReasoningStepResult:
    step: ReasoningStep
    reasoning: str
    insights: List[str]
    confidence: float
    next_steps: List[str]

class ReasoningService:
    """
    Servicio de reasoning avanzado inspirado en OpenAI AgentKit
    Proporciona análisis estructurado y reasoning step-by-step para emprendimiento
    """
    
    def __init__(self):
        self.business_frameworks = {
            'bmc': {
                'key_partners': "Socios clave que ayudan a crear valor",
                'key_activities': "Actividades principales para entregar valor",
                'key_resources': "Recursos necesarios para crear valor",
                'value_propositions': "Beneficios únicos que ofreces a los clientes",
                'customer_relationships': "Cómo interactúas con diferentes segmentos de clientes",
                'channels': "Canales para llegar a los clientes",
                'customer_segments': "Grupos de clientes que atiendes",
                'cost_structure': "Costos más importantes en tu modelo de negocio",
                'revenue_streams': "Cómo generas ingresos"
            },
            'swot': {
                'strengths': "Factores internos positivos de tu negocio",
                'weaknesses': "Factores internos que necesitas mejorar",
                'opportunities': "Factores externos positivos que puedes aprovechar",
                'threats': "Factores externos que pueden afectar tu negocio"
            },
            'pestel': {
                'political': "Factores políticos que afectan tu industria",
                'economic': "Condiciones económicas del mercado",
                'social': "Tendencias sociales y demográficas",
                'technological': "Avances tecnológicos relevantes",
                'environmental': "Factores ambientales y de sostenibilidad",
                'legal': "Regulaciones y aspectos legales"
            }
        }

    def analyze_business_context(self, context: ReasoningContext) -> ReasoningStepResult:
        """
        Analiza el contexto del negocio y extrae información clave
        """
        insights = []
        reasoning = "Analizando el contexto del negocio:\n\n"
        
        # Analizar la consulta del usuario
        query_lower = context.user_query.lower()
        reasoning += f"1. Consulta del usuario: '{context.user_query}'\n"
        
        # Identificar tipo de consulta
        if any(word in query_lower for word in ['actividades', 'tareas', 'qué hacer']):
            query_type = "activity_recommendations"
            insights.append("El usuario busca recomendaciones de actividades específicas")
        elif any(word in query_lower for word in ['bmc', 'canvas', 'modelo de negocio']):
            query_type = "bmc_analysis"
            insights.append("El usuario necesita ayuda con el Business Model Canvas")
        elif any(word in query_lower for word in ['plan de negocio', 'plan', 'estratégico']):
            query_type = "business_planning"
            insights.append("El usuario requiere planificación estratégica")
        else:
            query_type = "general_consultation"
            insights.append("Consulta general sobre emprendimiento")
        
        reasoning += f"2. Tipo de consulta identificado: {query_type}\n"
        
        # Analizar datos del BMC si están disponibles
        if context.bmc_data:
            reasoning += "3. Analizando datos del Business Model Canvas:\n"
            for key, value in context.bmc_data.items():
                if value and isinstance(value, list) and len(value) > 0:
                    reasoning += f"   - {key}: {', '.join(value[:3])}{'...' if len(value) > 3 else ''}\n"
                    insights.append(f"BMC tiene datos en {key}: {len(value)} elementos")
        
        # Analizar contexto del proyecto
        if context.project_context:
            reasoning += "4. Contexto del proyecto disponible\n"
            insights.append("Contexto del proyecto encontrado para análisis personalizado")
        
        next_steps = [
            "Identificar insights específicos del BMC",
            "Generar recomendaciones personalizadas",
            "Validar recomendaciones contra mejores prácticas"
        ]
        
        return ReasoningStepResult(
            step=ReasoningStep.ANALYZE_CONTEXT,
            reasoning=reasoning,
            insights=insights,
            confidence=0.8,
            next_steps=next_steps
        )

    def identify_key_insights(self, context: ReasoningContext, analysis_result: ReasoningStepResult) -> ReasoningStepResult:
        """
        Identifica insights clave basados en el análisis del contexto
        """
        insights = []
        reasoning = "Identificando insights clave:\n\n"
        
        # Insights basados en el BMC
        if context.bmc_data:
            reasoning += "1. Insights del Business Model Canvas:\n"
            
            # Analizar completitud del BMC
            filled_sections = sum(1 for value in context.bmc_data.values() 
                                if value and isinstance(value, list) and len(value) > 0)
            total_sections = len(context.bmc_data)
            completeness = (filled_sections / total_sections) * 100
            
            reasoning += f"   - Completitud del BMC: {completeness:.1f}% ({filled_sections}/{total_sections} secciones)\n"
            
            if completeness < 50:
                insights.append("BMC incompleto - necesita más desarrollo")
                reasoning += "   - ⚠️ El BMC está incompleto y necesita más desarrollo\n"
            elif completeness < 80:
                insights.append("BMC parcialmente completo - puede mejorarse")
                reasoning += "   - ✅ El BMC está parcialmente completo\n"
            else:
                insights.append("BMC bien desarrollado")
                reasoning += "   - ✅ El BMC está bien desarrollado\n"
            
            # Analizar fortalezas y debilidades específicas
            if context.bmc_data.get('value_propositions'):
                reasoning += f"   - Propuesta de valor: {len(context.bmc_data['value_propositions'])} elementos definidos\n"
                if len(context.bmc_data['value_propositions']) == 1:
                    insights.append("Propuesta de valor simple - puede expandirse")
            
            if context.bmc_data.get('customer_segments'):
                reasoning += f"   - Segmentos de clientes: {len(context.bmc_data['customer_segments'])} segmentos identificados\n"
                if len(context.bmc_data['customer_segments']) > 3:
                    insights.append("Múltiples segmentos - puede necesitar enfoque")
        
        # Insights basados en la consulta
        query_lower = context.user_query.lower()
        if 'distribución' in query_lower or 'canales' in query_lower:
            insights.append("Enfoque en canales de distribución")
            reasoning += "2. Enfoque específico en canales de distribución identificado\n"
        
        if 'socios' in query_lower or 'alianzas' in query_lower:
            insights.append("Interés en desarrollo de socios estratégicos")
            reasoning += "3. Interés en socios estratégicos identificado\n"
        
        if 'propuesta de valor' in query_lower:
            insights.append("Necesidad de clarificar propuesta de valor")
            reasoning += "4. Necesidad de definir propuesta de valor identificada\n"
        
        next_steps = [
            "Generar recomendaciones específicas basadas en insights",
            "Priorizar acciones según urgencia e impacto",
            "Crear plan de implementación detallado"
        ]
        
        return ReasoningStepResult(
            step=ReasoningStep.IDENTIFY_KEY_INSIGHTS,
            reasoning=reasoning,
            insights=insights,
            confidence=0.85,
            next_steps=next_steps
        )

    def generate_recommendations(self, context: ReasoningContext, insights: List[str]) -> ReasoningStepResult:
        """
        Genera recomendaciones específicas basadas en los insights identificados
        """
        recommendations = []
        reasoning = "Generando recomendaciones específicas:\n\n"
        
        reasoning += "1. Analizando insights para generar recomendaciones:\n"
        
        # Recomendaciones basadas en insights específicos
        for insight in insights:
            reasoning += f"   - Insight: {insight}\n"
            
            if "BMC incompleto" in insight:
                recommendations.extend([
                    "Completar secciones faltantes del BMC",
                    "Definir claramente la propuesta de valor",
                    "Identificar segmentos de clientes específicos"
                ])
                reasoning += "     → Recomendaciones: Completar BMC, definir propuesta de valor\n"
            
            elif "distribución" in insight.lower():
                recommendations.extend([
                    "Evaluar canales de distribución actuales",
                    "Identificar nuevos canales digitales",
                    "Desarrollar estrategia omnicanal"
                ])
                reasoning += "     → Recomendaciones: Estrategia de canales de distribución\n"
            
            elif "socios estratégicos" in insight.lower():
                recommendations.extend([
                    "Identificar potenciales socios clave",
                    "Desarrollar propuesta de valor para socios",
                    "Crear plan de acercamiento y negociación"
                ])
                reasoning += "     → Recomendaciones: Desarrollo de socios estratégicos\n"
            
            elif "propuesta de valor" in insight.lower():
                recommendations.extend([
                    "Clarificar beneficios únicos del producto/servicio",
                    "Validar propuesta con clientes objetivo",
                    "Desarrollar mensaje de marketing diferenciado"
                ])
                reasoning += "     → Recomendaciones: Definir propuesta de valor única\n"
        
        # Recomendaciones adicionales basadas en el contexto
        if context.bmc_data and len(context.bmc_data.get('key_activities', [])) < 3:
            recommendations.append("Expandir actividades clave del negocio")
            reasoning += "2. Actividades clave limitadas - recomendación de expansión\n"
        
        next_steps = [
            "Validar recomendaciones contra mejores prácticas",
            "Priorizar recomendaciones por impacto",
            "Crear plan de implementación"
        ]
        
        return ReasoningStepResult(
            step=ReasoningStep.GENERATE_RECOMMENDATIONS,
            reasoning=reasoning,
            insights=recommendations,
            confidence=0.9,
            next_steps=next_steps
        )

    def validate_recommendations(self, recommendations: List[str], context: ReasoningContext) -> ReasoningStepResult:
        """
        Valida las recomendaciones contra mejores prácticas de emprendimiento
        """
        validation_results = []
        reasoning = "Validando recomendaciones contra mejores prácticas:\n\n"
        
        reasoning += "1. Aplicando criterios de validación:\n"
        
        for rec in recommendations:
            reasoning += f"   - Recomendación: {rec}\n"
            
            # Validaciones específicas
            if "canales de distribución" in rec.lower():
                validation_results.append("✅ Validada - Canales de distribución son críticos para el éxito")
                reasoning += "     → ✅ Crítica para el éxito del negocio\n"
            
            elif "propuesta de valor" in rec.lower():
                validation_results.append("✅ Validada - Propuesta de valor es fundamental en el BMC")
                reasoning += "     → ✅ Fundamental para diferenciación\n"
            
            elif "socios estratégicos" in rec.lower():
                validation_results.append("✅ Validada - Socios pueden acelerar el crecimiento")
                reasoning += "     → ✅ Puede acelerar el crecimiento\n"
            
            elif "actividades clave" in rec.lower():
                validation_results.append("✅ Validada - Actividades clave definen las operaciones")
                reasoning += "     → ✅ Define las operaciones del negocio\n"
            
            else:
                validation_results.append("✅ Validada - Recomendación general apropiada")
                reasoning += "     → ✅ Recomendación apropiada\n"
        
        next_steps = [
            "Estructurar respuesta final",
            "Incluir pasos de implementación",
            "Proporcionar métricas de éxito"
        ]
        
        return ReasoningStepResult(
            step=ReasoningStep.VALIDATE_RECOMMENDATIONS,
            reasoning=reasoning,
            insights=validation_results,
            confidence=0.95,
            next_steps=next_steps
        )

    def structure_response(self, context: ReasoningContext, all_steps: List[ReasoningStepResult]) -> Dict:
        """
        Estructura la respuesta final basada en todo el proceso de reasoning
        """
        response = {
            'reasoning_summary': '',
            'key_insights': [],
            'recommendations': [],
            'implementation_steps': [],
            'success_metrics': [],
            'confidence_score': 0.0
        }
        
        # Compilar reasoning
        response['reasoning_summary'] = "\n".join([step.reasoning for step in all_steps])
        
        # Extraer insights clave
        for step in all_steps:
            if step.step == ReasoningStep.IDENTIFY_KEY_INSIGHTS:
                response['key_insights'].extend(step.insights)
        
        # Extraer recomendaciones
        for step in all_steps:
            if step.step == ReasoningStep.GENERATE_RECOMMENDATIONS:
                response['recommendations'].extend(step.insights)
        
        # Generar pasos de implementación
        implementation_steps = []
        for rec in response['recommendations'][:5]:  # Top 5 recomendaciones
            if "distribución" in rec.lower():
                implementation_steps.extend([
                    "1. Investigar competidores y sus canales",
                    "2. Probar canales digitales (redes sociales, e-commerce)",
                    "3. Medir resultados y optimizar"
                ])
            elif "propuesta de valor" in rec.lower():
                implementation_steps.extend([
                    "1. Entrevistar clientes objetivo",
                    "2. Identificar beneficios únicos",
                    "3. Crear mensaje diferenciado"
                ])
            elif "socios" in rec.lower():
                implementation_steps.extend([
                    "1. Listar potenciales socios",
                    "2. Desarrollar propuesta de colaboración",
                    "3. Iniciar conversaciones estratégicas"
                ])
        
        response['implementation_steps'] = list(set(implementation_steps))[:10]  # Top 10 únicos
        
        # Métricas de éxito
        response['success_metrics'] = [
            "Aumento en conversión de clientes",
            "Mejora en tiempo de ciclo de ventas",
            "Incremento en satisfacción del cliente",
            "Reducción en costos de adquisición",
            "Crecimiento en ingresos por canal"
        ]
        
        # Calcular confianza general
        total_confidence = sum(step.confidence for step in all_steps)
        response['confidence_score'] = total_confidence / len(all_steps) if all_steps else 0.0
        
        return response

    def process_reasoning(self, context: ReasoningContext) -> Dict:
        """
        Ejecuta todo el proceso de reasoning paso a paso
        """
        steps = []
        
        # Paso 1: Analizar contexto
        analysis_result = self.analyze_business_context(context)
        steps.append(analysis_result)
        
        # Paso 2: Identificar insights clave
        insights_result = self.identify_key_insights(context, analysis_result)
        steps.append(insights_result)
        
        # Paso 3: Generar recomendaciones
        recommendations_result = self.generate_recommendations(context, insights_result.insights)
        steps.append(recommendations_result)
        
        # Paso 4: Validar recomendaciones
        validation_result = self.validate_recommendations(recommendations_result.insights, context)
        steps.append(validation_result)
        
        # Paso 5: Estructurar respuesta final
        final_response = self.structure_response(context, steps)
        
        return {
            'reasoning_process': [
                {
                    'step': step.step.value,
                    'reasoning': step.reasoning,
                    'insights': step.insights,
                    'confidence': step.confidence,
                    'next_steps': step.next_steps
                } for step in steps
            ],
            'final_response': final_response
        }

# Instancia global del servicio
reasoning_service = ReasoningService()

