from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json
import httpx
import asyncio
from datetime import datetime, timedelta

from ..core.auth import get_current_user
from ..database import get_db
from ..models.user import User
from ..models.project import Project
from ..models.business_model_canvas import BusinessModelCanvas
from ..models.activity import ProjectActivity
from ..models.document import ProjectDocument
from ..schemas.business_model_canvas import BusinessModelCanvasCreate
from ..schemas.activity import ProjectActivityCreate
from ..config import settings

router = APIRouter()

# Preguntas de la conversación guiada
GUIDED_QUESTIONS = [
    {
        "id": "location",
        "question": "¿En qué ciudad o zona geográfica planeas operar tu negocio?",
        "type": "text",
        "placeholder": "Ej: Bogotá, Medellín, Cali, etc.",
        "required": True,
        "context": "Esta información nos ayudará a entender el mercado local y la competencia."
    },
    {
        "id": "target_customers",
        "question": "¿Qué tipo de clientes quieres atender?",
        "type": "text",
        "placeholder": "Ej: Empresas medianas, estudiantes universitarios, profesionales independientes, etc.",
        "required": True,
        "context": "Definir tu público objetivo es clave para el éxito del negocio."
    },
    {
        "id": "budget",
        "question": "¿Tienes un presupuesto estimado para iniciar el negocio?",
        "type": "text",
        "placeholder": "Ej: $10,000 USD, $50 millones COP, etc.",
        "required": True,
        "context": "El presupuesto determina la escala y alcance inicial del proyecto."
    },
    {
        "id": "competition",
        "question": "¿Sabes si ya existe algo similar en el mercado?",
        "type": "text",
        "placeholder": "Ej: Sí, hay 3 competidores principales / No, es un mercado nuevo / No estoy seguro",
        "required": True,
        "context": "Entender la competencia nos ayuda a posicionar tu propuesta de valor."
    },
    {
        "id": "resources",
        "question": "¿Qué recursos tienes disponibles? (equipo, experiencia, contactos, etc.)",
        "type": "text",
        "placeholder": "Ej: Equipo de 3 personas, experiencia en tecnología, contactos en la industria",
        "required": True,
        "context": "Los recursos disponibles determinan las capacidades iniciales."
    },
    {
        "id": "timeline",
        "question": "¿En qué tiempo planeas lanzar el negocio?",
        "type": "text",
        "placeholder": "Ej: 3 meses, 6 meses, 1 año",
        "required": True,
        "context": "El timeline afecta la planificación y priorización de actividades."
    }
]

class GuidedConversationRequest(BaseModel):
    business_idea: str
    answers: Dict[str, str]

class GuidedConversationResponse(BaseModel):
    project_id: int
    project_name: str
    bmc_data: Dict[str, Any]
    activities: List[Dict[str, Any]]
    business_plan: str

@router.get("/questions")
async def get_guided_questions():
    """Obtener las preguntas de la conversación guiada"""
    return {
        "questions": GUIDED_QUESTIONS,
        "total_questions": len(GUIDED_QUESTIONS)
    }

