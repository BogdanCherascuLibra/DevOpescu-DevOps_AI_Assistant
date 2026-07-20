"""
API service helpers.

This module rebuilds an agent for a stored conversation
by loading its previous messages and initializing the
LLM, embeddings, knowledge-base, and tool components.
"""

from agent import Agent
from conversation_context import ConversationContext
from conversation_manager import ConversationManager
from embeddings_client import EmbeddingsClient
from knowledge_base import KnowledgeBase
from llm_client import LLMClient
from tools.tools import tools


def create_agent_for_conversation(
    conversation_id: str,
    conversation_manager: ConversationManager,
) -> tuple[Agent, ConversationContext]:
    """
    Create an agent and restore the context of a stored conversation.
    """
    context = ConversationContext()

    # Load all previously stored messages into the active context.
    stored_messages = conversation_manager.get_messages(
        conversation_id
    )

    for message in stored_messages:
        context.add_message(
            {
                "role": message["role"],
                "content": message["content"],
            }
        )

    # Initialize the services required by the agent.
    llm_client = LLMClient()
    embeddings_client = EmbeddingsClient()
    knowledge_base = KnowledgeBase(
        embeddings_client
    )

    agent = Agent(
        llm_client,
        context,
        embeddings_client,
        knowledge_base,
        tools=tools,
    )

    return agent, context