from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field, HttpUrl


class ProcessStep(BaseModel):
    id: str
    name: str
    description: str
    upstream_ids: list[str] = []
    diagram_evidence: str


class EquipmentRequirement(BaseModel):
    id: str
    process_step_id: str
    category: str
    function: str
    quantity: int | None = None
    diagram_evidence: str
    constraints: list[str] = []


class ClarificationQuestion(BaseModel):
    key: str
    question: str
    why_critical: str
    blocking: bool


class DiagramAnalysis(BaseModel):
    process_summary: str
    process_steps: list[ProcessStep]
    equipment_requirements: list[EquipmentRequirement]
    clarification_questions: list[ClarificationQuestion]
    extraction_uncertainties: list[str]


class Evidence(BaseModel):
    claim: str
    value: str | None
    source_url: HttpUrl | None
    source_title: str | None
    retrieved_date: str | None
    status: Literal["verified", "supplier_claim", "comparable_only", "unknown"]
    note: str | None = None


class Candidate(BaseModel):
    requirement_id: str
    manufacturer: str
    model: str
    product_url: HttpUrl | None
    recommendation: Literal["recommended", "alternative", "not_qualified"]
    rationale: str
    price: Evidence
    lead_time: Evidence
    technical_evidence: list[Evidence]
    qualification_gaps: list[str]
    next_action: str


class BomResearch(BaseModel):
    candidates: list[Candidate]
    overall_uncertainties: list[str]
    human_decisions_required: list[str]


class ConfirmedRequirements(BaseModel):
    analysis: DiagramAnalysis
    human_assumptions: dict[str, str | int | float | bool | None]

