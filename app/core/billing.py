"""Lemon Squeezy billing integration for String Free."""

import hashlib
import hmac
import logging

from app.core.config import settings
from app.core.database import get_supabase_client
from app.models.enums import PlanTier

logger = logging.getLogger(__name__)


def _get_variant_to_plan_map() -> dict[str, PlanTier]:
    """Map Lemon Squeezy variant IDs to plan tiers."""
    mapping: dict[str, PlanTier] = {}
    if settings.lemon_squeezy_solo_variant_id:
        mapping[settings.lemon_squeezy_solo_variant_id] = PlanTier.SOLO
    if settings.lemon_squeezy_pro_variant_id:
        mapping[settings.lemon_squeezy_pro_variant_id] = PlanTier.PRO
    if settings.lemon_squeezy_team_variant_id:
        mapping[settings.lemon_squeezy_team_variant_id] = PlanTier.TEAM
    return mapping


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify Lemon Squeezy webhook signature using HMAC-SHA256."""
    secret = settings.lemon_squeezy_webhook_secret
    if not secret:
        logger.warning("LEMON_SQUEEZY_WEBHOOK_SECRET not configured, skipping verification")
        return False
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


async def handle_subscription_created(data: dict) -> None:
    """Handle subscription_created event from Lemon Squeezy."""
    await _upsert_subscription(data)


async def handle_subscription_updated(data: dict) -> None:
    """Handle subscription_updated event from Lemon Squeezy."""
    await _upsert_subscription(data)


async def handle_subscription_cancelled(data: dict) -> None:
    """Handle subscription_cancelled — downgrade user to FREE."""
    attrs = data.get("data", {}).get("attributes", {})
    user_email = attrs.get("user_email", "")
    if not user_email:
        logger.error("No user_email in subscription_cancelled event")
        return

    client = get_supabase_client()
    client.table("user_subscriptions").upsert(
        {
            "user_email": user_email,
            "plan_tier": PlanTier.FREE,
            "subscription_id": str(data.get("data", {}).get("id", "")),
            "status": "cancelled",
        },
        on_conflict="user_email",
    ).execute()
    logger.info("Subscription cancelled for %s, downgraded to FREE", user_email)


async def process_billing_webhook(event_name: str, data: dict) -> None:
    """Route a Lemon Squeezy webhook event to the appropriate handler."""
    handlers = {
        "subscription_created": handle_subscription_created,
        "subscription_updated": handle_subscription_updated,
        "subscription_cancelled": handle_subscription_cancelled,
    }
    handler = handlers.get(event_name)
    if handler:
        await handler(data)
    else:
        logger.info("Ignoring unhandled billing event: %s", event_name)


async def _upsert_subscription(data: dict) -> None:
    """Create or update a subscription record in Supabase."""
    attrs = data.get("data", {}).get("attributes", {})
    variant_id = str(attrs.get("variant_id", ""))
    user_email = attrs.get("user_email", "")
    subscription_id = str(data.get("data", {}).get("id", ""))

    if not user_email:
        logger.error("No user_email in subscription event")
        return

    variant_map = _get_variant_to_plan_map()
    plan_tier = variant_map.get(variant_id, PlanTier.FREE)

    client = get_supabase_client()
    client.table("user_subscriptions").upsert(
        {
            "user_email": user_email,
            "plan_tier": plan_tier,
            "subscription_id": subscription_id,
            "variant_id": variant_id,
            "status": attrs.get("status", "active"),
        },
        on_conflict="user_email",
    ).execute()
    logger.info("Subscription upserted for %s → %s", user_email, plan_tier)
