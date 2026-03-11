from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os

# Configurar logging antes de importar otros módulos
from .logging_config import configure_logging
configure_logging()

from .config import settings
from .api import auth, users, projects, activities, business_model_canvas, documents, masters, company, audit_log, activity_trello, chatbot, guided_conversation, educational_content, official_documents, agent_memory, proactive_suggestions, data_analysis, conversation_state, business_interview, hybrid_chatbot, news_feed, project_agent_output
from .database import engine, Base

# Crear tablas
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="InnovAI API",
    description="API para gestión de proyectos y Business Model Canvas",
    version="1.0.0"
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Asegura que cualquier error no controlado devuelva JSON (CORS se aplica a la respuesta)."""
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor", "error": type(exc).__name__},
    )


# Configurar CORS (en producción CORS_ORIGINS debe incluir la URL del frontend, ej. https://frontend-xxx.up.railway.app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Montar archivos estáticos
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Incluir routers
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(users.router, prefix="/api/users", tags=["Usuarios"])
app.include_router(projects.router, prefix="/api/projects", tags=["Proyectos"])
app.include_router(activities.router, prefix="/api/activities", tags=["Actividades"])
app.include_router(business_model_canvas.router, prefix="/api/bmc", tags=["Business Model Canvas"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documentos"])
app.include_router(masters.router, prefix="/api/masters", tags=["Maestros"])
app.include_router(company.router, prefix="/api/company", tags=["Empresas"])
app.include_router(audit_log.router, prefix="/api/audit-log", tags=["Bitácoras"])
app.include_router(activity_trello.router, prefix="/api/activity-trello", tags=["Actividades Trello"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["ChatBot IA"])
app.include_router(guided_conversation.router, prefix="/api/guided-conversation", tags=["Conversación Guiada"])
app.include_router(educational_content.router, prefix="/api/educational-content", tags=["Contenido Educativo"])
app.include_router(official_documents.router, prefix="/api/official-documents", tags=["Documentos Oficiales"])

# Agent Intelligence System
app.include_router(agent_memory.router, tags=["Agent Memory"])
app.include_router(proactive_suggestions.router, prefix="/api/proactive-suggestions", tags=["Proactive Suggestions"])
app.include_router(data_analysis.router, prefix="/api/data-analysis", tags=["Data Analysis"])
app.include_router(conversation_state.router, prefix="/api/conversation-state", tags=["Conversation State"])

# Business Interview System
app.include_router(business_interview.router, tags=["Business Interview"])

# Hybrid Chatbot System
app.include_router(hybrid_chatbot.router, prefix="/api/hybrid-chatbot", tags=["Hybrid Chatbot"])

# News Feed System
app.include_router(news_feed.router, prefix="/api", tags=["News Feed"])

# Agent Output (n8n) - salida del agente por proyecto
app.include_router(project_agent_output.router, prefix="/api", tags=["Agent Output"])

@app.on_event("startup")
async def startup_log():
    print("CORS allow_origins:", settings.CORS_ORIGINS)

@app.get("/")
async def root():
    return {"message": "Bienvenido a InnovAI API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API funcionando correctamente"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )
