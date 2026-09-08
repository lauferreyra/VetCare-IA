from datetime import date

from langchain_ollama import ChatOllama

from app.config import settings
from app.tools import all_tools


llm = ChatOllama(
    model=settings.llm_model,
)

llm_with_tools = llm.bind_tools(
    all_tools,
)


def call_agent(state):

    current_date = date.today().isoformat()

    messages = [
        {
            "role": "system",
            "content": (
                "Sos el asistente virtual de VetCare. "
                f"La fecha actual es {current_date}. "
                "Ayudá al usuario utilizando las "
                "herramientas disponibles. "
                "No inventes información. "
                "Cuando el usuario utilice fechas relativas "
                "como hoy o mañana, calculá la fecha usando "
                "la fecha actual."
            ),
        },
        *state["messages"],
    ]

    response = llm_with_tools.invoke(
        messages
    )

    return {
        "messages": [
            response
        ],
    }