"""Task REST endpoints for String Free."""

from fastapi import APIRouter, HTTPException, Query

from app.models.enums import TaskSource
from app.models.schemas import TaskCreate, TaskUpdate
from app.services import task_orchestrator

router = APIRouter()


@router.get("/")
async def list_tasks(
    user_id: str = Query(default="default"),
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[dict]:
    """List tasks for a user with optional status filter."""
    return await task_orchestrator.list_tasks(
        user_id=user_id,
        status_filter=status,
        limit=limit,
        offset=offset,
    )


@router.post("/", status_code=201)
async def create_task(body: TaskCreate) -> dict:
    """Create a new task."""
    return await task_orchestrator.create_task(
        user_id="default",
        title=body.title,
        description=body.description,
        priority=body.priority,
        source=body.source or TaskSource.API,
    )


@router.get("/{task_id}")
async def get_task(task_id: str) -> dict:
    """Get a single task by ID."""
    task = await task_orchestrator.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}")
async def update_task(task_id: str, body: TaskUpdate) -> dict:
    """Update task fields."""
    updates = body.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = await task_orchestrator.update_task(task_id, updates)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return result


@router.delete("/{task_id}")
async def delete_task(task_id: str) -> dict:
    """Soft-delete a task (archive it)."""
    result = await task_orchestrator.delete_task(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "archived", "id": task_id}
