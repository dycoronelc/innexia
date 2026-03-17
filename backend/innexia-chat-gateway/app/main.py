from fastapi import FastAPI

from app.api.v1.callbacks import router as callbacks_router
from app.api.v1.chat import router as chat_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.APP_DEBUG,
        version="1.0.0",
    )

    Base.metadata.create_all(bind=engine)

    app.include_router(chat_router)
    app.include_router(callbacks_router)

    @app.get("/")
    def healthcheck():
        return {
            "success": True,
            "app": settings.APP_NAME,
            "environment": settings.APP_ENV,
        }

    return app


app = create_app()
