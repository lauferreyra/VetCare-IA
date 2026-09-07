from langchain.agents import create_agent

from app.config import settings
from app.tools import get_available_appointments
from langchain_ollama import ChatOllama
from datetime import date
from langchain_core.messages import HumanMessage, AIMessage

llm = ChatOllama(
    model=settings.llm_model,
)

agent = create_agent(
    model=llm,
    tools=[get_available_appointments],
)

conversation_history = []

def get_current_date() -> str:
    return date.today().isoformat()

def run_agent(message: str):
    current_date = get_current_date()

    conversation_history.append(
        HumanMessage(content=message)
    )

    messages = [
        {
            "role": "system",
            "content": (
                f"La fecha actual es {current_date}. "
                "Cuando el usuario utilice fechas relativas "
                "como hoy, mañana o pasado mañana, "
                "utilizá esta fecha como referencia. "
                "No inventes años."
            ),
        },
        *conversation_history,
    ]

    print("HISTORIAL:")
    print(conversation_history)
    result = agent.invoke(
        {
            "messages": messages,
        }
    )

    final_message = result["messages"][-1]

    conversation_history.append(
        AIMessage(content=final_message.content)
    )

    return final_message.content