# Endpoints por agente – Workflow n8n

Cuando se usan **varios agentes** (uno por sección), cada agente debe llamar al endpoint correspondiente con el payload en **formato canónico** (o formato agente donde se indica). Todos los endpoints requieren autenticación: header `Authorization: Bearer <token>`.

Base URL de la API: `https://tu-dominio.com/api` (en local: `http://localhost:8000/api`).

---

## Resumen rápido

| Sección | Método | Ruta | Body (canónico / formato agente) |
|--------|--------|------|----------------------------------|
| Conversación | **PUT** | `/agent-output/project/{project_id}/conversacion` | Objeto `conversacion` |
| Business Model Canvas | **PUT** | `/agent-output/project/{project_id}/business-model-canvas` | Objeto BMC (formato agente) |
| Estrategia comercial | **PUT** | `/agent-output/project/{project_id}/estrategia-comercial` | Objeto estrategia comercial |
| Roadmap | **PUT** | `/agent-output/project/{project_id}/roadmap` | Objeto roadmap |
| Análisis financiero | **PUT** | `/agent-output/project/{project_id}/analisis-financiero` | Objeto análisis financiero |
| Análisis de riesgos | **PUT** | `/agent-output/project/{project_id}/analisis-riesgos` | Objeto análisis riesgos |
| Veredicto final | **PUT** | `/agent-output/project/{project_id}/veredicto` | Objeto veredicto |
| Plan de actividades | **PUT** | `/agent-output/project/{project_id}/plan-actividades` | Objeto con `plan_actividades` o directamente el objeto plan |

`{project_id}` es el ID numérico del proyecto (por ejemplo `42`).

---

## 1. Conversación

**PUT** `/api/agent-output/project/{project_id}/conversacion`

Actualiza solo el bloque de conversación (idea de negocio, historial de mensajes).

**Body (JSON):**

```json
{
  "mensajes_totales": 15,
  "idea_negocio_original": "Descripción de la idea de negocio",
  "historial_completo": [
    {
      "rol": "usuario",
      "mensaje": "Texto del mensaje",
      "timestamp": "2024-01-15T10:15:00Z"
    },
    {
      "rol": "asistente",
      "mensaje": "Respuesta del asistente",
      "timestamp": "2024-01-15T10:16:00Z"
    }
  ]
}
```

---

## 2. Business Model Canvas

**PUT** `/api/agent-output/project/{project_id}/business-model-canvas`

Acepta el **formato agente** (segmentos_clientes, propuesta_valor, etc.). El backend lo sincroniza a la tabla canónica `business_model_canvases` y guarda una copia en `project_agent_output`.

**Body (JSON):** mismo formato que la clave `business_model_canvas` en `n8n_agent_payload_example.json`:

- `segmentos_clientes` (objeto con descripcion, detalles, tamano_mercado_estimado)
- `propuesta_valor` (descripcion, beneficios_clave)
- `canales` (distribucion, comunicacion)
- `relacion_clientes` (tipo, estrategias)
- `fuentes_ingresos` (modelo, precios)
- `recursos_clave` (tecnologicos, humanos, financieros)
- `actividades_clave` (array)
- `alianzas_clave` (array)
- `estructura_costos` (costos_fijos, costos_variables)

---

## 3. Estrategia comercial

**PUT** `/api/agent-output/project/{project_id}/estrategia-comercial`

**Body (JSON):**

```json
{
  "analisis_mercado": {
    "tamano_mercado": "$500M anuales",
    "crecimiento_anual": "15%",
    "competidores_principales": ["Competidor A", "Competidor B"],
    "ventaja_competitiva": "Texto descriptivo"
  },
  "estrategia_precios": {
    "modelo": "Freemium con planes escalonados",
    "justificacion": "Texto",
    "descuentos": ["10% anual", "20% más de 5 licencias"]
  },
  "estrategia_marketing": {
    "canales_principales": ["Google Ads", "Facebook Ads"],
    "presupuesto_mensual": 2000,
    "kpis": ["CAC < $100", "LTV > $500"]
  },
  "estrategia_ventas": {
    "proceso": "Self-service con asistencia opcional",
    "ciclo_venta_estimado": "7 días",
    "tasa_conversion_objetivo": "3%"
  }
}
```

