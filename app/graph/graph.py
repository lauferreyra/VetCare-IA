from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from app.graph.nodes import call_agent
from app.graph.routers import route_agent
from app.graph.state import VetCareState
from app.tools import all_tools


builder = StateGraph(VetCareState)

builder.add_node(
    "agent",
    call_agent,
)

builder.add_node(
    "tools",
    ToolNode(all_tools),
)

builder.add_edge(
    START,
    "agent",
)

builder.add_conditional_edges(
    "agent",
    route_agent,
    {
        "tools": "tools",
        END: END,
    },
)

builder.add_edge(
    "tools",
    "agent",
)


checkpointer = InMemorySaver()

graph = builder.compile(
    checkpointer=checkpointer,
)