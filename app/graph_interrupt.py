from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class VetCareState(TypedDict):
    message: str
    name: str


def ask_name(state: VetCareState):
    print("\nNODE: ask_name")

    name = interrupt(
        "¿Cuál es tu nombre?"
    )

    return {
        "name": name,
    }


builder = StateGraph(VetCareState)

builder.add_node(
    "ask_name",
    ask_name,
)

builder.add_edge(
    START,
    "ask_name",
)

builder.add_edge(
    "ask_name",
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


print("\n--- PRIMERA EJECUCIÓN ---")

result = graph.invoke(
    {
        "message": "Hola",
        "name": "",
    },
    config,
)

print("\nRESULTADO:")
print(result)


print("\n--- RESUMIENDO EJECUCIÓN ---")

result = graph.invoke(
    Command(
        resume="Lautaro"
    ),
    config,
)

print("\nRESULTADO FINAL:")
print(result)