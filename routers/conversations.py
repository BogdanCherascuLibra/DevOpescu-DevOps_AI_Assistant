from fastapi import APIRouter, HTTPException

from api_dependencies import (
    conversation_manager,
    session_manager
)
from api_schemas import (
    CreateConversationRequest,
    SendMessageRequest
)
from api_services import create_agent_for_conversation


router = APIRouter(
    prefix="/users/{username}",
    tags=["Conversations"]
)


@router.post("/conversations")
def create_conversation(
    username: str,
    request: CreateConversationRequest
) -> dict:
    user_id = session_manager.get_or_create_user(
        username
    )

    title = request.title.strip()

    if not title:
        title = "New conversation"

    conversation_id = (
        conversation_manager.create_conversation(
            user_id,
            title
        )
    )

    return {
        "conversation_id": conversation_id,
        "title": title
    }


@router.get("/conversations")
def list_conversations(
    username: str
) -> list[dict]:
    user_id = session_manager.get_or_create_user(
        username
    )

    return conversation_manager.get_user_conversations(
        user_id
    )


@router.get("/conversations/{conversation_id}")
def get_conversation_history(
    username: str,
    conversation_id: str
) -> dict:
    user_id = session_manager.get_or_create_user(
        username
    )

    conversation = conversation_manager.get_conversation(
        conversation_id,
        user_id
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )

    messages = conversation_manager.get_messages(
    conversation_id
)

    usage = conversation_manager.get_usage(
        conversation_id
    )

    return {
        "conversation": conversation,
        "messages": messages,
        "usage": usage
    }


@router.post(
    "/conversations/{conversation_id}/messages"
)
def send_message(
    username: str,
    conversation_id: str,
    request: SendMessageRequest
) -> dict:
    user_id = session_manager.get_or_create_user(
        username
    )

    conversation = conversation_manager.get_conversation(
        conversation_id,
        user_id
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )

    message_text = request.message.strip()

    if not message_text:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    agent, context = create_agent_for_conversation(
        conversation_id,
        conversation_manager
    )

    conversation_manager.add_message(
        conversation_id,
        "user",
        message_text
    )

    try:
        response = agent.process_message(
            message_text
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="The chatbot could not generate a response."
        ) from error

    conversation_manager.add_message(
        conversation_id,
        "assistant",
        response
    )

    usage = context.get_tokens_usage()

    conversation_manager.update_usage(
        conversation_id,
        usage["input_tokens"],
        usage["output_tokens"],
        usage["total_cost"]
    )

    total_usage = conversation_manager.get_usage(
        conversation_id
    )

    return {
        "conversation_id": conversation_id,
        "response": response,
        "usage": total_usage
    }


@router.delete(
    "/conversations/{conversation_id}"
)
def delete_conversation(
    username: str,
    conversation_id: str
) -> dict:
    user_id = session_manager.get_or_create_user(
        username
    )

    deleted = conversation_manager.delete_conversation(
        conversation_id,
        user_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )

    return {
        "message": "Conversation deleted successfully."
    }