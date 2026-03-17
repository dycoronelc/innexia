from uuid import uuid4

from ..schemas.analysis_engine import OpportunityRequest


def build_engine_payload(data: OpportunityRequest) -> dict:
    request_id = f"REQ-{uuid4().hex[:16].upper()}"
    project_name = data.project_name or _infer_project_name(data.idea)

    payload = {
        "request_id": request_id,
        "project_name": project_name,
        "analysis_type": data.analysis_type,
        "language": data.language,
        "organization": {
            "name": data.organization,
        },
        "input_brief": {
            "title": project_name,
            "description": data.idea,
            "objective": "Evaluar viabilidad y diseñar estrategia de lanzamiento",
            "problem_statement": data.idea,
            "constraints": [],
        },
        "execution_options": {
            "run_modules": [
                "market_intelligence",
                "bmc",
                "strategy",
                "finance",
                "risks",
                "roadmap",
                "verdict",
                "activities",
            ],
            "generate_kanban": True,
            "generate_gantt": True,
            "persist_outputs": True,
        },
        "meta": {
            "workflow_version": "v5.2",
            "source": "api",
        },
    }

    if data.extra_context:
        payload["extra_context"] = data.extra_context

    return payload


def _infer_project_name(idea: str) -> str:
    idea = (idea or "").strip()
    return idea[:120] if idea else "Innexia Strategic Opportunity"
