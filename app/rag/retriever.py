from langchain_ollama import OllamaEmbeddings
from langchain_postgres import PGVector

from app.rag.ingest import (
    COLLECTION_NAME,
    DATABASE_URL,
)


def get_vector_store() -> PGVector:
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text",
    )

    return PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True,
    )


def search_knowledge(
    query: str,
    k: int = 4,
):
    vector_store = get_vector_store()

    return vector_store.similarity_search(
        query,
        k=k,
    )