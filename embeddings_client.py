import requests
import json

from config import (EMBEDDINGS_MODEL, EMBEDDINGS_ENDPOINT,
                     SEMANTIC_SEARCH_FIRST_N, EMBEDDINGS_FILE,
                     SEMANTIC_SEARCH_MIN_SIMILARITY)


class EmbeddingsClient:
    def get_embedding(self, text: str) -> list[float]:
        try:
            response = requests.post(
                EMBEDDINGS_ENDPOINT,
                json={
                    "model": EMBEDDINGS_MODEL,
                    "input": text
                }
            )

            if not response.ok:
                print("STATUS:", response.status_code)
                print("BODY:", response.text)

            response.raise_for_status()

            return response.json()["embeddings"][0]
    
        except requests.Timeout as exc:
            raise RuntimeError (
                "Serviciul de embeddings nu a raspuns la timp."
            ) from exc

        except requests.ConnectionError as exc:
            raise RuntimeError (
                "Nu ma pot conecta la Ollama."
            ) from exc

        except requests.RequestException as error:
            raise RuntimeError(
                f"Eroare la serviciul de embeddings: {error}"
            ) from error

        except (KeyError, IndexError, ValueError) as exc:
            raise RuntimeError(
                "Raspuns invalid primit de la serviciul de embeddings."
            ) from exc

    def cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """
        Computes the cosine similarity between two embedding vectors.

        Returns a float in the range [-1, 1]:
        1.0 - vectors are semantically identical
        0.0 - vectors are unrelated
        -1.0 - vectors are semantically opposite

        General interpretation:
        > 0.9      very similar
        0.7 - 0.9  similar
        0.5 - 0.7  somewhat related
        < 0.5      likely unrelated

        """
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a ** 2 for a in vec1) ** 0.5
        magnitude2 = sum(b ** 2 for b in vec2) ** 0.5
        return dot_product / (magnitude1 * magnitude2)
    
    def semantic_search(self, user_question: str) -> list[dict]:
        try:

            with EMBEDDINGS_FILE.open("r", encoding="utf-8") as file:
                embedded_chunks = json.load(file)

        except FileNotFoundError as exc:

            raise RuntimeError(
            "Fiierul embeddings.json nu exista."
            ) from exc

        except json.JSONDecodeError as exc:
            
            raise RuntimeError(
        "Fisierul embeddings.json este corupt."
            ) from exc
            

        question_embedding = self.get_embedding(user_question)

        results = []

        for chunk in embedded_chunks:
            similarity = self.cosine_similarity(question_embedding, chunk["embedding"])
            #print(similarity)

            if(similarity >= SEMANTIC_SEARCH_MIN_SIMILARITY):
                results.append(
                    {
                        "document_id": chunk["document_id"],
                        "chunk_index": chunk["chunk_index"],
                        "similarity": similarity,
                        "content": chunk["content"]
                    }
                )


        results.sort(key=lambda result: result["similarity"], reverse=True)
        return results[:SEMANTIC_SEARCH_FIRST_N]

if __name__ == "__main__":
    client = EmbeddingsClient()

    results = client.semantic_search(
        "How do I diagnose a Docker container that will not start?"
    )
    print(results)

    for result in results:
        print("Document:",result["document_id"])
        print("Chunk:",result["chunk_index"])
        print("Similarity:",round(result["similarity"], 4))
        print("Content:",result["content"])
        print("-" * 50)
