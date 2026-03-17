
# Innexia AI Strategy Engine – Persistence & JSON Contract Guide
**Purpose:** This document explains what data the AI Strategy Engine (via n8n agents) stores in the database and what JSON structures the application should expect and send when interacting with the system.

This document is intended to be provided to development tools (e.g., Cursor) so the backend and frontend know how to integrate with the AI Strategy Engine.

---

# 1. High Level Flow

User writes an idea such as:

> "Quiero lanzar una clínica digital en Panamá"

System pipeline:

```
User / Frontend
      ↓
API (FastAPI / Backend)
      ↓
n8n Webhook
      ↓
AI Strategy Engine
      ├ Supervisor Agent
      ├ Market Intelligence Agent
      ├ BMC Agent
      ├ Strategy Agent
      ├ Finance Agent
      ├ Risks Agent
      ├ Roadmap Agent
      ├ Verdict Agent
      └ Activities Agent
      ↓
Consolidator
      ↓
MySQL Persistence
      ↓
API response to frontend
```

---

# 2. Database Tables and Responsibilities

## 2.1 analysis_requests
Represents a single strategic analysis execution.

Stored when the workflow **starts**.

### Fields stored
| Field | Description |
|------|-------------|
request_id | Unique ID of the analysis run |
project_name | Name of the opportunity |
analysis_type | e.g. new_business, product |
organization_name | Organization requesting analysis |
input_json | Original user request |
status | pending / running / completed / failed |
workflow_version | Engine version |
execution_time_ms | Runtime |
created_at | Timestamp |

### Example JSON stored

```json
{
  "request_id": "REQ-2026-0001",
  "project_name": "Clinica Digital Panama",
  "analysis_type": "new_business",
  "organization_name": "Innexia",
  "input_json": {
    "idea": "Crear una clínica digital en Panamá"
  }
}
```

---

# 2.2 analysis_results

Stores the **final consolidated output** of the AI engine.

Created when workflow finishes.

### Fields stored

| Field | Description |
|------|-------------|
request_id | Links to analysis_requests |
consolidated_json | Full result JSON |
executive_summary | High level summary |
verdict_decision | avanzar / piloto / rediseñar |
confidence_score | Confidence of AI decision |
market_score | Market potential |
viability_score | Feasibility |
risk_score | Risk level |

---

# 2.3 analysis_modules

Stores output of each individual AI module.

Allows debugging and re-running modules.

Modules stored:

```
supervisor
market_intelligence
bmc
strategy
finance
risks
roadmap
verdict
activities
```

### Stored JSON example

```json
{
  "module_name": "market_intelligence",
  "output_json": {
    "market_analysis": {
      "market_overview": "Growing telemedicine adoption",
      "competitors": [],
      "opportunities": []
    }
  }
}
```

---

# 2.4 analysis_activities

Stores execution tasks produced by the Activities Agent.

Used to generate **Kanban and Gantt**.

### Example JSON

```json
{
  "activity_id": "A1",
  "epic": "MVP Development",
  "title": "Diseñar arquitectura de telemedicina",
  "priority": "alta",
  "estimated_days": 5,
  "phase_id": "P1"
}
```

---

# 2.5 analysis_risks

Stores structured risk analysis.

### Example JSON

```json
{
  "risk_id": "R1",
  "title": "Regulación médica",
  "category": "legal",
  "probability": "media",
  "impact": "alto",
  "mitigation": "Validar regulación con Ministerio de Salud"
}
```

---

# 3. JSON Contract Between AI Engine and Application

The AI engine ultimately produces **one consolidated JSON object**.

The application should expect the following structure.

```
{
  "request_id": "",
  "project_name": "",
  "market_analysis": {},
  "bmc": {},
  "strategy": {},
  "finance": {},
  "risks": [],
  "roadmap": {},
  "verdict": {},
  "activities": [],
  "kanban": {},
  "gantt": {},
  "summary": {}
}
```

---

# 4. Detailed JSON Sections

## 4.1 Market Analysis

```
{
  "market_analysis": {
    "market_overview": "",
    "target_market": [],
    "industry_trends": [],
    "competitors": [],
    "regulatory_factors": [],
    "opportunities": []
  }
}
```

---

## 4.2 Business Model Canvas

```
{
  "bmc": {
    "customer_segments": [],
    "value_propositions": [],
    "channels": [],
    "revenue_streams": [],
    "key_resources": [],
    "key_partners": []
  }
}
```

---

## 4.3 Strategy

```
{
  "strategy": {
    "swot": {},
    "strategic_objectives": [],
    "competitive_advantages": [],
    "strategic_recommendations": []
  }
}
```

---

## 4.4 Finance

```
{
  "finance": {
    "initial_investment": 0,
    "monthly_operating_cost": 0,
    "expected_revenue": 0,
    "payback_months": 0
  }
}
```

---

## 4.5 Risks

```
{
  "risks": [
    {
      "risk_id": "",
      "title": "",
      "probability": "",
      "impact": "",
      "mitigation": ""
    }
  ]
}
```

---

## 4.6 Roadmap

```
{
  "roadmap": {
    "phases": [
      {
        "phase_id": "",
        "name": "",
        "duration_weeks": 0
      }
    ]
  }
}
```

---

## 4.7 Activities

```
{
  "activities": [
    {
      "activity_id": "",
      "title": "",
      "priority": "",
      "estimated_days": 0,
      "phase_id": ""
    }
  ]
}
```

---

# 5. Kanban Format

```
{
  "kanban": {
    "columns": [
      {"id": "todo", "title": "To Do"},
      {"id": "in_progress", "title": "In Progress"},
      {"id": "review", "title": "Review"},
      {"id": "done", "title": "Done"}
    ],
    "cards": []
  }
}
```

---

# 6. Gantt Format

```
{
  "gantt": {
    "project_start": "",
    "tasks": [
      {
        "id": "",
        "name": "",
        "start": "",
        "end": "",
        "dependencies": []
      }
    ]
  }
}
```

---

# 7. Backend Responsibilities

Backend must:

1. Insert record into `analysis_requests`
2. Trigger n8n workflow
3. Wait for response
4. Store consolidated JSON into `analysis_results`
5. Store activities into `analysis_activities`
6. Store risks into `analysis_risks`
7. Return JSON to frontend

---

# 8. Frontend Responsibilities

Frontend should:

- display **Executive Summary**
- render **Business Model Canvas**
- show **Strategy**
- show **Financial Projection**
- render **Kanban**
- render **Gantt**
- show **Risk Matrix**

---

# 9. Recommended API Endpoint

```
POST /api/analyze-opportunity
```

### Request

```
{
  "idea": "Quiero lanzar una clínica digital en Panamá"
}
```

### Response

```
{
  "request_id": "REQ-2026-001",
  "status": "completed",
  "result": {...full strategy engine output...}
}
```

---

# 10. Vision

This AI Strategy Engine allows Innexia to provide automated strategic consulting.

User writes an idea → System generates:

- Market analysis
- Business model
- Strategy
- Financial plan
- Execution roadmap
- Risk assessment
- Action plan

This becomes the foundation of the **Innexia Strategic Intelligence Platform**.
