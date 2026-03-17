# Innexia AI Strategy Engine - FastAPI Backend Skeleton

Backend base para integrar:

- FastAPI
- MySQL
- n8n webhook
- AI Strategy Engine
- persistencia en tablas:
  - analysis_requests
  - analysis_results
  - analysis_modules
  - analysis_activities
  - analysis_risks

## Flujo

1. El frontend envía una idea a `POST /api/analyze-opportunity`
2. El backend crea un `request_id`
3. Guarda el request en `analysis_requests`
4. Invoca el webhook de n8n
5. Recibe el JSON consolidado del AI Strategy Engine
6. Guarda:
   - resultado consolidado
   - módulos
   - actividades
   - riesgos
7. Devuelve la respuesta al frontend

## Endpoints

- `POST /api/analyze-opportunity`
- `GET /api/analysis/{request_id}`
- `GET /health`

## Variables de entorno

Revisar `.env.example`

## Ejecución local

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# o .venv\Scripts\activate en Windows

pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Notas
- El proyecto usa SQLAlchemy 2.x
- La llamada a n8n asume respuesta síncrona del webhook
- Si deseas modo asíncrono, puedes cambiar el servicio `strategy_engine_service.py`
- Puedes pedirle a Cursor que compare este esqueleto con tu backend actual y fusione rutas, modelos y servicios
