"""API routes for income opportunity analysis."""

import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.core.database import get_supabase_client
from app.models.schemas import (
    OpportunityAnalysisRequest,
    OpportunityCreate,
    OpportunityRatingRequest,
    OpportunityResponse,
    OpportunityUpdate,
)
from app.services import opportunity_analyzer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.get("/", response_model=list[OpportunityResponse])
async def list_opportunities(
    user_id: str,
    status: str | None = None,
    opportunity_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[OpportunityResponse]:
    """List income opportunities for a user."""
    try:
        client = get_supabase_client()
        query = client.table("income_opportunities").select("*").eq("user_id", user_id)

        if status:
            query = query.eq("status", status)
        if opportunity_type:
            query = query.eq("opportunity_type", opportunity_type)

        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)

        response = query.execute()
        return [OpportunityResponse(**row) for row in response.data]

    except Exception as e:
        logger.error("Failed to list opportunities: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch opportunities")


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(opportunity_id: UUID) -> OpportunityResponse:
    """Get a single opportunity by ID."""
    try:
        client = get_supabase_client()
        response = (
            client.table("income_opportunities")
            .select("*")
            .eq("id", str(opportunity_id))
            .single()
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Opportunity not found")

        return OpportunityResponse(**response.data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get opportunity: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch opportunity")


@router.post("/analyze")
async def analyze_opportunities(
    user_id: str, request: OpportunityAnalysisRequest
) -> dict:
    """Trigger analysis of recent tasks for income opportunities."""
    try:
        # Fetch recent tasks for the user
        from datetime import datetime, timedelta

        client = get_supabase_client()
        cutoff_date = datetime.now() - timedelta(days=request.days)

        tasks_response = (
            client.table("tasks")
            .select("*")
            .gte("created_at", cutoff_date.isoformat())
            .order("created_at", desc=True)
            .execute()
        )

        if not tasks_response.data:
            return {
                "status": "no_tasks",
                "message": "No tasks found in the specified period",
                "opportunities_created": 0,
            }

        # Analyze patterns across tasks
        pattern_analysis = await opportunity_analyzer.analyze_task_patterns(
            tasks_response.data
        )

        opportunities_created = 0

        # Create opportunities from patterns
        for pattern in pattern_analysis.get("patterns", []):
            if pattern.get("confidence_score", 0.0) >= 0.6:
                opportunity_data = {
                    "user_id": user_id,
                    "title": f"{pattern.get('pattern_type', 'Opportunity')}: {pattern.get('description', '')[:50]}",
                    "description": pattern.get("opportunity_suggestion", ""),
                    "opportunity_type": _map_pattern_to_type(
                        pattern.get("pattern_type", "")
                    ),
                    "confidence_score": pattern.get("confidence_score", 0.0),
                    "estimated_effort": "medium",
                    "estimated_revenue_potential": "medium",
                    "ai_reasoning": pattern.get("description", ""),
                }

                client.table("income_opportunities").insert(opportunity_data).execute()
                opportunities_created += 1

        return {
            "status": "success",
            "message": f"Analysis complete for {len(tasks_response.data)} tasks",
            "opportunities_created": opportunities_created,
            "patterns_identified": len(pattern_analysis.get("patterns", [])),
        }

    except Exception as e:
        logger.error("Failed to analyze opportunities: %s", e)
        raise HTTPException(status_code=500, detail="Failed to analyze opportunities")


@router.patch("/{opportunity_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opportunity_id: UUID, update: OpportunityUpdate
) -> OpportunityResponse:
    """Update an opportunity (status, notes, etc.)."""
    try:
        client = get_supabase_client()
        update_data = update.model_dump(exclude_unset=True)
        update_data["updated_at"] = "now()"

        response = (
            client.table("income_opportunities")
            .update(update_data)
            .eq("id", str(opportunity_id))
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Opportunity not found")

        return OpportunityResponse(**response.data[0])

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update opportunity: %s", e)
        raise HTTPException(status_code=500, detail="Failed to update opportunity")


@router.post("/{opportunity_id}/rate")
async def rate_opportunity(
    opportunity_id: UUID, rating_request: OpportunityRatingRequest
) -> dict:
    """Rate the usefulness of an opportunity suggestion."""
    try:
        client = get_supabase_client()
        if not 1 <= rating_request.rating <= 5:
            raise HTTPException(
                status_code=400, detail="Rating must be between 1 and 5"
            )

        update_data = {
            "user_rating": rating_request.rating,
            "updated_at": "now()",
        }

        if rating_request.feedback:
            # Could store feedback in a separate table or append to user_notes
            current = (
                client.table("income_opportunities")
                .select("user_notes")
                .eq("id", str(opportunity_id))
                .single()
                .execute()
            )

            existing_notes = current.data.get("user_notes", "") if current.data else ""
            new_notes = (
                f"{existing_notes}\n\nRating {rating_request.rating}/5: {rating_request.feedback}".strip()
            )
            update_data["user_notes"] = new_notes

        response = (
            client.table("income_opportunities")
            .update(update_data)
            .eq("id", str(opportunity_id))
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Opportunity not found")

        return {
            "status": "success",
            "message": "Rating recorded",
            "rating": rating_request.rating,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to rate opportunity: %s", e)
        raise HTTPException(status_code=500, detail="Failed to rate opportunity")


@router.delete("/{opportunity_id}")
async def dismiss_opportunity(opportunity_id: UUID) -> dict:
    """Dismiss an opportunity (set status to dismissed)."""
    try:
        client = get_supabase_client()
        response = (
            client.table("income_opportunities")
            .update({"status": "dismissed", "updated_at": "now()"})
            .eq("id", str(opportunity_id))
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Opportunity not found")

        return {"status": "success", "message": "Opportunity dismissed"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to dismiss opportunity: %s", e)
        raise HTTPException(status_code=500, detail="Failed to dismiss opportunity")


def _map_pattern_to_type(pattern_type: str) -> str:
    """Map pattern type to opportunity type."""
    mapping = {
        "skill_trend": "consulting",
        "market_gap": "saas",
        "tool_opportunity": "marketplace",
        "emerging_expertise": "education",
    }
    return mapping.get(pattern_type, "monetization")