@router.post("/generate", response_model=GuidedConversationResponse)
async def generate_guided_business_plan(
    request: GuidedConversationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generar BMC, actividades y plan de negocio basado en conversación guiada"""
    
    try:
        print(f"Iniciando generación guiada para usuario {current_user.email}")
        print(f"Idea de negocio: {request.business_idea}")
        print(f"Respuestas: {request.answers}")
        
        # Crear el prompt mejorado con toda la información
        enhanced_prompt = create_enhanced_prompt(request.business_idea, request.answers)
        
        # Generar BMC mejorado
        bmc_data = await generate_enhanced_bmc(enhanced_prompt)
        
        # Generar actividades específicas
        activities = await generate_contextual_activities(enhanced_prompt, bmc_data)
        
        # Generar plan de negocio con formato mejorado
        business_plan = generate_business_plan(request.business_idea, request.answers, bmc_data)
        
        # Crear proyecto en la base de datos
        project = create_project_from_conversation(
            request.business_idea, 
            bmc_data, 
            current_user, 
            db
        )
        
        # Guardar BMC
        save_bmc_to_project(project.id, bmc_data, db)
        
        # Guardar actividades
        save_activities_to_project(project.id, activities, current_user.id, db)
        
        # Guardar plan de negocio como documento
        save_business_plan_document(project.id, business_plan, current_user.id, db)
        
        return GuidedConversationResponse(
            project_id=project.id,
            project_name=project.name,
            bmc_data=bmc_data,
            activities=activities,
            business_plan=business_plan
        )
        
    except Exception as e:
        print(f"Error en generación guiada: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar plan de negocio: {str(e)}"
        )

def create_enhanced_prompt(business_idea: str, answers: Dict[str, str]) -> str:
    """Crear prompt mejorado con toda la información de la conversación"""
    
    context = f"""
    IDEA DE NEGOCIO: {business_idea}
    
    INFORMACIÓN DEL CONTEXTO:
    - Ubicación: {answers.get('location', 'No especificada')}
    - Clientes objetivo: {answers.get('target_customers', 'No especificados')}
    - Presupuesto: {answers.get('budget', 'No especificado')}
    - Competencia: {answers.get('competition', 'No especificada')}
    - Recursos disponibles: {answers.get('resources', 'No especificados')}
    - Timeline: {answers.get('timeline', 'No especificado')}
    
    Basándote en esta información específica, genera:
    1. Un Business Model Canvas detallado y contextualizado
    2. Actividades específicas para este contexto
    3. Un plan de negocio ejecutivo
    """
    
    return context

async def generate_enhanced_bmc(prompt: str) -> Dict[str, Any]:
    """Generar BMC mejorado usando AI"""
    
    ai_prompt = f"""
    {prompt}
    
    Genera un Business Model Canvas en formato JSON con la siguiente estructura:
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
    
    Asegúrate de que cada elemento esté específicamente adaptado al contexto proporcionado.
    """
    
    try:
        # Usar OpenAI para generar BMC mejorado
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "Eres un experto en Business Model Canvas y emprendimiento."},
                        {"role": "user", "content": ai_prompt}
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.7
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Extraer JSON del response
                try:
                    # Buscar el JSON en el contenido
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    json_str = content[start:end]
                    bmc_data = json.loads(json_str)
                    return bmc_data
                except (json.JSONDecodeError, ValueError):
                    # Fallback si no se puede parsear JSON
                    return generate_fallback_bmc()
            else:
                print(f"Error en OpenAI API: {response.status_code}")
                return generate_fallback_bmc()
                
    except Exception as e:
        print(f"Error generando BMC mejorado: {e}")
        return generate_fallback_bmc()

async def generate_contextual_activities(prompt: str, bmc_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generar actividades específicas para el contexto"""
    
    ai_prompt = f"""
    {prompt}
    
    Business Model Canvas generado:
    {json.dumps(bmc_data, indent=2)}
    
    Genera 5-7 actividades específicas para este negocio en formato JSON:
    [
        {{
            "title": "Nombre de la actividad",
            "description": "Descripción detallada",
            "priority": "high/medium/low",
            "estimated_duration_days": 14,
            "context": "Por qué es importante para este negocio específico"
        }}
    ]
    
    Las actividades deben estar directamente relacionadas con el contexto y el BMC generado.
    """
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "Eres un experto en gestión de proyectos y emprendimiento."},
                        {"role": "user", "content": ai_prompt}
                    ],
                    "max_tokens": 800,
                    "temperature": 0.7
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                try:
                    start = content.find('[')
                    end = content.rfind(']') + 1
                    json_str = content[start:end]
                    activities = json.loads(json_str)
                    return activities
                except (json.JSONDecodeError, ValueError):
                    return generate_fallback_activities()
            else:
                return generate_fallback_activities()
                
    except Exception as e:
        print(f"Error generando actividades: {e}")
        return generate_fallback_activities()

