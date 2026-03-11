"""
API para la salida del agente IA (n8n): guardar, obtener y crear proyecto desde payload.
Incluye PUT por sección para editar tablas canónicas (estrategia, roadmap, análisis, riesgos, veredicto).
"""
from typing import Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from datetime import datetime

from ..core.auth import get_current_user
from ..database import get_db
from ..models.user import User
from ..models.project import Project, ProjectTag
from ..models.project_agent_output import ProjectAgentOutput
from ..models.activity import ProjectActivity
from ..models.category import Category
from ..models.location import Location
from ..models.status import Status
from ..models.tag import Tag
from ..models.audit_log import AuditLog
from ..schemas.project_agent_output import (
    ProjectAgentOutputCreate,
    ProjectAgentOutputUpdate,
    ProjectAgentOutputResponse,
    CreateProjectFromAgentPayload,
)
from ..schemas.project import ProjectWithDetails
from ..services.agent_bmc_sync import sync_agent_bmc_to_canvas
from ..services.agent_sections_sync import (
    sync_all_agent_sections,
    get_merged_sections,
    sync_agent_estrategia_comercial,
    sync_agent_roadmap,
    sync_agent_analisis_financiero,
    sync_agent_analisis_riesgos,
    sync_agent_veredicto,
)

router = APIRouter(prefix="/agent-output", tags=["Agent Output (n8n)"])


def _map_agent_activity_status(estado: str) -> str:
    m = {"PENDIENTE": "todo", "EN PROGRESO": "in-progress", "EN REVISIÓN": "review", "COMPLETADO": "completed"}
    return m.get((estado or "").upper(), "todo")


def _map_agent_priority(prioridad: str) -> str:
    m = {"ALTA": "high", "MEDIA": "medium", "BAJA": "low"}
    return m.get((prioridad or "").upper(), "medium")


