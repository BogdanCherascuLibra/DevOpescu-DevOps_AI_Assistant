"""
API request schemas.

This module defines the validated request bodies used by
the conversation-related FastAPI endpoints.
"""

from pydantic import BaseModel, Field


class CreateConversationRequest(BaseModel):
    """Request body used when creating a new conversation."""

    title: str = Field(
        default="New conversation",
        min_length=1,
        max_length=150,
    )


class SendMessageRequest(BaseModel):
    """Request body used when sending a message to the assistant."""

    message: str = Field(
        min_length=1,
    )