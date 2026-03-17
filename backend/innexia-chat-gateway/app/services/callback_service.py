from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.analysis_request_repository import AnalysisRequestRepository
from app.repositories.analysis_result_repository import AnalysisResultRepository
from app.schemas.callback import StrategyCallbackRequest


class CallbackService:
    def __init__(self, db: Session):
        self.db = db
        self.request_repo = AnalysisRequestRepository(db)
        self.result_repo = AnalysisResultRepository(db)

    def process_strategy_callback(self, payload: StrategyCallbackRequest) -> None:
        request = self.request_repo.get_by_request_id(payload.request_id)
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found",
            )

        completed_at = None
        if payload.completed_at:
            try:
                completed_at = datetime.fromisoformat(payload.completed_at.replace("Z", "+00:00")).replace(tzinfo=None)
            except Exception:
                completed_at = datetime.utcnow()

        error_code = None
        error_message = None

        if payload.error:
            error_code = payload.error.get("code")
            error_message = payload.error.get("message")

        self.request_repo.update_status(
            request,
            status=payload.status,
            progress=payload.progress if payload.progress is not None else request.progress,
            current_stage=payload.current_stage if payload.current_stage is not None else request.current_stage,
            error_code=error_code,
            error_message=error_message,
            workflow_version=payload.workflow_version,
            engine_version=payload.engine_version,
            completed_at=completed_at,
        )

        if payload.result:
            metrics = payload.metrics or {}

            result_data = {
                "result_json": payload.result,
                "executive_summary": payload.result.get("executive_summary"),
                "market_analysis_json": payload.result.get("market_analysis"),
                "bmc_json": payload.result.get("business_model_canvas"),
                "strategy_json": payload.result.get("strategy"),
                "financial_json": payload.result.get("financials"),
                "risks_json": payload.result.get("risks"),
                "roadmap_json": payload.result.get("roadmap"),
                "kanban_json": payload.result.get("kanban"),
                "gantt_json": payload.result.get("gantt"),
                "tokens_input": metrics.get("tokens_input"),
                "tokens_output": metrics.get("tokens_output"),
                "total_duration_seconds": metrics.get("total_duration_seconds"),
            }

            self.result_repo.upsert(payload.request_id, result_data)