def generate_business_plan(business_idea: str, answers: Dict[str, str], bmc_data: Dict[str, Any]) -> str:
    """Generar un plan de negocio profesional con formato mejorado"""
    
    # Extraer información de las respuestas
    location = answers.get('location', 'No especificado')
    target_customers = answers.get('target_customers', 'No especificado')
    budget = answers.get('budget', 'No especificado')
    competition = answers.get('competition', 'No especificado')
    resources = answers.get('resources', 'No especificado')
    timeline = answers.get('timeline', 'No especificado')
    
    # Generar contenido del plan de negocio
    plan_content = f"""
# PLAN DE NEGOCIO
## {business_idea.upper()}

---

### 📋 RESUMEN EJECUTIVO

**Idea de Negocio:** {business_idea}
**Ubicación:** {location}
**Público Objetivo:** {target_customers}
**Presupuesto Inicial:** {budget}
**Timeline de Lanzamiento:** {timeline}

---

### 🎯 ANÁLISIS DE MERCADO

#### Público Objetivo
- **Segmento Principal:** {target_customers}
- **Características Demográficas:** Segmento específico identificado
- **Necesidades Identificadas:** Basadas en el análisis del mercado

#### Análisis de Competencia
- **Estado del Mercado:** {competition}
- **Oportunidades de Diferenciación:** Identificadas en el BMC
- **Ventajas Competitivas:** Basadas en la propuesta de valor

---

### 💼 MODELO DE NEGOCIO

#### Propuesta de Valor
{format_bmc_section(bmc_data.get('value_propositions', []))}

#### Segmentos de Clientes
{format_bmc_section(bmc_data.get('customer_segments', []))}

#### Canales de Distribución
{format_bmc_section(bmc_data.get('channels', []))}

#### Relaciones con Clientes
{format_bmc_section(bmc_data.get('customer_relationships', []))}

#### Fuentes de Ingresos
{format_bmc_section(bmc_data.get('revenue_streams', []))}

#### Recursos Clave
{format_bmc_section(bmc_data.get('key_resources', []))}

#### Actividades Clave
{format_bmc_section(bmc_data.get('key_activities', []))}

#### Socios Clave
{format_bmc_section(bmc_data.get('key_partners', []))}

#### Estructura de Costos
{format_bmc_section(bmc_data.get('cost_structure', []))}

---

### 📊 PLAN FINANCIERO

#### Presupuesto Inicial
- **Inversión Requerida:** {budget}
- **Fuentes de Financiamiento:** Por definir
- **Proyección de Ingresos:** Basada en el modelo de negocio

#### Proyecciones Financieras
- **Año 1:** Estimación de ingresos y gastos
- **Año 2:** Crecimiento proyectado
- **Año 3:** Consolidación del negocio

---

### 🚀 PLAN DE IMPLEMENTACIÓN

#### Fase 1: Preparación ({timeline})
- Validación del modelo de negocio
- Desarrollo de prototipos
- Establecimiento de alianzas estratégicas

#### Fase 2: Lanzamiento
- Implementación de canales de distribución
- Campañas de marketing iniciales
- Captación de primeros clientes

#### Fase 3: Crecimiento
- Expansión de mercado
- Optimización de procesos
- Escalamiento del negocio

---

### ⚠️ ANÁLISIS DE RIESGOS

#### Riesgos Identificados
1. **Riesgo de Mercado:** Cambios en las preferencias del consumidor
2. **Riesgo Operacional:** Dificultades en la ejecución
3. **Riesgo Financiero:** Limitaciones de capital
4. **Riesgo Tecnológico:** Dependencia de tecnologías específicas

#### Estrategias de Mitigación
- Diversificación de productos/servicios
- Construcción de reservas financieras
- Desarrollo de capacidades internas
- Monitoreo continuo del mercado

---

### 📈 MÉTRICAS DE ÉXITO

#### KPIs Principales
- **Ingresos Mensuales:** Meta a definir
- **Número de Clientes:** Meta a definir
- **Tasa de Retención:** Meta a definir
- **Satisfacción del Cliente:** Meta a definir

#### Métricas de Seguimiento
- **ROI de Marketing:** Retorno de inversión en publicidad
- **Costo de Adquisición:** Costo por cliente nuevo
- **Valor de Vida del Cliente:** LTV proyectado

---

### 🎯 CONCLUSIONES Y RECOMENDACIONES

Este plan de negocio presenta una oportunidad viable en el mercado actual. La combinación de una propuesta de valor sólida, un mercado objetivo bien definido y recursos disponibles crea las condiciones para el éxito del proyecto.

**Próximos Pasos:**
1. Validar el modelo de negocio con clientes potenciales
2. Desarrollar prototipos y MVP
3. Establecer alianzas estratégicas
4. Implementar el plan de marketing
5. Monitorear métricas clave

---

*Documento generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}*
*Plan de Negocio para: {business_idea}*
"""
    
    return plan_content

