"""Pydantic schemas for String Free domain models."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import (
    ApprovalResult,
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
