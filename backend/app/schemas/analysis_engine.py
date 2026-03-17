from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class OpportunityRequest(BaseModel):
    idea: str = Field(..., examples=["Quiero lanzar una clínica digital en Panamá"])
    organization: str = Field(default="Innexia")
    language: str = Field(default="es")
    analysis_type: str = Field(default="new_business")
    project_name: Optional[str] = None
    created_by: Optional[str] = None
    extra_context: Optional[Dict[str, Any]] = None


class Competitor(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)


class MarketAnalysis(BaseModel):
    market_overview: Optional[str] = None
    target_market: List[str] = Field(default_factory=list)
    customer_needs: List[str] = Field(default_factory=list)
    industry_trends: List[str] = Field(default_factory=list)
    competitors: List[Union[Competitor, str]] = Field(default_factory=list)
    regulatory_factors: List[str] = Field(default_factory=list)
    barriers_to_entry: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    tam_sam_som: Dict[str, Any] = Field(default_factory=dict)
    assumptions: List[str] = Field(default_factory=list)


class BMC(BaseModel):
    customer_segments: List[str] = Field(default_factory=list)
    value_propositions: List[str] = Field(default_factory=list)
    channels: List[str] = Field(default_factory=list)
    customer_relationships: List[str] = Field(default_factory=list)
    revenue_streams: List[str] = Field(default_factory=list)
    key_resources: List[str] = Field(default_factory=list)
    key_activities: List[str] = Field(default_factory=list)
    key_partners: List[str] = Field(default_factory=list)
    cost_structure: List[str] = Field(default_factory=list)


class Strategy(BaseModel):
    swot: Dict[str, Any] = Field(default_factory=dict)
    strategic_objectives: List[str] = Field(default_factory=list)
    competitive_advantages: List[str] = Field(default_factory=list)
    critical_success_factors: List[str] = Field(default_factory=list)
    strategic_recommendations: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)


class Finance(BaseModel):
    initial_investment: Optional[float] = None
    monthly_operating_cost: Optional[float] = None
    expected_revenue: Optional[float] = None
    payback_months: Optional[float] = None
    assumptions: Dict[str, Any] = Field(default_factory=dict)
    projection_summary: Dict[str, Any] = Field(default_factory=dict)
    financial_observations: List[str] = Field(default_factory=list)


class Risk(BaseModel):
    risk_id: str
    title: str
    category: Optional[str] = None
    probability: Optional[str] = None
    impact: Optional[str] = None
    mitigation: Optional[str] = None
    owner: Optional[str] = None


class RoadmapPhase(BaseModel):
    phase_id: str
    name: str
    duration_weeks: int = 0
    goals: List[str] = Field(default_factory=list)
    deliverables: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)


class Roadmap(BaseModel):
    phases: List[RoadmapPhase] = Field(default_factory=list)
    milestones: List[Dict[str, Any]] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    project_start: Optional[str] = None
    project_end: Optional[str] = None


class Activity(BaseModel):
    activity_id: str
    epic: Optional[str] = None
    title: str
    description: Optional[str] = None
    priority: Optional[str] = None
    owner_role: Optional[str] = None
    estimated_days: Optional[int] = None
    depends_on: List[str] = Field(default_factory=list)
    kanban_status: str = "todo"
    phase_id: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    sort_order: Optional[int] = None


class Kanban(BaseModel):
    columns: List[Dict[str, Any]] = Field(default_factory=list)
    cards: List[Dict[str, Any]] = Field(default_factory=list)


class Gantt(BaseModel):
    project_start: Optional[str] = None
    tasks: List[Dict[str, Any]] = Field(default_factory=list)


class Summary(BaseModel):
    executive_summary: Optional[str] = None
    key_findings: List[str] = Field(default_factory=list)
    priority_actions: List[str] = Field(default_factory=list)


class Verdict(BaseModel):
    decision: Optional[str] = None
    confidence: Optional[float] = None
    reasons: List[str] = Field(default_factory=list)
    conditions_to_proceed: List[str] = Field(default_factory=list)
    executive_summary: Optional[str] = None


class StrategyEngineResult(BaseModel):
    request_id: str
    project_name: str
    workflow_version: str = "v5.2"
    status: str = "completed"
    input: Dict[str, Any] = Field(default_factory=dict)
    supervisor: Dict[str, Any] = Field(default_factory=dict)
    market_analysis: Union[MarketAnalysis, Dict[str, Any]] = Field(default_factory=dict)
    bmc: Union[BMC, Dict[str, Any]] = Field(default_factory=dict)
    strategy: Union[Strategy, Dict[str, Any]] = Field(default_factory=dict)
    finance: Union[Finance, Dict[str, Any]] = Field(default_factory=dict)
    risks: List[Risk] = Field(default_factory=list)
    roadmap: Union[Roadmap, Dict[str, Any]] = Field(default_factory=dict)
    verdict: Union[Verdict, Dict[str, Any]] = Field(default_factory=dict)
    activities: List[Activity] = Field(default_factory=list)
    kanban: Kanban = Field(default_factory=Kanban)
    gantt: Gantt = Field(default_factory=Gantt)
    summary: Summary = Field(default_factory=Summary)
    meta: Dict[str, Any] = Field(default_factory=dict)


class OpportunityResponse(BaseModel):
    request_id: str
    status: str
    result: Union[StrategyEngineResult, Dict[str, Any]]