def format_bmc_section(items: List[str]) -> str:
    """Formatear una sección del BMC para el plan de negocio"""
    if not items:
        return "- No especificado"
    
    formatted_items = []
    for i, item in enumerate(items, 1):
        formatted_items.append(f"{i}. {item}")
    
    return "\n".join(formatted_items)

def generate_marketing_plan(business_idea: str, answers: Dict[str, str], bmc_data: Dict[str, Any]) -> str:
    """Generar un plan de marketing profesional"""
    
    target_customers = answers.get('target_customers', 'No especificado')
    budget = answers.get('budget', 'No especificado')
    location = answers.get('location', 'No especificado')
    
    marketing_content = f"""
# PLAN DE MARKETING
## {business_idea.upper()}

---

### 📊 ANÁLISIS DE MERCADO

#### Público Objetivo
**Segmento Principal:** {target_customers}
**Ubicación:** {location}
**Características Demográficas:** Segmento específico identificado
**Comportamiento de Compra:** Por analizar

#### Análisis de Competencia
- **Competidores Directos:** Identificados en el análisis
- **Competidores Indirectos:** Mercados relacionados
- **Oportunidades de Diferenciación:** Basadas en la propuesta de valor

---

### 🎯 ESTRATEGIA DE MARKETING

#### Propuesta de Valor
{format_bmc_section(bmc_data.get('value_propositions', []))}

#### Posicionamiento
- **Posición en el Mercado:** Por definir
- **Mensaje Principal:** Basado en la propuesta de valor
- **Diferenciación:** Respecto a la competencia

---

### 📢 PLAN DE COMUNICACIÓN

#### Canales de Marketing
{format_bmc_section(bmc_data.get('channels', []))}

#### Estrategia de Contenido
1. **Contenido Educativo:** Información valiosa para el público objetivo
2. **Contenido Promocional:** Ofertas y beneficios específicos
3. **Contenido de Marca:** Construcción de identidad de marca

#### Calendario de Campañas
- **Mes 1:** Lanzamiento y awareness
- **Mes 2-3:** Consideración y conversión
- **Mes 4-6:** Retención y fidelización

---

### 💰 PRESUPUESTO DE MARKETING

#### Distribución del Presupuesto
- **Presupuesto Total:** {budget}
- **Marketing Digital:** 60% del presupuesto
- **Marketing Tradicional:** 25% del presupuesto
- **Eventos y Networking:** 15% del presupuesto

#### Canales de Inversión
1. **Redes Sociales:** Facebook, Instagram, LinkedIn
2. **Google Ads:** Búsqueda y display
3. **Email Marketing:** Campañas automatizadas
4. **Contenido:** Blog y recursos educativos

---

### 📈 MÉTRICAS Y KPIs

#### Métricas de Alcance
- **Impresiones:** Número de veces que se muestra el contenido
- **Alcance:** Número de personas únicas alcanzadas
- **Engagement:** Interacciones con el contenido

#### Métricas de Conversión
- **Tasa de Conversión:** Porcentaje de visitantes que se convierten
- **Costo por Adquisición:** Costo de obtener un nuevo cliente
- **ROI de Marketing:** Retorno de inversión en publicidad

#### Métricas de Retención
- **Tasa de Retención:** Porcentaje de clientes que regresan
- **Valor de Vida del Cliente:** LTV promedio
- **Satisfacción del Cliente:** NPS y encuestas

---

### 🚀 PLAN DE IMPLEMENTACIÓN

#### Fase 1: Preparación (Mes 1)
- Desarrollo de identidad de marca
- Creación de materiales de marketing
- Configuración de herramientas digitales

#### Fase 2: Lanzamiento (Mes 2)
- Campañas de awareness
- Activación de canales digitales
- Medición inicial de resultados

#### Fase 3: Optimización (Mes 3-6)
- Ajuste de estrategias basado en datos
- Escalamiento de campañas exitosas
- Desarrollo de nuevos canales

---

### ⚠️ RIESGOS Y MITIGACIÓN

#### Riesgos Identificados
1. **Cambios en Algoritmos:** Plataformas sociales
2. **Saturación del Mercado:** Competencia creciente
3. **Cambios en Preferencias:** Público objetivo
4. **Limitaciones de Presupuesto:** Restricciones financieras

#### Estrategias de Mitigación
- Diversificación de canales
- Construcción de audiencia orgánica
- Monitoreo continuo del mercado
- Optimización constante del presupuesto

---

*Documento generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}*
*Plan de Marketing para: {business_idea}*
"""
    
    return marketing_content

