from embeddings_client import EmbeddingsClient


class KnowledgeBase:
    def __init__(self, embeddings_client: EmbeddingsClient):
        self.embeddings_client = embeddings_client

    def retrieve(self, user_message: str) -> list[dict]:
        return self.embeddings_client.semantic_search(user_message)

    def build_context_message(
        self,
        user_message: str
    ) -> dict | None:
        try:
            results = self.retrieve(user_message)

        except RuntimeError as error:
            print(f"\nKnowledge base unavailable: {error}")

            return {
                "role": "system",
                "content": (
                    "The internal knowledge base is unavailable. "
                    "Answer using general DevOps knowledge. "
                    "Do not claim that internal documentation was consulted."
                )
            }

        if not results:
            return {
                "role": "system",
                "content": (
                    "No relevant information was found in the internal "
                    "knowledge base. Answer using general DevOps knowledge "
                    "and ask for missing technical details when necessary."
                )
            }

        context_parts = []

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
            )
        }