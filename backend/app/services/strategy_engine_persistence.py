import json
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from ..models.analysis_request import AnalysisRequest
from ..models.analysis_result import AnalysisResult
from ..models.analysis_module import AnalysisModule
from ..models.analysis_activity import AnalysisActivity
from ..models.analysis_risk import AnalysisRisk
from ..models.project_agent_output import ProjectAgentOutput
from ..models.activity import ProjectActivity
from ..services.agent_bmc_sync import sync_agent_bmc_to_canvas
from ..services.agent_sections_sync import sync_all_agent_sections


def create_analysis_request(
    db: Session,
    *,
    request_id: str,
    project_id: Optional[int],
    project_name: str,
    analysis_type: Optional[str],
    language_code: str,
    organization_name: Optional[str],
    input_payload: Dict[str, Any],
    workflow_version: str,
    created_by: Optional[str] = None,
) -> AnalysisRequest:
    record = AnalysisRequest(
        request_id=request_id,
        project_id=str(project_id) if project_id is not None else None,
        project_name=project_name or None,
        analysis_type=analysis_type or "full_strategy",
        language_code=language_code,
        organization_name=organization_name,
        input_message=((input_payload.get("input_brief") or {}).get("description") or (input_payload.get("project_name") or ""))[:65535] or "",
        input_json=json.dumps(input_payload, ensure_ascii=False),
        status="running",
        progress=10,
        current_stage="workflow_triggered",
        workflow_version=workflow_version,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def mark_analysis_completed(
    db: Session,
    *,
    request_id: str,
    execution_time_ms: Optional[int] = None,
) -> None:
    record = db.query(AnalysisRequest).filter(AnalysisRequest.request_id == request_id).first()
    if record:
        record.status = "completed"
        record.progress = 100
        record.current_stage = "completed"
        db.commit()


def mark_analysis_failed(
    db: Session,
    *,
    request_id: str,
    error_message: str,
) -> None:
    record = db.query(AnalysisRequest).filter(AnalysisRequest.request_id == request_id).first()
    if record:
        record.status = "failed"
        record.error_message = error_message
        db.commit()


def save_analysis_result(db: Session, *, request_id: str, result: Dict[str, Any]) -> AnalysisResult:
    summary = result.get("summary", {}) or {}
    verdict = result.get("verdict", {}) or {}
    result_str = json.dumps(result, ensure_ascii=False)
    executive = summary.get("executive_summary") or verdict.get("executive_summary")

    existing = db.query(AnalysisResult).filter(AnalysisResult.request_id == request_id).first()
    if existing:
        existing.result_json = result_str
        existing.executive_summary = executive
        existing.market_analysis_json = json.dumps(result["market_analysis"], ensure_ascii=False) if result.get("market_analysis") else None
        existing.bmc_json = json.dumps(result["bmc"], ensure_ascii=False) if result.get("bmc") else None
        existing.strategy_json = json.dumps(result["strategy"], ensure_ascii=False) if result.get("strategy") else None
        existing.financial_json = json.dumps(result["finance"], ensure_ascii=False) if result.get("finance") else None
        existing.risks_json = json.dumps(result["risks"], ensure_ascii=False) if result.get("risks") else None
        existing.roadmap_json = json.dumps(result["roadmap"], ensure_ascii=False) if result.get("roadmap") else None
        existing.kanban_json = json.dumps(result["kanban"], ensure_ascii=False) if result.get("kanban") else None
        existing.gantt_json = json.dumps(result["gantt"], ensure_ascii=False) if result.get("gantt") else None
        db.commit()
        db.refresh(existing)
        return existing

    record = AnalysisResult(
        request_id=request_id,
        result_json=result_str,
        executive_summary=executive,
        market_analysis_json=json.dumps(result["market_analysis"], ensure_ascii=False) if result.get("market_analysis") else None,
        bmc_json=json.dumps(result["bmc"], ensure_ascii=False) if result.get("bmc") else None,
        strategy_json=json.dumps(result["strategy"], ensure_ascii=False) if result.get("strategy") else None,
        financial_json=json.dumps(result["finance"], ensure_ascii=False) if result.get("finance") else None,
        risks_json=json.dumps(result["risks"], ensure_ascii=False) if result.get("risks") else None,
        roadmap_json=json.dumps(result["roadmap"], ensure_ascii=False) if result.get("roadmap") else None,
        kanban_json=json.dumps(result["kanban"], ensure_ascii=False) if result.get("kanban") else None,
        gantt_json=json.dumps(result["gantt"], ensure_ascii=False) if result.get("gantt") else None,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def save_analysis_modules(db: Session, *, request_id: str, result: Dict[str, Any]) -> None:
    module_map = {
        "supervisor": result.get("supervisor"),
        "market_intelligence": result.get("market_analysis"),
        "bmc": result.get("bmc"),
        "strategy": result.get("strategy"),
        "finance": result.get("finance"),
        "risks": result.get("risks"),
        "roadmap": result.get("roadmap"),
        "verdict": result.get("verdict"),
        "activities": result.get("activities"),
        "kanban": result.get("kanban"),
        "gantt": result.get("gantt"),
    }

    for module_name, output in module_map.items():
        if output is None:
            continue

        existing = (
            db.query(AnalysisModule)
            .filter(
                AnalysisModule.request_id == request_id,
                AnalysisModule.module_name == module_name,
            )
            .first()
        )

        payload = json.dumps(output, ensure_ascii=False)

        if existing:
            existing.module_status = "completed"
            existing.output_json = payload
        else:
            db.add(
                AnalysisModule(
                    request_id=request_id,
                    module_name=module_name,
                    module_status="completed",
                    output_json=payload,
                )
            )
    db.commit()


def replace_analysis_activities(
    db: Session,
    *,
    request_id: str,
    activities: List[Dict[str, Any]],
    gantt_tasks: Optional[List[Dict[str, Any]]] = None,
) -> None:
    """Guarda actividades; si gantt_tasks está presente, rellena start_date/end_date por activity id."""
    gantt_by_id = {}
    if gantt_tasks:
        for t in gantt_tasks:
            aid = t.get("id")
            if aid:
                gantt_by_id[aid] = {"start": t.get("start"), "end": t.get("end")}

    db.query(AnalysisActivity).filter(AnalysisActivity.request_id == request_id).delete()

    for idx, item in enumerate(activities, start=1):
        aid = item.get("activity_id", f"A{idx}")
        g = gantt_by_id.get(aid) or {}
        db.add(
            AnalysisActivity(
                request_id=request_id,
                activity_id=aid,
                epic=item.get("epic"),
                title=item.get("title", f"Actividad {idx}"),
                description=item.get("description"),
                priority=item.get("priority"),
                owner_role=item.get("owner_role"),
                estimated_days=item.get("estimated_days"),
                depends_on_json=json.dumps(item.get("depends_on", []), ensure_ascii=False),
                kanban_status=item.get("kanban_status", "todo"),
                phase_id=item.get("phase_id"),
                start_date=_safe_date(item.get("start_date") or g.get("start")),
                end_date=_safe_date(item.get("end_date") or g.get("end")),
                raw_json=json.dumps(item, ensure_ascii=False),
                sort_order=item.get("sort_order", idx),
            )
        )
    db.commit()


def replace_analysis_risks(db: Session, *, request_id: str, risks: List[Dict[str, Any]]) -> None:
    db.query(AnalysisRisk).filter(AnalysisRisk.request_id == request_id).delete()

    for idx, item in enumerate(risks, start=1):
        db.add(
            AnalysisRisk(
                request_id=request_id,
                risk_id=item.get("risk_id", f"R{idx}"),
                title=item.get("title", f"Riesgo {idx}"),
                category=item.get("category"),
                probability=item.get("probability"),
                impact=item.get("impact"),
                mitigation=item.get("mitigation"),
                owner=item.get("owner"),
                raw_json=json.dumps(item, ensure_ascii=False),
            )
        )
    db.commit()


def get_analysis_result(db: Session, *, request_id: str) -> Optional[Dict[str, Any]]:
    record = db.query(AnalysisResult).filter(AnalysisResult.request_id == request_id).first()
    if not record:
        return None
    raw = record.result_json
    return json.loads(raw) if isinstance(raw, str) else raw


def sync_result_to_project(
    db: Session,
    *,
    project_id: int,
    request_id: str,
    result: Dict[str, Any],
    status: Optional[str] = None,
    execution_time_ms: Optional[int] = None,
    modules_executed: Optional[Any] = None,
    modules_failed: Optional[Any] = None,
) -> ProjectAgentOutput:
    payload = map_strategy_engine_result_to_project_payload(result, request_id=request_id)

    row = db.query(ProjectAgentOutput).filter(ProjectAgentOutput.project_id == project_id).first()
    if row:
        row.request_id = request_id
        row.metadata_ = payload.get("metadata")
        row.supervisor_output = json.dumps(payload["supervisor_output"], ensure_ascii=False) if payload.get("supervisor_output") else None
        row.business_model_canvas = payload.get("business_model_canvas")
        row.estrategia_comercial = payload.get("estrategia_comercial")
        row.roadmap_estrategico = payload.get("roadmap_estrategico")
        row.analisis_financiero = payload.get("analisis_financiero")
        row.analisis_riesgos = payload.get("analisis_riesgos")
        row.veredicto_final = payload.get("veredicto_final")
        row.plan_actividades = payload.get("plan_actividades")
        row.kanban_json = payload.get("kanban_json")
        row.gantt_json = payload.get("gantt_json")
        row.summary_json = payload.get("summary_json")
        row.status = status or result.get("status") or "completed"
        row.execution_time_ms = execution_time_ms
        row.modules_executed = json.dumps(modules_executed, ensure_ascii=False) if modules_executed is not None else None
        row.modules_failed = json.dumps(modules_failed, ensure_ascii=False) if modules_failed is not None else None
    else:
        row = ProjectAgentOutput(
            project_id=project_id,
            request_id=request_id,
            metadata_=payload.get("metadata"),
            supervisor_output=json.dumps(payload["supervisor_output"], ensure_ascii=False) if payload.get("supervisor_output") else None,
            business_model_canvas=payload.get("business_model_canvas"),
            estrategia_comercial=payload.get("estrategia_comercial"),
            roadmap_estrategico=payload.get("roadmap_estrategico"),
            analisis_financiero=payload.get("analisis_financiero"),
            analisis_riesgos=payload.get("analisis_riesgos"),
            veredicto_final=payload.get("veredicto_final"),
            plan_actividades=payload.get("plan_actividades"),
            kanban_json=payload.get("kanban_json"),
            gantt_json=payload.get("gantt_json"),
            summary_json=payload.get("summary_json"),
            status=status or result.get("status") or "completed",
            execution_time_ms=execution_time_ms,
            modules_executed=json.dumps(modules_executed, ensure_ascii=False) if modules_executed is not None else None,
            modules_failed=json.dumps(modules_failed, ensure_ascii=False) if modules_failed is not None else None,
        )
        db.add(row)

    db.commit()
    db.refresh(row)

    if payload.get("business_model_canvas"):
        sync_agent_bmc_to_canvas(project_id, payload["business_model_canvas"], db)

    sync_all_agent_sections(
        project_id,
        {
            "estrategia_comercial": payload.get("estrategia_comercial"),
            "roadmap_estrategico": payload.get("roadmap_estrategico"),
            "analisis_financiero": payload.get("analisis_financiero"),
            "analisis_riesgos": payload.get("analisis_riesgos"),
            "veredicto_final": payload.get("veredicto_final"),
        },
        db,
    )

    sync_project_activities_from_result(db, project_id=project_id, request_id=request_id, result=result)
    return row


def map_strategy_engine_result_to_project_payload(result: Dict[str, Any], *, request_id: str) -> Dict[str, Any]:
    market_analysis = result.get("market_analysis") or {}
    strategy = result.get("strategy") or {}
    finance = result.get("finance") or {}
    roadmap = result.get("roadmap") or {}
    verdict = result.get("verdict") or {}
    summary = result.get("summary") or {}
    gantt = result.get("gantt") or {}
    kanban = result.get("kanban") or {}
    risks = result.get("risks") or []
    activities = result.get("activities") or []
    bmc = result.get("bmc") or {}

    business_model_canvas = _map_bmc_to_spanish(bmc)

    estrategia_comercial = {
        "analisis_mercado": market_analysis,
        "estrategia_precios": strategy.get("pricing_strategy"),
        "estrategia_marketing": strategy.get("marketing_strategy") or {
            "recomendaciones": strategy.get("strategic_recommendations") or strategy.get("recommendations") or []
        },
        "estrategia_ventas": strategy.get("sales_strategy"),
        "swot": strategy.get("swot"),
        "objetivos_estrategicos": strategy.get("strategic_objectives") or [],
        "ventajas_competitivas": strategy.get("competitive_advantages") or [],
        "factores_criticos_exito": strategy.get("critical_success_factors") or [],
        "recomendaciones_estrategicas": strategy.get("strategic_recommendations") or strategy.get("recommendations") or [],
        "assumptions": strategy.get("assumptions") or [],
    }

    # cronograma_total_meses: sumar duration_weeks de fases si no viene
    phases = roadmap.get("phases") or []
    duration_months = roadmap.get("duration_months")
    if duration_months is None and phases:
        total_weeks = sum(p.get("duration_weeks") or 0 for p in phases)
        duration_months = round(total_weeks / 4.33) if total_weeks else None
    project_end_date = roadmap.get("project_end")
    if not project_end_date and gantt.get("tasks"):
        from datetime import datetime
        ends = [t.get("end") for t in gantt["tasks"] if t.get("end")]
        if ends:
            try:
                project_end_date = max(ends)[:10]
            except Exception:
                pass

    roadmap_estrategico = {
        "fases": phases,
        "cronograma_total_meses": duration_months,
        "milestones": roadmap.get("milestones") or [],
        "assumptions": roadmap.get("assumptions") or [],
        "project_start_date": roadmap.get("project_start") or gantt.get("project_start"),
        "project_end_date": project_end_date,
        "gantt_json": gantt,
    }

    # Finance: n8n envía assumptions y projection_summary como objetos anidados
    fin_assumptions = finance.get("assumptions") or {}
    fin_projection = finance.get("projection_summary") or {}
    if isinstance(fin_assumptions, list):
        fin_assumptions = {}
    if isinstance(fin_projection, list):
        fin_projection = {}

    # inversion_inicial en BD es JSON: objeto con assumptions o escalar legacy
    inv_inicial = fin_assumptions if isinstance(fin_assumptions, dict) and fin_assumptions else finance.get("initial_investment")

    analisis_financiero = {
        "inversion_inicial": inv_inicial,
        "proyecciones_3_anos": fin_projection if isinstance(fin_projection, dict) else finance.get("projection_summary"),
        "metricas_clave": fin_projection if isinstance(fin_projection, dict) else finance.get("projection_summary"),
        "viabilidad_financiera": finance.get("viability"),
        "costo_operativo_mensual": fin_assumptions.get("monthly_operating_cost") if isinstance(fin_assumptions, dict) else finance.get("monthly_operating_cost"),
        "modelo_ingresos": fin_assumptions.get("pricing_model") if isinstance(fin_assumptions, dict) else finance.get("revenue_model"),
        "ingreso_mensual_esperado": fin_assumptions.get("expected_monthly_revenue") if isinstance(fin_assumptions, dict) else finance.get("expected_revenue"),
        "margen_estimado": fin_projection.get("estimated_margin") if isinstance(fin_projection, dict) else finance.get("estimated_margin"),
        "payback_meses": fin_projection.get("payback_months") if isinstance(fin_projection, dict) else finance.get("payback_months"),
        "observaciones": finance.get("financial_observations") or [],
    }

    analisis_riesgos = {
        "nivel_riesgo_general": result.get("meta", {}).get("risk_level"),
        "recomendaciones": verdict.get("conditions_to_proceed") or [],
        "assumptions": [],
        "riesgos_identificados": [
            {
                "risk_code": item.get("risk_id"),
                "categoria": item.get("category"),
                "riesgo": item.get("title"),
                "probabilidad": item.get("probability"),
                "impacto": item.get("impact"),
                "mitigacion": item.get("mitigation"),
                "owner": item.get("owner"),
                "source_request_id": request_id,
            }
            for item in risks
        ],
    }

    veredicto_final = {
        "decision": verdict.get("decision"),
        "confidence": verdict.get("confidence"),
        "puntuacion_general": verdict.get("score"),
        "fortalezas": verdict.get("strengths") or [],
        "debilidades": verdict.get("weaknesses") or [],
        "recomendacion_estrategica": verdict.get("strategic_recommendation"),
        "siguiente_paso": verdict.get("next_step"),
        "reasons": verdict.get("reasons") or [],
        "conditions_to_proceed": verdict.get("conditions_to_proceed") or [],
        "executive_summary": verdict.get("executive_summary") or summary.get("executive_summary"),
    }

    plan_actividades = {
        "activities": activities,
        "kanban": kanban,
        "gantt": gantt,
        "summary": summary,
    }

    return {
        "metadata": {
            "request_id": request_id,
            "workflow_version": result.get("workflow_version"),
            "status": result.get("status"),
            "meta": result.get("meta") or {},
            "supervisor": result.get("supervisor") or {},
            "source": "ai_strategy_engine",
        },
        "business_model_canvas": business_model_canvas,
        "estrategia_comercial": estrategia_comercial,
        "roadmap_estrategico": roadmap_estrategico,
        "analisis_financiero": analisis_financiero,
        "analisis_riesgos": analisis_riesgos,
        "veredicto_final": veredicto_final,
        "plan_actividades": plan_actividades,
        "kanban_json": kanban,
        "gantt_json": gantt,
        "summary_json": summary,
        "supervisor_output": result.get("supervisor"),
    }


def _map_bmc_to_spanish(bmc: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "segmentos_clientes": bmc.get("customer_segments") or [],
        "propuesta_valor": bmc.get("value_propositions") or [],
        "canales": bmc.get("channels") or [],
        "relacion_clientes": bmc.get("customer_relationships") or [],
        "fuentes_ingresos": bmc.get("revenue_streams") or [],
        "recursos_clave": bmc.get("key_resources") or [],
        "actividades_clave": bmc.get("key_activities") or [],
        "alianzas_clave": bmc.get("key_partners") or [],
        "estructura_costos": bmc.get("cost_structure") or [],
    }


def _safe_date(value: Any):
    if not value or not isinstance(value, str):
        return None
    try:
        from datetime import date

        return date.fromisoformat(value[:10])
    except Exception:
        return None


def _safe_datetime(value: Any):
    """Parsea string ISO a datetime para project_activities.start_date/due_date."""
    if not value or not isinstance(value, str):
        return None
    try:
        from datetime import datetime

        s = value[:19] if len(value) > 10 else value[:10] + " 00:00:00"
        return datetime.fromisoformat(s.replace(" ", "T"))
    except Exception:
        return None


def sync_project_activities_from_result(
    db: Session,
    *,
    project_id: int,
    request_id: str,
    result: Dict[str, Any],
) -> None:
    """
    Crea o actualiza project_activities desde body.activities y fechas en gantt.tasks.
    Usa las columnas del modelo ProjectActivity (title, description, status, priority, start_date, due_date).
    """
    activities = result.get("activities") or []
    gantt = result.get("gantt") or {}
    gantt_tasks = gantt.get("tasks") or []
    gantt_by_id = {t["id"]: t for t in gantt_tasks if t.get("id")}

    from datetime import datetime, timedelta
    base = datetime.utcnow()

    for idx, act in enumerate(activities):
        aid = act.get("activity_id") or f"A{idx + 1}"
        g = gantt_by_id.get(aid) or {}
        start_dt = _safe_datetime(g.get("start")) or base + timedelta(days=idx)
        end_dt = _safe_datetime(g.get("end")) or start_dt + timedelta(days=act.get("estimated_days") or 1)

        existing = (
            db.query(ProjectActivity)
            .filter(
                ProjectActivity.project_id == project_id,
                ProjectActivity.title == (act.get("title") or ""),
            )
            .first()
        )
        if existing:
            existing.description = act.get("description")
            existing.status = (act.get("kanban_status") or "todo").replace("in_progress", "in-progress")
            existing.priority = (act.get("priority") or "medium").lower()
            existing.start_date = start_dt
            existing.due_date = end_dt
        else:
            db.add(
                ProjectActivity(
                    project_id=project_id,
                    title=act.get("title") or f"Actividad {idx + 1}",
                    description=act.get("description"),
                    status=(act.get("kanban_status") or "todo").replace("in_progress", "in-progress"),
                    priority=(act.get("priority") or "medium").lower(),
                    start_date=start_dt,
                    due_date=end_dt,
                )
            )
    db.commit()


def _to_decimal(value: Any):
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except Exception:
        return None


def persist_n8n_response(
    db: Session,
    body: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Persiste en BD todo el resultado del workflow n8n (body ya extraído).
    Crea o actualiza analysis_requests, analysis_results, analysis_modules,
    analysis_activities, analysis_risks; si hay project_id (en analysis_request
    o en body), sincroniza project_agent_output y tablas canónicas.
    """
    request_id = (body.get("request_id") or "").strip()
    if not request_id:
        return {"ok": False, "error": "request_id requerido en el body"}

    project_name = body.get("project_name") or "Sin nombre"
    workflow_version = body.get("workflow_version") or "v1"
    status = body.get("status") or "completed"
    meta = body.get("meta") or {}
    execution_time_ms = meta.get("execution_time_ms")
    if execution_time_ms is None and meta.get("completed_at") and meta.get("created_at"):
        # Calcular aprox si no viene
        try:
            from datetime import datetime
            end = datetime.fromisoformat(meta["completed_at"].replace("Z", "+00:00"))
            start = datetime.fromisoformat(meta["created_at"].replace("Z", "+00:00"))
            execution_time_ms = int((end - start).total_seconds() * 1000)
        except Exception:
            pass
    modules_executed = meta.get("modules_executed")
    modules_failed = meta.get("modules_failed")

    # project_id opcional: body.project_id o body.input.project_id (para callback sin request previo)
    input_data = body.get("input") or body
    input_dict = input_data if isinstance(input_data, dict) else {}
    optional_project_id = body.get("project_id") or input_dict.get("project_id")

    ar = db.query(AnalysisRequest).filter(AnalysisRequest.request_id == request_id).first()
    if not ar:
        org = input_dict.get("organization") or {}
        org_name = org.get("name") if isinstance(org, dict) else None
        create_analysis_request(
            db,
            request_id=request_id,
            project_id=int(optional_project_id) if optional_project_id is not None else None,
            project_name=project_name,
            analysis_type=body.get("analysis_type") or input_dict.get("analysis_type"),
            language_code=body.get("language") or "es",
            organization_name=org_name,
            input_payload=body.get("input") or body,
            workflow_version=workflow_version,
        )
        ar = db.query(AnalysisRequest).filter(AnalysisRequest.request_id == request_id).first()

    if ar:
        ar.status = status
        db.commit()

    save_analysis_result(db, request_id=request_id, result=body)
    save_analysis_modules(db, request_id=request_id, result=body)
    gantt = body.get("gantt") or {}
    replace_analysis_activities(
        db,
        request_id=request_id,
        activities=body.get("activities") or [],
        gantt_tasks=gantt.get("tasks"),
    )
    replace_analysis_risks(db, request_id=request_id, risks=body.get("risks") or [])

    project_id = ar.project_id if ar else None
    if project_id is None and optional_project_id is not None:
        project_id = optional_project_id
    if project_id is not None:
        sync_result_to_project(
            db,
            project_id=int(project_id),
            request_id=request_id,
            result=body,
            status=status,
            execution_time_ms=execution_time_ms,
            modules_executed=modules_executed,
            modules_failed=modules_failed,
        )

    return {
        "ok": True,
        "request_id": request_id,
        "status": status,
        "project_id": int(project_id) if project_id is not None else None,
    }
