"""Supabase client initialization for String Free."""

from supabase import Client, create_client

from app.core.config import settings


def get_supabase_client() -> Client:
    """Create and return a Supabase client instance."""
    return create_client(
        str(settings.supabase_url),
        settings.supabase_key,
    )


supabase_client: Client = get_supabase_client()
