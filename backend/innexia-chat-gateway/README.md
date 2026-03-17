# Innexia Chat Gateway

Esqueleto FastAPI para un gateway asíncrono de chat/análisis conectado a n8n y MySQL.

## Ejecutar

1. Copia `.env.example` a `.env`
2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecuta:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Endpoints

- `POST /api/v1/chat/submit`
- `GET /api/v1/chat/status/{request_id}`
- `GET /api/v1/chat/result/{request_id}`
- `POST /api/v1/callbacks/strategy`
