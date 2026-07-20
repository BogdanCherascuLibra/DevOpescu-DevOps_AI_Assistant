"""
Embeddings and semantic-search client.

This module communicates with the local embeddings service,
computes cosine similarity, and retrieves relevant knowledge
chunks for a user question.
"""

import json

import requests

from config import (
    EMBEDDINGS_ENDPOINT,
    EMBEDDINGS_FILE,
    EMBEDDINGS_MODEL,
    SEMANTIC_SEARCH_FIRST_N,
    SEMANTIC_SEARCH_MIN_SIMILARITY,
)


class EmbeddingsClient:
    """Handle embedding generation and semantic search."""

    def get_embedding(self, text: str) -> list[float]:
        """Return the embedding vector generated for the provided text."""
        try:
            response = requests.post(
                EMBEDDINGS_ENDPOINT,
                json={
                    "model": EMBEDDINGS_MODEL,
                    "input": text,
                },
                timeout=10,
            )

            response.raise_for_status()

            return response.json()["embeddings"][0]

        except requests.Timeout as exc:
            raise RuntimeError(
                "Serviciul de embeddings nu a răspuns la timp."
            ) from exc

        except requests.ConnectionError as exc:
            raise RuntimeError(
                "Nu mă pot conecta la Ollama."
            ) from exc

        except requests.RequestException as exc:
            raise RuntimeError(
                f"Eroare la serviciul de embeddings: {exc}"
            ) from exc

        except (KeyError, IndexError, ValueError) as exc:
            raise RuntimeError(
                "Răspuns invalid primit de la serviciul de embeddings."
            ) from exc

    def cosine_similarity(
        self,
        vec1: list[float],
        vec2: list[float],
    ) -> float:
        """Compute cosine similarity between two embedding vectors."""
        dot_product = sum(
            first * second
            for first, second in zip(vec1, vec2)
        )

        magnitude1 = sum(
            value**2
            for value in vec1
        ) ** 0.5

        magnitude2 = sum(
            value**2
            for value in vec2
        ) ** 0.5

        return dot_product / (magnitude1 * magnitude2)

    def semantic_search(
        self,
        user_question: str,
    ) -> list[dict]:
        """
        Return the most relevant knowledge chunks
        for the provided user question.
        """
        try:
            with EMBEDDINGS_FILE.open(
                "r",
                encoding="utf-8",
            ) as file:
                embedded_chunks = json.load(file)

        except FileNotFoundError as exc:
            raise RuntimeError(
                "Fișierul embeddings.json nu există."
            ) from exc

        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Fișierul embeddings.json este corupt."
            ) from exc

        question_embedding = self.get_embedding(
            user_question
        )

        results = []

        for chunk in embedded_chunks:
            similarity = self.cosine_similarity(
                question_embedding,
                chunk["embedding"],
            )

            if similarity >= SEMANTIC_SEARCH_MIN_SIMILARITY:
                results.append(
                    {
                        "document_id": chunk["document_id"],
                        "chunk_index": chunk["chunk_index"],
                        "similarity": similarity,
                        "content": chunk["content"],
                    }
                )

        results.sort(
            key=lambda result: result["similarity"],
            reverse=True,
        )

        return results[:SEMANTIC_SEARCH_FIRST_N]