def generate_market_research(business_idea: str, answers: Dict[str, str], bmc_data: Dict[str, Any]) -> str:
    """Generar una investigación de mercado profesional"""
    
    location = answers.get('location', 'No especificado')
    target_customers = answers.get('target_customers', 'No especificado')
    competition = answers.get('competition', 'No especificado')
    
    research_content = f"""
# INVESTIGACIÓN DE MERCADO
## {business_idea.upper()}

---

### 📋 RESUMEN EJECUTIVO

**Objetivo del Estudio:** Analizar la viabilidad de {business_idea} en {location}
**Metodología:** Análisis de mercado, competencia y tendencias
**Período de Estudio:** {datetime.now().strftime('%B %Y')}

---

### 🎯 ANÁLISIS DEL MERCADO

#### Tamaño del Mercado
- **Mercado Total Disponible:** Por cuantificar
- **Mercado Objetivo:** {target_customers}
- **Mercado Alcanzable:** Segmento específico

#### Tendencias del Mercado
1. **Tendencias Tecnológicas:** Evolución de la tecnología
2. **Tendencias Sociales:** Cambios en comportamiento del consumidor
3. **Tendencias Económicas:** Factores macroeconómicos
4. **Tendencias Regulatorias:** Cambios en normativas

---

### 👥 ANÁLISIS DEL CONSUMIDOR

#### Perfil del Cliente Objetivo
**Demografía:**
- Edad: Por definir
- Género: Por definir
- Ingresos: Por definir
- Educación: Por definir

**Psicografía:**
- Estilo de vida: Por definir
- Valores: Por definir
- Intereses: Por definir
- Comportamiento de compra: Por definir

#### Necesidades y Puntos de Dolor
{format_bmc_section(bmc_data.get('value_propositions', []))}

#### Comportamiento de Compra
- **Proceso de Decisión:** Por analizar
- **Factores de Influencia:** Por identificar
- **Canales de Compra:** Por definir
- **Frecuencia de Compra:** Por determinar

---

### 🏢 ANÁLISIS DE COMPETENCIA

#### Estado de la Competencia
**Análisis:** {competition}

#### Competidores Principales
1. **Competidor Directo 1:** Análisis por realizar
2. **Competidor Directo 2:** Análisis por realizar
3. **Competidor Indirecto 1:** Análisis por realizar

#### Análisis FODA de Competidores
**Fortalezas:**
- Por analizar

**Debilidades:**
- Por analizar

**Oportunidades:**
- Por analizar

**Amenazas:**
- Por analizar

---

### 📊 ANÁLISIS DE OPORTUNIDADES

#### Oportunidades Identificadas
1. **Oportunidad de Mercado:** Basada en necesidades insatisfechas
2. **Oportunidad Tecnológica:** Nuevas tecnologías disponibles
3. **Oportunidad de Diferenciación:** Propuesta de valor única
4. **Oportunidad de Expansión:** Mercados relacionados

#### Amenazas y Riesgos
1. **Riesgo de Mercado:** Cambios en preferencias
2. **Riesgo Competitivo:** Entrada de nuevos competidores
3. **Riesgo Tecnológico:** Obsolescencia tecnológica
4. **Riesgo Regulatorio:** Cambios en normativas

---

### 💡 RECOMENDACIONES ESTRATÉGICAS

#### Posicionamiento Recomendado
- **Posición en el Mercado:** Por definir
- **Mensaje Principal:** Basado en la propuesta de valor
- **Diferenciación:** Respecto a la competencia

#### Estrategia de Entrada
1. **Fase 1:** Validación del mercado
2. **Fase 2:** Lanzamiento piloto
3. **Fase 3:** Expansión gradual
4. **Fase 4:** Consolidación

#### Canales de Distribución Recomendados
{format_bmc_section(bmc_data.get('channels', []))}

---

### 📈 PROYECCIONES DE MERCADO

#### Proyecciones de Crecimiento
- **Año 1:** Estimación inicial
- **Año 2:** Crecimiento proyectado
- **Año 3:** Consolidación esperada

#### Factores de Crecimiento
1. **Factores Internos:** Capacidades de la empresa
2. **Factores Externos:** Condiciones del mercado
3. **Factores Tecnológicos:** Evolución de la tecnología
4. **Factores Sociales:** Cambios en comportamiento

---

### 🔍 METODOLOGÍA DE INVESTIGACIÓN

#### Fuentes de Información
- **Investigación Primaria:** Entrevistas y encuestas
- **Investigación Secundaria:** Reportes y estudios existentes
- **Análisis de Competencia:** Estudio de competidores
- **Análisis de Tendencias:** Investigación de tendencias

#### Limitaciones del Estudio
- **Alcance:** Limitado a {location}
- **Período:** Análisis actual
- **Metodología:** Basada en información disponible

---

### 📋 CONCLUSIONES

La investigación de mercado indica que {business_idea} tiene potencial en el mercado de {location}. El análisis de la competencia y las necesidades del consumidor sugieren oportunidades de diferenciación y crecimiento.

**Recomendación Principal:** Proceder con el desarrollo del proyecto con las estrategias identificadas en este estudio.

---

*Documento generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}*
*Investigación de Mercado para: {business_idea}*
"""
    
    return research_content

