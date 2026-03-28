"""Tests for AI service with mocked Gemini responses."""

from unittest.mock import MagicMock, patch

import pytest

from app.services.ai_service import parse_text_to_task, summarize_error


@pytest.fixture
def mock_gemini():
    """Mock the Gemini generative model."""
    with patch("app.services.ai_service._get_model") as mock:
        mock_model = MagicMock()
        mock.return_value = mock_model
        yield mock_model


class TestParseTextToTask:
    @pytest.mark.asyncio
    async def test_parse_returns_structured_task(self, mock_gemini):
        mock_response = MagicMock()
        mock_response.text = (
            '{"title": "Fix login bug", "description": "Users cannot log in", '
            '"priority": "high", "due_date": null, "tags": ["bug", "auth"]}'
        )
        mock_gemini.generate_content.return_value = mock_response

        result = await parse_text_to_task("fix the login bug, users can't log in")
        assert result["title"] == "Fix login bug"
        assert result["priority"] == "high"
        assert "bug" in result["tags"]

    @pytest.mark.asyncio
    async def test_parse_handles_markdown_fencing(self, mock_gemini):
        mock_response = MagicMock()
        mock_response.text = (
            '```json\n{"title": "Deploy v2", "description": "Ship version 2", '
            '"priority": "medium", "due_date": null, "tags": []}\n```'
        )
        mock_gemini.generate_content.return_value = mock_response

        result = await parse_text_to_task("deploy version 2")
        assert result["title"] == "Deploy v2"

    @pytest.mark.asyncio
    async def test_parse_returns_fallback_on_error(self, mock_gemini):
        mock_gemini.generate_content.side_effect = Exception("API error")

        result = await parse_text_to_task("some task text")
        assert result["title"] == "some task text"
        assert result["priority"] == "medium"
        assert result["tags"] == []


class TestSummarizeError:
    @pytest.mark.asyncio
    async def test_summarize_returns_summary(self, mock_gemini):
        mock_response = MagicMock()
        mock_response.text = (
            '{"summary": "NullPointerException in user service", '
            '"proposed_fix": "Add null check before accessing user.name"}'
        )
        mock_gemini.generate_content.return_value = mock_response

        result = await summarize_error(
            {"message": "NullPointerException", "module": "user_service"}
        )
        assert "NullPointerException" in result["summary"]
        assert "null check" in result["proposed_fix"]

    @pytest.mark.asyncio
    async def test_summarize_returns_fallback_on_error(self, mock_gemini):
        mock_gemini.generate_content.side_effect = Exception("API error")

        result = await summarize_error({"message": "Something broke"})
        assert result["summary"] == "Something broke"
        assert "Investigate" in result["proposed_fix"]
