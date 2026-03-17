from sqlalchemy.orm import Session

from app.db.models import AnalysisResult


class AnalysisResultRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_request_id(self, request_id: str) -> AnalysisResult | None:
        return (
            self.db.query(AnalysisResult)
            .filter(AnalysisResult.request_id == request_id)
            .first()
        )

    def upsert(self, request_id: str, data: dict) -> AnalysisResult:
        obj = self.get_by_request_id(request_id)

        if obj is None:
            obj = AnalysisResult(request_id=request_id, **data)
            self.db.add(obj)
        else:
            for key, value in data.items():
                setattr(obj, key, value)
            self.db.add(obj)

        self.db.commit()
        self.db.refresh(obj)
        return obj