---

## 4. Roadmap estratégico

**PUT** `/api/agent-output/project/{project_id}/roadmap`

**Body (JSON):**

```json
{
  "cronograma_total_meses": 21,
  "fases": [
    {
      "fase": "MVP",
      "duracion_meses": 3,
      "hitos": ["Hito 1", "Hito 2"],
      "recursos_necesarios": ["2 desarrolladores", "$15,000"]
    },
    {
      "fase": "Crecimiento",
      "duracion_meses": 6,
      "hitos": ["Hito A", "Hito B"],
      "recursos_necesarios": ["4 personas", "$50,000"]
    }
  ]
}
```

---

## 5. Análisis financiero

**PUT** `/api/agent-output/project/{project_id}/analisis-financiero`

**Body (JSON):**

```json
{
  "inversion_inicial": {
    "total": 50000,
    "desglose": [
      {"concepto": "Desarrollo", "monto": 30000},
      {"concepto": "Marketing", "monto": 15000}
    ]
  },
  "proyecciones_3_anos": [
    {
      "ano": 1,
      "ingresos": 120000,
      "costos": 150000,
      "utilidad_neta": -30000,
      "clientes_estimados": 200
    },
    {
      "ano": 2,
      "ingresos": 480000,
      "costos": 300000,
      "utilidad_neta": 180000,
      "clientes_estimados": 800
    },
    {
      "ano": 3,
      "ingresos": 1200000,
      "costos": 600000,
      "utilidad_neta": 600000,
      "clientes_estimados": 2000
    }
  ],
  "metricas_clave": {
    "roi_3_anos": "1100%",
    "punto_equilibrio_meses": 18,
    "ltv_cac_ratio": 5,
    "margen_bruto": "70%"
  },
  "viabilidad_financiera": "ALTA"
}
```

---

## 6. Análisis de riesgos

**PUT** `/api/agent-output/project/{project_id}/analisis-riesgos`

**Body (JSON):**

```json
{
  "nivel_riesgo_general": "MEDIO",
  "recomendaciones": [
    "Validar PMF antes de escalar",
    "Mantener runway de al menos 12 meses"
  ],
  "riesgos_identificados": [
    {
      "categoria": "Mercado",
      "riesgo": "Competencia de grandes players",
      "probabilidad": "MEDIA",
      "impacto": "ALTO",
      "mitigacion": "Enfoque en nicho y servicio personalizado"
    },
    {
      "categoria": "Financiero",
      "riesgo": "Burn rate alto en fase inicial",
      "probabilidad": "ALTA",
      "impacto": "ALTO",
      "mitigacion": "Control de gastos e inversión temprana"
    }
  ]
}
```

---

## 7. Veredicto final

**PUT** `/api/agent-output/project/{project_id}/veredicto`

**Body (JSON):**

```json
{
  "decision": "POSITIVO",
  "puntuacion_general": 8.5,
  "fortalezas": [
    "Mercado grande y en crecimiento",
    "Propuesta de valor clara"
  ],
  "debilidades": [
    "Competencia establecida",
    "Inversión inicial significativa"
  ],
  "recomendacion_estrategica": "Proceder con el proyecto. Enfocarse en validación del MVP...",
  "siguiente_paso": "Desarrollar MVP en 3 meses y conseguir 10 clientes beta"
}
```

---

## 8. Plan de actividades

**PUT** `/api/agent-output/project/{project_id}/plan-actividades`

Guarda el plan en `project_agent_output.plan_actividades` y crea las actividades del array como actividades del proyecto (tabla `activities`). No borra actividades existentes; añade las nuevas.

**Body (JSON):** puede ser el objeto completo `plan_actividades` o un objeto que lo contenga:

