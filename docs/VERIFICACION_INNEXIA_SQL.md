# Verificación: innexia.sql vs código backend

Este documento resume la comparación entre el esquema de `mysql/innexia.sql` (estructura sugerida para guardar lo que viene de n8n) y el código del backend, y los cambios aplicados para alinearlos.

## Tablas canónicas (n8n / agente)

Las siguientes tablas son la fuente única para visualización y edición; `project_agent_output` conserva el JSON crudo como auditoría.

### 1. project_estrategia_comercial

| innexia.sql | Modelo antes | Cambio en código |
|-------------|--------------|-------------------|
| analisis_mercado, estrategia_precios, estrategia_marketing, estrategia_ventas | ✅ | - |
| swot, objetivos_estrategicos, ventajas_competitivas, factores_criticos_exito, recomendaciones_estrategicas, assumptions | ❌ | **Añadidos** al modelo y al sync / get_merged_sections |

### 2. project_roadmap

| innexia.sql | Modelo antes | Cambio en código |
|-------------|--------------|-------------------|
| cronograma_total_meses, fases | ✅ | - |
| milestones, assumptions, project_start_date, project_end_date, gantt_json | ❌ | **Añadidos** al modelo; fechas parseadas desde string ISO en sync; get_merged_sections devuelve fechas en ISO |

### 3. project_analisis_financiero

| innexia.sql | Modelo antes | Cambio en código |
|-------------|--------------|-------------------|
| inversion_inicial, proyecciones_3_anos, metricas_clave, viabilidad_financiera | ✅ | - |
| costo_operativo_mensual, modelo_ingresos, ingreso_mensual_esperado, margen_estimado, payback_meses, observaciones | ❌ | **Añadidos** al modelo y al sync / get_merged_sections |

### 4. project_analisis_riesgos

| innexia.sql | Modelo antes | Cambio en código |
|-------------|--------------|-------------------|
| nivel_riesgo_general, recomendaciones | ✅ | - |
| assumptions | ❌ | **Añadido** al modelo y al sync / get_merged_sections |

### 5. project_riesgo

| innexia.sql | Modelo antes | Cambio en código |
|-------------|--------------|-------------------|
| categoria, riesgo, probabilidad, impacto, mitigacion, orden | ✅ | - |
| risk_code (UNIQUE con project_id), owner, source_request_id | ❌ | **Añadidos** al modelo; en sync se usa `risk_code` del agente o se genera R1, R2, … |

### 6. project_veredicto

| innexia.sql | Modelo antes | Cambio en código |
|-------------|--------------|-------------------|
| decision, puntuacion_general, fortalezas, debilidades, recomendacion_estrategica, siguiente_paso | ✅ | - |
| confidence, reasons, conditions_to_proceed, executive_summary | ❌ | **Añadidos** al modelo y al sync / get_merged_sections |

---

## Cambios realizados en el código

1. **Modelos** (`backend/app/models/`):  
   Se añadieron las columnas anteriores en  
   `project_analisis_financiero.py`, `project_analisis_riesgos.py`,  
   `project_estrategia_comercial.py`, `project_roadmap.py`,  
   `project_veredicto.py` y en la clase `ProjectRiesgo` de  
   `project_analisis_riesgos.py`.

2. **Sync** (`backend/app/services/agent_sections_sync.py`):  
   - Todas las funciones `sync_agent_*` actualizan y crean filas con los nuevos campos.  
   - En riesgos, se usa `risk_code` del payload o se genera `R1`, `R2`, … para cumplir con `UNIQUE(project_id, risk_code)` de innexia.sql.  
   - Fechas de roadmap: helper `_parse_date()` para convertir strings ISO a `date` antes de guardar.

3. **get_merged_sections**:  
   Devuelve los nuevos campos en cada sección (estrategia, roadmap, análisis financiero, análisis riesgos con risk_code/owner/source_request_id en cada riesgo, veredicto).

4. **API**:  
   Los PUT por sección ya usan `Dict[str, Any]`, así que aceptan los nuevos campos sin cambios de contrato.

---

## project_agent_output (tabla de auditoría)

En `innexia.sql`, `project_agent_output` además tiene:

- `request_id` (UNIQUE)
- `supervisor_output`
- `kanban_json`, `gantt_json`, `summary_json`
- `status`, `execution_time_ms`, `modules_executed`, `modules_failed`

El modelo actual del backend no incluye estas columnas. Si en el futuro quieres guardar `request_id` (por idempotencia con n8n), `status` o tiempos de ejecución, habría que añadirlas al modelo `ProjectAgentOutput` y, si aplica, a los endpoints que crean/actualizan esa fila.

---

## Migraciones de base de datos

Si tu base de datos se creó con el script antiguo (`mysql/agent_sections_tables.sql`) y no con `innexia.sql`, tendrás que añadir las columnas nuevas con `ALTER TABLE` (o ejecutar la parte correspondiente de innexia.sql). Los modelos de SQLAlchemy ya están preparados para leer/escribir esas columnas en cuanto existan en la BD.
