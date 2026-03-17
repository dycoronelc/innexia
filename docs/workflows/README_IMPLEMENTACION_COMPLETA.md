# Innexia AI Strategy Engine v2.3 — Implementación completa

Este paquete deja separadas las responsabilidades en 4 workflows:

1. **IASE_v5_CORE_v2.3**
   - Núcleo del Strategy Engine.
   - Se ejecuta como subworkflow.
   - No conoce callbacks ni detalles del chat.

2. **IASE_v5_HTTP_WRAPPER_v2.3**
   - Wrapper HTTP del Core.
   - Conserva compatibilidad con llamadas `POST` externas.

3. **IASE_CHAT_WEBHOOK_ASYNC_v2.3**
   - Orquestador asíncrono para app/FastAPI o para ser invocado por el chat.
   - Inserta `analysis_requests`, responde `202` rápido, ejecuta el Core, guarda resultados, hace callback y registra logs.

4. **IASE_CHAT_TRIGGER_ASYNC_v2.3**
   - Fachada para el chat nativo de n8n.
   - Resuelve intención/contexto con el agente, dispara el workflow async por webhook y responde al chat inmediatamente con el `request_id`.

---

## Flujo recomendado en producción

### Caso A. Usuario conversa en el chat de n8n

`Chat Trigger -> intent resolver -> build engine payload -> POST a IASE_CHAT_WEBHOOK_ASYNC_v2.3 -> respuesta inmediata al chat`

Luego el workflow webhook continúa en segundo plano:

`queue -> core -> MySQL -> callback -> logs`

### Caso B. Aplicación / FastAPI envía una solicitud directa

`App/FastAPI -> POST a IASE_CHAT_WEBHOOK_ASYNC_v2.3`

Ese flujo ya responde `202` inmediato y continúa el procesamiento.

### Caso C. Otro sistema quiere invocar el engine como API sin orquestación async

`POST -> IASE_v5_HTTP_WRAPPER_v2.3 -> IASE_v5_CORE_v2.3`

---

## Orden de importación en n8n

Importa en este orden:

1. `IASE_v5_CORE_v2.3.json`
2. `IASE_v5_HTTP_WRAPPER_v2.3.json`
3. `IASE_CHAT_WEBHOOK_ASYNC_v2.3.json`
4. `IASE_CHAT_TRIGGER_ASYNC_v2.3.json`

Después de importar, guarda cada workflow una vez para que n8n refresque referencias internas.

---

## Placeholders que debes reemplazar

### En `IASE_CHAT_WEBHOOK_ASYNC_v2.3`
- `REPLACE_WITH_CORE_WORKFLOW_ID`
- `REPLACE_WITH_MYSQL_CREDENTIAL_ID`
- `REPLACE_WITH_FASTAPI_HOST`
- `REPLACE_WITH_CALLBACK_SHARED_TOKEN`

### En `IASE_CHAT_TRIGGER_ASYNC_v2.3`
- `REPLACE_WITH_N8N_HOST`
- `REPLACE_WITH_FASTAPI_HOST`

### En `IASE_v5_HTTP_WRAPPER_v2.3`
- `REPLACE_WITH_FASTAPI_HOST`
- `REPLACE_WITH_CORE_WORKFLOW_ID` si aún no quedó resuelto al importar

---

## Credenciales necesarias

### 1. MySQL
Nombre esperado en los nodos:
- `MySQL Innexia`

### 2. OpenAI
El workflow `IASE_CHAT_TRIGGER_ASYNC_v2.3` reutiliza el mismo nodo de modelo/agent que ya usabas. Revisa que siga apuntando a la credencial correcta.

### 3. Callback token
Tu FastAPI debe validar el header `X-Callback-Token`.

**Qué poner en `REPLACE_WITH_CALLBACK_SHARED_TOKEN`:**  
Debes usar **exactamente el mismo valor** que tienes en el backend como variable de entorno `CALLBACK_SHARED_TOKEN` (por ejemplo en Railway). Ese es el secreto que n8n envía en el header `X-Callback-Token` y el backend lo compara para aceptar o rechazar el callback.  
- Opción recomendada en n8n: crear una variable de entorno o credencial en n8n con ese valor y en el nodo usar algo como `{{ $env.CALLBACK_SHARED_TOKEN }}` en lugar de escribir el token en el código del workflow.  
- Si lo dejas como texto literal, sustituye `'REPLACE_WITH_CALLBACK_SHARED_TOKEN'` por tu token real (ej. una contraseña larga y aleatoria) tanto en **Build Success Callback Payload** como en **Build Failure Payload**.

---

## De dónde salen `callback_url` y `callback_token` en el flujo

En los nodos **HTTP Callback Success** y **HTTP Callback Failed** se usan `{{ $json.callback_url }}` y `{{ $json.callback_token }}`. Esos valores vienen del nodo **anterior** en cada rama:

| Nodo HTTP        | Nodo anterior que genera `$json` | Origen de `callback_url` | Origen de `callback_token` |
|------------------|----------------------------------|---------------------------|----------------------------|
| HTTP Callback Success | **Build Success Callback Payload** | `input.callback_url` (del nodo **Normalize Async Input**) | Literal en el código: `'REPLACE_WITH_CALLBACK_SHARED_TOKEN'` (debes reemplazarlo por tu token real o por una expresión que lea credencial/variable de n8n) |
| HTTP Callback Failed   | **Build Failure Payload**        | Igual: `input.callback_url` desde **Normalize Async Input** | Igual: literal en el código del nodo (reemplazar igual que arriba) |

