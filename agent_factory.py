from agent import Agent
from conversation_context import ConversationContext
from conversation_manager import ConversationManager
from embeddings_client import EmbeddingsClient
from knowledge_base import KnowledgeBase
from llm_client import LLMClient
from tools.tools import tools


conversation_manager = ConversationManager()

llm_client = LLMClient()
embeddings_client = EmbeddingsClient()
knowledge_base = KnowledgeBase(embeddings_client)


def create_agent(conversation_id: str) -> tuple[Agent, ConversationContext]:
    context = ConversationContext()

    stored_messages = conversation_manager.get_messages(
        conversation_id
    )

    for message in stored_messages:
        context.add_message({
            "role": message["role"],
            "content": message["content"]
        })

    agent = Agent(
        llm_client,
        context,
        embeddings_client,
        knowledge_base,
        tools=tools
    )

    return agent, context