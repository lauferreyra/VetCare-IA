from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class VetCareState(TypedDict):
    message: str
    counter: int


def process_message(state: VetCareState):
    print("NODE: process_message")

    return {
        "counter": state["counter"] + 1,
    }


builder = StateGraph(VetCareState)

builder.add_node(
    "process_message",
    process_message,
)

builder.add_edge(
    START,
    "process_message",
)

builder.add_edge(
    "process_message",
    END,
)


checkpointer = InMemorySaver()

graph = builder.compile(
    checkpointer=checkpointer,
)


config = {
    "configurable": {
        "thread_id": "conversation-1",
    }
}


print("\n--- PRIMER MENSAJE ---")

result_1 = graph.invoke(
    {
        "message": "Hola",
        "counter": 0,
    },
    config,
)

print(result_1)


print("\n--- SEGUNDO MENSAJE ---")

result_2 = graph.invoke(
    {
        "message": "¿Seguimos?"
    },
    config,
)

print(result_2)