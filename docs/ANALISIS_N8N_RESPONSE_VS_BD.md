# Análisis: n8nResponse.json vs innexia.sql

Este documento resume la comparación entre el JSON de respuesta del workflow n8n (`docs/n8nResponse.json`) y la estructura actual de la base de datos (`docs/innexia.sql`), y los cambios necesarios para persistir toda la información.

---

## 1. Estructura de la respuesta n8n

El archivo de ejemplo muestra que **n8n devuelve un array** con un solo elemento:

```json
[
  {
    "response": {
      "body": {
        "request_id": "REQ-...",
        "project_name": "...",
        "workflow_version": "v5.3",
        "status": "completed",
        "language": "es",
        "input": { ... },
        "supervisor": { ... },
        "market_analysis": { ... },
        "bmc": { ... },
        "strategy": { ... },
        "finance": { ... },
        "risks": [ ... ],
        "roadmap": { ... },
        "verdict": { ... },
        "activities": [ ... ],
        "kanban": { ... },
        "gantt": { ... },
        "summary": { ... },
        "meta": { ... }
      }
    }
  }
]
```

Por tanto, el backend debe **extraer el cuerpo útil** así:

- Si la respuesta es una **lista**, tomar el primer elemento: `data = response_json[0]`.
- Luego tomar el cuerpo: `body = data.get("response", {}).get("body") or data.get("body") or data`.
- Todo el mapeo a BD debe hacerse sobre `body`.

---

## 2. Tablas de BD involucradas y mapeo desde n8n

### 2.1 Tablas por `request_id` (analysis_*)

| Tabla | Origen en n8n | Comentario |
|-------|----------------|------------|
| **analysis_requests** | `body.request_id`, `body.project_name`, `body.workflow_version`, `body.status`, `body.language`, `body.input` | Ya existe. Asegurar que `input_json` guarde `body.input` completo. |
| **analysis_results** | `body` completo en `consolidated_json`; `body.summary.executive_summary`, `body.verdict` para campos escalares | `meta` en n8n no trae `market_score`, `viability_score`, `risk_score`; están en `verdict.confidence` y en summary. Valorar rellenar desde verdict/summary o dejar NULL. |
| **analysis_modules** | Por cada módulo: `supervisor`, `market_analysis`, `bmc`, `strategy`, `finance`, `risks`, `roadmap`, `verdict`, `activities`; opcionalmente `kanban` y `gantt` como módulos | n8n envía también `kanban` y `gantt`; se pueden persistir como módulos si se desea trazabilidad por módulo. |
| **analysis_activities** | `body.activities[]` | Cada ítem: `activity_id`, `epic`, `title`, `description`, `priority`, `owner_role`, `estimated_days`, `depends_on`, `kanban_status`, `phase_id`. Las fechas `start_date`/`end_date` vienen en **gantt.tasks[]** (por id de actividad). |
| **analysis_risks** | `body.risks[]` | `risk_id`, `title`, `category`, `probability`, `impact`, `mitigation`, `owner`. Coincide con la tabla. |

### 2.2 Tabla `project_agent_output`

En **innexia.sql** la tabla tiene más columnas que el modelo actual en código:

**Columnas en BD (innexia.sql):**

- `id`, `project_id`, `request_id`
- `metadata`, `supervisor_output`, `conversacion`
- `business_model_canvas`, `estrategia_comercial`, `roadmap_estrategico`, `analisis_financiero`, `analisis_riesgos`, `veredicto_final`, `plan_actividades`
- `kanban_json`, `gantt_json`, `summary_json`
- `status`, `execution_time_ms`, `modules_executed`, `modules_failed`
- `created_at`, `updated_at`

**Modelo actual (ProjectAgentOutput):**  
Faltan: `request_id`, `supervisor_output`, `conversacion`, `kanban_json`, `gantt_json`, `summary_json`, `status`, `execution_time_ms`, `modules_executed`, `modules_failed`.

**Mapeo desde n8n:**

- `request_id` ← `body.request_id`
- `metadata` ← objeto con `request_id`, `workflow_version`, `status`, `meta`, etc.
- `supervisor_output` ← `body.supervisor` (JSON)
- `conversacion` ← si n8n envía historial de chat, sino null
- `kanban_json` ← `body.kanban`
- `gantt_json` ← `body.gantt`
- `summary_json` ← `body.summary`
- `status` ← `body.status`
- `execution_time_ms` ← calcular o recibir desde `body.meta`
- `modules_executed` ← `body.meta.modules_executed` (array; guardar como JSON string o texto)
- `modules_failed` ← `body.meta.modules_failed`

### 2.3 Tablas canónicas por proyecto

#### business_model_canvases

- n8n: `body.bmc` con listas (customer_segments, value_propositions, channels, etc.).
- La BD tiene columnas por bloque (key_partners, key_activities, …).
- El mapeo actual en `_map_bmc_to_spanish` usa nombres en español; para la tabla canónica se rellenan los campos desde ese mapeo (ya implementado en sync con `sync_agent_bmc_to_canvas`). **Sin cambios de esquema**; asegurar que el origen sea siempre `body.bmc`.

