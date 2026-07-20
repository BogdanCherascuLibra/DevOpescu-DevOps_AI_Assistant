from pydantic import BaseModel, Field


class CreateConversationRequest(BaseModel):
    title: str = Field(
        default="New conversation",
        min_length=1,
        max_length=150
    )


class SendMessageRequest(BaseModel):
    message: str = Field(
        min_length=1
    )