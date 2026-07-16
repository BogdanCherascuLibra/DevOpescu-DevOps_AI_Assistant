import json
from pathlib import Path
from config import CHUNK_SIZE

KNOWLEDGE_PATH = Path(__file__).parent / "knowledge"

def split_chunk(text: str) -> list[str]:
    chunks = []

    for i in range(0, len(text), CHUNK_SIZE):
        chunk = text[i:i + CHUNK_SIZE]
        chunks.append(chunk)

    return chunks

def load_and_chunk_documents() -> list[dict]:
    all_chunks = []
    for dir_name in ["facts", "procedures"]:
        dir_path = KNOWLEDGE_PATH / dir_name
        registry_path = dir_path / "registry.json"

    with registry_path.open("r", encoding="utf-8") as file:
        registry = json.load(file)

    for doc in registry:
        if doc["always_load"] :
            continue
            
        doc_path = (dir_path / f"{doc['id']}.md")

        content = doc_path.read_text(encoding="utf-8").strip()

        doc_chunks = split_chunk(content)

        for chunk_index, chunk_content in enumerate(doc_chunks):
            all_chunks.append({
                "document_id": doc['id'],
                "chunk_index": chunk_index,
                "chunk_content": chunk_content
            })

    return all_chunks


if __name__ == "__main__":
    chunks = load_and_chunk_documents()

    for chunk in chunks:
        print(chunk)
        print("-" * 50)