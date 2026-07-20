"""
Embedding generation utilities.

This module loads knowledge-base chunks, generates embeddings
for each chunk, and stores them in the configured JSON file.
"""

import json
from pathlib import Path

from config import EMBEDDINGS_FILE
from document_chunker import load_and_chunk_documents
from embeddings_client import EmbeddingsClient


def generate_embeddings() -> list[dict]:
    """Generate embeddings for all knowledge-base chunks."""
    chunks = load_and_chunk_documents()
    embedding_client = EmbeddingsClient()

    embedded_chunks = []

    for chunk in chunks:
        embedding = embedding_client.get_embedding(
            chunk["chunk_content"]
        )

        embedded_chunks.append(
            {
                "document_id": chunk["document_id"],
                "chunk_index": chunk["chunk_index"],
                "content": chunk["chunk_content"],
                "embedding": embedding,
            }
        )

    return embedded_chunks


def save_embeddings(embedded_chunks: list[dict]) -> None:
    """Save generated embeddings to the configured JSON file."""
    EMBEDDINGS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with EMBEDDINGS_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            embedded_chunks,
            file,
            indent=2,
        )


def knowledge_changed() -> bool:
    """
    Check whether the knowledge base was modified
    after the embeddings file was generated.
    """
    if not EMBEDDINGS_FILE.exists():
        return True

    embeddings_time = EMBEDDINGS_FILE.stat().st_mtime
    knowledge_path = Path(__file__).parent / "knowledge"

    for directory in ["facts", "procedures"]:
        directory_path = knowledge_path / directory

        for file_path in directory_path.glob("*"):
            if (
                file_path.suffix in {".md", ".json"}
                and file_path.stat().st_mtime > embeddings_time
            ):
                return True

    return False


def generate_and_save_embeddings() -> None:
    """Generate embeddings only when the knowledge base has changed."""
    if not knowledge_changed():
        print("The knowledge base has not changed.")
        return

    embedded_chunks = generate_embeddings()
    save_embeddings(embedded_chunks)

    print("Embeddings generated successfully.")


if __name__ == "__main__":
    generate_and_save_embeddings()
    