def create_project_from_conversation(
    business_idea: str, 
    bmc_data: Dict[str, Any], 
    current_user: User, 
    db: Session
) -> Project:
    """Crear proyecto basado en la conversación guiada"""
    
    # Usar la primera propuesta de valor como nombre del proyecto
    project_name = bmc_data.get("value_propositions", [business_idea])[0] if bmc_data.get("value_propositions") else business_idea
    
    project = Project(
        name=project_name,
        description=f"Proyecto generado mediante conversación guiada: {business_idea}",
        category_id=1,  # Categoría por defecto
        location_id=1,  # Ubicación por defecto
        status_id=1,    # Estado activo
        owner_id=current_user.id,
        company_id=current_user.company_id
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return project

def save_bmc_to_project(project_id: int, bmc_data: Dict[str, Any], db: Session):
    """Guardar BMC en la base de datos"""
    
    bmc = BusinessModelCanvas(
        project_id=project_id,
        key_partners=json.dumps(bmc_data.get("key_partners", [])),
        key_activities=json.dumps(bmc_data.get("key_activities", [])),
        key_resources=json.dumps(bmc_data.get("key_resources", [])),
        value_propositions=json.dumps(bmc_data.get("value_propositions", [])),
        customer_relationships=json.dumps(bmc_data.get("customer_relationships", [])),
        channels=json.dumps(bmc_data.get("channels", [])),
        customer_segments=json.dumps(bmc_data.get("customer_segments", [])),
        cost_structure=json.dumps(bmc_data.get("cost_structure", [])),
        revenue_streams=json.dumps(bmc_data.get("revenue_streams", []))
    )
    
    db.add(bmc)
    db.commit()

def save_activities_to_project(project_id: int, activities: List[Dict[str, Any]], user_id: int, db: Session):
    """Guardar actividades en la base de datos"""
    
    for i, activity_data in enumerate(activities):
        start_date = datetime.now() + timedelta(days=i * 2)
        duration_days = activity_data.get("estimated_duration_days", 7)
        due_date = start_date + timedelta(days=duration_days)
        
        activity = ProjectActivity(
            title=activity_data.get("title", f"Actividad {i+1}"),
            description=activity_data.get("description", ""),
            status="todo",
            priority=activity_data.get("priority", "medium"),
            project_id=project_id,
            start_date=start_date,
            due_date=due_date
        )
        
        db.add(activity)
    
    db.commit()

def save_business_plan_document(project_id: int, business_plan: str, user_id: int, db: Session):
    """Guardar plan de negocio como documento"""
    
    # Por ahora guardamos el contenido como texto
    # En el futuro podríamos generar un archivo Word real
    document = ProjectDocument(
        name="Plan de Negocio",
        original_name="plan_negocio.txt",
        file_type="text/plain",
        file_size=len(business_plan.encode('utf-8')),
        description="Plan de negocio generado mediante conversación guiada",
        project_id=project_id,
        uploader_id=user_id,
        file_path="plan_negocio.txt",  # Por ahora guardamos como archivo de texto
    )
    
    db.add(document)
    db.commit()

# Funciones de fallback
def generate_fallback_bmc() -> Dict[str, Any]:
    """BMC de fallback si falla la generación AI"""
    return {
        "key_partners": ["Socios estratégicos", "Proveedores"],
        "key_activities": ["Desarrollo de software", "Gestión de proyectos"],
        "key_resources": ["Equipo de desarrollo", "Infraestructura tecnológica"],
        "value_propositions": ["Plataforma intuitiva", "Gestión eficiente"],
        "customer_relationships": ["Soporte personalizado", "Comunidad activa"],
        "channels": ["Plataforma web", "Aplicación móvil"],
        "customer_segments": ["Empresas medianas", "Startups"],
        "cost_structure": ["Desarrollo", "Marketing", "Operaciones"],
        "revenue_streams": ["Suscripciones", "Servicios premium"]
    }

def generate_fallback_activities() -> List[Dict[str, Any]]:
    """Actividades de fallback"""
    return [
        {
            "title": "Investigación de Mercado",
            "description": "Realizar análisis de mercado y competencia",
            "priority": "high",
            "estimated_duration_days": 14,
            "context": "Fundamental para entender el entorno del negocio"
        },
        {
            "title": "Desarrollo de MVP",
            "description": "Crear versión mínima viable del producto",
            "priority": "high",
            "estimated_duration_days": 30,
            "context": "Permite validar la propuesta de valor"
        },
        {
            "title": "Estrategia de Marketing",
            "description": "Definir estrategia de posicionamiento y promoción",
            "priority": "medium",
            "estimated_duration_days": 21,
            "context": "Esencial para llegar a los clientes objetivo"
        }
    ]