#### project_estrategia_comercial

- n8n: `body.market_analysis` + `body.strategy` (swot, strategic_objectives, competitive_advantages, etc.).
- Mapeo actual en `map_strategy_engine_result_to_project_payload`:
  - `analisis_mercado` ← `market_analysis` completo.
  - `swot`, `objetivos_estrategicos`, `ventajas_competitivas`, etc. desde `strategy`.
- **Ajuste:** En n8n no existen `strategy.pricing_strategy`, `marketing_strategy`, `sales_strategy`; están en `finance.assumptions.pricing_model` y en textos de strategy. Habría que rellenar estrategia_precios / marketing / ventas desde lo que exista (por ejemplo resúmenes o dejarlos como null/objeto vacío).

#### project_analisis_financiero

- n8n: `body.finance` con:
  - `assumptions`: `initial_investment`, `monthly_operating_cost`, `pricing_model`, `expected_monthly_revenue`
  - `projection_summary`: `year_1_revenue`, `year_1_cost`, `estimated_margin`, `payback_months`
  - `financial_observations`: array de strings
- La BD tiene: `inversion_inicial`, `proyecciones_3_anos`, `metricas_clave` (JSON), más campos escalares.
- **Cambio necesario:** En `map_strategy_engine_result_to_project_payload` (y donde se construya el payload de análisis financiero):
  - `inversion_inicial`: guardar como JSON, por ejemplo `finance.assumptions` o `{ "initial_investment": finance.assumptions.initial_investment }`.
  - `proyecciones_3_anos`: `finance.projection_summary`.
  - `metricas_clave`: mismo objeto o derivado de projection_summary.
  - Escalares: `costo_operativo_mensual` ← `finance.assumptions.monthly_operating_cost`, `ingreso_mensual_esperado` ← `finance.assumptions.expected_monthly_revenue`, `modelo_ingresos` ← `finance.assumptions.pricing_model`, `margen_estimado` ← `finance.projection_summary.estimated_margin`, `payback_meses` ← `finance.projection_summary.payback_months`, `observaciones` ← `finance.financial_observations`.

#### project_analisis_riesgos / project_riesgo

- n8n: `body.risks[]` con risk_id, title, category, probability, impact, mitigation, owner.
- `sync_agent_analisis_riesgos` ya escribe en `project_analisis_riesgos` (cabecera) y en `project_riesgo` (filas).
- El payload actual incluye `riesgos_identificados` con `risk_code` (← risk_id), `riesgo` (← title), etc. **Compatible**; solo asegurar que el payload que llega a `sync_all_agent_sections` sea el que construye `map_strategy_engine_result_to_project_payload` para analisis_riesgos (con riesgos_identificados y nivel_riesgo_general si se tiene).

#### project_roadmap

- n8n: `body.roadmap` con `phases[]` (phase_id, name, duration_weeks, goals, deliverables, dependencies), `milestones`, `assumptions`; y `body.gantt` con `project_start` y `tasks[]`.
- Mapeo actual: `fases` ← roadmap.phases, `gantt_json` ← gantt.
- **Ajuste:** `cronograma_total_meses` no viene explícito; se puede calcular sumando `duration_weeks` de las fases y pasando a meses, o dejarlo null. `project_start_date` / `project_end_date` pueden tomarse de `gantt.project_start` y del último end de gantt.tasks.

#### project_veredicto

- n8n: `body.verdict` con `decision`, `confidence`, `reasons`, `conditions_to_proceed`, `executive_summary`.
- La BD tiene también `puntuacion_general`, `fortalezas`, `debilidades`, `recomendacion_estrategica`, `siguiente_paso`.
- **Ajuste:** `confidence` → columna `confidence`; `reasons` → `reasons`; `conditions_to_proceed` → `conditions_to_proceed`; `executive_summary` → `executive_summary`. Si n8n no envía fortalezas/debilidades/puntuacion_general, se pueden dejar null o rellenar desde `body.summary` si hay equivalencia.

#### project_activities

- n8n: `body.activities[]` y fechas en `body.gantt.tasks[]` (por activity id).
- La tabla tiene: activity_code, title, description, epic, status, priority, owner_role, estimated_days, depends_on_json, kanban_status, phase_id, start_date, due_date, source_request_id, ai_generated=1.
- **Falta:** Sincronizar actividades del resultado n8n a `project_activities` (insertar/actualizar por project_id y source_request_id). Hoy solo se persisten en `analysis_activities` y en `plan_actividades` (JSON). Sería necesario un paso que, al sincronizar a proyecto, también llene `project_activities` desde `body.activities` y fechas de `body.gantt.tasks`.

---

## 3. Resumen de cambios recomendados

### 3.1 Backend – Extracción de la respuesta n8n

