"""Error learning service — processes Sentry webhooks into improvement tasks."""

import logging

from app.core.config import settings
from app.core.database import get_supabase_client
from app.services import ai_service, task_orchestrator, telegram_service

logger = logging.getLogger(__name__)


async def process_sentry_webhook(payload: dict) -> dict:
    """Process a Sentry webhook payload.

    1. Extract error details
    2. Get AI summary + proposed fix
    3. Create an improvement task
    4. Send Telegram notification

    Returns the created improvement task dict.
    """
    # Extract error details from Sentry payload
    error_data = _extract_sentry_error(payload)

    # Store the raw error
    client = get_supabase_client()
    error_record = (
        client.table("errors")
        .insert(
            {
                "environment": error_data.get("environment"),
                "module": error_data.get("module"),
                "category": "integration",
                "severity": error_data.get("severity", "high"),
                "summary": error_data.get("message"),
                "raw_detail": str(payload)[:5000],
                "status": "open",
            }
        )
        .execute()
    )
    error_id = error_record.data[0]["id"] if error_record.data else None

    # Get AI summary
    ai_result = await ai_service.summarize_error(error_data)
    summary = ai_result.get("summary", error_data.get("message", "Unknown error"))
    proposed_fix = ai_result.get("proposed_fix", "Investigate error logs.")

    # Create improvement task
    improvement = (
        client.table("improvement_tasks")
        .insert(
            {
                "title": f"Fix: {summary[:80]}",
                "error_summary": summary,
                "proposed_fix": proposed_fix,
                "priority": error_data.get("severity", "high"),
                "structural_flag": True,
                "status": "draft",
                "source_error_id": error_id,
            }
        )
        .execute()
    )

    # Also create a regular task for tracking
    await task_orchestrator.create_task(
        user_id="system",
        title=f"[Error] {summary[:80]}",
        description=f"Summary: {summary}\n\nProposed fix: {proposed_fix}",
        priority=error_data.get("severity", "high"),
        source="error_auto",
    )

    # Send Telegram notification
    chat_id = settings.telegram_chat_id
    if chat_id:
        await telegram_service.send_notification(
            chat_id,
            f"<b>Error Detected</b>\n\n"
            f"<b>Summary:</b> {summary}\n\n"
            f"<b>Proposed Fix:</b> {proposed_fix}\n\n"
            f"<b>Environment:</b> {error_data.get('environment', 'unknown')}",
        )

    return improvement.data[0] if improvement.data else {}


def _extract_sentry_error(payload: dict) -> dict:
    """Extract relevant fields from a Sentry webhook payload."""
    event = payload.get("event", payload.get("data", {}).get("event", {}))
    return {
        "message": event.get("title", event.get("message", "Unknown error")),
        "environment": event.get("environment", "production"),
        "module": event.get("culprit", event.get("transaction", "")),
        "severity": _sentry_level_to_severity(event.get("level", "error")),
        "platform": event.get("platform", ""),
        "timestamp": event.get("timestamp", ""),
    }


def _sentry_level_to_severity(level: str) -> str:
    """Map Sentry level to our severity enum."""
    mapping = {
        "fatal": "critical",
        "error": "high",
        "warning": "medium",
        "info": "low",
        "debug": "low",
    }
    return mapping.get(level, "medium")
