"""AI service for income opportunity detection and analysis."""

import json
import logging
from datetime import datetime, timedelta
from uuid import UUID

import google.generativeai as genai

from app.core.config import settings

logger = logging.getLogger(__name__)

_OPPORTUNITY_DETECTION_PROMPT = (
    "You are a business opportunity analyst for software developers and indie hackers. "
    "Analyze the following task data and identify potential income opportunities. "
    "Consider: monetization potential, consulting opportunities, SaaS products, "
    "marketplace items (templates, tools, packages), educational content, or affiliate partnerships. "
    "Return JSON with: opportunities (array), each containing: "
    "type (monetization/consulting/saas/marketplace/affiliate/education), "
    "title (short, clear), description (2-3 sentences), "
    "confidence_score (0.0-1.0, be realistic), reasoning (why this is viable), "
    "estimated_effort (low/medium/high), revenue_potential (low/medium/high). "
    "Only suggest realistic opportunities based on actual work patterns. "
    "Return ONLY valid JSON, no markdown fencing."
)

_PATTERN_ANALYSIS_PROMPT = (
    "You are analyzing a developer's work patterns and task history. "
    "Given these tasks over time, identify valuable patterns: "
    "1) Recurring skills or technical domains (e.g., always building REST APIs, ML models) "
    "2) Market gaps or pain points they repeatedly solve "
    "3) Tools, libraries, or processes they've built that others might need "
    "4) Emerging expertise areas worth monetizing (e.g., specialization in a framework). "
    "Return JSON with: patterns (array), each with: "
    "pattern_type (skill_trend/market_gap/tool_opportunity/emerging_expertise), "
    "description (what the pattern is), "
    "opportunity_suggestion (how to monetize it), "
    "confidence_score (0.0-1.0). "
    "Return ONLY valid JSON, no markdown fencing."
)

_MAX_RETRIES = 2


def _get_model() -> genai.GenerativeModel:
    """Configure and return the Gemini model."""
    genai.configure(api_key=settings.gemini_api_key)
    return genai.GenerativeModel("gemini-1.5-flash")


async def analyze_task_for_opportunities(task_data: dict) -> dict:
    """Analyze a single task for income opportunity signals.

    Args:
        task_data: Dict with task details (title, description, tags, etc.)

    Returns:
        Dict with opportunities array or empty result on failure.
    """
    model = _get_model()
    task_str = json.dumps(task_data, default=str)[:2000]

    for attempt in range(_MAX_RETRIES + 1):
        try:
            response = model.generate_content(
                [
                    {"role": "user", "parts": [_OPPORTUNITY_DETECTION_PROMPT]},
                    {
                        "role": "model",
                        "parts": ["Understood. Send me the task data to analyze."],
                    },
                    {"role": "user", "parts": [task_str]},
                ]
            )
            text = response.text.strip()

            # Strip markdown fencing if present
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()

            result = json.loads(text)
            return result  # type: ignore[no-any-return]

        except (json.JSONDecodeError, Exception) as e:
            logger.warning(
                "AI opportunity analysis attempt %d failed: %s", attempt + 1, e
            )
            if attempt == _MAX_RETRIES:
                logger.error("All opportunity analysis retries exhausted")
                return {"opportunities": []}

    return {"opportunities": []}


async def analyze_task_patterns(tasks_data: list[dict]) -> dict:
    """Analyze patterns across multiple tasks to identify trends.

    Args:
        tasks_data: List of task dicts with details

    Returns:
        Dict with patterns array or empty result on failure.
    """
    model = _get_model()

    # Summarize tasks for token efficiency
    tasks_summary = []
    for task in tasks_data[:50]:  # Limit to recent 50 tasks
        tasks_summary.append(
            {
                "title": task.get("title", ""),
                "description": task.get("description", "")[:200],
                "priority": task.get("priority", ""),
                "created_at": str(task.get("created_at", "")),
            }
        )

    tasks_str = json.dumps(tasks_summary, default=str)[:4000]

    for attempt in range(_MAX_RETRIES + 1):
        try:
            response = model.generate_content(
                [
                    {"role": "user", "parts": [_PATTERN_ANALYSIS_PROMPT]},
                    {
                        "role": "model",
                        "parts": ["Ready. Send me the task history to analyze."],
                    },
                    {"role": "user", "parts": [tasks_str]},
                ]
            )
            text = response.text.strip()

            # Strip markdown fencing if present
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()

            result = json.loads(text)
            return result  # type: ignore[no-any-return]

        except (json.JSONDecodeError, Exception) as e:
            logger.warning("AI pattern analysis attempt %d failed: %s", attempt + 1, e)
            if attempt == _MAX_RETRIES:
                logger.error("All pattern analysis retries exhausted")
                return {"patterns": []}

    return {"patterns": []}


async def evaluate_opportunity_viability(opportunity_data: dict) -> dict:
    """Evaluate and score an opportunity suggestion.

    Args:
        opportunity_data: Dict with opportunity details

    Returns:
        Dict with viability score and feedback.
    """
    # For now, return the data as-is
    # In future, could add market research, competition analysis, etc.
    return {
        "viable": opportunity_data.get("confidence_score", 0.0) >= 0.6,
        "score": opportunity_data.get("confidence_score", 0.0),
        "feedback": "Opportunity meets minimum confidence threshold."
        if opportunity_data.get("confidence_score", 0.0) >= 0.6
        else "Low confidence - needs more validation.",
    }
