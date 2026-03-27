"""Pydantic schemas for String Free domain models."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional

from app.models.enums import (
    TaskStatus,
    Severity,
    ApprovalResult,
    TaskSource,
)


# --- Task Schemas ---

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    structural_flag: bool = False
    priority: Optional[str] = None
    source: TaskSource = TaskSource.MANUAL


class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    status: TaskStatus
    structural_flag: bool
    priority: Optional[str] = None
    source: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# --- Approval Schemas ---

class ApprovalCreate(BaseModel):
    task_id: UUID
    requested_by: Optional[str] = None


class ApprovalResponse(BaseModel):
    id: UUID
    task_id: UUID
    result: ApprovalResult
    requested_by: Optional[str] = None
    decided_by: Optional[str] = None
    note: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# --- Error Schemas ---

class ErrorCreate(BaseModel):
    environment: Optional[str] = None
    module: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[Severity] = None
    source_layer: Optional[str] = None
    trigger_action: Optional[str] = None
    summary: Optional[str] = None
    raw_detail: Optional[str] = None
    probable_cause: Optional[str] = None


class ErrorResponse(BaseModel):
    id: UUID
    timestamp: datetime
    environment: Optional[str] = None
    module: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[Severity] = None
    summary: Optional[str] = None
    status: Optional[str] = None
    created_at: datetime


# --- Improvement Task Schemas ---

class ImprovementTaskCreate(BaseModel):
    title: str
    error_summary: Optional[str] = None
    proposed_fix: Optional[str] = None
    priority: Optional[str] = None
    structural_flag: bool = True
    source_error_id: Optional[UUID] = None


class ImprovementTaskResponse(BaseModel):
    id: UUID
    title: str
    error_summary: Optional[str] = None
    proposed_fix: Optional[str] = None
    priority: Optional[str] = None
    structural_flag: bool
    status: TaskStatus
    source_error_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
