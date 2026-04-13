"""Telegram bot service for String Free."""

import logging

import httpx

from app.core.config import settings
from app.core.database import get_supabase_client
from app.models.enums import TaskSource
from app.services import ai_service, task_orchestrator

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot{token}"


def _api_url(method: str) -> str:
    return f"{TELEGRAM_API.format(token=settings.telegram_bot_token)}/{method}"


async def send_message(chat_id: str | int, text: str, reply_markup: dict | None = None) -> dict:
    """Send a Telegram message. Returns the API response."""
    payload: dict = {"chat_id": str(chat_id), "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    async with httpx.AsyncClient() as client:
        resp = await client.post(_api_url("sendMessage"), json=payload)
        return resp.json()  # type: ignore[no-any-return]


async def send_notification(chat_id: str | int, message: str) -> dict:
    """Convenience wrapper to send a plain notification."""
    return await send_message(chat_id, message)


async def answer_callback_query(callback_query_id: str, text: str = "") -> dict:
    """Answer an inline keyboard callback."""
    payload = {"callback_query_id": callback_query_id, "text": text}
    async with httpx.AsyncClient() as client:
        resp = await client.post(_api_url("answerCallbackQuery"), json=payload)
        return resp.json()  # type: ignore[no-any-return]


async def edit_message_text(
    chat_id: str | int, message_id: int, text: str, reply_markup: dict | None = None
) -> dict:
    """Edit an existing Telegram message."""
    payload: dict = {
        "chat_id": str(chat_id),
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML",
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    async with httpx.AsyncClient() as client:
        resp = await client.post(_api_url("editMessageText"), json=payload)
        return resp.json()  # type: ignore[no-any-return]


def _task_approval_keyboard(task_id: str) -> dict:
    """Build an inline keyboard for task approval."""
    return {
        "inline_keyboard": [
            [
                {"text": "Approve", "callback_data": f"approve:{task_id}"},
                {"text": "Reject", "callback_data": f"reject:{task_id}"},
                {"text": "Edit Priority", "callback_data": f"editprio:{task_id}"},
            ]
        ]
    }


async def handle_command(update: dict) -> None:
    """Process a Telegram bot command from an update."""
    message = update.get("message", {})
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")
    user_id = str(message.get("from", {}).get("id", ""))

    if not chat_id or not text:
        return

    client = get_supabase_client()

    if text.startswith("/start"):
        await send_message(
            chat_id,
            "<b>Welcome to String Free!</b>\n\n"
            "I help you manage tasks with AI.\n\n"
            "<b>Commands:</b>\n"
            "/task &lt;message&gt; — Create a task from text\n"
            "/list — Show active tasks\n"
            "/done &lt;id&gt; — Complete a task\n"
            "/help — Show this guide",
        )

    elif text.startswith("/task "):
        raw = text[6:].strip()
        if not raw:
            await send_message(chat_id, "Please provide a task description after /task")
            return
        parsed = await ai_service.parse_text_to_task(raw)
        task = await task_orchestrator.create_task(
            user_id=user_id,
            title=parsed.get("title", raw[:100]),
            description=parsed.get("description"),
            priority=parsed.get("priority", "medium"),
            source=TaskSource.TELEGRAM,
        )
        task_id = task.get("id", "unknown")
        await send_message(
            chat_id,
            f"<b>New Task Created</b>\n"
            f"<b>Title:</b> {parsed.get('title', raw[:100])}\n"
            f"<b>Priority:</b> {parsed.get('priority', 'medium')}\n"
            f"<b>ID:</b> <code>{task_id}</code>",
            reply_markup=_task_approval_keyboard(str(task_id)),
        )

    elif text.startswith("/list"):
        tasks = await task_orchestrator.list_tasks(user_id=user_id, limit=10)
        if not tasks:
            await send_message(chat_id, "No active tasks found.")
            return
        lines = []
        for t in tasks:
            status = t.get("status", "draft")
            title = t.get("title", "Untitled")
            tid = str(t.get("id", ""))[:8]
            lines.append(f"• [{status}] {title} (<code>{tid}</code>)")
        await send_message(chat_id, "<b>Your Tasks:</b>\n" + "\n".join(lines))

    elif text.startswith("/done "):
        task_id = text[6:].strip()
        if not task_id:
            await send_message(chat_id, "Please provide a task ID after /done")
            return
        result = await task_orchestrator.complete_task(task_id)
        if result:
            await send_message(chat_id, f"Task <code>{task_id[:8]}</code> marked as completed!")
        else:
            await send_message(chat_id, f"Task <code>{task_id[:8]}</code> not found.")

    elif text.startswith("/help"):
        await send_message(
            chat_id,
            "<b>String Free Commands:</b>\n\n"
            "/start — Welcome message\n"
            "/task &lt;message&gt; — AI parses your message into a task\n"
            "/list — Show your active tasks\n"
            "/done &lt;id&gt; — Mark a task as complete\n"
            "/opportunities — List income opportunities\n"
            "/opportunity &lt;id&gt; — Get details on an opportunity\n"
            "/pursue &lt;id&gt; — Mark opportunity as pursuing\n"
            "/help — Show this reference",
        )

    elif text.startswith("/opportunities"):
        # Fetch opportunities for user
        response = (
            client.table("income_opportunities")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(10)
            .execute()
        )

        if not response.data:
            await send_message(
                chat_id,
                "<b>No Opportunities Found</b>\n\n"
                "Use /task to create tasks. I'll analyze them and suggest income opportunities!",
            )
            return

        lines = ["<b>💰 Your Income Opportunities:</b>\n"]
        for opp in response.data:
            status = opp.get("status", "identified")
            title = opp.get("title", "Untitled")[:50]
            opp_id = str(opp.get("id", ""))[:8]
            confidence = opp.get("confidence_score", 0.0)
            lines.append(
                f"• [{status}] {title}\n  Confidence: {confidence:.0%} | ID: <code>{opp_id}</code>"
            )

        await send_message(chat_id, "\n".join(lines))

    elif text.startswith("/opportunity "):
        opp_id = text[13:].strip()
        if not opp_id:
            await send_message(chat_id, "Please provide an opportunity ID")
            return

        response = (
            client.table("income_opportunities")
            .select("*")
            .eq("id", opp_id)
            .single()
            .execute()
        )

        if not response.data:
            await send_message(chat_id, f"Opportunity <code>{opp_id[:8]}</code> not found.")
            return

        opp = response.data
        message_text = (
            f"<b>💡 Opportunity Details</b>\n\n"
            f"<b>Title:</b> {opp.get('title', 'Untitled')}\n"
            f"<b>Type:</b> {opp.get('opportunity_type', 'unknown')}\n"
            f"<b>Status:</b> {opp.get('status', 'identified')}\n"
            f"<b>Confidence:</b> {opp.get('confidence_score', 0.0):.0%}\n\n"
            f"<b>Description:</b>\n{opp.get('description', 'No description')}\n\n"
            f"<b>Effort:</b> {opp.get('estimated_effort', 'unknown')}\n"
            f"<b>Revenue Potential:</b> {opp.get('estimated_revenue_potential', 'unknown')}"
        )

        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "Pursue", "callback_data": f"pursue_opp:{opp_id}"},
                    {"text": "Dismiss", "callback_data": f"dismiss_opp:{opp_id}"},
                ]
            ]
        }

        await send_message(chat_id, message_text, reply_markup=keyboard)

    elif text.startswith("/pursue "):
        opp_id = text[8:].strip()
        if not opp_id:
            await send_message(chat_id, "Please provide an opportunity ID")
            return

        response = (
            client.table("income_opportunities")
            .update({"status": "pursuing", "updated_at": "now()"})
            .eq("id", opp_id)
            .execute()
        )

        if response.data:
            await send_message(
                chat_id, f"✅ Opportunity <code>{opp_id[:8]}</code> marked as pursuing!"
            )
        else:
            await send_message(chat_id, f"Opportunity <code>{opp_id[:8]}</code> not found.")

    elif text.startswith("/help"):
        await send_message(
            chat_id,
            "<b>String Free Commands:</b>\n\n"
            "/start — Welcome message\n"
            "/task &lt;message&gt; — AI parses your message into a task\n"
            "/list — Show your active tasks\n"
            "/done &lt;id&gt; — Mark a task as complete\n"
            "/opportunities — List income opportunities\n"
            "/opportunity &lt;id&gt; — Get details on an opportunity\n"
            "/pursue &lt;id&gt; — Mark opportunity as pursuing\n"
            "/help — Show this reference",
        )


