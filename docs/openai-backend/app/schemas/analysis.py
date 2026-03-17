from typing import Any
from pydantic import BaseModel, Field


class OpportunityRequest(BaseModel):
    idea: str = Field(..., examples=["Quiero lanzar una clínica digital en Panamá"])
    organization: str = Field(default="Innexia")
    language: str = Field(default="es")
    analysis_type: str = Field(default="new_business")
    project_name: str | None = None
    created_by: str | None = None
    extra_context: dict[str, Any] | None = None


class Competitor(BaseModel):
    name: str | None = None
    type: str | None = None
    strengths: list[str] = []
    weaknesses: list[str] = []


class MarketAnalysis(BaseModel):
    market_overview: str | None = None
    target_market: list[str] = []
    customer_needs: list[str] = []
    industry_trends: list[str] = []
    competitors: list[Competitor] | list[str] = []
    regulatory_factors: list[str] = []
    barriers_to_entry: list[str] = []
    opportunities: list[str] = []
    tam_sam_som: dict[str, Any] = {}
    assumptions: list[str] = []


class BMC(BaseModel):
    customer_segments: list[str] = []
    value_propositions: list[str] = []
    channels: list[str] = []
    customer_relationships: list[str] = []
    revenue_streams: list[str] = []
    key_resources: list[str] = []
    key_activities: list[str] = []
    key_partners: list[str] = []
    cost_structure: list[str] = []


class Strategy(BaseModel):
    swot: dict[str, Any] = {}
    strategic_objectives: list[str] = []
    competitive_advantages: list[str] = []
    critical_success_factors: list[str] = []
    strategic_recommendations: list[str] = []
    assumptions: list[str] = []


class Finance(BaseModel):
    assumptions: dict[str, Any] = {}
    projection_summary: dict[str, Any] = {}
    financial_observations: list[str] = []


class Risk(BaseModel):
    risk_id: str
    title: str
    category: str | None = None
    probability: str | None = None
    impact: str | None = None
    mitigation: str | None = None
    owner: str | None = None


class RoadmapPhase(BaseModel):
    phase_id: str
    name: str
    duration_weeks: int = 0
    goals: list[str] = []
    deliverables: list[str] = []
    dependencies: list[str] = []


class Roadmap(BaseModel):
    phases: list[RoadmapPhase] = []
    milestones: list[dict[str, Any]] = []
    assumptions: list[str] = []


class Activity(BaseModel):
    activity_id: str
    epic: str | None = None
    title: str
    description: str | None = None
    priority: str | None = None
    owner_role: str | None = None
    estimated_days: int | None = None
    depends_on: list[str] = []
    kanban_status: str = "todo"
    phase_id: str | None = None


class Kanban(BaseModel):
    columns: list[dict[str, Any]] = []
    cards: list[dict[str, Any]] = []


class Gantt(BaseModel):
    project_start: str | None = None
    tasks: list[dict[str, Any]] = []


class Summary(BaseModel):
    executive_summary: str | None = None
    key_findings: list[str] = []
    priority_actions: list[str] = []


class StrategyEngineResult(BaseModel):
    request_id: str
    project_name: str
    workflow_version: str = "v5.2"
    status: str = "completed"
    input: dict[str, Any] = {}
    supervisor: dict[str, Any] = {}
    market_analysis: dict[str, Any] = {}
    bmc: dict[str, Any] = {}
    strategy: dict[str, Any] = {}
    finance: dict[str, Any] = {}
    risks: list[Risk] = []
    roadmap: dict[str, Any] = {}
    verdict: dict[str, Any] = {}
    activities: list[Activity] = []
    kanban: Kanban = Kanban()
    gantt: Gantt = Gantt()
    summary: Summary = Summary()
    meta: dict[str, Any] = {}


class OpportunityResponse(BaseModel):
    request_id: str
    status: str
    result: StrategyEngineResult | dict[str, Any]
