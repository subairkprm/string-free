"""Supabase client singleton for String Free."""

import logging

from supabase import Client, create_client

from app.core.config import settings

logger = logging.getLogger(__name__)

_supabase_client: Client | None = None


def get_supabase_client() -> Client:
    """Return the singleton Supabase client, creating it on first call."""
    global _supabase_client  # noqa: PLW0603
    if _supabase_client is None:
        url = str(settings.supabase_url)
        key = settings.supabase_key
        if not url or not key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set")
        _supabase_client = create_client(url, key)
        logger.info("Supabase client initialized")
    return _supabase_client