def _ensure_project_access(project_id: int, current_user: User, db: Session) -> Project:
    project = db.query(Project).filter(Project.id == project_id, Project.company_id == current_user.company_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado")
    return project


def _agent_response(
    project_id: int,
    message: str,
    mode: str = "update",
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Respuesta estándar para el agente de n8n (status, message, project_id, mode, success)."""
    out: Dict[str, Any] = {
        "status": "completed",
        "message": message,
        "project_id": str(project_id),
        "mode": mode,
        "success": True,
    }
    if extra:
        out.update(extra)
    return out


@router.get("/project/{project_id}", response_model=ProjectAgentOutputResponse)
async def get_project_agent_output(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtener la salida del agente para un proyecto."""
    project = db.query(Project).filter(Project.id == project_id, Project.company_id == current_user.company_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado")

    row = db.query(ProjectAgentOutput).filter(ProjectAgentOutput.project_id == project_id).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay datos del agente para este proyecto")

    merged = get_merged_sections(db, project_id)
    estrategia = merged["estrategia_comercial"] if merged["estrategia_comercial"] else row.estrategia_comercial
    roadmap = merged["roadmap_estrategico"] if merged["roadmap_estrategico"] else row.roadmap_estrategico
    analisis_fin = merged["analisis_financiero"] if merged["analisis_financiero"] else row.analisis_financiero
    analisis_ries = merged["analisis_riesgos"] if merged["analisis_riesgos"] else row.analisis_riesgos
    veredicto = merged["veredicto_final"] if merged["veredicto_final"] else row.veredicto_final

    return ProjectAgentOutputResponse(
        id=row.id,
        project_id=row.project_id,
        metadata=row.metadata_,
        conversacion=row.conversacion,
        business_model_canvas=row.business_model_canvas,
        estrategia_comercial=estrategia,
        roadmap_estrategico=roadmap,
        analisis_financiero=analisis_fin,
        analisis_riesgos=analisis_ries,
        veredicto_final=veredicto,
        plan_actividades=row.plan_actividades,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.put("/project/{project_id}", response_model=ProjectAgentOutputResponse)
async def upsert_project_agent_output(
    project_id: int,
    payload: ProjectAgentOutputCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Crear o actualizar la salida del agente para un proyecto existente."""
    project = db.query(Project).filter(Project.id == project_id, Project.company_id == current_user.company_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado")

    row = db.query(ProjectAgentOutput).filter(ProjectAgentOutput.project_id == project_id).first()
    if row:
        row.metadata_ = payload.metadata
        row.conversacion = payload.conversacion
        row.business_model_canvas = payload.business_model_canvas
        row.estrategia_comercial = payload.estrategia_comercial
        row.roadmap_estrategico = payload.roadmap_estrategico
        row.analisis_financiero = payload.analisis_financiero
        row.analisis_riesgos = payload.analisis_riesgos
        row.veredicto_final = payload.veredicto_final
        row.plan_actividades = payload.plan_actividades
    else:
        row = ProjectAgentOutput(
            project_id=project_id,
            metadata_=payload.metadata,
            conversacion=payload.conversacion,
            business_model_canvas=payload.business_model_canvas,
            estrategia_comercial=payload.estrategia_comercial,
            roadmap_estrategico=payload.roadmap_estrategico,
            analisis_financiero=payload.analisis_financiero,
            analisis_riesgos=payload.analisis_riesgos,
            veredicto_final=payload.veredicto_final,
            plan_actividades=payload.plan_actividades,
        )
        db.add(row)
    db.commit()
    db.refresh(row)

    # Sincronizar BMC del agente a business_model_canvases (fuente única para edición)
    if payload.business_model_canvas:
        sync_agent_bmc_to_canvas(project_id, payload.business_model_canvas, db)
    # Sincronizar resto de secciones a tablas canónicas
    sync_all_agent_sections(
        project_id,
        {
            "estrategia_comercial": payload.estrategia_comercial,
            "roadmap_estrategico": payload.roadmap_estrategico,
            "analisis_financiero": payload.analisis_financiero,
            "analisis_riesgos": payload.analisis_riesgos,
            "veredicto_final": payload.veredicto_final,
        },
        db,
    )

    merged = get_merged_sections(db, project_id)
    estrategia = merged["estrategia_comercial"] or row.estrategia_comercial
    roadmap = merged["roadmap_estrategico"] or row.roadmap_estrategico
    analisis_fin = merged["analisis_financiero"] or row.analisis_financiero
    analisis_ries = merged["analisis_riesgos"] or row.analisis_riesgos
    veredicto = merged["veredicto_final"] or row.veredicto_final

    return ProjectAgentOutputResponse(
        id=row.id,
        project_id=row.project_id,
        metadata=row.metadata_,
        conversacion=row.conversacion,
        business_model_canvas=row.business_model_canvas,
        estrategia_comercial=estrategia,
        roadmap_estrategico=roadmap,
        analisis_financiero=analisis_fin,
        analisis_riesgos=analisis_ries,
        veredicto_final=veredicto,
        plan_actividades=row.plan_actividades,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.put("/project/{project_id}/estrategia-comercial")
async def update_estrategia_comercial(
    project_id: int,
    body: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza la estrategia comercial del proyecto (tabla canónica)."""
    _ensure_project_access(project_id, current_user, db)
    sync_agent_estrategia_comercial(project_id, body, db)
    return _agent_response(project_id, "Estrategia comercial actualizada correctamente en el proyecto.")


@router.put("/project/{project_id}/roadmap")
async def update_roadmap(
    project_id: int,
    body: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza el roadmap del proyecto (tabla canónica)."""
    _ensure_project_access(project_id, current_user, db)
    sync_agent_roadmap(project_id, body, db)
    return _agent_response(project_id, "Roadmap estratégico actualizado correctamente en el proyecto.")


@router.put("/project/{project_id}/analisis-financiero")
async def update_analisis_financiero(
    project_id: int,
    body: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza el análisis financiero del proyecto (tabla canónica)."""
    _ensure_project_access(project_id, current_user, db)
    sync_agent_analisis_financiero(project_id, body, db)
    return _agent_response(project_id, "Análisis financiero actualizado correctamente en el proyecto.")


@router.put("/project/{project_id}/analisis-riesgos")
async def update_analisis_riesgos(
    project_id: int,
    body: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza el análisis de riesgos del proyecto (tablas canónicas)."""
    _ensure_project_access(project_id, current_user, db)
    sync_agent_analisis_riesgos(project_id, body, db)
    return _agent_response(project_id, "Análisis de riesgos actualizado correctamente en el proyecto.")


@router.put("/project/{project_id}/veredicto")
async def update_veredicto(
    project_id: int,
    body: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza el veredicto del proyecto (tabla canónica). Un futuro agente puede re-analizar y actualizar."""
    _ensure_project_access(project_id, current_user, db)
    sync_agent_veredicto(project_id, body, db)
    return _agent_response(project_id, "Veredicto actualizado correctamente en el proyecto.")


@router.put("/project/{project_id}/conversacion")
async def update_conversacion(
    project_id: int,
    body: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza solo la conversación del agente (project_agent_output.conversacion). Para uso del agente de conversación en n8n."""
    _ensure_project_access(project_id, current_user, db)
    row = db.query(ProjectAgentOutput).filter(ProjectAgentOutput.project_id == project_id).first()
    if row:
        row.conversacion = body
    else:
        row = ProjectAgentOutput(project_id=project_id, conversacion=body)
        db.add(row)
    db.commit()
    return _agent_response(project_id, "Conversación actualizada correctamente en el proyecto.")


@router.put("/project/{project_id}/business-model-canvas")
async def update_business_model_canvas(
    project_id: int,
    body: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza el BMC del proyecto. Acepta el formato agente (segmentos_clientes, propuesta_valor, etc.); se sincroniza a business_model_canvases y se guarda copia en project_agent_output."""
    _ensure_project_access(project_id, current_user, db)
    sync_agent_bmc_to_canvas(project_id, body, db)
    row = db.query(ProjectAgentOutput).filter(ProjectAgentOutput.project_id == project_id).first()
    if row:
        row.business_model_canvas = body
        db.commit()
    else:
        agent_row = ProjectAgentOutput(project_id=project_id, business_model_canvas=body)
        db.add(agent_row)
        db.commit()
    return _agent_response(project_id, "Business Model Canvas actualizado correctamente en el proyecto.")


@router.put("/project/{project_id}/plan-actividades")
async def update_plan_actividades(
    project_id: int,
    body: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza el plan de actividades: guarda el JSON en project_agent_output.plan_actividades y crea las actividades del array en el proyecto (POST a activities)."""
    project = _ensure_project_access(project_id, current_user, db)
    plan = body.get("plan_actividades") or body
    actividades = (plan.get("actividades") or [])
    for act in actividades:
        try:
            start = act.get("fecha_inicio") or "2024-01-01"
            end = act.get("fecha_fin") or "2024-01-31"
            if isinstance(start, str):
                start = datetime.fromisoformat(start.replace("Z", "+00:00"))
            else:
                start = datetime(2024, 1, 1)
            if isinstance(end, str):
                end = datetime.fromisoformat(end.replace("Z", "+00:00"))
            else:
                end = datetime(2024, 1, 31)
        except Exception:
            start = datetime(2024, 1, 1)
            end = datetime(2024, 1, 31)
        db_act = ProjectActivity(
            title=(act.get("titulo") or "Actividad")[:200],
            description=act.get("descripcion"),
            status=_map_agent_activity_status(act.get("estado")),
            priority=_map_agent_priority(act.get("prioridad")),
            project_id=project_id,
            start_date=start,
            due_date=end,
        )
        db.add(db_act)
    db.commit()
    row = db.query(ProjectAgentOutput).filter(ProjectAgentOutput.project_id == project_id).first()
    if row:
        row.plan_actividades = plan if isinstance(plan, dict) and "actividades" in plan else {"generado": True, "actividades": actividades, "resumen": body.get("resumen") or {}}
        db.commit()
    else:
        agent_row = ProjectAgentOutput(project_id=project_id, plan_actividades=plan if isinstance(plan, dict) and "actividades" in plan else {"generado": True, "actividades": actividades, "resumen": body.get("resumen") or {}})
        db.add(agent_row)
        db.commit()
    return _agent_response(
        project_id,
        f"Plan de actividades actualizado correctamente. Se crearon {len(actividades)} actividades en el proyecto.",
        extra={"activities_created": len(actividades)},
    )


@router.post("/create-project", response_model=ProjectWithDetails)
async def create_project_from_agent(
    body: CreateProjectFromAgentPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Crea un proyecto nuevo a partir de la salida del agente (salidaAgente.json).
    Crea: proyecto, fila en project_agent_output, BMC si viene en el payload y actividades desde plan_actividades.
    """
    p = body.payload
    name = body.name or (p.get("conversacion") or {}).get("idea_negocio_original", "Proyecto desde agente")[:200]
    description = body.description or name

    category = db.query(Category).filter(Category.company_id == current_user.company_id).first()
    if not category:
        category = Category(name="General", company_id=current_user.company_id)
        db.add(category)
        db.commit()
        db.refresh(category)

    location = db.query(Location).filter(Location.company_id == current_user.company_id).first()
    if not location:
        location = Location(name="Sin ubicación", company_id=current_user.company_id)
        db.add(location)
        db.commit()
        db.refresh(location)

    status_obj = db.query(Status).filter(Status.company_id == current_user.company_id).first()
    if not status_obj:
        status_obj = Status(name="Activo", company_id=current_user.company_id)
        db.add(status_obj)
        db.commit()
        db.refresh(status_obj)

    project = Project(
        name=name,
        description=description,
        company_id=current_user.company_id,
        category_id=body.category_id or category.id,
        location_id=body.location_id or location.id,
        status_id=status_obj.id,
        owner_id=current_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    bmc_data = p.get("business_model_canvas")
    bmc_created = False
    if bmc_data:
        bmc_created = sync_agent_bmc_to_canvas(project.id, bmc_data, db)

    sync_all_agent_sections(
        project.id,
        {
            "estrategia_comercial": p.get("estrategia_comercial"),
            "roadmap_estrategico": p.get("roadmap_estrategico"),
            "analisis_financiero": p.get("analisis_financiero"),
            "analisis_riesgos": p.get("analisis_riesgos"),
            "veredicto_final": p.get("veredicto_final"),
        },
        db,
    )

    plan = p.get("plan_actividades") or {}
    actividades = (plan.get("actividades") or [])
    for act in actividades:
        try:
            start = act.get("fecha_inicio") or "2024-01-01"
            end = act.get("fecha_fin") or "2024-01-31"
            if isinstance(start, str):
                start = datetime.fromisoformat(start.replace("Z", "+00:00"))
            else:
                start = datetime(2024, 1, 1)
            if isinstance(end, str):
                end = datetime.fromisoformat(end.replace("Z", "+00:00"))
            else:
                end = datetime(2024, 1, 31)
        except Exception:
            start = datetime(2024, 1, 1)
            end = datetime(2024, 1, 31)
        db_act = ProjectActivity(
            title=(act.get("titulo") or "Actividad")[:200],
            description=act.get("descripcion"),
            status=_map_agent_activity_status(act.get("estado")),
            priority=_map_agent_priority(act.get("prioridad")),
            project_id=project.id,
            start_date=start,
            due_date=end,
        )
        db.add(db_act)
    db.commit()

    agent_row = ProjectAgentOutput(
        project_id=project.id,
        metadata_=p.get("metadata"),
        conversacion=p.get("conversacion"),
        business_model_canvas=p.get("business_model_canvas"),
        estrategia_comercial=p.get("estrategia_comercial"),
        roadmap_estrategico=p.get("roadmap_estrategico"),
        analisis_financiero=p.get("analisis_financiero"),
        analisis_riesgos=p.get("analisis_riesgos"),
        veredicto_final=p.get("veredicto_final"),
        plan_actividades=p.get("plan_actividades"),
    )
    db.add(agent_row)
    db.commit()
    db.refresh(project)

    status_mapping = {"Activo": "active", "Inactivo": "inactive", "Completado": "completed"}
    response_status = status_mapping.get(status_obj.name, "active")
    return ProjectWithDetails(
        id=project.id,
        name=project.name,
        description=project.description,
        category=category.name,
        location=location.name,
        status=response_status,
        owner_id=project.owner_id,
        created_at=project.created_at,
        updated_at=project.updated_at,
        tags=[],
        owner_name=current_user.full_name,
        activities_count=len(actividades),
        documents_count=0,
        has_business_model_canvas=bmc_created,
    )
