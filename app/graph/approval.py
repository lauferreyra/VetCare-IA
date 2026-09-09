from langgraph.types import interrupt
from langchain_core.messages import ToolMessage

WRITE_TOOLS = {
    "create_appointment",
    "cancel_appointment",
}


def approval_node(state):
    last_message = state["messages"][-1]

    tool_calls = getattr(last_message, "tool_calls", [])

    write_calls = [
        tool_call
        for tool_call in tool_calls
        if tool_call["name"] in WRITE_TOOLS
    ]

    # No hay operaciones de escritura.
    if not write_calls:
        return {
            "approval_status": "approved",
        }

    approval_data = {
        "type": "approval_required",
        "message": "El asistente quiere realizar una operación sobre tus turnos.",
        "operations": [
            {
                "tool": tool_call["name"],
                "arguments": tool_call["args"],
            }
            for tool_call in write_calls
        ],
    }

    decision = interrupt(approval_data)

    if decision is True:
        return {
            "approval_status": "approved",
        }

    denied_messages = [
        ToolMessage(
            content="El usuario no aprobó esta operación.",
            tool_call_id=tool_call["id"],
        )
        for tool_call in write_calls
    ]

    return {
        "approval_status": "denied",
        "messages": denied_messages,
    }