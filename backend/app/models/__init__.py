from .company import Company
from .user import User
from .project import Project, ProjectTag
from .activity import ProjectActivity, ActivityAssignee, ActivityTag, ActivityLabel
from .activity_comment import ActivityComment
from .activity_checklist import ActivityChecklist, ActivityChecklistItem
from .activity_attachment import ActivityAttachment
from .document import ProjectDocument, GeneratedDocument, DocumentTemplate, DocumentGenerationLog
from .business_model_canvas import BusinessModelCanvas
from .audit_log import AuditLog
from .category import Category
from .tag import Tag
from .location import Location
from .status import Status

# Nuevos modelos para el sistema de contenido educativo
from .educational_content import EducationalContent
from .external_content_source import ExternalContentSource
from .official_document import OfficialDocument
from .educational_category import EducationalCategory
from .educational_tag import EducationalTag

# Modelos para la memoria del agente
from .agent_memory import AgentMemory, ConversationSession, ConversationMessage, UserContext

# Modelos para sugerencias proactivas
from .proactive_suggestions import ProactiveSuggestion, SuggestionRule, UserSuggestionPreference

# Modelos para análisis de datos
from .data_analysis import UserAnalytics, RecommendationEngine, DataSource, AnalyticsEvent, LearningPath

# Modelos para gestión avanzada de estado de conversaciones
from .conversation_state import ConversationState, ConversationFlow, StateTransition, ConversationThread

from .project_agent_output import ProjectAgentOutput
from .project_estrategia_comercial import ProjectEstrategiaComercial
from .project_roadmap import ProjectRoadmap
from .project_analisis_financiero import ProjectAnalisisFinanciero
from .project_analisis_riesgos import ProjectAnalisisRiesgos, ProjectRiesgo
from .project_veredicto import ProjectVeredicto
from .analysis_request import AnalysisRequest
from .analysis_result import AnalysisResult
from .analysis_module import AnalysisModule
from .analysis_activity import AnalysisActivity
from .analysis_risk import AnalysisRisk

# Lista de todos los modelos para crear tablas
__all__ = [
    "Company",
    "User",
    "Project", 
    "ProjectTag",
    "ProjectActivity",
    "ActivityAssignee",
    "ActivityTag",
    "ActivityLabel",
    "ActivityComment",
    "ActivityChecklist",
    "ActivityChecklistItem",
    "ActivityAttachment",
    "ProjectDocument",
    "GeneratedDocument",
    "DocumentTemplate", 
    "DocumentGenerationLog",
    "BusinessModelCanvas",
    "AuditLog",
    "Category",
    "Tag",
    "Location",
    "Status",
    # Nuevos modelos
    "EducationalContent",
    "ExternalContentSource",
    "OfficialDocument",
    "EducationalCategory",
    "EducationalTag",
    # Modelos de memoria del agente
    "AgentMemory",
    "ConversationSession", 
    "ConversationMessage",
    "UserContext",
    # Modelos de sugerencias proactivas
    "ProactiveSuggestion",
    "SuggestionRule",
    "UserSuggestionPreference",
    # Modelos de análisis de datos
    "UserAnalytics",
    "RecommendationEngine",
    "DataSource",
    "AnalyticsEvent",
    "LearningPath",
    # Modelos de gestión avanzada de estado de conversaciones
    "ConversationState",
    "ConversationFlow",
    "StateTransition",
    "ConversationThread",
    "ProjectAgentOutput",
    "ProjectEstrategiaComercial",
    "ProjectRoadmap",
    "ProjectAnalisisFinanciero",
    "ProjectAnalisisRiesgos",
    "ProjectRiesgo",
    "ProjectVeredicto",
    "AnalysisRequest",
    "AnalysisResult",
    "AnalysisModule",
    "AnalysisActivity",
    "AnalysisRisk",
]

