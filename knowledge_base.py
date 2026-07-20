"""
Knowledge-base retrieval and RAG context construction.

This module retrieves relevant internal documentation
and converts it into a temporary context message for the agent.
"""

from embeddings_client import EmbeddingsClient


class KnowledgeBase:
    """Manage semantic retrieval from the internal knowledge base."""

    def __init__(
        self,
        embeddings_client: EmbeddingsClient,
    ):
        self.embeddings_client = embeddings_client

    def retrieve(
        self,
        user_message: str,
    ) -> list[dict]:
        """Retrieve knowledge chunks relevant to the user message."""
        return self.embeddings_client.semantic_search(
            user_message
        )

    def build_context_message(
        self,
        user_message: str,
    ) -> dict | None:
        """
        Build a temporary system message containing relevant RAG context.

        When the knowledge base is unavailable or no relevant results
        are found, the model is instructed to use general knowledge.
        """
        try:
            results = self.retrieve(user_message)

        except RuntimeError as error:
            # RAG failure does not stop the chatbot from responding.
            print(f"\nKnowledge base unavailable: {error}")

            return {
                "role": "system",
                "content": (
                    "The internal knowledge base is unavailable. "
                    "Answer using general DevOps knowledge. "
                    "Do not claim that internal documentation was consulted."
                ),
            }

        if not results:
            return {
                "role": "system",
                "content": (
                    "No relevant information was found in the internal "
                    "knowledge base. Answer using general DevOps knowledge "
                    "and ask for missing technical details when necessary."
                ),
            }

        context_parts = []

        # Format each retrieved chunk before injecting it into the prompt.
        for result in results:
            context_parts.append(
                f"Document: {result['document_id']}\n"
                f"Content:\n{result['content']}"
            )

        return {
            "role": "system",
            "content": (
                "Use the following internal knowledge when relevant.\n"
                "You may also use general DevOps knowledge.\n"
                "Do not invent information from these documents.\n\n"
                + "\n\n---\n\n".join(context_parts)
            ),
        }