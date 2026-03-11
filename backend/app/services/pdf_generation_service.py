"""
Servicio para generar documentos PDF profesionales
"""
import os
import io
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import Color, black, blue, darkblue, grey
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import logging

logger = logging.getLogger(__name__)

class DocumentType(Enum):
    BUSINESS_PLAN = "business_plan"
    MARKETING_PLAN = "marketing_plan"
    MARKET_RESEARCH = "market_research"
    BUSINESS_MODEL_ALTERNATIVES = "business_model_alternatives"
    PROJECT_REPORT = "project_report"

class DocumentRequest:
    def __init__(self, 
                 document_type: DocumentType,
                 title: str,
                 content: Dict[str, Any],
                 project_name: Optional[str] = None,
                 company_name: Optional[str] = None,
                 author: Optional[str] = None):
        self.document_type = document_type
        self.title = title
        self.content = content
        self.project_name = project_name or "Proyecto InnovAI"
        self.company_name = company_name or "InnovAI"
        self.author = author or "InnovAI Assistant"

class PDFGenerationService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Configurar estilos personalizados para los documentos"""
        # Estilo para títulos principales
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=darkblue,
            alignment=TA_CENTER
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=darkblue,
            alignment=TA_LEFT
        ))
        
        # Estilo para subtítulos secundarios
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            textColor=blue,
            alignment=TA_LEFT
        ))
        
        # Estilo para texto normal
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            leading=14
        ))
        
        # Estilo para texto en cursiva
        self.styles.add(ParagraphStyle(
            name='CustomItalic',
            parent=self.styles['Italic'],
            fontSize=10,
            spaceAfter=6,
            textColor=grey,
            alignment=TA_JUSTIFY
        ))

    def generate_document(self, request: DocumentRequest) -> bytes:
        """Generar documento PDF basado en el tipo y contenido"""
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Construir contenido del documento
            story = []
            
            # Portada
            self._add_cover_page(story, request)
            story.append(PageBreak())
            
            # Tabla de contenidos
            self._add_table_of_contents(story, request)
            story.append(PageBreak())
            
            # Contenido principal
            self._add_main_content(story, request)
            
            # Construir PDF
            doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
            
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error generando PDF: {str(e)}")
            raise

    def _add_cover_page(self, story, request: DocumentRequest):
        """Agregar portada del documento"""
        # Logo o título principal
        story.append(Spacer(1, 2*inch))
        
        title = Paragraph(request.title, self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.5*inch))
        
        # Información del proyecto
        project_info = f"""
        <b>Proyecto:</b> {request.project_name}<br/>
        <b>Empresa:</b> {request.company_name}<br/>
        <b>Generado por:</b> {request.author}<br/>
        <b>Fecha:</b> {datetime.now().strftime('%d de %B de %Y')}
        """
        
        info_para = Paragraph(project_info, self.styles['CustomNormal'])
        story.append(info_para)
        story.append(Spacer(1, 1*inch))
        
        # Pie de página de la portada
        footer = Paragraph(
            "Este documento fue generado automáticamente por InnovAI<br/>"
            "Sistema de Gestión de Proyectos y Business Model Canvas",
            self.styles['CustomItalic']
        )
        story.append(footer)

    def _add_table_of_contents(self, story, request: DocumentRequest):
        """Agregar tabla de contenidos"""
        story.append(Paragraph("Tabla de Contenidos", self.styles['CustomHeading1']))
        story.append(Spacer(1, 0.3*inch))
        
        # Generar tabla de contenidos basada en el tipo de documento
        if request.document_type == DocumentType.BUSINESS_PLAN:
            toc_items = [
                "1. Resumen Ejecutivo",
                "2. Descripción de la Empresa", 
                "3. Análisis de Mercado",
                "4. Estructura Organizacional",
                "5. Línea de Productos/Servicios",
                "6. Estrategia de Marketing y Ventas",
                "7. Requisitos de Financiamiento",
                "8. Proyecciones Financieras",
                "9. Apéndices"
            ]
        elif request.document_type == DocumentType.MARKETING_PLAN:
            toc_items = [
                "1. Resumen del Mercado",
                "2. Análisis de Competencia",
                "3. Estrategia de Marketing",
                "4. Plan de Comunicación",
                "5. Presupuesto de Marketing",
                "6. Métricas y KPIs",
                "7. Cronograma de Implementación"
            ]
        elif request.document_type == DocumentType.MARKET_RESEARCH:
            toc_items = [
                "1. Resumen Ejecutivo",
                "2. Metodología de Investigación",
                "3. Análisis del Mercado",
                "4. Análisis de Competencia",
                "5. Análisis del Cliente",
                "6. Conclusiones y Recomendaciones"
            ]
        elif request.document_type == DocumentType.BUSINESS_MODEL_ALTERNATIVES:
            toc_items = [
                "1. Resumen Ejecutivo",
                "2. Análisis del Modelo Actual",
                "3. Modelos de Negocio Alternativos",
                "4. Análisis Comparativo",
                "5. Recomendaciones de Implementación",
                "6. Plan de Transición",
                "7. Métricas de Éxito"
            ]
        else:
            toc_items = [
                "1. Resumen Ejecutivo",
                "2. Análisis del Proyecto",
                "3. Recomendaciones",
                "4. Anexos"
            ]
        
        for item in toc_items:
            story.append(Paragraph(item, self.styles['CustomNormal']))
            story.append(Spacer(1, 0.1*inch))

    def _add_main_content(self, story, request: DocumentRequest):
        """Agregar contenido principal del documento"""
        content = request.content
        
        if request.document_type == DocumentType.BUSINESS_PLAN:
            self._add_business_plan_content(story, content)
        elif request.document_type == DocumentType.MARKETING_PLAN:
            self._add_marketing_plan_content(story, content)
        elif request.document_type == DocumentType.MARKET_RESEARCH:
            self._add_market_research_content(story, content)
        elif request.document_type == DocumentType.BUSINESS_MODEL_ALTERNATIVES:
            self._add_business_model_alternatives_content(story, content)
        else:
            self._add_generic_content(story, content)

    def _add_business_plan_content(self, story, content: Dict[str, Any]):
        """Agregar contenido específico del plan de negocio"""
        
        # 1. Resumen Ejecutivo
        story.append(Paragraph("1. Resumen Ejecutivo", self.styles['CustomHeading1']))
        story.append(Paragraph(content.get('executive_summary', 'No disponible'), self.styles['CustomNormal']))
        story.append(Spacer(1, 0.2*inch))
        
        # 2. Descripción de la Empresa
        story.append(Paragraph("2. Descripción de la Empresa", self.styles['CustomHeading1']))
        story.append(Paragraph(content.get('company_description', 'No disponible'), self.styles['CustomNormal']))
        story.append(Spacer(1, 0.2*inch))
        
        # 3. Análisis de Mercado
        story.append(Paragraph("3. Análisis de Mercado", self.styles['CustomHeading1']))
        market_analysis = content.get('market_analysis', {})
        
        story.append(Paragraph("3.1 Tamaño del Mercado", self.styles['CustomHeading2']))
        story.append(Paragraph(market_analysis.get('market_size', 'No disponible'), self.styles['CustomNormal']))
        
        story.append(Paragraph("3.2 Mercado Objetivo", self.styles['CustomHeading2']))
        story.append(Paragraph(market_analysis.get('target_market', 'No disponible'), self.styles['CustomNormal']))
        
        story.append(Paragraph("3.3 Tendencias del Mercado", self.styles['CustomHeading2']))
        trends = market_analysis.get('market_trends', [])
        if trends:
            for trend in trends:
                story.append(Paragraph(f"• {trend}", self.styles['CustomNormal']))
        else:
            story.append(Paragraph("No disponible", self.styles['CustomNormal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # 4. Estructura Organizacional
        story.append(Paragraph("4. Estructura Organizacional", self.styles['CustomHeading1']))
        org_management = content.get('organization_management', {})
        
        story.append(Paragraph("4.1 Estructura Organizacional", self.styles['CustomHeading2']))
        story.append(Paragraph(org_management.get('organizational_structure', 'No disponible'), self.styles['CustomNormal']))
        
        story.append(Paragraph("4.2 Equipo de Gestión", self.styles['CustomHeading2']))
        management_team = org_management.get('management_team', [])
        if management_team:
            for member in management_team:
                story.append(Paragraph(f"<b>{member.get('name', 'N/A')}</b> - {member.get('position', 'N/A')}", self.styles['CustomNormal']))
                story.append(Paragraph(f"Experiencia: {member.get('experience', 'N/A')}", self.styles['CustomNormal']))
                story.append(Spacer(1, 0.1*inch))
        else:
            story.append(Paragraph("No disponible", self.styles['CustomNormal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # 5. Línea de Productos/Servicios
        story.append(Paragraph("5. Línea de Productos/Servicios", self.styles['CustomHeading1']))
        service_product = content.get('service_product_line', {})
        
        story.append(Paragraph("5.1 Descripción", self.styles['CustomHeading2']))
        story.append(Paragraph(service_product.get('description', 'No disponible'), self.styles['CustomNormal']))
        
        story.append(Paragraph("5.2 Características", self.styles['CustomHeading2']))
        features = service_product.get('features', [])
        if features:
            for feature in features:
                story.append(Paragraph(f"• {feature}", self.styles['CustomNormal']))
        else:
            story.append(Paragraph("No disponible", self.styles['CustomNormal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # 6. Estrategia de Marketing y Ventas
        story.append(Paragraph("6. Estrategia de Marketing y Ventas", self.styles['CustomHeading1']))
        marketing_sales = content.get('marketing_sales', {})
        
        story.append(Paragraph("6.1 Estrategia de Marketing", self.styles['CustomHeading2']))
        story.append(Paragraph(marketing_sales.get('marketing_strategy', 'No disponible'), self.styles['CustomNormal']))
        
        story.append(Paragraph("6.2 Estrategia de Ventas", self.styles['CustomHeading2']))
        story.append(Paragraph(marketing_sales.get('sales_strategy', 'No disponible'), self.styles['CustomNormal']))
        
        story.append(Paragraph("6.3 Estrategia de Precios", self.styles['CustomHeading2']))
        story.append(Paragraph(marketing_sales.get('pricing_strategy', 'No disponible'), self.styles['CustomNormal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # 7. Requisitos de Financiamiento
        story.append(Paragraph("7. Requisitos de Financiamiento", self.styles['CustomHeading1']))
        funding = content.get('funding_requirements', {})
        
        story.append(Paragraph("7.1 Necesidades de Financiamiento", self.styles['CustomHeading2']))
        story.append(Paragraph(funding.get('funding_needs', 'No disponible'), self.styles['CustomNormal']))
        
        story.append(Paragraph("7.2 Uso de Fondos", self.styles['CustomHeading2']))
        use_of_funds = funding.get('use_of_funds', [])
        if use_of_funds:
            for use in use_of_funds:
                story.append(Paragraph(f"• {use}", self.styles['CustomNormal']))
        else:
            story.append(Paragraph("No disponible", self.styles['CustomNormal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # 8. Proyecciones Financieras
        story.append(Paragraph("8. Proyecciones Financieras", self.styles['CustomHeading1']))
        financial_projections = content.get('financial_projections', {})
        
        # Proyecciones de ingresos
        story.append(Paragraph("8.1 Proyecciones de Ingresos", self.styles['CustomHeading2']))
        revenue_projections = financial_projections.get('revenue_projections', [])
        if revenue_projections:
            for i, projection in enumerate(revenue_projections, 1):
                story.append(Paragraph(f"Año {i}: ${projection.get('revenue', 'N/A'):,}", self.styles['CustomNormal']))
        else:
            story.append(Paragraph("No disponible", self.styles['CustomNormal']))
        
        # Análisis de punto de equilibrio
        story.append(Paragraph("8.2 Análisis de Punto de Equilibrio", self.styles['CustomHeading2']))
        story.append(Paragraph(financial_projections.get('break_even_analysis', 'No disponible'), self.styles['CustomNormal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # 9. Apéndices
        story.append(Paragraph("9. Apéndices", self.styles['CustomHeading1']))
        story.append(Paragraph(content.get('appendix', 'No disponible'), self.styles['CustomNormal']))

    def _add_marketing_plan_content(self, story, content: Dict[str, Any]):
        """Agregar contenido específico del plan de marketing"""
        
        # 1. Resumen del Mercado
        story.append(Paragraph("1. Resumen del Mercado", self.styles['CustomHeading1']))
        story.append(Paragraph(content.get('market_overview', 'No disponible'), self.styles['CustomNormal']))
        story.append(Spacer(1, 0.2*inch))
        
        # 2. Audiencia Objetivo
        story.append(Paragraph("2. Audiencia Objetivo", self.styles['CustomHeading1']))
        target_audience = content.get('target_audience', {})
        
        # Audiencia Primaria
        story.append(Paragraph("2.1 Audiencia Primaria", self.styles['CustomHeading2']))
        primary = target_audience.get('primary', {})
        story.append(Paragraph(f"<b>Descripción:</b> {primary.get('description', 'No disponible')}", self.styles['CustomNormal']))
        story.append(Paragraph(f"<b>Tamaño:</b> {primary.get('size', 'No disponible')}", self.styles['CustomNormal']))
        
        characteristics = primary.get('characteristics', [])
        if characteristics:
            story.append(Paragraph("Características:", self.styles['CustomHeading2']))
            for char in characteristics:
                story.append(Paragraph(f"• {char}", self.styles['CustomNormal']))
        
        pain_points = primary.get('pain_points', [])
        if pain_points:
            story.append(Paragraph("Puntos de Dolor:", self.styles['CustomHeading2']))
            for pain in pain_points:
                story.append(Paragraph(f"• {pain}", self.styles['CustomNormal']))
        
        # Audiencia Secundaria
        story.append(Paragraph("2.2 Audiencia Secundaria", self.styles['CustomHeading2']))
        secondary = target_audience.get('secondary', {})
        story.append(Paragraph(f"<b>Descripción:</b> {secondary.get('description', 'No disponible')}", self.styles['CustomNormal']))
        story.append(Paragraph(f"<b>Tamaño:</b> {secondary.get('size', 'No disponible')}", self.styles['CustomNormal']))
        
        # Demografía
        story.append(Paragraph("2.3 Demografía", self.styles['CustomHeading2']))
        demographics = target_audience.get('demographics', {})
        story.append(Paragraph(f"<b>Rango de Edad:</b> {demographics.get('age_range', 'No disponible')}", self.styles['CustomNormal']))
        story.append(Paragraph(f"<b>Género:</b> {demographics.get('gender', 'No disponible')}", self.styles['CustomNormal']))
        story.append(Paragraph(f"<b>Nivel de Ingresos:</b> {demographics.get('income_level', 'No disponible')}", self.styles['CustomNormal']))
        story.append(Paragraph(f"<b>Educación:</b> {demographics.get('education', 'No disponible')}", self.styles['CustomNormal']))
        story.append(Paragraph(f"<b>Ubicación:</b> {demographics.get('location', 'No disponible')}", self.styles['CustomNormal']))
        
        occupations = demographics.get('occupation', [])
        if occupations:
            story.append(Paragraph("Ocupaciones:", self.styles['CustomHeading2']))
            for occ in occupations:
                story.append(Paragraph(f"• {occ}", self.styles['CustomNormal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # 3. Objetivos de Marketing
        story.append(Paragraph("3. Objetivos de Marketing", self.styles['CustomHeading1']))
        objectives = content.get('marketing_objectives', [])
        if objectives:
            for i, obj in enumerate(objectives, 1):
                story.append(Paragraph(f"{i}. {obj}", self.styles['CustomNormal']))
        else:
            story.append(Paragraph("No disponible", self.styles['CustomNormal']))
        story.append(Spacer(1, 0.2*inch))
        
        # 4. Estrategias de Marketing
        story.append(Paragraph("4. Estrategias de Marketing", self.styles['CustomHeading1']))
        strategies = content.get('marketing_strategies', [])
        if strategies:
            for i, strategy in enumerate(strategies, 1):
                story.append(Paragraph(f"4.{i} {strategy.get('channel', 'Canal sin nombre')}", self.styles['CustomHeading2']))
                story.append(Paragraph(f"<b>Enfoque:</b> {strategy.get('approach', 'No disponible')}", self.styles['CustomNormal']))
                
                tactics = strategy.get('tactics', [])
                if tactics:
                    story.append(Paragraph("Tácticas:", self.styles['CustomHeading2']))
                    for tactic in tactics:
                        story.append(Paragraph(f"• {tactic}", self.styles['CustomNormal']))
                
                story.append(Paragraph(f"<b>Presupuesto:</b> ${strategy.get('budget', 0):,}", self.styles['CustomNormal']))
                
                results = strategy.get('expected_results', [])
                if results:
                    story.append(Paragraph("Resultados Esperados:", self.styles['CustomHeading2']))
                    for result in results:
                        story.append(Paragraph(f"• {result}", self.styles['CustomNormal']))
                
                story.append(Spacer(1, 0.1*inch))
        else:
            story.append(Paragraph("No disponible", self.styles['CustomNormal']))
        story.append(Spacer(1, 0.2*inch))
        
        # 5. Presupuesto
        story.append(Paragraph("5. Plan de Presupuesto", self.styles['CustomHeading1']))
        budget = content.get('budget_allocation', {})
        story.append(Paragraph(f"<b>Presupuesto Total:</b> ${budget.get('total_budget', 0):,}", self.styles['CustomNormal']))
        
        # Asignación por canal
        channel_allocation = budget.get('channel_allocation', [])
        if channel_allocation:
            story.append(Paragraph("5.1 Asignación por Canal", self.styles['CustomHeading2']))
            for allocation in channel_allocation:
                story.append(Paragraph(f"<b>{allocation.get('channel', 'Canal')}:</b> {allocation.get('percentage', 0)*100:.1f}% - ${allocation.get('amount', 0):,}", self.styles['CustomNormal']))
                story.append(Paragraph(f"Justificación: {allocation.get('rationale', 'No disponible')}", self.styles['CustomNormal']))
        
        # Asignación por timeline
        timeline_allocation = budget.get('timeline_allocation', [])
        if timeline_allocation:
            story.append(Paragraph("5.2 Asignación por Timeline", self.styles['CustomHeading2']))
            for allocation in timeline_allocation:
                story.append(Paragraph(f"<b>{allocation.get('period', 'Período')}:</b> {allocation.get('percentage', 0)*100:.1f}% - ${allocation.get('amount', 0):,}", self.styles['CustomNormal']))
                activities = allocation.get('activities', [])
                if activities:
                    story.append(Paragraph("Actividades:", self.styles['CustomHeading2']))
                    for activity in activities:
                        story.append(Paragraph(f"• {activity}", self.styles['CustomNormal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # 6. Timeline de Implementación
        story.append(Paragraph("6. Timeline de Implementación", self.styles['CustomHeading1']))
        story.append(Paragraph(content.get('timeline', 'No disponible'), self.styles['CustomNormal']))
        story.append(Spacer(1, 0.2*inch))
        
        # 7. KPIs y Métricas
        story.append(Paragraph("7. KPIs y Métricas", self.styles['CustomHeading1']))
        kpis = content.get('kpis', [])
        if kpis:
            for i, kpi in enumerate(kpis, 1):
                story.append(Paragraph(f"{i}. {kpi}", self.styles['CustomNormal']))
        else:
            story.append(Paragraph("No disponible", self.styles['CustomNormal']))

    def _add_market_research_content(self, story, content: Dict[str, Any]):
        """Agregar contenido específico de investigación de mercado"""
        
        # 1. Resumen Ejecutivo
        story.append(Paragraph("1. Resumen Ejecutivo", self.styles['CustomHeading1']))
        story.append(Paragraph(content.get('executive_summary', 'No disponible'), self.styles['CustomNormal']))
        story.append(Spacer(1, 0.2*inch))
        
        # 2. Objetivos de la Investigación
        story.append(Paragraph("2. Objetivos de la Investigación", self.styles['CustomHeading1']))
        objectives = content.get('research_objectives', [])
        if objectives:
            for i, obj in enumerate(objectives, 1):
                story.append(Paragraph(f"{i}. {obj}", self.styles['CustomNormal']))
        else:
            story.append(Paragraph("No disponible", self.styles['CustomNormal']))
        story.append(Spacer(1, 0.2*inch))
        
        # 3. Metodología
        story.append(Paragraph("3. Metodología", self.styles['CustomHeading1']))
        story.append(Paragraph(content.get('methodology', 'No disponible'), self.styles['CustomNormal']))
        story.append(Spacer(1, 0.2*inch))
        
        # 4. Visión General del Mercado
        story.append(Paragraph("4. Visión General del Mercado", self.styles['CustomHeading1']))
        market_overview = content.get('market_overview', {})
        
        story.append(Paragraph(f"<b>Tamaño del Mercado:</b> {market_overview.get('market_size', 'No disponible')}", self.styles['CustomNormal']))
        story.append(Paragraph(f"<b>Crecimiento del Mercado:</b> {market_overview.get('market_growth', 'No disponible')}", self.styles['CustomNormal']))
        
        # Segmentos del mercado
        segments = market_overview.get('market_segments', [])
        if segments:
            story.append(Paragraph("4.1 Segmentos del Mercado", self.styles['CustomHeading2']))
            for segment in segments:
                story.append(Paragraph(f"<b>{segment.get('name', 'Segmento')}</b>", self.styles['CustomNormal']))
                story.append(Paragraph(f"Tamaño: {segment.get('size', 'No disponible')}", self.styles['CustomNormal']))
                story.append(Paragraph(f"Tasa de Crecimiento: {segment.get('growth_rate', 'No disponible')}", self.styles['CustomNormal']))
                
                characteristics = segment.get('characteristics', [])
                if characteristics:
                    story.append(Paragraph("Características:", self.styles['CustomHeading2']))
                    for char in characteristics:
                        story.append(Paragraph(f"• {char}", self.styles['CustomNormal']))
                
                needs = segment.get('needs', [])
                if needs:
                    story.append(Paragraph("Necesidades:", self.styles['CustomHeading2']))
                    for need in needs:
                        story.append(Paragraph(f"• {need}", self.styles['CustomNormal']))
                
                story.append(Spacer(1, 0.1*inch))
        
        # Impulsores clave
        drivers = market_overview.get('key_drivers', [])
        if drivers:
            story.append(Paragraph("4.2 Impulsores Clave del Mercado", self.styles['CustomHeading2']))
            for driver in drivers:
                story.append(Paragraph(f"• {driver}", self.styles['CustomNormal']))
        
        # Desafíos
        challenges = market_overview.get('challenges', [])
        if challenges:
            story.append(Paragraph("4.3 Desafíos del Mercado", self.styles['CustomHeading2']))
            for challenge in challenges:
                story.append(Paragraph(f"• {challenge}", self.styles['CustomNormal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # 5. Insights del Cliente
        story.append(Paragraph("5. Insights del Cliente", self.styles['CustomHeading1']))
        customer_insights = content.get('customer_insights', {})
        
        # Viaje del cliente
        journey = customer_insights.get('customer_journey', [])
        if journey:
            story.append(Paragraph("5.1 Viaje del Cliente", self.styles['CustomHeading2']))
            for stage in journey:
                story.append(Paragraph(f"<b>{stage.get('stage', 'Etapa')}</b>", self.styles['CustomNormal']))
                
                touchpoints = stage.get('touchpoints', [])
                if touchpoints:
                    story.append(Paragraph("Puntos de Contacto:", self.styles['CustomHeading2']))
                    for tp in touchpoints:
                        story.append(Paragraph(f"• {tp}", self.styles['CustomNormal']))
                
                emotions = stage.get('emotions', [])
                if emotions:
                    story.append(Paragraph("Emociones:", self.styles['CustomHeading2']))
                    for emotion in emotions:
                        story.append(Paragraph(f"• {emotion}", self.styles['CustomNormal']))
                
                needs = stage.get('needs', [])
                if needs:
                    story.append(Paragraph("Necesidades:", self.styles['CustomHeading2']))
                    for need in needs:
                        story.append(Paragraph(f"• {need}", self.styles['CustomNormal']))
                
                story.append(Spacer(1, 0.1*inch))
        
        # Puntos de dolor
        pain_points = customer_insights.get('pain_points', [])
        if pain_points:
            story.append(Paragraph("5.2 Puntos de Dolor Identificados", self.styles['CustomHeading2']))
            for pain in pain_points:
                story.append(Paragraph(f"• {pain}", self.styles['CustomNormal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # 6. Paisaje Competitivo
        story.append(Paragraph("6. Paisaje Competitivo", self.styles['CustomHeading1']))
        competitive = content.get('competitive_landscape', {})
        
        # Participación de mercado
        market_share = competitive.get('market_share', [])
        if market_share:
            story.append(Paragraph("6.1 Participación de Mercado", self.styles['CustomHeading2']))
            for share in market_share:
                story.append(Paragraph(f"<b>{share.get('company', 'Empresa')}:</b> {share.get('percentage', 0):.1f}% - Tendencia: {share.get('trend', 'N/A')}", self.styles['CustomNormal']))
        
        # Posiciones competitivas
        positions = competitive.get('competitive_positions', [])
        if positions:
            story.append(Paragraph("6.2 Posiciones Competitivas", self.styles['CustomHeading2']))
            for position in positions:
                story.append(Paragraph(f"<b>{position.get('company', 'Empresa')} - {position.get('position', 'Posición')}</b>", self.styles['CustomNormal']))
                
                strengths = position.get('strengths', [])
                if strengths:
                    story.append(Paragraph("Fortalezas:", self.styles['CustomHeading2']))
                    for strength in strengths:
                        story.append(Paragraph(f"• {strength}", self.styles['CustomNormal']))
                
                weaknesses = position.get('weaknesses', [])
                if weaknesses:
                    story.append(Paragraph("Debilidades:", self.styles['CustomHeading2']))
                    for weakness in weaknesses:
                        story.append(Paragraph(f"• {weakness}", self.styles['CustomNormal']))
                
                story.append(Spacer(1, 0.1*inch))
        
        story.append(Spacer(1, 0.2*inch))
        
        # 7. Oportunidades de Mercado
        story.append(Paragraph("7. Oportunidades de Mercado", self.styles['CustomHeading1']))
        opportunities = content.get('market_opportunities', [])
        if opportunities:
            for i, opportunity in enumerate(opportunities, 1):
                story.append(Paragraph(f"{i}. {opportunity}", self.styles['CustomNormal']))
        else:
            story.append(Paragraph("No disponible", self.styles['CustomNormal']))
        story.append(Spacer(1, 0.2*inch))
        
        # 8. Recomendaciones
        story.append(Paragraph("8. Recomendaciones", self.styles['CustomHeading1']))
        recommendations = content.get('recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                story.append(Paragraph(f"{i}. {rec}", self.styles['CustomNormal']))
        else:
            story.append(Paragraph("No disponible", self.styles['CustomNormal']))
        story.append(Spacer(1, 0.2*inch))
        
        # 9. Apéndices
        story.append(Paragraph("9. Apéndices", self.styles['CustomHeading1']))
        appendices = content.get('appendices', [])
        if appendices:
            for i, appendix in enumerate(appendices, 1):
                story.append(Paragraph(f"{i}. {appendix}", self.styles['CustomNormal']))
        else:
            story.append(Paragraph("No disponible", self.styles['CustomNormal']))

    def _add_business_model_alternatives_content(self, story, content: Dict[str, Any]):
        """Agregar contenido específico de modelos de negocio alternativos"""
        
        # 1. Resumen Ejecutivo
        story.append(Paragraph("1. Resumen Ejecutivo", self.styles['CustomHeading1']))
        story.append(Paragraph(content.get('executive_summary', 'No disponible'), self.styles['CustomNormal']))
        story.append(Spacer(1, 0.2*inch))
        
        # 2. Análisis del Modelo Actual
        story.append(Paragraph("2. Análisis del Modelo Actual", self.styles['CustomHeading1']))
        current_model = content.get('current_model', {})
        
        story.append(Paragraph("2.1 Descripción del Modelo Actual", self.styles['CustomHeading2']))
        story.append(Paragraph(current_model.get('description', 'No disponible'), self.styles['CustomNormal']))
        
        story.append(Paragraph("2.2 Fortalezas del Modelo Actual", self.styles['CustomHeading2']))
        strengths = current_model.get('strengths', [])
        if strengths:
            for strength in strengths:
                story.append(Paragraph(f"• {strength}", self.styles['CustomNormal']))
        else:
            story.append(Paragraph("No disponible", self.styles['CustomNormal']))
        
        story.append(Paragraph("2.3 Debilidades del Modelo Actual", self.styles['CustomHeading2']))
        weaknesses = current_model.get('weaknesses', [])
        if weaknesses:
            for weakness in weaknesses:
                story.append(Paragraph(f"• {weakness}", self.styles['CustomNormal']))
        else:
            story.append(Paragraph("No disponible", self.styles['CustomNormal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # 3. Modelos de Negocio Alternativos
        story.append(Paragraph("3. Modelos de Negocio Alternativos", self.styles['CustomHeading1']))
        alternatives = content.get('alternatives', [])
        
        if alternatives:
            for i, alternative in enumerate(alternatives, 1):
                story.append(Paragraph(f"3.{i} {alternative.get('name', 'Modelo Alternativo')}", self.styles['CustomHeading2']))
                story.append(Paragraph(f"<b>Descripción:</b> {alternative.get('description', 'No disponible')}", self.styles['CustomNormal']))
                
                # Características principales
                features = alternative.get('key_features', [])
                if features:
                    story.append(Paragraph("Características Principales:", self.styles['CustomHeading2']))
                    for feature in features:
                        story.append(Paragraph(f"• {feature}", self.styles['CustomNormal']))
                
                # Ventajas
                advantages = alternative.get('advantages', [])
                if advantages:
                    story.append(Paragraph("Ventajas:", self.styles['CustomHeading2']))
                    for advantage in advantages:
                        story.append(Paragraph(f"• {advantage}", self.styles['CustomNormal']))
                
                # Desventajas
                disadvantages = alternative.get('disadvantages', [])
                if disadvantages:
                    story.append(Paragraph("Desventajas:", self.styles['CustomHeading2']))
                    for disadvantage in disadvantages:
                        story.append(Paragraph(f"• {disadvantage}", self.styles['CustomNormal']))
                
                # Casos de uso
                use_cases = alternative.get('use_cases', [])
                if use_cases:
                    story.append(Paragraph("Casos de Uso:", self.styles['CustomHeading2']))
                    for use_case in use_cases:
                        story.append(Paragraph(f"• {use_case}", self.styles['CustomNormal']))
                
                story.append(Spacer(1, 0.1*inch))
        else:
            story.append(Paragraph("No disponible", self.styles['CustomNormal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # 4. Análisis Comparativo
        story.append(Paragraph("4. Análisis Comparativo", self.styles['CustomHeading1']))
        comparison = content.get('comparison', {})
        
        story.append(Paragraph("4.1 Criterios de Evaluación", self.styles['CustomHeading2']))
        criteria = comparison.get('evaluation_criteria', [])
        if criteria:
            for criterion in criteria:
                story.append(Paragraph(f"• {criterion}", self.styles['CustomNormal']))
        else:
            story.append(Paragraph("No disponible", self.styles['CustomNormal']))
        
        story.append(Paragraph("4.2 Matriz Comparativa", self.styles['CustomHeading2']))
        story.append(Paragraph(comparison.get('comparative_matrix', 'No disponible'), self.styles['CustomNormal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # 5. Recomendaciones de Implementación
        story.append(Paragraph("5. Recomendaciones de Implementación", self.styles['CustomHeading1']))
        recommendations = content.get('implementation_recommendations', {})
        
        story.append(Paragraph("5.1 Modelo Recomendado", self.styles['CustomHeading2']))
        story.append(Paragraph(recommendations.get('recommended_model', 'No disponible'), self.styles['CustomNormal']))
        
        story.append(Paragraph("5.2 Justificación de la Recomendación", self.styles['CustomHeading2']))
        story.append(Paragraph(recommendations.get('justification', 'No disponible'), self.styles['CustomNormal']))
        
        story.append(Paragraph("5.3 Consideraciones Especiales", self.styles['CustomHeading2']))
        considerations = recommendations.get('special_considerations', [])
        if considerations:
            for consideration in considerations:
                story.append(Paragraph(f"• {consideration}", self.styles['CustomNormal']))
        else:
            story.append(Paragraph("No disponible", self.styles['CustomNormal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # 6. Plan de Transición
        story.append(Paragraph("6. Plan de Transición", self.styles['CustomHeading1']))
        transition_plan = content.get('transition_plan', {})
        
        story.append(Paragraph("6.1 Fases de Implementación", self.styles['CustomHeading2']))
        phases = transition_plan.get('implementation_phases', [])
        if phases:
            for i, phase in enumerate(phases, 1):
                story.append(Paragraph(f"Fase {i}: {phase.get('name', 'Fase sin nombre')}", self.styles['CustomNormal']))
                story.append(Paragraph(f"Duración: {phase.get('duration', 'No especificada')}", self.styles['CustomNormal']))
                story.append(Paragraph(f"Actividades: {phase.get('activities', 'No especificadas')}", self.styles['CustomNormal']))
                story.append(Spacer(1, 0.1*inch))
        else:
            story.append(Paragraph("No disponible", self.styles['CustomNormal']))
        
        story.append(Paragraph("6.2 Recursos Necesarios", self.styles['CustomHeading2']))
        resources = transition_plan.get('required_resources', [])
        if resources:
            for resource in resources:
                story.append(Paragraph(f"• {resource}", self.styles['CustomNormal']))
        else:
            story.append(Paragraph("No disponible", self.styles['CustomNormal']))
        
        story.append(Paragraph("6.3 Riesgos y Mitigaciones", self.styles['CustomHeading2']))
        risks = transition_plan.get('risks_mitigations', [])
        if risks:
            for risk in risks:
                story.append(Paragraph(f"• {risk}", self.styles['CustomNormal']))
        else:
            story.append(Paragraph("No disponible", self.styles['CustomNormal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # 7. Métricas de Éxito
        story.append(Paragraph("7. Métricas de Éxito", self.styles['CustomHeading1']))
        success_metrics = content.get('success_metrics', {})
        
        story.append(Paragraph("7.1 KPIs Principales", self.styles['CustomHeading2']))
        kpis = success_metrics.get('primary_kpis', [])
        if kpis:
            for kpi in kpis:
                story.append(Paragraph(f"• {kpi}", self.styles['CustomNormal']))
        else:
            story.append(Paragraph("No disponible", self.styles['CustomNormal']))
        
        story.append(Paragraph("7.2 Métricas de Seguimiento", self.styles['CustomHeading2']))
        tracking_metrics = success_metrics.get('tracking_metrics', [])
        if tracking_metrics:
            for metric in tracking_metrics:
                story.append(Paragraph(f"• {metric}", self.styles['CustomNormal']))
        else:
            story.append(Paragraph("No disponible", self.styles['CustomNormal']))
        
        story.append(Paragraph("7.3 Cronograma de Evaluación", self.styles['CustomHeading2']))
        story.append(Paragraph(success_metrics.get('evaluation_timeline', 'No disponible'), self.styles['CustomNormal']))

    def _add_generic_content(self, story, content: Dict[str, Any]):
        """Agregar contenido genérico"""
        story.append(Paragraph("Contenido del Documento", self.styles['CustomHeading1']))
        story.append(Paragraph("Contenido genérico del documento...", self.styles['CustomNormal']))

    def _add_header_footer(self, canvas, doc):
        """Agregar encabezado y pie de página a cada página"""
        # Encabezado
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(darkblue)
        canvas.drawString(72, A4[1] - 50, "InnovAI - Sistema de Gestión de Proyectos")
        
        # Pie de página
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(grey)
        canvas.drawString(72, 30, f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        canvas.drawRightString(A4[0] - 72, 30, f"Página {doc.page}")
        canvas.restoreState()

