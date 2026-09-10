from pathlib import Path

from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter


COLLECTION_NAME = "vetcare_knowledge"

DATABASE_URL = (
    "postgresql+psycopg://postgres:postgres@localhost:5432/vetcare"
)

DOCUMENTS_PATH = Path("documents")


def load_documents() -> list[Document]:
    documents = []

    for path in DOCUMENTS_PATH.rglob("*.md"):
        content = path.read_text(encoding="utf-8")

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source": str(path),
                },
            )
        )

    return documents


def create_vector_store() -> PGVector:
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text",
    )

    return PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True,
    )


def ingest():
    print("Loading documents...")

    documents = load_documents()

    print(f"Documents loaded: {len(documents)}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )

    chunks = splitter.split_documents(documents)

    print(f"Chunks created: {len(chunks)}")

    vector_store = create_vector_store()

    vector_store.add_documents(chunks)

    print("Documents indexed successfully.")


if __name__ == "__main__":
    ingest()