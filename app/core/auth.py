"""Plan-based feature gating for String Free."""

from dataclasses import dataclass

from app.core.database import get_supabase_client
from app.models.enums import PlanTier

PLAN_LIMITS: dict[PlanTier, dict[str, int]] = {
    PlanTier.FREE: {"tasks_per_month": 10, "error_analyses_per_month": 5, "team_members": 1},
    PlanTier.SOLO: {"tasks_per_month": -1, "error_analyses_per_month": 50, "team_members": 1},
    PlanTier.PRO: {"tasks_per_month": -1, "error_analyses_per_month": -1, "team_members": 1},
    PlanTier.TEAM: {"tasks_per_month": -1, "error_analyses_per_month": -1, "team_members": 5},
}


@dataclass
class PlanCheckResult:
    allowed: bool
    current_usage: int
    limit: int
    tier: PlanTier


async def get_user_plan(user_id: str) -> PlanTier:
    """Look up the user's current plan tier from Supabase."""
    client = get_supabase_client()
    result = (
        client.table("user_subscriptions")
        .select("plan_tier")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if result.data:
        return PlanTier(result.data[0]["plan_tier"])
    return PlanTier.FREE


async def get_monthly_usage(user_id: str, feature: str) -> int:
    """Count usage of a feature for the current calendar month."""
    client = get_supabase_client()

    if feature == "tasks_per_month":
        result = (
            client.table("tasks")
            .select("id", count="exact")  # type: ignore[arg-type]
            .eq("user_id", user_id)
            .gte("created_at", _month_start())
            .execute()
        )
    elif feature == "error_analyses_per_month":
        result = (
            client.table("errors")
            .select("id", count="exact")  # type: ignore[arg-type]
            .eq("user_id", user_id)
            .gte("created_at", _month_start())
            .execute()
        )
    else:
        return 0

    return result.count or 0


async def check_plan_limit(user_id: str, feature: str) -> PlanCheckResult:
    """Check whether a user can use a feature given their plan limits."""
    tier = await get_user_plan(user_id)
    limits = PLAN_LIMITS[tier]
    limit = limits.get(feature, 0)

    # -1 means unlimited
    if limit == -1:
        return PlanCheckResult(allowed=True, current_usage=0, limit=-1, tier=tier)

    current_usage = await get_monthly_usage(user_id, feature)
    return PlanCheckResult(
        allowed=current_usage < limit,
        current_usage=current_usage,
        limit=limit,
        tier=tier,
    )


def _month_start() -> str:
    """Return ISO timestamp for the first day of the current month."""
    from datetime import UTC, datetime

    now = datetime.now(UTC)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
