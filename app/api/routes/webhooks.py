"""External webhook endpoints for Sentry and Lemon Squeezy billing."""

import logging

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request

from app.core import billing
from app.services import error_analyzer

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/sentry")
async def sentry_webhook(request: Request, background_tasks: BackgroundTasks) -> dict:
    """Receive Sentry alert webhooks and route to error analyzer."""
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc

    background_tasks.add_task(error_analyzer.process_sentry_webhook, payload)
    return {"status": "accepted"}


@router.post("/billing")
async def billing_webhook(
    request: Request,
    x_signature: str | None = Header(default=None, alias="X-Signature"),
) -> dict:
    """Receive Lemon Squeezy billing webhooks."""
    body = await request.body()

    # Verify signature if secret is configured
    if x_signature and not billing.verify_webhook_signature(body, x_signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc

    event_name = payload.get("meta", {}).get("event_name", "")
    if not event_name:
        raise HTTPException(status_code=400, detail="Missing event_name in payload")

    await billing.process_billing_webhook(event_name, payload)
    return {"status": "accepted", "event": event_name}
