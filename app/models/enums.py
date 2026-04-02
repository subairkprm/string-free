"""Domain enums for String Free, mirroring Supabase DB enums."""

from enum import StrEnum


class TaskStatus(StrEnum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    INPROGRESS = "inprogress"
    BLOCKED = "blocked"
    REVIEW = "review"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(StrEnum):
    ARCHITECTURE = "architecture"
    LOGIC = "logic"
    VALIDATION = "validation"
    UIUX = "uiux"
    INTEGRATION = "integration"
    MCP = "mcp"
    ENVIRONMENT = "environment"
    DATA = "data"
    WORKFLOW = "workflow"


class ApprovalResult(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class TaskSource(StrEnum):
    TELEGRAM = "telegram"
    API = "api"
    ERROR_AUTO = "error_auto"
    MANUAL = "manual"


class PlanTier(StrEnum):
    FREE = "free"
    SOLO = "solo"
    PRO = "pro"
    TEAM = "team"


class OpportunityType(StrEnum):
    MONETIZATION = "monetization"
    CONSULTING = "consulting"
    SAAS = "saas"
    MARKETPLACE = "marketplace"
    AFFILIATE = "affiliate"
    EDUCATION = "education"


class OpportunityStatus(StrEnum):
    IDENTIFIED = "identified"
    EVALUATING = "evaluating"
    PURSUING = "pursuing"
    IMPLEMENTED = "implemented"
    DISMISSED = "dismissed"
