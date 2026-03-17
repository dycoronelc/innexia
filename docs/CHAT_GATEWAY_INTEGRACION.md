# Integración Chat Gateway (n8n)

El backend integra el flujo sugerido por **innexia-chat-gateway** para comunicarse con los workflows de n8n.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/chat/submit` | Envía mensaje, crea `analysis_request`, dispara n8n y devuelve `request_id`. |
| GET | `/api/v1/chat/status/{request_id}` | Estado de la solicitud (status, progress, current_stage, error). |
| GET | `/api/v1/chat/result/{request_id}` | Resultado consolidado del análisis (cuando esté listo). |
| POST | `/api/v1/callbacks/strategy` | Callback que n8n invoca al terminar (header `X-Callback-Token`). |

## Flujo

1. **Frontend/Cliente** → `POST /api/v1/chat/submit` con `message`, `project_id` (opcional), `callback_url` (opcional), etc.
2. **Backend** crea una fila en `analysis_requests` (status `running`), llama al webhook de n8n con `request_id`, `message`, `callback_url`, etc.
3. **n8n** ejecuta el workflow y al final hace `POST` a `callback_url` (o a `https://tu-backend/api/v1/callbacks/strategy`) con el body en formato **StrategyCallbackRequest**: `request_id`, `status`, `progress`, `current_stage`, `completed_at`, `result`, `error`, `metrics`, etc. Debe enviar el header **`X-Callback-Token`** = `CALLBACK_SHARED_TOKEN`.
4. **Backend** actualiza `analysis_requests` y `analysis_results`; si hay `project_id`, sincroniza a `project_agent_output` y tablas canónicas.
5. **Frontend** puede hacer polling a `GET /api/v1/chat/status/{request_id}` y luego `GET /api/v1/chat/result/{request_id}`.

## Variables de entorno

- **N8N_WEBHOOK_URL**: URL del webhook de n8n para el flujo chat (si no se define, se usa `N8N_STRATEGY_ENGINE_WEBHOOK_URL`).
- **CALLBACK_SHARED_TOKEN**: Token secreto que n8n debe enviar en el header `X-Callback-Token` al llamar a `/api/v1/callbacks/strategy`. Si no se configura, el callback no exige token (útil solo en desarrollo).

## Migración BD (opcional)

Para guardar `progress`, `current_stage`, `callback_url`, etc. en `analysis_requests`, ejecutar:

```bash
mysql -u usuario -p innexia < mysql/chat_gateway_columns.sql
```

Si alguna columna ya existe, comentar la línea correspondiente en el script.

## Formato del callback (StrategyCallbackRequest)

n8n debe enviar un JSON como:

```json
{
  "request_id": "req_20260110120000_abc123",
  "project_id": 1,
  "status": "completed",
  "progress": 100,
  "current_stage": "completed",
  "completed_at": "2026-01-10T12:05:00Z",
  "workflow_version": "v5.3",
  "result": {
    "executive_summary": "...",
    "market_analysis": { ... },
    "business_model_canvas": { ... },
    "strategy": { ... },
    "financials": { ... },
    "risks": [ ... ],
    "roadmap": { ... },
    "kanban": { ... },
    "gantt": { ... }
  },
  "metrics": { "tokens_input": 1000, "tokens_output": 500 },
  "error": null
}
```

El backend mapea `business_model_canvas` → `bmc`, `financials` → `finance` y sincroniza con las tablas canónicas del proyecto cuando existe `project_id`.

## Relación con el callback “full body”

- **`POST /api/strategy-engine/callback`**: Acepta el JSON completo que devuelve n8n (p. ej. array con `response.body`). No requiere token. Idóneo cuando n8n envía todo el body en un solo POST.
- **`POST /api/v1/callbacks/strategy`**: Acepta el formato **StrategyCallbackRequest** (status, progress, result, error). Requiere `X-Callback-Token` si está configurado. Idóneo para el flujo chat gateway.

Puedes usar uno u otro según cómo esté configurado el workflow en n8n.
