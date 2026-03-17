from sqlalchemy.orm import Session

from app.db.models import AnalysisRequest


class AnalysisRequestRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> AnalysisRequest:
        obj = AnalysisRequest(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_by_request_id(self, request_id: str) -> AnalysisRequest | None:
        return (
            self.db.query(AnalysisRequest)
            .filter(AnalysisRequest.request_id == request_id)
            .first()
        )

    def update_status(
        self,
        request: AnalysisRequest,
        *,
        status: str | None = None,
        progress: int | None = None,
        current_stage: str | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
        workflow_version: str | None = None,
        engine_version: str | None = None,
        completed_at=None,
    ) -> AnalysisRequest:
        if status is not None:
            request.status = status
        if progress is not None:
            request.progress = progress
        if current_stage is not None:
            request.current_stage = current_stage
        if error_code is not None:
            request.error_code = error_code
        if error_message is not None:
            request.error_message = error_message
        if workflow_version is not None:
            request.workflow_version = workflow_version
        if engine_version is not None:
            request.engine_version = engine_version
        if completed_at is not None:
            request.completed_at = completed_at

        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request
