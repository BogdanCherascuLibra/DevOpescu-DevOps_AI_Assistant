"""
Health-check API route.

This module exposes a lightweight endpoint used to verify
that the DevOpescu backend is running.
"""

from fastapi import APIRouter


router = APIRouter(
    tags=["Health"],
)


@router.get("/health")
def health_check() -> dict:
    """Return the current status of the API service."""
    return {
        "status": "ok",
        "service": "DevOpescu API",
    }