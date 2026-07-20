"""
Application entry point.

This module provides a simple command-line
interface for interacting with the agent.
"""

from agent import Agent
from llm_client import LLMClient
from conversation_context import ConversationContext
from tools.tools import tools
from embeddings_client import EmbeddingsClient
from knowledge_base import KnowledgeBase
from database import initialize_database
from session_manager import SessionManager
from conversation_manager import ConversationManager
from conversation_exporter import ConversationExporter
from conversation_importer import ConversationImporter


def main():
    initialize_database()

    session_manager = SessionManager()
    conversation_manager = ConversationManager()

    conversation_exporter = ConversationExporter(conversation_manager)
    conversation_importer = ConversationImporter(conversation_manager)

    username = input("Username: ").strip()

    if not username:
        print("Username-ul nu poate fi gol.")
        return
    
    user_id = session_manager.get_or_create_user(username)
    session_id = session_manager.create_session(user_id)

    conversations = conversation_manager.get_user_conversations(user_id)

    print("\n1. Conversatie noua")

    for index, conversation in enumerate(conversations, start=2):
        print(f"{index}. {conversation['title']}")

    choice = input("\nAlege conversatia: ").strip()

    if choice == "1":
        title = input("Titlul conversatiei: ").strip()

        if not title:
            title = "DevOps conversation"

        conversation_id = conversation_manager.create_conversation(
            user_id,
            title=title
        )

    else:
        try:
            selected_index = int(choice) - 2
            conversation_id = conversations[selected_index]["id"]

        except (ValueError, IndexError):
            print("Optiune invalida.")
            session_manager.close_session(session_id)
            return
    
    context = ConversationContext()

    stored_messages = conversation_manager.get_messages(
        conversation_id
    )

    for message in stored_messages:
        context.add_message({
            "role": message["role"],
            "content": message["content"]
        })

    llm_client = LLMClient()

    embeddings_client = EmbeddingsClient()
    knowledge_base = KnowledgeBase(embeddings_client)

    agent = Agent(llm_client, context, embeddings_client, knowledge_base, tools=tools)

    print("Salut, sunt DevOpescu, asistentul tau pentru probleme de DevOps, cu ce te pot ajuta ?")

    while True:
        user_input = input(f"\n{username}: ")

        if user_input.lower() == "exit":
            session_manager.close_session(session_id)
            break

        conversation_manager.add_message(
            conversation_id,
            "user",
            user_input
        )

        response = agent.process_message(user_input)

        conversation_manager.add_message(
            conversation_id,
            "assistant",
            response
        )

        session_manager.update_activity(session_id)

        tokens_usage = context.get_tokens_usage()

        print(f"\nDevOpescu: {response}")
        print(f"Input tokens total: {tokens_usage['input_tokens']}")
        print(f"Output tokens total: {tokens_usage['output_tokens']}")
        print(
            f"Total cost estimat: "
            f"${tokens_usage['total_cost']:.6f}"
        )


if __name__ == "__main__":
    main()
