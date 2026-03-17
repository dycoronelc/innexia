# Contrato Backend ↔ n8n (workflows docs/workflows)

Resumen de qué envía y qué recibe cada parte según los workflows en `docs/workflows` y el backend actual.

---

## 1. Flujos en n8n (resumen)

| Workflow | Rol | Entrada | Salida / Efecto |
|----------|-----|---------|------------------|
| **IASE_CHAT_TRIGGER_ASYNC_v2.3** | Chat nativo n8n | Mensaje del usuario (chat) | Resuelve intención, construye payload, llama al webhook async, responde al chat con `request_id` |
| **IASE_CHAT_WEBHOOK_ASYNC_v2.3** | Orquestador async | POST con payload estructurado | Responde 202 + `request_id`, ejecuta CORE, escribe MySQL, hace callback a FastAPI |
| **IASE_v5_HTTP_WRAPPER_v2.3** | API síncrona | POST con payload | Ejecuta CORE y devuelve resultado en la respuesta (sin callback) |
| **IASE_v5_CORE_v2.3** | Motor de análisis | Input normalizado (subworkflow) | `success`, `request_id`, `status`, `result`, `metrics`, `error` |

---

## 2. Qué envía el backend a n8n

### Caso A: App/FastAPI dispara el orquestador async (recomendado)

**URL:** `POST https://<N8N_HOST>/webhook/innexia-chat-submit-async-v2-3`

**Body (JSON) — contrato esperado por IASE_CHAT_WEBHOOK_ASYNC_v2.3:**

```json
{
  "request_id": "REQ-ABC123",
  "project_id": "1",
  "project_name": "Clinica Digital Panama",
  "analysis_type": "new_business",
  "language": "es",
  "organization": {
    "name": "Innexia",
    "industry": "tecnologia y salud",
    "country": "Panama"
  },
  "input_brief": {
    "title": "Clinica Digital Panama",
    "description": "Quiero lanzar una clínica digital en Panamá",
    "objective": "Validar y diseñar la estrategia",
    "problem_statement": "Existe oportunidad para servicios digitales de salud",
    "constraints": []
  },
  "execution_options": {
    "run_modules": ["market_intelligence", "bmc", "strategy", "finance", "risks", "roadmap", "verdict", "activities"],
    "generate_kanban": true,
    "generate_gantt": true,
    "persist_outputs": true,
    "strict_json": true
  },
  "chat_context": {
    "session_id": "SES-123",
    "user_id": "user_001",
    "project_id": "1",
    "original_message": "Quiero lanzar una clínica digital en Panamá"
  },
  "callback_url": "https://backend-production-8fc10.up.railway.app/api/v1/callbacks/strategy",
  "meta": {
    "workflow_version": "v2.3-chat-webhook-async",
    "source": "chat_trigger_gateway"
  }
}
```

- **request_id:** opcional; si no se envía, n8n lo genera.
- **project_id:** string o número; n8n lo reenvía en el callback.
- **callback_url:** opcional; si no se envía, n8n usa el fallback configurado (debe ser la URL de tu FastAPI).

**Respuesta inmediata (202):**

```json
{
  "success": true,
  "request_id": "REQ-ABC123",
  "status": "queued",
  "message": "Solicitud recibida y en proceso"
}
```

---

### Caso B: Llamada síncrona (HTTP Wrapper)

**URL:** `POST https://<N8N_HOST>/webhook/innexia-ai-strategic-analysis-v5-wrapper-v2-3`

**Body:** El mismo esquema que arriba (sin necesidad de `callback_url` si no quieres callback).

**Respuesta:** El resultado completo del CORE (síncrono): `success`, `request_id`, `status`, `result`, `metrics`, `error`.

---

## 3. Qué envía n8n al backend (callback)

Cuando el orquestador async termina (éxito o error), n8n hace:

**POST** a `callback_url` (ej. `https://backend-production-8fc10.up.railway.app/api/v1/callbacks/strategy`)

**Headers:**

- `X-Callback-Token`: valor de `CALLBACK_SHARED_TOKEN` (mismo que en Railway).
- `Content-Type`: `application/json`

**Body (formato StrategyCallbackRequest):**

