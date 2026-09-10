from langchain_ollama import ChatOllama

from app.rag.retriever import search_knowledge


llm = ChatOllama(
    model="qwen3:8b",
    temperature=0,
)


def answer_with_rag(query: str) -> str:
    documents = search_knowledge(query, k=4)

    if not documents:
        return "No encontré información relevante en la base de conocimiento."

    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    prompt = f"""
Sos el asistente veterinario de VetCare.

Respondé la pregunta del usuario utilizando únicamente
la información disponible en el contexto.

Si el contexto no contiene información suficiente para
responder, indicá que no encontraste información suficiente.

No inventes información.

Contexto:

{context}

Pregunta del usuario:

{query}
"""

    response = llm.invoke(prompt)

    return response.content