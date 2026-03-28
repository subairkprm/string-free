"""Task engine — CRUD operations for tasks via Supabase."""

import logging
from uuid import UUID

from app.core.database import get_supabase_client
from app.models.enums import TaskSource, TaskStatus

logger = logging.getLogger(__name__)


async def create_task(
    user_id: str,
    title: str,
    description: str | None = None,
    priority: str | None = None,
    source: TaskSource = TaskSource.MANUAL,
) -> dict:
    """Create a new task in Supabase and return the created record."""
    client = get_supabase_client()
    payload: dict = {
        "title": title,
        "description": description,
        "priority": priority,
        "source": source.value,
        "status": TaskStatus.DRAFT.value,
    }
    # Include user_id if the tasks table supports it
    if user_id:
        payload["user_id"] = user_id

    result = client.table("tasks").insert(payload).execute()
    logger.info("Task created: %s", result.data[0]["id"] if result.data else "unknown")
    return result.data[0] if result.data else {}


async def update_task(task_id: str | UUID, updates: dict) -> dict:
    """Update task fields. Returns the updated record."""
    client = get_supabase_client()
    result = client.table("tasks").update(updates).eq("id", str(task_id)).execute()
    return result.data[0] if result.data else {}


async def list_tasks(
    user_id: str,
    status_filter: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """List tasks for a user, optionally filtered by status."""
    client = get_supabase_client()
    query = client.table("tasks").select("*").eq("user_id", user_id)

    if status_filter:
        query = query.eq("status", status_filter)

    query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
    result = query.execute()
    return result.data or []


async def complete_task(task_id: str | UUID) -> dict:
    """Mark a task as completed."""
    return await update_task(task_id, {"status": TaskStatus.COMPLETED.value})


async def delete_task(task_id: str | UUID) -> dict:
    """Soft-delete a task by setting status to archived."""
    return await update_task(task_id, {"status": TaskStatus.ARCHIVED.value})


async def get_task(task_id: str | UUID) -> dict | None:
    """Fetch a single task by ID."""
    client = get_supabase_client()
    result = client.table("tasks").select("*").eq("id", str(task_id)).limit(1).execute()
    return result.data[0] if result.data else None
