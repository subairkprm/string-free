"""Domain enums for String Free, mirroring Supabase DB enums."""

from enum import Enum


class TaskStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    INPROGRESS = "inprogress"
    BLOCKED = "blocked"
    REVIEW = "review"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    ARCHITECTURE = "architecture"
    LOGIC = "logic"
    VALIDATION = "validation"
    UIUX = "uiux"
    INTEGRATION = "integration"
    MCP = "mcp"
    ENVIRONMENT = "environment"
    DATA = "data"
    WORKFLOW = "workflow"


class ApprovalResult(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class TaskSource(str, Enum):
    TELEGRAM = "telegram"
    API = "api"
    ERROR_AUTO = "error_auto"
    MANUAL = "manual"
