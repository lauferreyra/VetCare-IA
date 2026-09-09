from datetime import date

from langchain_ollama import ChatOllama

from app.config import settings
from app.tools import all_tools


llm = ChatOllama(
    model=settings.llm_model,
)

llm_with_tools = llm.bind_tools(all_tools)


def call_agent(state):
    current_date = date.today().isoformat()

    messages = [
        {
            "role": "system",
            "content": f"""
Sos el asistente virtual de VetCare.

La fecha actual es {current_date}.

REGLAS:

- Nunca inventes mascotas.
- Nunca inventes turnos.
- Nunca inventes horarios.
- Nunca inventes IDs.
- Utilizá las herramientas para obtener información real.
- Para disponibilidad utilizá una fecha YYYY-MM-DD.
- Para crear un turno necesitás pet_id, slot_id y reason.
- Nunca crees un turno sin tener esos tres datos.
- Nunca canceles un turno sin tener el appointment_id.
""",
        },
        *state["messages"],
    ]

    response = llm_with_tools.invoke(messages)

    print("\n==============================")
    print("AI MESSAGE")
    print(response)
    print("==============================\n")

    return {
        "messages": [response],
    }