async def handle_callback_query(update: dict) -> None:
    """Process inline keyboard button presses."""
    callback = update.get("callback_query", {})
    data = callback.get("data", "")
    callback_id = callback.get("id", "")
    message = callback.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")

    if not data or not chat_id:
        return

    client = get_supabase_client()
    action, _, task_id = data.partition(":")

    if action == "approve":
        await task_orchestrator.update_task(task_id, {"status": "approved"})
        await edit_message_text(
            chat_id, message_id, f"Task <code>{task_id[:8]}</code> — <b>Approved</b>"
        )
        await answer_callback_query(callback_id, "Task approved!")

    elif action == "reject":
        await task_orchestrator.update_task(task_id, {"status": "archived"})
        await edit_message_text(
            chat_id, message_id, f"Task <code>{task_id[:8]}</code> — <b>Rejected</b>"
        )
        await answer_callback_query(callback_id, "Task rejected.")

    elif action == "editprio":
        await edit_message_text(
            chat_id,
            message_id,
            f"Task <code>{task_id[:8]}</code> — Choose priority:",
            reply_markup={
                "inline_keyboard": [
                    [
                        {"text": "Low", "callback_data": f"setprio:low:{task_id}"},
                        {"text": "Medium", "callback_data": f"setprio:medium:{task_id}"},
                        {"text": "High", "callback_data": f"setprio:high:{task_id}"},
                        {"text": "Critical", "callback_data": f"setprio:critical:{task_id}"},
                    ]
                ]
            },
        )
        await answer_callback_query(callback_id)

    elif action == "setprio":
        # data format: setprio:<priority>:<task_id>
        parts = data.split(":", 2)
        if len(parts) == 3:
            priority = parts[1]
            tid = parts[2]
            await task_orchestrator.update_task(tid, {"priority": priority})
            await edit_message_text(
                chat_id,
                message_id,
                f"Task <code>{tid[:8]}</code> — Priority set to <b>{priority}</b>",
            )
            await answer_callback_query(callback_id, f"Priority → {priority}")

    elif action == "pursue_opp":
        # Mark opportunity as pursuing
        client.table("income_opportunities").update(
            {"status": "pursuing", "updated_at": "now()"}
        ).eq("id", task_id).execute()

        await edit_message_text(
            chat_id,
            message_id,
            f"✅ Opportunity <code>{task_id[:8]}</code> — Now <b>Pursuing</b>",
        )
        await answer_callback_query(callback_id, "Marked as pursuing!")

    elif action == "dismiss_opp":
        # Mark opportunity as dismissed
        client.table("income_opportunities").update(
            {"status": "dismissed", "updated_at": "now()"}
        ).eq("id", task_id).execute()

        await edit_message_text(
            chat_id,
            message_id,
            f"❌ Opportunity <code>{task_id[:8]}</code> — <b>Dismissed</b>",
        )
        await answer_callback_query(callback_id, "Opportunity dismissed.")


async def process_update(update: dict) -> None:
    """Route a Telegram update to the appropriate handler."""
    if "callback_query" in update:
        await handle_callback_query(update)
    elif "message" in update:
        await handle_command(update)
