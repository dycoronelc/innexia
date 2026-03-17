from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.models.analysis import (
    AnalysisActivity,
    AnalysisModule,
    AnalysisRequest,
    AnalysisResult,
    AnalysisRisk,
)


def create_analysis_request(
    db: Session,
    *,
    request_id: str,
    project_name: str,
    analysis_type: str | None,
    organization_name: str | None,
    input_payload: dict[str, Any],
    workflow_version: str,
    created_by: str | None = None,
) -> AnalysisRequest:
    record = AnalysisRequest(
        request_id=request_id,
        project_name=project_name,
        analysis_type=analysis_type,
        organization_name=organization_name,
        input_json=json.dumps(input_payload, ensure_ascii=False),
        status="running",
        workflow_version=workflow_version,
        created_by=created_by,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def mark_analysis_completed(
    db: Session,
    *,
    request_id: str,
    execution_time_ms: int | None = None,
) -> None:
    record = db.query(AnalysisRequest).filter(AnalysisRequest.request_id == request_id).first()
    if record:
        record.status = "completed"
        record.execution_time_ms = execution_time_ms
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


def save_analysis_result(db: Session, *, request_id: str, result: dict[str, Any]) -> AnalysisResult:
    summary = result.get("summary", {}) or {}
    verdict = result.get("verdict", {}) or {}

    existing = db.query(AnalysisResult).filter(AnalysisResult.request_id == request_id).first()
    if existing:
        existing.consolidated_json = json.dumps(result, ensure_ascii=False)
        existing.executive_summary = summary.get("executive_summary")
        existing.verdict_decision = verdict.get("decision")
        existing.confidence_score = _to_decimal(verdict.get("confidence"))
        db.commit()
        db.refresh(existing)
        return existing

    record = AnalysisResult(
        request_id=request_id,
        consolidated_json=json.dumps(result, ensure_ascii=False),
        executive_summary=summary.get("executive_summary"),
        verdict_decision=verdict.get("decision"),
        confidence_score=_to_decimal(verdict.get("confidence")),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def save_analysis_modules(db: Session, *, request_id: str, result: dict[str, Any]) -> None:
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


def replace_analysis_activities(db: Session, *, request_id: str, activities: list[dict[str, Any]]) -> None:
    db.query(AnalysisActivity).filter(AnalysisActivity.request_id == request_id).delete()

    for idx, item in enumerate(activities, start=1):
        db.add(
            AnalysisActivity(
                request_id=request_id,
                activity_id=item.get("activity_id", f"A{idx}"),
                epic=item.get("epic"),
                title=item.get("title", f"Actividad {idx}"),
                description=item.get("description"),
                priority=item.get("priority"),
                owner_role=item.get("owner_role"),
                estimated_days=item.get("estimated_days"),
                depends_on_json=json.dumps(item.get("depends_on", []), ensure_ascii=False),
                kanban_status=item.get("kanban_status", "todo"),
                phase_id=item.get("phase_id"),
                raw_json=json.dumps(item, ensure_ascii=False),
                sort_order=idx,
            )
        )
    db.commit()


def replace_analysis_risks(db: Session, *, request_id: str, risks: list[dict[str, Any]]) -> None:
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


def get_analysis_result(db: Session, *, request_id: str) -> dict[str, Any] | None:
    record = db.query(AnalysisResult).filter(AnalysisResult.request_id == request_id).first()
    if not record:
        return None
    return json.loads(record.consolidated_json)


def _to_decimal(value: Any):
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except Exception:
        return None
