"""
Utilidades para generar documentos PDF
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from typing import Dict, Any, Optional


def generate_business_plan_pdf(
    business_plan_data: Dict[str, Any], 
    project_name: str, 
    output_path: str
) -> str:
    """
    Genera un PDF del plan de negocio
    
    Args:
        business_plan_data: Datos del plan de negocio
        project_name: Nombre del proyecto
        output_path: Ruta donde guardar el PDF
    
    Returns:
        str: Ruta del archivo PDF generado
    """
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Obtener estilos
    styles = getSampleStyleSheet()
    
    # Crear estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.darkblue,
        alignment=1  # Centrado
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.darkblue
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        leading=14
    )
    
    # Contenido del documento
    story = []
    
    # Título principal
    story.append(Paragraph("PLAN DE NEGOCIO", title_style))
    story.append(Paragraph(f"<b>Proyecto:</b> {project_name}", normal_style))
    story.append(Paragraph(f"<b>Fecha de generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
    story.append(Spacer(1, 20))
    
    # Extraer datos del plan de negocio
    business_plan = business_plan_data.get('business_plan', {})
    
    # Resumen Ejecutivo
    if business_plan.get('executive_summary'):
        story.append(Paragraph("1. RESUMEN EJECUTIVO", heading_style))
        story.append(Paragraph(business_plan['executive_summary'], normal_style))
        story.append(Spacer(1, 12))
    
    # Análisis de Mercado
    if business_plan.get('market_analysis'):
        story.append(Paragraph("2. ANÁLISIS DE MERCADO", heading_style))
        story.append(Paragraph(business_plan['market_analysis'], normal_style))
        story.append(Spacer(1, 12))
    
    # Proyecciones Financieras
    if business_plan.get('financial_projections'):
        story.append(Paragraph("3. PROYECCIONES FINANCIERAS", heading_style))
        story.append(Paragraph(business_plan['financial_projections'], normal_style))
        story.append(Spacer(1, 12))
    
    # Plan Operacional
    if business_plan.get('operational_plan'):
        story.append(Paragraph("4. PLAN OPERACIONAL", heading_style))
        story.append(Paragraph(business_plan['operational_plan'], normal_style))
        story.append(Spacer(1, 12))
    
    # Estrategia de Marketing
    if business_plan.get('marketing_strategy'):
        story.append(Paragraph("5. ESTRATEGIA DE MARKETING", heading_style))
        story.append(Paragraph(business_plan['marketing_strategy'], normal_style))
        story.append(Spacer(1, 12))
    
    # Análisis de Riesgos
    if business_plan.get('risk_analysis'):
        story.append(Paragraph("6. ANÁLISIS DE RIESGOS", heading_style))
        story.append(Paragraph(business_plan['risk_analysis'], normal_style))
        story.append(Spacer(1, 12))
    
    # Información adicional si está disponible
    if business_plan.get('target_audience'):
        story.append(Paragraph("7. AUDIENCIA OBJETIVO", heading_style))
        story.append(Paragraph(business_plan['target_audience'], normal_style))
        story.append(Spacer(1, 12))
    
    if business_plan.get('competitive_analysis'):
        story.append(Paragraph("8. ANÁLISIS COMPETITIVO", heading_style))
        story.append(Paragraph(business_plan['competitive_analysis'], normal_style))
        story.append(Spacer(1, 12))
    
    if business_plan.get('success_metrics'):
        story.append(Paragraph("9. MÉTRICAS DE ÉXITO", heading_style))
        story.append(Paragraph(business_plan['success_metrics'], normal_style))
        story.append(Spacer(1, 12))
    
    # Pie de página
    story.append(Spacer(1, 30))
    story.append(Paragraph(
        f"<i>Documento generado automáticamente por InnovAI el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}</i>",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.grey, alignment=1)
    ))
    
    # Construir el PDF
    doc.build(story)
    
    return output_path


def generate_marketing_plan_pdf(
    marketing_plan_data: Dict[str, Any], 
    project_name: str, 
    output_path: str
) -> str:
    """
    Genera un PDF del plan de marketing
    
    Args:
        marketing_plan_data: Datos del plan de marketing
        project_name: Nombre del proyecto
        output_path: Ruta donde guardar el PDF
    
    Returns:
        str: Ruta del archivo PDF generado
    """
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Obtener estilos
    styles = getSampleStyleSheet()
    
    # Crear estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.darkblue,
        alignment=1  # Centrado
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.darkblue
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        leading=14
    )
    
    # Contenido del documento
    story = []
    
    # Título principal
    story.append(Paragraph("PLAN DE MARKETING", title_style))
    story.append(Paragraph(f"<b>Proyecto:</b> {project_name}", normal_style))
    story.append(Paragraph(f"<b>Fecha de generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
    story.append(Spacer(1, 20))
    
    # Extraer datos del plan de marketing
    marketing_plan = marketing_plan_data.get('marketing_plan', {})
    
    # Estrategia de Marketing
    if marketing_plan.get('marketing_strategy'):
        story.append(Paragraph("1. ESTRATEGIA DE MARKETING", heading_style))
        story.append(Paragraph(marketing_plan['marketing_strategy'], normal_style))
        story.append(Spacer(1, 12))
    
    # Audiencia Objetivo
    if marketing_plan.get('target_audience'):
        story.append(Paragraph("2. AUDIENCIA OBJETIVO", heading_style))
        story.append(Paragraph(marketing_plan['target_audience'], normal_style))
        story.append(Spacer(1, 12))
    
    # Canales de Promoción
    if marketing_plan.get('promotion_channels'):
        story.append(Paragraph("3. CANALES DE PROMOCIÓN", heading_style))
        story.append(Paragraph(marketing_plan['promotion_channels'], normal_style))
        story.append(Spacer(1, 12))
    
    # Presupuesto de Marketing
    if marketing_plan.get('marketing_budget'):
        story.append(Paragraph("4. PRESUPUESTO DE MARKETING", heading_style))
        story.append(Paragraph(marketing_plan['marketing_budget'], normal_style))
        story.append(Spacer(1, 12))
    
    # Análisis Competitivo
    if marketing_plan.get('competitive_analysis'):
        story.append(Paragraph("5. ANÁLISIS COMPETITIVO", heading_style))
        story.append(Paragraph(marketing_plan['competitive_analysis'], normal_style))
        story.append(Spacer(1, 12))
    
    # Métricas de Éxito
    if marketing_plan.get('success_metrics'):
        story.append(Paragraph("6. MÉTRICAS DE ÉXITO", heading_style))
        story.append(Paragraph(marketing_plan['success_metrics'], normal_style))
        story.append(Spacer(1, 12))
    
    # Pie de página
    story.append(Spacer(1, 30))
    story.append(Paragraph(
        f"<i>Documento generado automáticamente por InnovAI el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}</i>",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.grey, alignment=1)
    ))
    
    # Construir el PDF
    doc.build(story)
    
    return output_path


def create_project_directory(project_id: int, upload_dir: str) -> str:
    """
    Crea el directorio del proyecto si no existe
    
    Args:
        project_id: ID del proyecto
        upload_dir: Directorio base de uploads
    
    Returns:
        str: Ruta del directorio del proyecto
    """
    project_dir = os.path.join(upload_dir, str(project_id))
    os.makedirs(project_dir, exist_ok=True)
    return project_dir


def generate_unique_filename(base_name: str, extension: str = '.pdf') -> str:
    """
    Genera un nombre único para el archivo
    
    Args:
        base_name: Nombre base del archivo
        extension: Extensión del archivo
    
    Returns:
        str: Nombre único del archivo
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # Limpiar el nombre base
    clean_name = ''.join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    clean_name = clean_name.replace(' ', '_')
    return f"{clean_name}_{timestamp}{extension}"


