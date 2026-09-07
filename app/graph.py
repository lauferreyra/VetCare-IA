from typing import TypedDict

from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph

from app.config import settings


class VetCareState(TypedDict):
    message: str
    response: str
    attempts: int
    valid: bool


llm = ChatOllama(
    model=settings.llm_model,
)


def analyze_message(state: VetCareState):
    print("\nNODE: analyze_message")

    print("Mensaje:", state["message"])
    print("Intento:", state["attempts"])

    return {
        "attempts": state["attempts"] + 1,
    }


def validate_message(state: VetCareState):
    print("NODE: validate_message")

    # Simulamos una validación.
    # Para aprender el loop, consideramos inválidos
    # los dos primeros intentos.
    if state["attempts"] >= 3:
        return {
            "valid": True,
        }

    return {
        "valid": False,
    }


def retry_message(state: VetCareState):
    print("NODE: retry_message")

    return {
        "response": "El mensaje necesita ser procesado nuevamente.",
    }


def generate_response(state: VetCareState):
    print("NODE: generate_response")

    response = llm.invoke(
        state["message"]
    )

    return {
        "response": response.content,
    }


def route_validation(state: VetCareState):
    if state["valid"]:
        return "generate_response"

    if state["attempts"] >= 3:
        return "generate_response"

    return "retry_message"


builder = StateGraph(VetCareState)


builder.add_node(
    "analyze_message",
    analyze_message,
)

builder.add_node(
    "validate_message",
    validate_message,
)

builder.add_node(
    "retry_message",
    retry_message,
)

builder.add_node(
    "generate_response",
    generate_response,
)


builder.add_edge(
    START,
    "analyze_message",
)

builder.add_edge(
    "analyze_message",
    "validate_message",
)


builder.add_conditional_edges(
    "validate_message",
    route_validation,
    {
        "generate_response": "generate_response",
        "retry_message": "retry_message",
    },
)


builder.add_edge(
    "retry_message",
    "analyze_message",
)


builder.add_edge(
    "generate_response",
    END,
)


graph = builder.compile()


result = graph.invoke(
    {
        "message": "Quiero sacar un turno para Firulais",
        "response": "",
        "attempts": 0,
        "valid": False,
    }
)


print("\nRESULTADO FINAL:")
print(result)