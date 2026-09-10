from langchain_core.tools import tool

from app.rag.retriever import search_knowledge


@tool
def search_veterinary_knowledge(query: str) -> str:
    """
    Busca información relevante en la base de conocimiento
    veterinaria de VetCare.
    """

    documents = search_knowledge(
        query=query,
        k=4,
    )

    if not documents:
        return "No se encontró información relevante."

    results = []

    for document in documents:
        source = document.metadata.get(
            "source",
            "unknown",
        )

        results.append(
            f"""
Fuente: {source}

Contenido:
{document.page_content}
"""
        )

    return "\n".join(results)