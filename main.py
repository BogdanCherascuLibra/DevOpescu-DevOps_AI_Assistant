"""
Application entry point.

This module provides a command-line interface for:
- user and session management;
- creating or reopening conversations;
- loading conversation history;
- interacting with the DevOps assistant;
- displaying token usage and estimated cost.
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



def main():
    """Initialize the application and start the command-line chat loop."""

    # Ensure that the SQLite database and its tables exist.
    initialize_database()

    # Create the managers used for sessions and conversations.
    session_manager = SessionManager()
    conversation_manager = ConversationManager()

    # Ask the user to identify themselves.
    username = input("Username: ").strip()

    if not username:
        print("Username-ul nu poate fi gol.")
        return

    # Retrieve the existing user or create a new one.
    user_id = session_manager.get_or_create_user(username)

    # Start a new application session.
    session_id = session_manager.create_session(user_id)

    # Load all conversations belonging to the current user.
    conversations = conversation_manager.get_user_conversations(user_id)

    print("\n1. Conversatie noua")

    # Display the existing conversations as selectable options.
    for index, conversation in enumerate(conversations, start=2):
        print(f"{index}. {conversation['title']}")

    choice = input("\nAlege conversatia: ").strip()

    if choice == "1":
        # Create a new conversation.
        title = input("Titlul conversatiei: ").strip()

        if not title:
            title = "DevOps conversation"

        conversation_id = conversation_manager.create_conversation(
            user_id,
            title=title
        )

    else:
        # Open one of the existing conversations.
        try:
            selected_index = int(choice) - 2
            conversation_id = conversations[selected_index]["id"]

        except (ValueError, IndexError):
            print("Optiune invalida.")
            session_manager.close_session(session_id)
            return

    # Create the conversation context.
    context = ConversationContext()

    # Load stored messages into the active context.
    stored_messages = conversation_manager.get_messages(
        conversation_id
    )

    for message in stored_messages:
        context.add_message({
            "role": message["role"],
            "content": message["content"]
        })

    # Initialize the LLM and knowledge-base components.
    llm_client = LLMClient()

    embeddings_client = EmbeddingsClient()
    knowledge_base = KnowledgeBase(embeddings_client)

    # Create the main agent.
    agent = Agent(
        llm_client,
        context,
        embeddings_client,
        knowledge_base,
        tools=tools
    )

    print(
        "Salut, sunt DevOpescu, asistentul tau pentru "
        "probleme de DevOps, cu ce te pot ajuta ?"
    )

    # Start the interactive conversation loop.
    while True:
        user_input = input(f"\n{username}: ")

        if user_input.lower() == "exit":
            session_manager.close_session(session_id)
            break

        # Save the user's message in the database.
        conversation_manager.add_message(
            conversation_id,
            "user",
            user_input
        )

        # Generate the assistant response.
        response = agent.process_message(user_input)

        # Save the assistant response in the database.
        conversation_manager.add_message(
            conversation_id,
            "assistant",
            response
        )

        # Update the session activity timestamp.
        session_manager.update_activity(session_id)

        # Read the current token and cost statistics.
        tokens_usage = context.get_tokens_usage()

        print(f"\nDevOpescu: {response}")
        print(
            f"Input tokens total: "
            f"{tokens_usage['input_tokens']}"
        )
        print(
            f"Output tokens total: "
            f"{tokens_usage['output_tokens']}"
        )
        print(
            f"Total cost estimat: "
            f"${tokens_usage['total_cost']:.6f}"
        )


if __name__ == "__main__":
    main()
    