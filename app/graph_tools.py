from datetime import date
from typing import TypedDict

from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.config import settings
from app.tools import get_available_appointments


class AgentState(TypedDict):
    messages: list


# ============================================================
# LLM
# ============================================================

llm = ChatOllama(
    model=settings.llm_model,
)


# ============================================================
# TOOLS
# ============================================================

tools = [
    get_available_appointments,
]


llm_with_tools = llm.bind_tools(tools)


# ============================================================
# NODE - LLM
# ============================================================

def call_model(state: AgentState):

    print("\nNODE: call_model")

    current_date = date.today().isoformat()

    messages = [
        {
            "role": "system",
            "content": (
                f"La fecha actual es {current_date}. "
                "Cuando el usuario diga hoy, mañana, "
                "pasado mañana u otra fecha relativa, "
                "calculá correctamente la fecha usando "
                "la fecha actual. "
                "Nunca inventes fechas."
            ),
        },
        *state["messages"],
    ]

    response = llm_with_tools.invoke(messages)

    print("AI:", response)

    return {
        "messages": [response],
    }


# ============================================================
# TOOL NODE
# ============================================================

tool_node = ToolNode(tools)


# ============================================================
# GRAPH
# ============================================================

builder = StateGraph(AgentState)


builder.add_node(
    "llm",
    call_model,
)

builder.add_node(
    "tools",
    tool_node,
)


# ============================================================
# START
# ============================================================

builder.add_edge(
    START,
    "llm",
)


# ============================================================
# LLM → TOOLS / END
# ============================================================

builder.add_conditional_edges(
    "llm",
    tools_condition,
    {
        "tools": "tools",
        END: END,
    },
)


# ============================================================
# TOOLS → LLM
# ============================================================

builder.add_edge(
    "tools",
    "llm",
)


# ============================================================
# CHECKPOINTER
# ============================================================

checkpointer = InMemorySaver()

graph = builder.compile(
    checkpointer=checkpointer,
)


# ============================================================
# CONFIG
# ============================================================

config = {
    "configurable": {
        "thread_id": "tools-demo-1",
    }
}


# ============================================================
# TEST
# ============================================================

result = graph.invoke(
    {
        "messages": [
            HumanMessage(
                content=(
                    "¿Qué turnos hay disponibles "
                    "para mañana?"
                )
            )
        ]
    },
    config,
)


print("\n==============================")
print("RESULTADO FINAL")
print("==============================")


for message in result["messages"]:

    print(
        type(message).__name__,
        ":",
        message.content,
    )