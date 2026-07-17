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


def main():
    context = ConversationContext()

    llm_client = LLMClient()

    embeddings_client = EmbeddingsClient()

    agent = Agent(llm_client, context, embeddings_client, tools=tools)

    print("Salut, sunt DevOpescu, asistentul tau pentru probleme de DevOps, cu ce te pot ajuta ?")

    while True:
        user_input = input(
            "\nYou: "
        )

        if user_input.lower() == "exit":
            break

        response = agent.process_message(user_input)

        tokens_usage = context.get_tokens_usage()

        print(f"\nDevOpescu: {response}")
        print(f"Input tokens total {tokens_usage["input_tokens"]}")
        print(f"Output tokens total {tokens_usage["output_tokens"]}")
        print(f"Total cost estimat: ${tokens_usage['total_cost']:.6f}")


if __name__ == "__main__":
    main()
