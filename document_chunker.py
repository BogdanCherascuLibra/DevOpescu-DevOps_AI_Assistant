"""
Knowledge document chunking utilities.

This module loads documents marked for semantic search
and splits their content into paragraph-based chunks.
"""

import json
from pathlib import Path

from config import CHUNK_SIZE


KNOWLEDGE_PATH = Path(__file__).parent / "knowledge"


def split_chunk(text: str) -> list[str]:
    """
    Split text into chunks while keeping complete paragraphs together.
    """
    paragraphs = text.split("\n\n")

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        paragraph = paragraph.strip()

        if not paragraph:
            continue

        proposed_chunk = (
            f"{current_chunk}\n\n{paragraph}"
            if current_chunk
            else paragraph
        )

        # Add the paragraph to the current chunk when it fits.
        if len(proposed_chunk) <= CHUNK_SIZE:
            current_chunk = proposed_chunk
        else:
            # Save the completed chunk before starting a new one.
            if current_chunk:
                chunks.append(current_chunk)

            current_chunk = paragraph

    # Preserve the final chunk after all paragraphs are processed.
    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def load_and_chunk_documents() -> list[dict]:
    """
    Load documents marked with always_load=false and return their chunks.
    """
    all_chunks = []

    # Facts and procedures may both contain documents used by RAG.
    for directory_name in ["facts", "procedures"]:
        directory_path = KNOWLEDGE_PATH / directory_name
        registry_path = directory_path / "registry.json"

        with registry_path.open("r", encoding="utf-8") as file:
            registry = json.load(file)

        for document in registry:
            # Documents loaded permanently in the system prompt do not
            # need to be included in the embeddings index.
            if document["always_load"]:
                continue

            document_path = (
                directory_path / f"{document['id']}.md"
            )

            content = document_path.read_text(
                encoding="utf-8"
            ).strip()

            document_chunks = split_chunk(content)

            for chunk_index, chunk_content in enumerate(
                document_chunks
            ):
                all_chunks.append(
                    {
                        "document_id": document["id"],
                        "chunk_index": chunk_index,
                        "chunk_content": chunk_content,
                    }
                )

    return all_chunks