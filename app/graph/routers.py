from langgraph.prebuilt import tools_condition


def route_agent(state):
    return tools_condition(state)


def route_approval(state):
    if state["approval_status"] == "denied":
        return "agent"

    return "tools"