from app.tools.knowledge import search_veterinary_knowledge


result = search_veterinary_knowledge.invoke(
    {
        "query": "¿Qué tengo que saber sobre las vacunas de mi perro?"
    }
)

print(result)