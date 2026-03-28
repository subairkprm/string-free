"""Telegram webhook endpoint for String Free."""

import logging

from fastapi import APIRouter, BackgroundTasks, Request

from app.services import telegram_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks) -> dict:
    """Receive Telegram updates and process them asynchronously."""
    update = await request.json()
    background_tasks.add_task(telegram_service.process_update, update)
    return {"ok": True}
