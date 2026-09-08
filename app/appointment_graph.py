from typing import TypedDict

from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.ai_models import ChatIntent
from app.config import settings
from app.prompts import intent_prompt


class AppointmentState(TypedDict):
    message: str
    intent: str
    pet_name: str | None
    date: str | None
    available: bool
    confirmed: bool | None
    response: str


# ============================================================
# LLM
# ============================================================

llm = ChatOllama(
    model=settings.llm_model,
)

structured_llm = llm.with_structured_output(ChatIntent)

intent_chain = intent_prompt | structured_llm


# ============================================================
# NODE 1 - Analizar pedido
# ============================================================

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


# ============================================================
# ROUTER 1 - ¿Tenemos fecha?
# ============================================================

def check_date(state: AppointmentState):

    print("\nROUTER: check_date")

    if state["date"]:
        return "has_date"

    return "missing_date"


# ============================================================
# NODE 2 - Pedir fecha
# ============================================================

def ask_for_date(state: AppointmentState):

    print("\nNODE: ask_for_date")

    date = interrupt(
        "¿Para qué día querés el turno?"
    )

    return {
        "date": date,
    }


# ============================================================
# NODE 3 - Buscar disponibilidad
# ============================================================

def find_available_appointments(state: AppointmentState):

    print("\nNODE: find_available_appointments")

    # Por ahora simulamos la API
    available = True

    return {
        "available": available,
    }


# ============================================================
# ROUTER 2 - ¿Hay disponibilidad?
# ============================================================

def check_availability(state: AppointmentState):

    print("\nROUTER: check_availability")

    if state["available"]:
        return "available"

    return "not_available"


# ============================================================
# NODE 4 - Mostrar disponibilidad
# ============================================================

def show_available_appointments(state: AppointmentState):

    print("\nNODE: show_available_appointments")

    return {
        "response": (
            f"Encontré turnos disponibles para "
            f"{state['pet_name']} el {state['date']}. "
            "¿Querés reservarlo?"
        ),
    }


# ============================================================
# NODE 5 - Pedir confirmación
# ============================================================

def ask_confirmation(state: AppointmentState):

    print("\nNODE: ask_confirmation")

    confirmation = interrupt(
        "¿Querés confirmar el turno? Respondé sí o no."
    )

    normalized = confirmation.lower().strip()

    return {
        "confirmed": normalized in {
            "sí",
            "si",
            "yes",
        }
    }


# ============================================================
# ROUTER 3 - ¿Confirmó?
# ============================================================

def check_confirmation(state: AppointmentState):

    print("\nROUTER: check_confirmation")

    if state["confirmed"]:
        return "confirmed"

    return "rejected"


# ============================================================
# NODE 6 - Reservar
# ============================================================

def book_appointment(state: AppointmentState):

    print("\nNODE: book_appointment")

    return {
        "response": (
            f"¡Listo! Reservé el turno para "
            f"{state['pet_name']} el {state['date']}."
        ),
    }


# ============================================================
# NODE 7 - Cancelar flujo
# ============================================================

def cancel_booking(state: AppointmentState):

    print("\nNODE: cancel_booking")

    return {
        "response": "Perfecto, no reservé el turno.",
    }


# ============================================================
# GRAPH
# ============================================================

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

builder.add_node(
    "show_available_appointments",
    show_available_appointments,
)

builder.add_node(
    "ask_confirmation",
    ask_confirmation,
)

builder.add_node(
    "book_appointment",
    book_appointment,
)

builder.add_node(
    "cancel_booking",
    cancel_booking,
)


# ============================================================
# EDGES
# ============================================================

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


builder.add_conditional_edges(
    "find_available_appointments",
    check_availability,
    {
        "available": "show_available_appointments",
        "not_available": END,
    },
)


builder.add_edge(
    "show_available_appointments",
    "ask_confirmation",
)


builder.add_conditional_edges(
    "ask_confirmation",
    check_confirmation,
    {
        "confirmed": "book_appointment",
        "rejected": "cancel_booking",
    },
)


builder.add_edge(
    "book_appointment",
    END,
)


builder.add_edge(
    "cancel_booking",
    END,
)


# ============================================================
# CHECKPOINTER
# ============================================================

checkpointer = InMemorySaver()

graph = builder.compile(
    checkpointer=checkpointer,
)


# ============================================================
# TEST
# ============================================================

config = {
    "configurable": {
        "thread_id": "appointment-1",
    },
}


print("\n==============================")
print("MENSAJE 1")
print("==============================")


result = graph.invoke(
    {
        "message": "Quiero sacar un turno para Firulais",
        "intent": "",
        "pet_name": None,
        "date": None,
        "available": False,
        "confirmed": None,
        "response": "",
    },
    config,
)


print("\nRESULTADO:")
print(result)


print("\n==============================")
print("MENSAJE 2")
print("==============================")


result = graph.invoke(
    Command(
        resume="mañana",
    ),
    config,
)


print("\nRESULTADO:")
print(result)


print("\n==============================")
print("MENSAJE 3")
print("==============================")


result = graph.invoke(
    Command(
        resume="sí",
    ),
    config,
)


print("\nRESULTADO FINAL:")
print(result)