**Cadena de `callback_url`:**  
1. El **Webhook** recibe el POST con el body (donde el cliente puede enviar `callback_url` o `callbackUrl`).  
2. **Normalize Async Input** lee ese body y define `callbackUrl = src.callback_url || src.callbackUrl || src.meta?.callback_url || 'https://REPLACE_WITH_FASTAPI_HOST/api/v1/callbacks/strategy'` y lo incluye en el objeto que devuelve (`callback_url`).  
3. Más adelante, **Build Success Callback Payload** y **Build Failure Payload** hacen `const input = $('Normalize Async Input').first().json` y ponen `callback_url: input.callback_url` en su salida.  
4. Los nodos **HTTP Callback Success** y **HTTP Callback Failed** reciben esa salida como `$json`, por eso `{{ $json.callback_url }}` es la URL del callback (la que envió el cliente o el fallback con REPLACE_WITH_FASTAPI_HOST).

Resumen: **callback_url** lo define el primer nodo del flujo a partir del request; **callback_token** lo defines tú reemplazando `REPLACE_WITH_CALLBACK_SHARED_TOKEN` en los dos nodos de “Build … Payload”.

---

## URLs que debes decidir

### URL del webhook async
`https://REPLACE_WITH_N8N_HOST/webhook/innexia-chat-submit-async-v2-3`

### URL del callback FastAPI
`https://REPLACE_WITH_FASTAPI_HOST/api/v1/callbacks/strategy`

---

## Cómo queda `callback_url`

En esta versión ya no se intenta deducir desde la salida del Core.
Ahora queda definido explícitamente:
- desde el input entrante si viene `callback_url` o `callbackUrl`
- o usando el fallback por defecto a FastAPI

---

## Contrato esperado por `IASE_CHAT_WEBHOOK_ASYNC_v2.3`

```json
{
  "request_id": "REQ-ABC123",
  "project_id": "proj_001",
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
    "project_id": "proj_001",
    "original_message": "Quiero lanzar una clínica digital en Panamá"
  },
  "callback_url": "https://api.innexia.ai/api/v1/callbacks/strategy",
  "meta": {
    "workflow_version": "v2.3-chat-trigger-async",
    "source": "chat_trigger_gateway"
  }
}
```

Respuesta inmediata esperada:

```json
{
  "success": true,
  "request_id": "REQ-ABC123",
  "status": "queued",
  "message": "Solicitud recibida y en proceso"
}
```

---

## Qué hace cada workflow

### `IASE_v5_CORE_v2.3`
- recibe input ya normalizado por subworkflow
- corre supervisor y módulos estratégicos
- consolida el resultado
- devuelve `success`, `request_id`, `status`, `result`, `metrics`, `error`

### `IASE_v5_HTTP_WRAPPER_v2.3`
- recibe `POST`
- normaliza input HTTP
- llama al Core por subworkflow
- devuelve resultado síncrono

### `IASE_CHAT_WEBHOOK_ASYNC_v2.3`
- recibe una solicitud ya estructurada
- escribe/upserta `analysis_requests` como `queued`
- devuelve `202` rápido
- marca `processing`
- ejecuta el Core
- guarda `analysis_results`
- marca `completed` o `failed`
- hace callback a FastAPI
- escribe `callback_logs`

### `IASE_CHAT_TRIGGER_ASYNC_v2.3`
- conserva el `Chat Trigger`
- mantiene el agente de intención/contexto
- decide si hay suficiente información o si debe pedir follow-up
- cuando sí hay contexto suficiente:
  - construye payload
  - dispara el workflow async por webhook
  - responde al chat de inmediato con mensaje de cola + `request_id`

---

## Tablas esperadas

- `analysis_requests`
- `analysis_results`
- `callback_logs`

Asegúrate de que existan las columnas de estado/progreso/callback que definimos antes.

---

## Secuencia de prueba recomendada

### Prueba 1 — Core solo
1. Ejecuta `IASE_v5_HTTP_WRAPPER_v2.3`
2. Manda un payload simple desde Postman
3. Verifica que el Core responda bien

### Prueba 2 — Orquestador webhook async
1. Ejecuta `IASE_CHAT_WEBHOOK_ASYNC_v2.3`
2. Envía un payload estructurado
3. Debe responder de inmediato con `queued`
4. Revisa en MySQL `analysis_requests`, `analysis_results` y `callback_logs`

### Prueba 3 — Chat trigger
1. Habla con `IASE_CHAT_TRIGGER_ASYNC_v2.3`
2. Usa un prompt como `Quiero lanzar una clínica digital en Panamá`
3. Debe responderte con mensaje tipo cola y `request_id`
4. Revisa que el webhook async haya recibido la solicitud

---

## Ajustes recomendados antes de producción

1. Agregar reintentos de callback
2. Reemplazar token simple por HMAC
3. Agregar notificación al frontend
4. Agregar observabilidad por módulo
