"""Gemini AI service for task parsing and error summarization."""

import json
import logging

import google.generativeai as genai

from app.core.config import settings

logger = logging.getLogger(__name__)

_TASK_PARSE_PROMPT = (
    "You are a task parsing assistant. Extract a structured task from the user's message. "
    "Return JSON with: title, description, priority (low/medium/high/critical), "
    "due_date (ISO format or null), tags (list of strings). "
    "Return ONLY valid JSON, no markdown fencing."
)

_ERROR_SUMMARY_PROMPT = (
    "You are a software error analyst. Given the following error payload, provide: "
    "1) A concise human-readable summary of what went wrong. "
    "2) A proposed fix or investigation step. "
    "Return JSON with: summary, proposed_fix. Return ONLY valid JSON, no markdown fencing."
)

_MAX_RETRIES = 2


def _get_model() -> genai.GenerativeModel:
    """Configure and return the Gemini model."""
    genai.configure(api_key=settings.gemini_api_key)
    return genai.GenerativeModel("gemini-1.5-flash")


async def parse_text_to_task(raw_text: str) -> dict:
    """Send text to Gemini and return a structured task dict.

    Returns dict with keys: title, description, priority, due_date, tags.
    On failure, returns a fallback dict built from the raw text.
    """
    model = _get_model()
    for attempt in range(_MAX_RETRIES + 1):
        try:
            response = model.generate_content(
                [
                    {"role": "user", "parts": [_TASK_PARSE_PROMPT]},
                    {"role": "model", "parts": ["Understood. Send me the message to parse."]},
                    {"role": "user", "parts": [raw_text]},
                ]
            )
            text = response.text.strip()
            # Strip markdown fencing if present
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
            return json.loads(text)  # type: ignore[no-any-return]
        except (json.JSONDecodeError, Exception) as e:
            logger.warning("AI parse attempt %d failed: %s", attempt + 1, e)
            if attempt == _MAX_RETRIES:
                logger.error("All AI parse retries exhausted, returning fallback")
                return {
                    "title": raw_text[:100],
                    "description": raw_text,
                    "priority": "medium",
                    "due_date": None,
                    "tags": [],
                }
    return {}  # unreachable but satisfies type checker


async def summarize_error(error_payload: dict) -> dict:
    """Take Sentry error data and return a summary + proposed fix.

    Returns dict with keys: summary, proposed_fix.
    """
    model = _get_model()
    payload_str = json.dumps(error_payload, default=str)[:4000]  # Truncate for token limits
    for attempt in range(_MAX_RETRIES + 1):
        try:
            response = model.generate_content(
                [
                    {"role": "user", "parts": [_ERROR_SUMMARY_PROMPT]},
                    {"role": "model", "parts": ["Ready. Send me the error payload."]},
                    {"role": "user", "parts": [payload_str]},
                ]
            )
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
            return json.loads(text)  # type: ignore[no-any-return]
        except (json.JSONDecodeError, Exception) as e:
            logger.warning("AI error summary attempt %d failed: %s", attempt + 1, e)
            if attempt == _MAX_RETRIES:
                logger.error("All AI summary retries exhausted, returning fallback")
                return {
                    "summary": error_payload.get("message", "Unknown error"),
                    "proposed_fix": "Investigate the error logs for more details.",
                }
    return {}  # unreachable but satisfies type checker