- En el servicio que recibe la respuesta de n8n (p. ej. `strategy_engine_service`):
  - Si `response_data` es lista, usar `body = (response_data[0] if response_data else {}).get("response", {}).get("body")` o equivalente, y si no existe `response.body`, usar `data.get("body") or response_data[0]`.
  - Todo el flujo posterior (guardar en analysis_*, project_agent_output, canónicas) debe usar este `body` como “result”.

### 3.2 Backend – Modelo `ProjectAgentOutput`

- Añadir columnas (o alinear modelo con BD): `request_id`, `supervisor_output`, `conversacion`, `kanban_json`, `gantt_json`, `summary_json`, `status`, `execution_time_ms`, `modules_executed`, `modules_failed`.
- En la persistencia (p. ej. `sync_result_to_project`), rellenar estos campos desde `body` y desde el payload ya mapeado.

### 3.3 Backend – Persistencia en `project_agent_output`

- Escribir en la misma actualización/creación:
  - `request_id`, `metadata`, `supervisor_output`, `conversacion`
  - `business_model_canvas`, `estrategia_comercial`, `roadmap_estrategico`, `analisis_financiero`, `analisis_riesgos`, `veredicto_final`, `plan_actividades`
  - `kanban_json` = body.kanban, `gantt_json` = body.gantt, `summary_json` = body.summary
  - `status`, `execution_time_ms`, `modules_executed`, `modules_failed`

### 3.4 Backend – Mapeo de financiero

- En `map_strategy_engine_result_to_project_payload` (o donde se arme `analisis_financiero`):
  - Leer `finance.assumptions` y `finance.projection_summary`.
  - Asignar escalares como arriba (costo_operativo_mensual, ingreso_mensual_esperado, modelo_ingresos, margen_estimado, payback_meses, observaciones).
  - Asignar `inversion_inicial` y `proyecciones_3_anos` como JSON (objetos).

### 3.5 Backend – Roadmap

- Opcional: calcular `cronograma_total_meses` desde `roadmap.phases[].duration_weeks`.
- Rellenar `project_start_date` y `project_end_date` desde `gantt.project_start` y último `gantt.tasks[].end`.

### 3.6 Backend – Actividades en proyecto

- Añadir sincronización de `body.activities` (y fechas de gantt) a `project_activities`: crear/actualizar filas por project_id con `source_request_id` y `ai_generated=1`.

### 3.7 analysis_results – scores

- Si se desean `market_score`, `viability_score`, `risk_score` y n8n no los envía en `meta`, rellenar desde `verdict.confidence` o desde summary si hay campos equivalentes; si no, dejarlos en null.

### 3.8 analysis_activities – fechas

- Al guardar `analysis_activities`, enriquecer cada actividad con `start_date` y `end_date` buscando en `gantt.tasks` por `task.id === activity_id`.

---

## 4. Orden sugerido de implementación

1. **Extracción del body** desde la respuesta en array y `response.body`.
2. **Modelo ProjectAgentOutput**: añadir columnas faltantes y migración si aplica.
3. **Payload a project_agent_output**: incluir request_id, supervisor, kanban, gantt, summary, status, execution_time_ms, modules_executed/modules_failed.
4. **Mapeo de finance** (assumptions + projection_summary) a analisis_financiero y a project_analisis_financiero.
5. **Roadmap**: cronograma_total_meses y fechas desde gantt.
6. **Sincronización de project_activities** desde body.activities + gantt.tasks.
7. **analysis_activities**: rellenar start_date/end_date desde gantt.tasks.
8. (Opcional) **analysis_results**: rellenar market/viability/risk score desde verdict o summary.

Con estos cambios, toda la información relevante del `n8nResponse.json` quedará almacenada en la base de datos actual (`innexia.sql`) sin necesidad de nuevas tablas.

---

## 5. Endpoint para recibir el JSON de n8n

Se añadió el endpoint **`POST /api/strategy-engine/callback`** para que el workflow de n8n envíe el resultado completo y se actualicen todos los datos en la BD.

- **URL:** `POST /api/strategy-engine/callback`
- **Body:** El JSON tal como lo devuelve n8n (array `[{ "response": { "body": { ... } } }]` o objeto con `body`/`result`).
- **Respuesta:** `{ "ok": true, "request_id": "...", "status": "...", "project_id": ... }` o error 400/500.
- **Comportamiento:**
  1. Se extrae el `body` del payload (array + `response.body` o `body` o `result`).
  2. Se crea o actualiza `analysis_requests` (si no existía la request, se crea con `project_id` opcional).
  3. Se persisten `analysis_results`, `analysis_modules`, `analysis_activities`, `analysis_risks`.
  4. Si hay `project_id` (en la request previa o en `body.project_id` / `body.input.project_id`), se actualiza `project_agent_output` y las tablas canónicas (BMC, estrategia, roadmap, financiero, riesgos, veredicto, actividades).

**Uso desde n8n:** Configurar un nodo HTTP Request (POST) al final del workflow apuntando a `https://tu-backend/api/strategy-engine/callback`, con el body siendo la salida completa del flujo. Opcionalmente incluir `project_id` en el body o en `input` si el análisis no se inició desde la app.