```json
{
  "request_id": "REQ-ABC123",
  "project_id": "1",
  "status": "completed",
  "progress": 100,
  "current_stage": "completed",
  "completed_at": "2026-03-17T12:00:00.000Z",
  "engine_version": "IASE_v5_CORE_v2.3",
  "workflow_version": "v2.3-chat-webhook-async",
  "result": {
    "summary": {
      "executive_summary": "...",
      "key_findings": [],
      "priority_actions": []
    },
    "market_analysis": { ... },
    "business_model_canvas": { ... },
    "strategy": { ... },
    "financials": { ... },
    "risks": [ ... ],
    "roadmap": { ... },
    "kanban": { ... },
    "gantt": { ... }
  },
  "metrics": {
    "tokens_input": 1000,
    "tokens_output": 500,
    "total_duration_seconds": 120
  },
  "error": null
}
```

En caso de fallo, n8n envía algo como:

```json
{
  "request_id": "REQ-ABC123",
  "project_id": "1",
  "status": "failed",
  "progress": 100,
  "current_stage": "failed",
  "completed_at": "...",
  "result": null,
  "metrics": {},
  "error": {
    "code": "ENGINE_OUTPUT_INVALID",
    "message": "Strategy Engine Core returned an invalid response"
  }
}
```

El backend ya acepta este formato en `POST /api/v1/callbacks/strategy` y mapea `result.business_model_canvas` → bmc, `result.financials` → finance, etc.

---

## 3.1. Payload desde FastAPI (chat submit)

Cuando el backend recibe `POST /api/v1/chat/submit` con `message`, `project_id`, etc., construye y envía a n8n un payload en el formato esperado por **IASE_CHAT_WEBHOOK_ASYNC**:

- **request_id:** generado en backend.
- **project_id:** string (ej. `"1"`).
- **project_name:** derivado del mensaje o "Chat analysis".
- **input_brief:** `title` = project_name, `description` y `problem_statement` = mensaje del usuario.
- **execution_options:** módulos completos, `generate_kanban`/`generate_gantt` en true.
- **chat_context:** session_id, user_id, project_id, original_message.
- **callback_url:** la URL del backend para callbacks (ej. `https://.../api/v1/callbacks/strategy`).

Así n8n recibe siempre un body ya alineado con el contrato del webhook y el CORE tiene contexto suficiente.

---

## 4. Qué debe hacer el backend (resumen)

| Acción | Dónde | Detalle |
|--------|--------|---------|
| Disparar análisis async | Servicio que llame a n8n | POST al webhook `innexia-chat-submit-async-v2-3` con el payload de §2. Incluir `callback_url` = `https://backend-production-8fc10.up.railway.app/api/v1/callbacks/strategy`. |
| Recibir resultado | `POST /api/v1/callbacks/strategy` | Recibe el body de §3, valida `X-Callback-Token`, actualiza `analysis_requests` y `analysis_results`, y si hay `project_id` sincroniza a `project_agent_output` y tablas canónicas. |
| Consultar estado | `GET /api/v1/chat/status/{request_id}` | Devuelve status, progress, current_stage, error (n8n también escribe en MySQL; el backend puede leer de ahí o solo del callback). |
| Consultar resultado | `GET /api/v1/chat/result/{request_id}` | Devuelve el resultado consolidado (n8n escribe en `analysis_results`; el callback además actualiza/sincroniza en el backend). |

---

## 5. Placeholders en n8n a reemplazar

Según `README_IMPLEMENTACION_COMPLETA.md`:

- **IASE_CHAT_WEBHOOK_ASYNC_v2.3:**  
  `REPLACE_WITH_FASTAPI_HOST` → `backend-production-8fc10.up.railway.app` (con `https://`).  
  `REPLACE_WITH_CALLBACK_SHARED_TOKEN` → mismo valor que la variable `CALLBACK_SHARED_TOKEN` en Railway.

- **IASE_CHAT_TRIGGER_ASYNC_v2.3:**  
  `REPLACE_WITH_N8N_HOST` → host de tu n8n (ej. `innexia.app.n8n.cloud`).  
  `REPLACE_WITH_FASTAPI_HOST` → mismo que arriba.

Así n8n llamará a la URL correcta del API y enviará el token que el backend espera.

---

## 6. Tablas MySQL que usa n8n

- **analysis_requests:** n8n hace INSERT/UPDATE (queued → processing → completed/failed).
- **analysis_results:** n8n hace INSERT/UPDATE con `result_json`, `executive_summary`, columnas por módulo, tokens, etc.
- **callback_logs:** n8n escribe cada intento de callback.

El backend puede leer de `analysis_requests` y `analysis_results` (por ejemplo para status y result); el callback a FastAPI sirve para notificar y para que el backend sincronice a `project_agent_output` y tablas canónicas cuando exista `project_id`.
