from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.ai_models import ChatIntent
from app.config import settings
from app.prompts import intent_prompt
from langchain_ollama import ChatOllama


class AppointmentState(TypedDict):
    message: str
    intent: str
    pet_name: str | None
    date: str | None
    response: str


llm = ChatOllama(
    model=settings.llm_model,
)

structured_llm = llm.with_structured_output(ChatIntent)

intent_chain = intent_prompt | structured_llm


def analyze_request(state: AppointmentState):
    print("\nNODE: analyze_request")

    result = intent_chain.invoke(
        {
            "question": state["message"],
        }
    )

    print("Intent:", result.intent)
    print("Pet:", result.pet_name)
    print("Date:", result.date)

    return {
        "intent": result.intent,
        "pet_name": result.pet_name,
        "date": result.date,
    }


def check_date(state: AppointmentState):
    print("\nNODE: check_date")

    if state["date"]:
        return "has_date"

    return "missing_date"


def ask_for_date(state: AppointmentState):
    print("\nNODE: ask_for_date")

    date = interrupt(
        "¿Para qué día querés el turno?"
    )

    return {
        "date": date,
    }


def find_available_appointments(state: AppointmentState):
    print("\nNODE: find_available_appointments")

    return {
        "response": (
            f"Buscando turnos disponibles para "
            f"{state['pet_name']} el {state['date']}."
        ),
    }


builder = StateGraph(AppointmentState)


builder.add_node(
    "analyze_request",
    analyze_request,
)

builder.add_node(
    "ask_for_date",
    ask_for_date,
)

builder.add_node(
    "find_available_appointments",
    find_available_appointments,
)


builder.add_edge(
    START,
    "analyze_request",
)


builder.add_conditional_edges(
    "analyze_request",
    check_date,
    {
        "missing_date": "ask_for_date",
        "has_date": "find_available_appointments",
    },
)


builder.add_edge(
    "ask_for_date",
    "find_available_appointments",
)


builder.add_edge(
    "find_available_appointments",
    END,
)


checkpointer = InMemorySaver()

graph = builder.compile(
    checkpointer=checkpointer,
)


config = {
    "configurable": {
        "thread_id": "appointment-1",
    },
}


print("\n--- PRIMER MENSAJE ---")

result = graph.invoke(
    {
        "message": "Quiero sacar un turno para Firulais",
        "intent": "",
        "pet_name": None,
        "date": None,
        "response": "",
    },
    config,
)

print("\nRESULTADO:")
print(result)


print("\n--- USUARIO RESPONDE ---")

result = graph.invoke(
    Command(
        resume="mañana",
    ),
    config,
)

print("\nRESULTADO FINAL:")
print(result)