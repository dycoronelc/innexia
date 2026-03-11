# BMC: Fuente única de verdad (business_model_canvases)

## Decisión de diseño

- **Fuente única para visualización y edición del BMC:** tabla `business_model_canvases`.
- **En `project_agent_output`:** el campo `business_model_canvas` (JSON) se mantiene como **copia de auditoría** de lo que envió el agente (n8n). No se usa para editar ni para mostrar en la pestaña BMC.

## Flujo

1. **Llega salida del agente** (PUT `/api/agent-output/project/{id}` o POST `create-project` con payload que incluye `business_model_canvas`).
2. Se guarda el payload completo en `project_agent_output` (incluido el JSON del BMC).
3. **Sincronización:** se mapea el JSON del agente al formato de `business_model_canvases` y se hace **create o update** del registro de BMC de ese proyecto.
4. La **pestaña Business Model Canvas** del proyecto sigue leyendo y escribiendo solo contra `business_model_canvases` (API `/api/bmc/`). Cualquier edición del usuario se persiste ahí.
5. **Resto de secciones (estrategia comercial, roadmap, análisis financiero, riesgos, veredicto):** misma estrategia. Cada una tiene su **tabla canónica** (ver más abajo). Al guardar salida del agente se sincronizan a esas tablas; el GET de agent-output devuelve datos desde las tablas canónicas si existen (si no, desde el JSON de `project_agent_output`). La edición se hace vía PUT por sección (`/project/{id}/estrategia-comercial`, `/roadmap`, etc.), que actualiza la tabla canónica. Un **futuro agente** puede re-analizar el proyecto y generar un nuevo veredicto (y actualizar las demás secciones) guardando de nuevo en agent-output; los datos se vuelven a sincronizar a las tablas canónicas.

## Mapeo agente → business_model_canvases

| Agente (salidaAgente.json)     | business_model_canvases   |
|--------------------------------|---------------------------|
| alianzas_clave                 | key_partners              |
| actividades_clave              | key_activities            |
| recursos_clave (tecnol.+hum.+fin.) | key_resources        |
| propuesta_valor (beneficios_clave/descripcion) | value_propositions |
| relacion_clientes (estrategias/tipo) | customer_relationships |
| canales (distribucion + comunicacion) | channels        |
| segmentos_clientes (detalles/descripcion) | customer_segments |
| estructura_costos (costos_fijos + costos_variables) | cost_structure |
| fuentes_ingresos (precios / modelo) | revenue_streams   |

## Resumen

- **BMC editable:** siempre en `business_model_canvases`. Al recibir datos del agente se sincronizan ahí; la pestaña BMC solo usa esta tabla.
- **BMC del agente (auditoría):** en `project_agent_output.business_model_canvas`; no se usa para edición ni para la pestaña BMC.

---

## Tablas canónicas por sección del agente

Igual que el BMC, cada sección del JSON del agente tiene una **tabla como fuente única** para visualización y edición. El JSON en `project_agent_output` queda como auditoría.

| Sección                 | Tabla canónica                 | Sync desde agente | PUT edición |
|-------------------------|--------------------------------|------------------|-------------|
| Estrategia comercial    | `project_estrategia_comercial`  | Sí               | `PUT /project/{id}/estrategia-comercial` |
| Roadmap                 | `project_roadmap`               | Sí               | `PUT /project/{id}/roadmap` |
| Análisis financiero     | `project_analisis_financiero`  | Sí               | `PUT /project/{id}/analisis-financiero` |
| Riesgos                 | `project_analisis_riesgos` + `project_riesgo` | Sí | `PUT /project/{id}/analisis-riesgos` |
| Veredicto               | `project_veredicto`            | Sí               | `PUT /project/{id}/veredicto` |

- **GET** `/api/agent-output/project/{id}`: devuelve para cada sección los datos de la tabla canónica si existe; si no, el JSON de `project_agent_output`.
- **Re-análisis:** un segundo agente puede volver a analizar el proyecto y enviar un nuevo payload (PUT agent-output o flujo n8n). Se vuelve a sincronizar todo a las tablas canónicas; por ejemplo, se actualiza el veredicto en `project_veredicto`.
