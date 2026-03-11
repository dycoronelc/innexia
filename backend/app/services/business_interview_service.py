"""
Servicio para realizar entrevistas guiadas de negocios
Recopila información estructurada para generar BMC y documentos de alta calidad
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)

class BusinessStage(str, Enum):
    IDEA = "idea"
    EARLY_STAGE = "early_stage"
    GROWTH = "growth"
    MATURE = "mature"

class Industry(str, Enum):
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FOOD_DELIVERY = "food_delivery"
    EDUCATION = "education"
    FINANCE = "finance"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    SERVICES = "services"
    OTHER = "other"

class BusinessInterviewData(BaseModel):
    """Datos recopilados durante la entrevista"""
    business_name: Optional[str] = None
    business_description: Optional[str] = None
    industry: Optional[Industry] = None
    stage: Optional[BusinessStage] = None
    target_market: Optional[str] = None
    unique_value_proposition: Optional[str] = None
    revenue_model: Optional[str] = None
    key_partners: List[str] = []
    key_resources: List[str] = []
    key_activities: List[str] = []
    customer_segments: List[str] = []
    customer_relationships: List[str] = []
    channels: List[str] = []
    cost_structure: List[str] = []
    revenue_streams: List[str] = []
    budget: Optional[float] = None
    team_size: Optional[int] = None
    location: Optional[str] = None
    timeline: Optional[str] = None
    goals: List[str] = []
    challenges: List[str] = []
    competitive_advantages: List[str] = []

class InterviewQuestion(BaseModel):
    """Estructura de una pregunta de la entrevista"""
    id: str
    question: str
    field: str
    type: str  # "text", "multiple_choice", "number", "list"
    options: Optional[List[str]] = None
    required: bool = True
    follow_up_questions: Optional[List[str]] = None

class BusinessInterviewService:
    """Servicio para manejar entrevistas de negocios"""
    
    def __init__(self):
        self.questions = self._initialize_questions()
        self.current_question_index = 0
        self.interview_data = BusinessInterviewData()
        self.completed_fields = set()
    
    def _initialize_questions(self) -> List[InterviewQuestion]:
        """Inicializa las preguntas de la entrevista"""
        return [
            InterviewQuestion(
                id="business_name",
                question="¿Cuál es el nombre de tu empresa o proyecto?",
                field="business_name",
                type="text",
                required=True
            ),
            InterviewQuestion(
                id="business_description",
                question="Cuéntame brevemente sobre tu idea de negocio. ¿Qué producto o servicio ofreces?",
                field="business_description",
                type="text",
                required=True
            ),
            InterviewQuestion(
                id="industry",
                question="¿En qué industria o sector se encuentra tu negocio?",
                field="industry",
                type="multiple_choice",
                options=[
                    "Tecnología",
                    "Salud y bienestar",
                    "Delivery de comida",
                    "Educación",
                    "Finanzas",
                    "Retail/Comercio",
                    "Manufactura",
                    "Servicios",
                    "Otro"
                ],
                required=True
            ),
            InterviewQuestion(
                id="stage",
                question="¿En qué etapa se encuentra tu negocio?",
                field="stage",
                type="multiple_choice",
                options=[
                    "Solo tengo la idea",
                    "Etapa temprana (primeros pasos)",
                    "En crecimiento",
                    "Empresa establecida"
                ],
                required=True
            ),
            InterviewQuestion(
                id="target_market",
                question="¿Quiénes son tus clientes objetivo? Describe tu mercado meta.",
                field="target_market",
                type="text",
                required=True
            ),
            InterviewQuestion(
                id="unique_value_proposition",
                question="¿Qué hace único a tu producto o servicio? ¿Por qué los clientes elegirían tu empresa?",
                field="unique_value_proposition",
                type="text",
                required=True
            ),
            InterviewQuestion(
                id="revenue_model",
                question="¿Cómo planeas generar ingresos? Describe tu modelo de monetización.",
                field="revenue_model",
                type="text",
                required=True
            ),
            InterviewQuestion(
                id="budget",
                question="¿Cuál es tu presupuesto inicial disponible para el negocio? (en USD)",
                field="budget",
                type="number",
                required=False
            ),
            InterviewQuestion(
                id="team_size",
                question="¿Cuántas personas forman parte de tu equipo actualmente?",
                field="team_size",
                type="number",
                required=False
            ),
            InterviewQuestion(
                id="location",
                question="¿En qué ciudad o región planeas operar?",
                field="location",
                type="text",
                required=False
            ),
            InterviewQuestion(
                id="timeline",
                question="¿Cuál es tu cronograma para lanzar el negocio?",
                field="timeline",
                type="text",
                required=False
            ),
            InterviewQuestion(
                id="goals",
                question="¿Cuáles son tus principales objetivos para los próximos 6-12 meses?",
                field="goals",
                type="text",
                required=False
            ),
            InterviewQuestion(
                id="challenges",
                question="¿Cuáles son los principales desafíos que anticipas enfrentar?",
                field="challenges",
                type="text",
                required=False
            )
        ]
    
    def get_next_question(self, current_data: Dict[str, Any]) -> Optional[InterviewQuestion]:
        """Obtiene la siguiente pregunta basada en los datos actuales"""
        # Actualizar datos actuales
        self._update_interview_data(current_data)
        
        # Buscar la siguiente pregunta no respondida
        for question in self.questions:
            if question.field not in self.completed_fields:
                return question
        
        return None
    
    def _update_interview_data(self, data: Dict[str, Any]):
        """Actualiza los datos de la entrevista"""
        for field, value in data.items():
            if hasattr(self.interview_data, field) and value is not None:
                setattr(self.interview_data, field, value)
                self.completed_fields.add(field)
    
    def is_interview_complete(self) -> bool:
        """Verifica si la entrevista está completa"""
        required_fields = {q.field for q in self.questions if q.required}
        return required_fields.issubset(self.completed_fields)
    
    def get_completion_percentage(self) -> float:
        """Calcula el porcentaje de completitud de la entrevista"""
        total_questions = len(self.questions)
        completed_questions = len(self.completed_fields)
        return (completed_questions / total_questions) * 100
    
    def generate_business_prompt(self) -> str:
        """Genera un prompt detallado basado en los datos de la entrevista"""
        if not self.is_interview_complete():
            raise ValueError("La entrevista no está completa")
        
        prompt = f"""
        Genera un Business Model Canvas completo y detallado para el siguiente negocio:

        INFORMACIÓN DEL NEGOCIO:
        - Nombre: {self.interview_data.business_name}
        - Descripción: {self.interview_data.business_description}
        - Industria: {self.interview_data.industry}
        - Etapa: {self.interview_data.stage}
        - Mercado objetivo: {self.interview_data.target_market}
        - Propuesta de valor única: {self.interview_data.unique_value_proposition}
        - Modelo de ingresos: {self.interview_data.revenue_model}
        - Presupuesto: ${self.interview_data.budget or 'No especificado'}
        - Tamaño del equipo: {self.interview_data.team_size or 'No especificado'}
        - Ubicación: {self.interview_data.location or 'No especificado'}
        - Cronograma: {self.interview_data.timeline or 'No especificado'}
        - Objetivos: {', '.join(self.interview_data.goals) if self.interview_data.goals else 'No especificados'}
        - Desafíos: {', '.join(self.interview_data.challenges) if self.interview_data.challenges else 'No especificados'}

        REQUISITOS:
        1. Genera un BMC específico y detallado para esta industria y etapa
        2. Incluye elementos específicos del mercado objetivo mencionado
        3. Considera el presupuesto y recursos disponibles
        4. Adapta las actividades a la ubicación geográfica
        5. Incluye estrategias para superar los desafíos mencionados
        6. Alinea las recomendaciones con los objetivos establecidos

        FORMATO DE RESPUESTA:
        Responde ÚNICAMENTE con un JSON válido que contenga:
        {{
            "bmc": {{
                "key_partners": ["partner1", "partner2", ...],
                "key_activities": ["activity1", "activity2", ...],
                "key_resources": ["resource1", "resource2", ...],
                "value_propositions": ["value1", "value2", ...],
                "customer_relationships": ["relationship1", "relationship2", ...],
                "channels": ["channel1", "channel2", ...],
                "customer_segments": ["segment1", "segment2", ...],
                "cost_structure": ["cost1", "cost2", ...],
                "revenue_streams": ["revenue1", "revenue2", ...]
            }},
            "recommended_activities": [
                {{
                    "name": "Nombre de la actividad",
                    "description": "Descripción detallada",
                    "priority": "high|medium|low",
                    "estimated_duration": "X semanas/meses",
                    "required_resources": ["recurso1", "recurso2"],
                    "expected_outcome": "Resultado esperado"
                }}
            ],
            "business_insights": {{
                "market_opportunity": "Análisis de la oportunidad de mercado",
                "competitive_advantages": ["ventaja1", "ventaja2"],
                "risk_factors": ["riesgo1", "riesgo2"],
                "success_factors": ["factor1", "factor2"]
            }}
        }}
        """
        return prompt
    
    def generate_document_prompts(self) -> Dict[str, str]:
        """Genera prompts específicos para cada tipo de documento"""
        base_info = f"""
        INFORMACIÓN DEL NEGOCIO:
        - Nombre: {self.interview_data.business_name}
        - Descripción: {self.interview_data.business_description}
        - Industria: {self.interview_data.industry}
        - Mercado objetivo: {self.interview_data.target_market}
        - Propuesta de valor: {self.interview_data.unique_value_proposition}
        - Modelo de ingresos: {self.interview_data.revenue_model}
        - Presupuesto: ${self.interview_data.budget or 'No especificado'}
        - Ubicación: {self.interview_data.location or 'No especificado'}
        """
        
        return {
            "business_plan": f"""
            {base_info}
            
            Genera un Plan de Negocio completo y profesional que incluya:
            1. Resumen Ejecutivo
            2. Descripción de la Empresa
            3. Análisis de Mercado
            4. Organización y Gestión
            5. Descripción del Producto/Servicio
            6. Estrategia de Marketing y Ventas
            7. Proyecciones Financieras
            8. Análisis de Riesgos
            9. Cronograma de Implementación
            10. Conclusiones y Recomendaciones
            
            El documento debe ser específico para la industria {self.interview_data.industry} y considerar el presupuesto de ${self.interview_data.budget or 'limitado'}.
            """,
            
            "marketing_plan": f"""
            {base_info}
            
            Genera un Plan de Marketing detallado que incluya:
            1. Análisis de Mercado Objetivo
            2. Posicionamiento y Diferenciación
            3. Estrategias de Marketing Digital
            4. Canales de Distribución
            5. Estrategias de Precios
            6. Plan de Comunicación
            7. Presupuesto de Marketing
            8. Métricas y KPIs
            9. Cronograma de Campañas
            10. Análisis de Competencia
            
            Adapta las estrategias al mercado de {self.interview_data.location or 'la región'} y al presupuesto disponible.
            """,
            
            "financial_projections": f"""
            {base_info}
            
            Genera Proyecciones Financieras que incluyan:
            1. Proyección de Ingresos (3 años)
            2. Proyección de Gastos Operativos
            3. Flujo de Caja Proyectado
            4. Punto de Equilibrio
            5. Análisis de Rentabilidad
            6. Necesidades de Financiamiento
            7. Escenarios Optimista/Pesimista
            8. Métricas Financieras Clave
            9. Plan de Inversión
            10. Estrategia de Salida
            
            Considera el presupuesto inicial de ${self.interview_data.budget or 'limitado'} y el modelo de ingresos especificado.
            """,
            
            "market_analysis": f"""
            {base_info}
            
            Genera un Análisis de Mercado completo que incluya:
            1. Tamaño y Crecimiento del Mercado
            2. Segmentación de Clientes
            3. Análisis de Competencia
            4. Tendencias del Mercado
            5. Barreras de Entrada
            6. Oportunidades de Mercado
            7. Amenazas del Mercado
            8. Análisis PESTEL
            9. Análisis FODA
            10. Recomendaciones Estratégicas
            
            Enfócate en el mercado de {self.interview_data.location or 'la región'} y la industria {self.interview_data.industry}.
            """
        }
    
    def get_interview_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen de la entrevista"""
        return {
            "completion_percentage": self.get_completion_percentage(),
            "completed_fields": list(self.completed_fields),
            "remaining_fields": [q.field for q in self.questions if q.field not in self.completed_fields],
            "data": self.interview_data.dict()
        }

