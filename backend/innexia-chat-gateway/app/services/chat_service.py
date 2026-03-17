from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.analysis_request_repository import AnalysisRequestRepository
from app.repositories.analysis_result_repository import AnalysisResultRepository
from app.schemas.chat import ChatSubmitRequest
from app.services.n8n_service import N8NService
from app.utils.ids import generate_request_id


class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.request_repo = AnalysisRequestRepository(db)
        self.result_repo = AnalysisResultRepository(db)
        self.n8n_service = N8NService()

    async def submit_chat(self, payload: ChatSubmitRequest) -> str:
        request_id = generate_request_id()

        metadata = payload.metadata or {}
        session_id = metadata.get("session_id")

        request_data = {
            "request_id": request_id,
            "project_id": payload.project_id,
            "user_id": payload.user_id,
            "session_id": session_id,
            "organization_name": payload.organization_name,
            "analysis_type": payload.analysis_type,
            "language_code": payload.language_code,
            "input_message": payload.message,
            "input_json": payload.model_dump(),
            "status": "queued",
            "progress": 5,
            "current_stage": "queued",
            "callback_url": payload.callback_url,
        }

        self.request_repo.create(request_data)

        n8n_payload = {
            "request_id": request_id,
            "project_id": payload.project_id,
            "user_id": payload.user_id,
            "message": payload.message,
            "analysis_type": payload.analysis_type,
            "language_code": payload.language_code,
            "organization_name": payload.organization_name,
            "callback_url": payload.callback_url,
            "metadata": payload.metadata or {},
        }

        try:
            await self.n8n_service.trigger_strategy_workflow(n8n_payload)
        except Exception as exc:
            request = self.request_repo.get_by_request_id(request_id)
            if request:
                self.request_repo.update_status(
                    request,
                    status="failed",
                    progress=100,
                    current_stage="n8n_trigger_failed",
                    error_code="N8N_TRIGGER_ERROR",
                    error_message=str(exc),
                    completed_at=datetime.utcnow(),
                )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Could not trigger n8n workflow: {exc}",
            ) from exc

        request = self.request_repo.get_by_request_id(request_id)
        if request:
            self.request_repo.update_status(
                request,
                status="processing",
                progress=10,
                current_stage="workflow_triggered",
            )

        return request_id

    def get_status(self, request_id: str):
        request = self.request_repo.get_by_request_id(request_id)
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found",
            )
        return request

    def get_result(self, request_id: str):
        request = self.request_repo.get_by_request_id(request_id)
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found",
            )

        result = self.result_repo.get_by_request_id(request_id)
        return request, result