```json
{
  "plan_actividades": {
    "generado": true,
    "actividades": [
      {
        "id": "ACT-001",
        "titulo": "Definición de arquitectura técnica",
        "descripcion": "Diseñar arquitectura cloud escalable",
        "fecha_inicio": "2024-01-15",
        "fecha_fin": "2024-01-29",
        "duracion_dias": 14,
        "responsable": "CTO",
        "prioridad": "ALTA",
        "estado": "PENDIENTE",
        "dependencias": [],
        "etiquetas": ["desarrollo", "mvp"]
      },
      {
        "id": "ACT-002",
        "titulo": "Desarrollo funcionalidades core MVP",
        "descripcion": "Implementar gestión de inventario básica",
        "fecha_inicio": "2024-01-30",
        "fecha_fin": "2024-03-15",
        "duracion_dias": 45,
        "responsable": "Equipo Desarrollo",
        "prioridad": "ALTA",
        "estado": "PENDIENTE",
        "dependencias": ["ACT-001"],
        "etiquetas": ["desarrollo", "mvp"]
      }
    ],
    "resumen": {
      "total_actividades": 8,
      "duracion_total_dias": 350,
      "fecha_inicio_proyecto": "2024-01-15",
      "fecha_fin_estimada": "2024-12-31"
    }
  }
}
```

O enviar directamente el objeto interno (con `actividades` y opcionalmente `generado` y `resumen`):

```json
{
  "generado": true,
  "actividades": [ ... ],
  "resumen": { ... }
}
```

**Mapeo de campos de actividad:**

- `prioridad`: `"ALTA"` → high, `"MEDIA"` → medium, `"BAJA"` → low  
- `estado`: `"PENDIENTE"` → todo, `"EN PROGRESO"` → in-progress, `"EN REVISIÓN"` → review, `"COMPLETADO"` → completed  

---

## Crear proyecto desde cero (opcional)

Si el workflow **crea un proyecto nuevo** (no actualiza uno existente), usar:

**POST** `/api/agent-output/create-project`

**Body (JSON):**

```json
{
  "payload": {
    "conversacion": { ... },
    "business_model_canvas": { ... },
    "estrategia_comercial": { ... },
    "roadmap_estrategico": { ... },
    "analisis_financiero": { ... },
    "analisis_riesgos": { ... },
    "veredicto_final": { ... },
    "plan_actividades": { ... }
  },
  "name": "Nombre del proyecto (opcional)",
  "description": "Descripción (opcional)",
  "category_id": 1,
  "location_id": 1
}
```

Con un solo payload se crea el proyecto y se rellenan todas las secciones. Si usas varios agentes, lo habitual es tener ya el proyecto creado y que cada agente haga **PUT** a su endpoint con `project_id`.

---

## Autenticación

En n8n, obtener el token con **POST** `/api/auth/login` (o el flujo que uses) y enviarlo en cada request:

- Header: `Authorization: Bearer <token>`
- Content-Type: `application/json`

El usuario asociado al token debe tener acceso al proyecto (misma company).

---

## Respuesta de los PUT por sección

Todos los PUT por sección devuelven, en caso de éxito, un objeto pensado para el agente de n8n:

```json
{
  "status": "completed",
  "message": "Estrategia comercial actualizada correctamente en el proyecto.",
  "project_id": "123",
  "mode": "update",
  "success": true
}
```

- **status**: `"completed"` cuando la operación fue correcta.
- **message**: Mensaje legible indicando qué se actualizó (varía por endpoint).
- **project_id**: ID del proyecto en formato string.
- **mode**: `"update"` (actualización de proyecto existente).
- **success**: `true`.

El PUT de **plan de actividades** añade un campo opcional:

```json
{
  "status": "completed",
  "message": "Plan de actividades actualizado correctamente. Se crearon 8 actividades en el proyecto.",
  "project_id": "123",
  "mode": "update",
  "success": true,
  "activities_created": 8
}
```

En caso de error (proyecto no encontrado, no autorizado, etc.) la API devuelve código HTTP 4xx y un cuerpo con `detail`; en n8n puedes mapear eso a una respuesta tipo:

```json
{
  "status": "error",
  "message": "Proyecto no encontrado",
  "project_id": "123",
  "mode": "update",
  "success": false
}
```
