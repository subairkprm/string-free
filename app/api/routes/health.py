"""Health check endpoint for String Free."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health():
    """Return system health status."""
    return {
        "status": "online",
        "system": "String Free Build",
        "version": "0.1.0",
    }
