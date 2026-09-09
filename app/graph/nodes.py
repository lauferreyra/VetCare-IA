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

Podés utilizar las herramientas disponibles para
consultar y modificar información de VetCare.

REGLAS:

- Nunca inventes mascotas.
- Nunca inventes turnos.
- Nunca inventes horarios.
- Nunca inventes IDs.
- Utilizá las herramientas para obtener información real.
- Para disponibilidad utilizá una fecha en formato YYYY-MM-DD.
- Cuando el usuario diga "hoy", "mañana", "viernes", etc.,
  convertí la expresión a una fecha concreta utilizando
  la fecha actual.
- Para crear un turno necesitás:
  petId
  slotId
  reason
- Para cancelar un turno necesitás:
  appointmentId
""",
        },
        *state["messages"],
    ]

    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response],
    }