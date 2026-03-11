# Payload del agente n8n – Análisis estratégico

Este documento describe el **JSON que debe enviar el agente de n8n** para almacenar todos los datos del análisis estratégico en el proyecto.

> **Varios agentes (uno por sección):** si en n8n usas un agente distinto por cada sección, cada uno debe llamar a su propio endpoint PUT. Ver **[N8N_ENDPOINTS_POR_AGENTE.md](./N8N_ENDPOINTS_POR_AGENTE.md)** para la lista de endpoints POST/PUT por sección y el formato del body.

## Archivo de ejemplo

- **`n8n_agent_payload_example.json`**: ejemplo completo del payload. Puede usarse tal cual en pruebas o como referencia para construir la salida del agente.

## Endpoints que consumen este payload

| Método | Ruta | Uso |
|--------|------|-----|
| **PUT** | `/api/agent-output/project/{project_id}` | Actualizar la salida del agente de un **proyecto existente**. Body: el objeto JSON completo (sin envolver en `payload`). |
| **POST** | `/api/agent-output/create-project` | **Crear un proyecto nuevo** a partir del análisis. Body: `{ "payload": { ...objeto JSON completo... }, "name": "opcional", "description": "opcional" }`. |

Todos los endpoints requieren autenticación (Bearer token).

## Estructura del JSON

Todas las claves de primer nivel son **opcionales**. El backend guarda el JSON en `project_agent_output` y, cuando existen, sincroniza a las tablas canónicas para edición.

| Clave | Descripción |
|-------|-------------|
| **metadata** | Metadatos del workflow (timestamp, versión, modelo usado). |
| **conversacion** | Resumen de la conversación: `mensajes_totales`, `idea_negocio_original`, `historial_completo` (array de mensajes con `rol`, `mensaje`, `timestamp`). |
| **business_model_canvas** | BMC en formato agente: `segmentos_clientes`, `propuesta_valor`, `canales`, `relacion_clientes`, `fuentes_ingresos`, `recursos_clave`, `actividades_clave`, `alianzas_clave`, `estructura_costos`. Se sincroniza a la tabla `business_model_canvases`. |
| **estrategia_comercial** | `analisis_mercado`, `estrategia_precios`, `estrategia_marketing`, `estrategia_ventas`. Sincroniza a `project_estrategia_comercial`. |
| **roadmap_estrategico** | `fases` (array de `{ fase, duracion_meses, hitos[], recursos_necesarios[] }`), `cronograma_total_meses`. Sincroniza a `project_roadmap`. |
| **analisis_financiero** | `inversion_inicial` (total + desglose), `proyecciones_3_anos`, `metricas_clave`, `viabilidad_financiera`. Sincroniza a `project_analisis_financiero`. |
| **analisis_riesgos** | `riesgos_identificados` (array de `{ categoria, riesgo, probabilidad, impacto, mitigacion }`), `nivel_riesgo_general`, `recomendaciones`. Sincroniza a `project_analisis_riesgos` y `project_riesgo`. |
| **veredicto_final** | `decision`, `puntuacion_general`, `fortalezas[]`, `debilidades[]`, `recomendacion_estrategica`, `siguiente_paso`. Sincroniza a `project_veredicto`. |
| **plan_actividades** | `generado`, `actividades[]` (cada una con id, titulo, descripcion, fecha_inicio, fecha_fin, responsable, prioridad, estado, dependencias, etiquetas), `resumen`. Al crear proyecto con POST, las actividades se crean en el proyecto. |

## Tipos de datos esperados

- **Números**: `total`, `monto`, `presupuesto_mensual`, `duracion_meses`, `ano`, `ingresos`, `costos`, `utilidad_neta`, `clientes_estimados`, `puntuacion_general`, `punto_equilibrio_meses` → number.
- **Fechas**: formato ISO 8601, p. ej. `"2024-01-15"` o `"2024-01-15T10:30:00Z"`.
- **Prioridad/estado en actividades**: `prioridad` (ej. `"ALTA"`, `"MEDIA"`, `"BAJA"`), `estado` (ej. `"PENDIENTE"`, `"EN PROGRESO"`, `"COMPLETADO"`).
- **Probabilidad/impacto en riesgos**: texto, p. ej. `"ALTA"`, `"MEDIA"`, `"BAJO"`.

## Uso desde n8n

1. El nodo que construye la salida del agente debe generar un objeto JSON con la estructura anterior.
2. Para **actualizar un proyecto existente**: enviar ese objeto en el body del PUT a `/api/agent-output/project/{project_id}` (header `Authorization: Bearer <token>`).
3. Para **crear un proyecto nuevo**: enviar en el body del POST a `/api/agent-output/create-project` un objeto `{ "payload": <objeto anterior>, "name": "...", "description": "..." }` (nombre y descripción opcionales; si no se envían, se infieren de `conversacion.idea_negocio_original`).

El backend guarda el JSON en `project_agent_output` y sincroniza cada sección a su tabla canónica para que la aplicación pueda mostrar y editar los datos en las pestañas del proyecto.
