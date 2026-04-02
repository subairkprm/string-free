"""Pydantic schemas for String Free domain models."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import (
    ApprovalResult,
    OpportunityStatus,
    OpportunityType,
    Severity,
    TaskSource,
    TaskStatus,
)

# --- Task Schemas ---


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    structural_flag: bool = False
    priority: str | None = None
    source: TaskSource = TaskSource.MANUAL


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    structural_flag: bool | None = None
    priority: str | None = None


class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: str | None = None
    status: TaskStatus
    structural_flag: bool
    priority: str | None = None
    source: str | None = None
    created_at: datetime
    updated_at: datetime


# --- Approval Schemas ---


class ApprovalCreate(BaseModel):
    task_id: UUID
    requested_by: str | None = None


class ApprovalResponse(BaseModel):
    id: UUID
    task_id: UUID
    result: ApprovalResult
    requested_by: str | None = None
    decided_by: str | None = None
    note: str | None = None
    created_at: datetime
    updated_at: datetime


# --- Error Schemas ---


class ErrorCreate(BaseModel):
    environment: str | None = None
    module: str | None = None
    category: str | None = None
    severity: Severity | None = None
    source_layer: str | None = None
    trigger_action: str | None = None
    summary: str | None = None
    raw_detail: str | None = None
    probable_cause: str | None = None


class ErrorResponse(BaseModel):
    id: UUID
    timestamp: datetime
    environment: str | None = None
    module: str | None = None
    category: str | None = None
    severity: Severity | None = None
    summary: str | None = None
    status: str | None = None
    created_at: datetime


# --- Improvement Task Schemas ---


class ImprovementTaskCreate(BaseModel):
    title: str
    error_summary: str | None = None
    proposed_fix: str | None = None
    priority: str | None = None
    structural_flag: bool = True
    source_error_id: UUID | None = None


class ImprovementTaskResponse(BaseModel):
    id: UUID
    title: str
    error_summary: str | None = None
    proposed_fix: str | None = None
    priority: str | None = None
    structural_flag: bool
    status: TaskStatus
    source_error_id: UUID | None = None
    created_at: datetime
    updated_at: datetime


# --- Webhook Schemas ---


class WebhookPayload(BaseModel):
    """Generic webhook payload wrapper."""

    event: str | None = None
    data: dict | None = None


class SentryWebhookPayload(BaseModel):
    """Sentry webhook event payload."""

    action: str | None = None
    data: dict | None = None
    actor: dict | None = None


class BillingWebhookPayload(BaseModel):
    """Lemon Squeezy webhook payload."""

    meta: dict | None = None
    data: dict | None = None


# --- AI Response Schemas ---


class AIParsedTask(BaseModel):
    """Response from AI task parsing."""

    title: str
    description: str | None = None
    priority: str = "medium"
    due_date: str | None = None
    tags: list[str] = []


class AIErrorSummary(BaseModel):
    """Response from AI error summarization."""

    summary: str
    proposed_fix: str


# --- Income Opportunity Schemas ---


class OpportunityCreate(BaseModel):
    user_id: str
    title: str
    description: str
    opportunity_type: OpportunityType
    confidence_score: float | None = None
    estimated_effort: str | None = None
    estimated_revenue_potential: str | None = None
    source_task_ids: list[UUID] | None = None
    ai_reasoning: str | None = None


class OpportunityUpdate(BaseModel):
    status: OpportunityStatus | None = None
    user_notes: str | None = None
    user_rating: int | None = None


class OpportunityResponse(BaseModel):
    id: UUID
    user_id: str
    title: str
    description: str
    opportunity_type: OpportunityType
    status: OpportunityStatus
    confidence_score: float | None = None
    estimated_effort: str | None = None
    estimated_revenue_potential: str | None = None
    source_task_ids: list[UUID] | None = None
    analysis_date: datetime
    ai_reasoning: str | None = None
    user_notes: str | None = None
    user_rating: int | None = None
    created_at: datetime
    updated_at: datetime


class OpportunityAnalysisRequest(BaseModel):
    days: int = 30
    force_refresh: bool = False


class OpportunityRatingRequest(BaseModel):
    rating: int
    feedback: str | None = None


# --- AI Opportunity Analysis Schemas ---


class AIOpportunity(BaseModel):
    """Single opportunity identified by AI."""

    type: str
    title: str
    description: str
    confidence_score: float
    reasoning: str
    estimated_effort: str
    revenue_potential: str


class AIOpportunityAnalysis(BaseModel):
    """Response from AI opportunity detection."""

    opportunities: list[AIOpportunity]


class AIPattern(BaseModel):
    """Pattern identified from task history."""

    pattern_type: str
    description: str
    opportunity_suggestion: str
    confidence_score: float


class AIPatternAnalysis(BaseModel):
    """Response from AI pattern analysis."""

    patterns: list[AIPattern]
