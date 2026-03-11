import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkflowNode(Enum):
    START = "start"
    CONDITION = "condition"
    ACTION = "action"
    PARALLEL = "parallel"
    WAIT = "wait"
    END = "end"

@dataclass
class WorkflowStep:
    id: str
    node_type: WorkflowNode
    name: str
    condition: Optional[Callable] = None
    action: Optional[Callable] = None
    next_steps: List[str] = None
    parallel_steps: List[str] = None
    wait_time: Optional[int] = None  # en segundos

@dataclass
class WorkflowExecution:
    id: str
    workflow_id: str
    status: WorkflowStatus
    current_step: str
    context: Dict[str, Any]
    start_time: datetime
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    results: Dict[str, Any] = None

class WorkflowService:
    """
    Servicio de workflows inteligentes inspirado en OpenAI AgentKit
    Maneja flujos condicionales y automatización para el chatbot de emprendimiento
    """
    
    def __init__(self):
        self.workflows = {}
        self.executions = {}
        self._register_default_workflows()
    
    def _register_default_workflows(self):
        """Registra workflows por defecto para emprendimiento"""
        
        # Workflow para análisis de BMC
        self.workflows['bmc_analysis'] = {
            'id': 'bmc_analysis',
            'name': 'Análisis de Business Model Canvas',
            'description': 'Analiza y mejora el BMC del usuario',
            'steps': [
                WorkflowStep(
                    id='start_bmc',
                    node_type=WorkflowNode.START,
                    name='Iniciar análisis BMC'
                ),
                WorkflowStep(
                    id='check_bmc_completeness',
                    node_type=WorkflowNode.CONDITION,
                    name='Verificar completitud del BMC',
                    condition=self._check_bmc_completeness,
                    next_steps=['complete_bmc', 'analyze_bmc']
                ),
                WorkflowStep(
                    id='complete_bmc',
                    node_type=WorkflowNode.ACTION,
                    name='Completar BMC faltante',
                    action=self._complete_bmc_sections,
                    next_steps=['analyze_bmc']
                ),
                WorkflowStep(
                    id='analyze_bmc',
                    node_type=WorkflowNode.ACTION,
                    name='Analizar BMC existente',
                    action=self._analyze_bmc_strengths,
                    next_steps=['generate_recommendations']
                ),
                WorkflowStep(
                    id='generate_recommendations',
                    node_type=WorkflowNode.ACTION,
                    name='Generar recomendaciones',
                    action=self._generate_bmc_recommendations,
                    next_steps=['end_bmc']
                ),
                WorkflowStep(
                    id='end_bmc',
                    node_type=WorkflowNode.END,
                    name='Finalizar análisis BMC'
                )
            ]
        }
        
        # Workflow para recomendaciones de actividades
        self.workflows['activity_recommendations'] = {
            'id': 'activity_recommendations',
            'name': 'Recomendaciones de Actividades',
            'description': 'Genera actividades específicas basadas en el contexto del negocio',
            'steps': [
                WorkflowStep(
                    id='start_activities',
                    node_type=WorkflowNode.START,
                    name='Iniciar recomendaciones de actividades'
                ),
                WorkflowStep(
                    id='analyze_business_context',
                    node_type=WorkflowNode.ACTION,
                    name='Analizar contexto del negocio',
                    action=self._analyze_business_context,
                    next_steps=['identify_activity_areas']
                ),
                WorkflowStep(
                    id='identify_activity_areas',
                    node_type=WorkflowNode.ACTION,
                    name='Identificar áreas de actividad',
                    action=self._identify_activity_areas,
                    next_steps=['prioritize_activities']
                ),
                WorkflowStep(
                    id='prioritize_activities',
                    node_type=WorkflowNode.ACTION,
                    name='Priorizar actividades',
                    action=self._prioritize_activities,
                    next_steps=['create_activity_plan']
                ),
                WorkflowStep(
                    id='create_activity_plan',
                    node_type=WorkflowNode.ACTION,
                    name='Crear plan de actividades',
                    action=self._create_activity_plan,
                    next_steps=['end_activities']
                ),
                WorkflowStep(
                    id='end_activities',
                    node_type=WorkflowNode.END,
                    name='Finalizar recomendaciones'
                )
            ]
        }
        
        # Workflow para validación de ideas de negocio
        self.workflows['business_idea_validation'] = {
            'id': 'business_idea_validation',
            'name': 'Validación de Ideas de Negocio',
            'description': 'Valida y mejora ideas de negocio del usuario',
            'steps': [
                WorkflowStep(
                    id='start_validation',
                    node_type=WorkflowNode.START,
                    name='Iniciar validación de idea'
                ),
                WorkflowStep(
                    id='extract_idea_details',
                    node_type=WorkflowNode.ACTION,
                    name='Extraer detalles de la idea',
                    action=self._extract_idea_details,
                    next_steps=['validate_market_fit']
                ),
                WorkflowStep(
                    id='validate_market_fit',
                    node_type=WorkflowNode.CONDITION,
                    name='Validar fit de mercado',
                    condition=self._validate_market_fit,
                    next_steps=['improve_idea', 'validate_financials']
                ),
                WorkflowStep(
                    id='improve_idea',
                    node_type=WorkflowNode.ACTION,
                    name='Mejorar la idea',
                    action=self._improve_business_idea,
                    next_steps=['validate_financials']
                ),
                WorkflowStep(
                    id='validate_financials',
                    node_type=WorkflowNode.ACTION,
                    name='Validar viabilidad financiera',
                    action=self._validate_financial_viability,
                    next_steps=['generate_next_steps']
                ),
                WorkflowStep(
                    id='generate_next_steps',
                    node_type=WorkflowNode.ACTION,
                    name='Generar próximos pasos',
                    action=self._generate_validation_next_steps,
                    next_steps=['end_validation']
                ),
                WorkflowStep(
                    id='end_validation',
                    node_type=WorkflowNode.END,
                    name='Finalizar validación'
                )
            ]
        }

    # Métodos de condición para workflows
    def _check_bmc_completeness(self, context: Dict) -> bool:
        """Verifica si el BMC está completo"""
        bmc_data = context.get('bmc_data', {})
        filled_sections = sum(1 for value in bmc_data.values() 
                            if value and isinstance(value, list) and len(value) > 0)
        total_sections = len(bmc_data)
        completeness = (filled_sections / total_sections) * 100 if total_sections > 0 else 0
        return completeness >= 70

    def _validate_market_fit(self, context: Dict) -> bool:
        """Valida si la idea tiene fit de mercado"""
        idea_details = context.get('idea_details', {})
        has_target_market = bool(idea_details.get('target_market'))
        has_problem_solution = bool(idea_details.get('problem') and idea_details.get('solution'))
        has_competitive_advantage = bool(idea_details.get('competitive_advantage'))
        return has_target_market and has_problem_solution and has_competitive_advantage

    # Métodos de acción para workflows
    def _complete_bmc_sections(self, context: Dict) -> Dict:
        """Completa secciones faltantes del BMC"""
        bmc_data = context.get('bmc_data', {})
        missing_sections = []
        
        for key, value in bmc_data.items():
            if not value or (isinstance(value, list) and len(value) == 0):
                missing_sections.append(key)
        
        recommendations = []
        for section in missing_sections:
            if section == 'value_propositions':
                recommendations.append("Definir claramente qué valor único ofreces a tus clientes")
            elif section == 'customer_segments':
                recommendations.append("Identificar segmentos específicos de clientes objetivo")
            elif section == 'channels':
                recommendations.append("Determinar canales para llegar a tus clientes")
            elif section == 'key_partners':
                recommendations.append("Identificar socios clave para tu negocio")
        
        return {
            'action': 'complete_bmc_sections',
            'missing_sections': missing_sections,
            'recommendations': recommendations,
            'message': f"Se identificaron {len(missing_sections)} secciones faltantes en el BMC"
        }

    def _analyze_bmc_strengths(self, context: Dict) -> Dict:
        """Analiza las fortalezas del BMC"""
        bmc_data = context.get('bmc_data', {})
        strengths = []
        weaknesses = []
        
        # Analizar cada sección
        for key, value in bmc_data.items():
            if value and isinstance(value, list) and len(value) > 0:
                if len(value) >= 3:
                    strengths.append(f"Sección '{key}' bien desarrollada ({len(value)} elementos)")
                else:
                    weaknesses.append(f"Sección '{key}' puede expandirse (solo {len(value)} elementos)")
        
        return {
            'action': 'analyze_bmc_strengths',
            'strengths': strengths,
            'weaknesses': weaknesses,
            'score': len(strengths) / (len(strengths) + len(weaknesses)) if (len(strengths) + len(weaknesses)) > 0 else 0
        }

    def _generate_bmc_recommendations(self, context: Dict) -> Dict:
        """Genera recomendaciones específicas para el BMC"""
        analysis = context.get('bmc_analysis', {})
        weaknesses = analysis.get('weaknesses', [])
        
        recommendations = []
        for weakness in weaknesses:
            if 'value_propositions' in weakness.lower():
                recommendations.append({
                    'section': 'value_propositions',
                    'recommendation': 'Desarrollar propuesta de valor más específica y diferenciada',
                    'priority': 'high',
                    'actions': [
                        'Entrevistar clientes para entender sus necesidades',
                        'Comparar con competidores directos',
                        'Crear mensaje único y memorable'
                    ]
                })
            elif 'customer_segments' in weakness.lower():
                recommendations.append({
                    'section': 'customer_segments',
                    'recommendation': 'Definir segmentos de clientes más específicos',
                    'priority': 'high',
                    'actions': [
                        'Crear personas de cliente detalladas',
                        'Validar segmentos con investigación de mercado',
                        'Priorizar segmentos por potencial'
                    ]
                })
        
        return {
            'action': 'generate_bmc_recommendations',
            'recommendations': recommendations,
            'total_recommendations': len(recommendations)
        }

    def _analyze_business_context(self, context: Dict) -> Dict:
        """Analiza el contexto del negocio para recomendaciones de actividades"""
        user_query = context.get('user_query', '').lower()
        bmc_data = context.get('bmc_data', {})
        
        business_phase = "startup"  # default
        if any(word in user_query for word in ['escalar', 'crecer', 'expansión']):
            business_phase = "growth"
        elif any(word in user_query for word in ['validar', 'probar', 'prototipo']):
            business_phase = "validation"
        
        context_analysis = {
            'business_phase': business_phase,
            'key_focus_areas': [],
            'priority_level': 'medium'
        }
        
        # Identificar áreas de enfoque basadas en la consulta
        if 'distribución' in user_query or 'canales' in user_query:
            context_analysis['key_focus_areas'].append('distribution')
        if 'socios' in user_query or 'alianzas' in user_query:
            context_analysis['key_focus_areas'].append('partnerships')
        if 'marketing' in user_query or 'ventas' in user_query:
            context_analysis['key_focus_areas'].append('marketing_sales')
        
        return {
            'action': 'analyze_business_context',
            'context_analysis': context_analysis,
            'message': f"Contexto analizado: fase {business_phase}, enfoque en {len(context_analysis['key_focus_areas'])} áreas"
        }

    def _identify_activity_areas(self, context: Dict) -> Dict:
        """Identifica áreas específicas de actividad basadas en el contexto"""
        context_analysis = context.get('business_context_analysis', {})
        focus_areas = context_analysis.get('key_focus_areas', [])
        business_phase = context_analysis.get('business_phase', 'startup')
        
        activity_areas = []
        
        # Actividades por área de enfoque
        if 'distribution' in focus_areas:
            activity_areas.extend([
                'Desarrollo de canales digitales',
                'Optimización de canales existentes',
                'Análisis de competencia en distribución'
            ])
        
        if 'partnerships' in focus_areas:
            activity_areas.extend([
                'Identificación de socios potenciales',
                'Desarrollo de propuestas de colaboración',
                'Negociación de acuerdos estratégicos'
            ])
        
        if 'marketing_sales' in focus_areas:
            activity_areas.extend([
                'Desarrollo de estrategia de marketing digital',
                'Creación de materiales de ventas',
                'Implementación de CRM'
            ])
        
        # Actividades por fase del negocio
        if business_phase == 'validation':
            activity_areas.extend([
                'Validación de mercado',
                'Desarrollo de MVP',
                'Pruebas con clientes'
            ])
        elif business_phase == 'growth':
            activity_areas.extend([
                'Escalamiento de operaciones',
                'Expansión a nuevos mercados',
                'Optimización de procesos'
            ])
        
        return {
            'action': 'identify_activity_areas',
            'activity_areas': activity_areas,
            'total_areas': len(activity_areas),
            'business_phase': business_phase
        }

    def _prioritize_activities(self, context: Dict) -> Dict:
        """Prioriza las actividades identificadas"""
        activity_areas = context.get('activity_areas', [])
        
        # Sistema de priorización basado en impacto y urgencia
        prioritized_activities = []
        
        for i, activity in enumerate(activity_areas[:10]):  # Top 10
            priority_score = 10 - i  # Decreciente
            urgency = 'high' if i < 3 else 'medium' if i < 6 else 'low'
            impact = 'high' if 'desarrollo' in activity.lower() or 'creación' in activity.lower() else 'medium'
            
            prioritized_activities.append({
                'activity': activity,
                'priority_score': priority_score,
                'urgency': urgency,
                'impact': impact,
                'estimated_effort': '1-2 semanas' if urgency == 'high' else '2-4 semanas'
            })
        
        return {
            'action': 'prioritize_activities',
            'prioritized_activities': prioritized_activities,
            'high_priority_count': len([a for a in prioritized_activities if a['urgency'] == 'high'])
        }

    def _create_activity_plan(self, context: Dict) -> Dict:
        """Crea un plan detallado de actividades"""
        prioritized_activities = context.get('prioritized_activities', [])
        
        activity_plan = {
            'immediate_actions': [],  # Próximas 2 semanas
            'short_term': [],         # Próximo mes
            'medium_term': []         # Próximos 3 meses
        }
        
        for activity in prioritized_activities:
            if activity['urgency'] == 'high':
                activity_plan['immediate_actions'].append(activity)
            elif activity['urgency'] == 'medium':
                activity_plan['short_term'].append(activity)
            else:
                activity_plan['medium_term'].append(activity)
        
        return {
            'action': 'create_activity_plan',
            'activity_plan': activity_plan,
            'total_activities': len(prioritized_activities),
            'timeline': '3 meses'
        }

    # Métodos para validación de ideas de negocio
    def _extract_idea_details(self, context: Dict) -> Dict:
        """Extrae detalles específicos de la idea de negocio"""
        user_query = context.get('user_query', '')
        
        # Análisis básico de la idea (en un caso real, usaríamos NLP más avanzado)
        idea_details = {
            'description': user_query,
            'industry': self._identify_industry(user_query),
            'target_market': self._identify_target_market(user_query),
            'problem': self._identify_problem(user_query),
            'solution': self._identify_solution(user_query)
        }
        
        return {
            'action': 'extract_idea_details',
            'idea_details': idea_details,
            'completeness_score': self._calculate_idea_completeness(idea_details)
        }

    def _improve_business_idea(self, context: Dict) -> Dict:
        """Mejora la idea de negocio identificando áreas de desarrollo"""
        idea_details = context.get('idea_details', {})
        improvements = []
        
        if not idea_details.get('target_market'):
            improvements.append("Definir claramente el mercado objetivo y sus características")
        
        if not idea_details.get('problem'):
            improvements.append("Identificar el problema específico que resuelve tu idea")
        
        if not idea_details.get('solution'):
            improvements.append("Describir cómo tu solución aborda el problema identificado")
        
        return {
            'action': 'improve_business_idea',
            'improvements': improvements,
            'areas_to_develop': len(improvements)
        }

    def _validate_financial_viability(self, context: Dict) -> Dict:
        """Valida la viabilidad financiera de la idea"""
        idea_details = context.get('idea_details', {})
        
        # Análisis básico de viabilidad (en un caso real, sería más sofisticado)
        viability_checks = {
            'market_size': 'medium',  # Basado en industria identificada
            'revenue_potential': 'high' if idea_details.get('solution') else 'unknown',
            'cost_structure': 'unknown',
            'scalability': 'medium'
        }
        
        return {
            'action': 'validate_financial_viability',
            'viability_checks': viability_checks,
            'overall_viability': 'positive'  # Simplificado para demo
        }

    def _generate_validation_next_steps(self, context: Dict) -> Dict:
        """Genera próximos pasos para validar la idea"""
        next_steps = [
            "Realizar investigación de mercado detallada",
            "Crear prototipo o MVP",
            "Validar con clientes potenciales",
            "Desarrollar modelo financiero básico",
            "Identificar competidores y diferenciadores"
        ]
        
        return {
            'action': 'generate_validation_next_steps',
            'next_steps': next_steps,
            'timeline': '4-6 semanas'
        }

    # Métodos auxiliares
    def _identify_industry(self, text: str) -> str:
        """Identifica la industria basada en palabras clave"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['comida', 'aliment', 'restaurante', 'food']):
            return 'Food & Beverage'
        elif any(word in text_lower for word in ['tech', 'software', 'app', 'digital']):
            return 'Technology'
        elif any(word in text_lower for word in ['salud', 'health', 'médico', 'fitness']):
            return 'Healthcare'
        else:
            return 'General'

    def _identify_target_market(self, text: str) -> str:
        """Identifica el mercado objetivo"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['profesionales', 'empresas', 'oficinas']):
            return 'B2B Professional'
        elif any(word in text_lower for word in ['consumidores', 'personas', 'familias']):
            return 'B2C Consumer'
        else:
            return 'Mixed'

    def _identify_problem(self, text: str) -> str:
        """Identifica el problema que resuelve"""
        # Simplificado - en un caso real usaríamos NLP avanzado
        return "Problema identificado en el análisis" if len(text) > 20 else "Problema no claramente definido"

    def _identify_solution(self, text: str) -> str:
        """Identifica la solución propuesta"""
        return "Solución identificada en el análisis" if len(text) > 20 else "Solución no claramente definida"

    def _calculate_idea_completeness(self, idea_details: Dict) -> float:
        """Calcula qué tan completa está la idea"""
        filled_fields = sum(1 for value in idea_details.values() if value and value != 'unknown')
        total_fields = len(idea_details)
        return (filled_fields / total_fields) * 100

    # Método principal para ejecutar workflows
    async def execute_workflow(self, workflow_id: str, context: Dict) -> Dict:
        """Ejecuta un workflow específico"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} no encontrado")
        
        workflow = self.workflows[workflow_id]
        execution_id = f"{workflow_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        execution = WorkflowExecution(
            id=execution_id,
            workflow_id=workflow_id,
            status=WorkflowStatus.RUNNING,
            current_step=workflow['steps'][0].id,
            context=context,
            start_time=datetime.now(),
            results={}
        )
        
        self.executions[execution_id] = execution
        
        try:
            # Ejecutar workflow paso a paso
            current_step_id = workflow['steps'][0].id
            step_map = {step.id: step for step in workflow['steps']}
            
            while current_step_id:
                step = step_map[current_step_id]
                execution.current_step = current_step_id
                
                logger.info(f"Ejecutando paso: {step.name}")
                
                # Ejecutar acción o condición
                if step.action:
                    result = step.action(execution.context)
                    execution.results[step.id] = result
                    execution.context.update(result)
                
                # Determinar siguiente paso
                if step.node_type == WorkflowNode.END:
                    current_step_id = None
                elif step.node_type == WorkflowNode.CONDITION and step.condition:
                    condition_result = step.condition(execution.context)
                    # Simplificado: tomar primer next_step si condición es True
                    current_step_id = step.next_steps[0] if condition_result and step.next_steps else None
                elif step.next_steps:
                    current_step_id = step.next_steps[0]
                else:
                    current_step_id = None
            
            execution.status = WorkflowStatus.COMPLETED
            execution.end_time = datetime.now()
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error_message = str(e)
            execution.end_time = datetime.now()
            logger.error(f"Error en workflow {workflow_id}: {e}")
        
        return {
            'execution_id': execution_id,
            'status': execution.status.value,
            'results': execution.results,
            'context': execution.context,
            'duration': (execution.end_time - execution.start_time).total_seconds() if execution.end_time else None,
            'error': execution.error_message
        }

    def get_workflow_info(self, workflow_id: str) -> Dict:
        """Obtiene información sobre un workflow"""
        if workflow_id not in self.workflows:
            return {'error': f'Workflow {workflow_id} no encontrado'}
        
        workflow = self.workflows[workflow_id]
        return {
            'id': workflow['id'],
            'name': workflow['name'],
            'description': workflow['description'],
            'steps': [
                {
                    'id': step.id,
                    'name': step.name,
                    'node_type': step.node_type.value
                } for step in workflow['steps']
            ]
        }

    def list_workflows(self) -> List[Dict]:
        """Lista todos los workflows disponibles"""
        return [
            {
                'id': workflow['id'],
                'name': workflow['name'],
                'description': workflow['description']
            }
            for workflow in self.workflows.values()
        ]

# Instancia global del servicio
workflow_service = WorkflowService()

