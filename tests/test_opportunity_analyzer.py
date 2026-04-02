"""Tests for income opportunity analyzer service."""

import pytest

from app.services import opportunity_analyzer


@pytest.mark.asyncio
async def test_analyze_task_for_opportunities_returns_dict():
    """Test that analyze_task_for_opportunities returns a dict."""
    task_data = {
        "title": "Build REST API for user management",
        "description": "Create FastAPI endpoints for CRUD operations on users",
        "priority": "high",
        "tags": ["api", "backend", "fastapi"],
    }

    result = await opportunity_analyzer.analyze_task_for_opportunities(task_data)

    assert isinstance(result, dict)
    assert "opportunities" in result


@pytest.mark.asyncio
async def test_analyze_task_patterns_returns_dict():
    """Test that analyze_task_patterns returns a dict."""
    tasks_data = [
        {
            "title": "Build React dashboard",
            "description": "Create admin panel with charts",
            "created_at": "2024-01-01T00:00:00Z",
        },
        {
            "title": "Build React form",
            "description": "User registration form",
            "created_at": "2024-01-15T00:00:00Z",
        },
        {
            "title": "Build React table",
            "description": "Data table with sorting",
            "created_at": "2024-02-01T00:00:00Z",
        },
    ]

    result = await opportunity_analyzer.analyze_task_patterns(tasks_data)

    assert isinstance(result, dict)
    assert "patterns" in result


@pytest.mark.asyncio
async def test_evaluate_opportunity_viability():
    """Test opportunity viability evaluation."""
    opportunity_data = {
        "confidence_score": 0.75,
        "title": "Test Opportunity",
        "type": "consulting",
    }

    result = await opportunity_analyzer.evaluate_opportunity_viability(opportunity_data)

    assert isinstance(result, dict)
    assert "viable" in result
    assert "score" in result
    assert result["viable"] is True  # 0.75 >= 0.6
    assert result["score"] == 0.75


@pytest.mark.asyncio
async def test_evaluate_opportunity_viability_low_confidence():
    """Test viability evaluation with low confidence."""
    opportunity_data = {
        "confidence_score": 0.4,
        "title": "Low Confidence Opportunity",
    }

    result = await opportunity_analyzer.evaluate_opportunity_viability(opportunity_data)

    assert result["viable"] is False  # 0.4 < 0.6
    assert result["score"] == 0.4


def test_get_model():
    """Test that _get_model returns a Gemini model instance."""
    model = opportunity_analyzer._get_model()
    assert model is not None
    # Check it's the expected model type
    assert hasattr(model, "generate_content")
