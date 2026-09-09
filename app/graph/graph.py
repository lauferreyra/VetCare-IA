from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from app.graph.booking import (
    confirm_booking,
    create_booking,
    load_availability,
    process_date,
    process_reason,
    select_slot,
    show_availability,
    start_booking,
)
from app.graph.state import VetCareState


# --------------------------------------------------
# ROUTER PRINCIPAL
# --------------------------------------------------


def route_booking_stage(state):

    stage = state.get(
        "booking_stage"
    )

    print("\n================ ROUTING BOOKING ================")

    print(
        "booking_stage:",
        stage,
    )

    print(
        "pet_id:",
        state.get("pet_id"),
    )

    print(
        "pet_name:",
        state.get("pet_name"),
    )

    print(
        "date:",
        state.get("date"),
    )

    print(
        "available_slots:",
        bool(state.get("available_slots")),
    )

    print(
        "slot_id:",
        state.get("slot_id"),
    )

    print(
        "slot_time:",
        state.get("slot_time"),
    )

    print(
        "reason:",
        state.get("reason"),
    )

    # ----------------------------------------------
    # NEW BOOKING
    # ----------------------------------------------

    if not stage:
        print("→ start_booking")
        return "start_booking"

    # ----------------------------------------------
    # DATE
    # ----------------------------------------------

    if stage == "select_date":
        print("→ process_date")
        return "process_date"

    # ----------------------------------------------
    # AVAILABILITY
    # ----------------------------------------------

    if stage == "load_availability":
        print("→ availability")
        return "availability"

    # ----------------------------------------------
    # SLOT
    # ----------------------------------------------

    if stage == "select_slot":
        print("→ select_slot")
        return "select_slot"

    # ----------------------------------------------
    # REASON
    # ----------------------------------------------

    if stage == "select_reason":
        print("→ process_reason")
        return "process_reason"

    # ----------------------------------------------
    # CONFIRMATION
    # ----------------------------------------------

    if stage == "confirm":
        print("→ confirm")
        return "confirm"

    # ----------------------------------------------
    # COMPLETED
    # ----------------------------------------------

    print("→ END")

    return END


# --------------------------------------------------
# ROUTER AFTER START
# --------------------------------------------------


def route_after_start(state):

    stage = state.get(
        "booking_stage"
    )

    if stage == "load_availability":
        return "availability"

    return END


# --------------------------------------------------
# ROUTER AFTER DATE
# --------------------------------------------------


def route_after_date(state):

    if state.get(
        "booking_stage"
    ) == "load_availability":

        return "availability"

    return END


# --------------------------------------------------
# ROUTER AFTER REASON
# --------------------------------------------------


def route_after_reason(state):

    if state.get(
        "booking_stage"
    ) == "confirm":

        return "confirm"

    return END


# --------------------------------------------------
# ROUTER AFTER CONFIRMATION
# --------------------------------------------------


def route_after_confirmation(state):

    if state.get(
        "approval_status"
    ) == "approved":

        return "create"

    return END


# --------------------------------------------------
# GRAPH
# --------------------------------------------------


builder = StateGraph(
    VetCareState
)


# --------------------------------------------------
# NODES
# --------------------------------------------------


builder.add_node(
    "start_booking",
    start_booking,
)

builder.add_node(
    "process_date",
    process_date,
)

builder.add_node(
    "availability",
    load_availability,
)

builder.add_node(
    "show_availability",
    show_availability,
)

builder.add_node(
    "select_slot",
    select_slot,
)

builder.add_node(
    "process_reason",
    process_reason,
)

builder.add_node(
    "confirm",
    confirm_booking,
)

builder.add_node(
    "create",
    create_booking,
)


# --------------------------------------------------
# START
# --------------------------------------------------


builder.add_conditional_edges(
    START,
    route_booking_stage,
    {
        "start_booking": "start_booking",
        "process_date": "process_date",
        "availability": "availability",
        "select_slot": "select_slot",
        "process_reason": "process_reason",
        "confirm": "confirm",
        END: END,
    },
)


# --------------------------------------------------
# START BOOKING
# --------------------------------------------------


builder.add_conditional_edges(
    "start_booking",
    route_after_start,
    {
        "availability": "availability",
        END: END,
    },
)


# --------------------------------------------------
# PROCESS DATE
# --------------------------------------------------


builder.add_conditional_edges(
    "process_date",
    route_after_date,
    {
        "availability": "availability",
        END: END,
    },
)


# --------------------------------------------------
# AVAILABILITY
# --------------------------------------------------


builder.add_edge(
    "availability",
    "show_availability",
)

builder.add_edge(
    "show_availability",
    END,
)


# --------------------------------------------------
# SELECT SLOT
# --------------------------------------------------


builder.add_edge(
    "select_slot",
    END,
)


# --------------------------------------------------
# PROCESS REASON
# --------------------------------------------------


builder.add_conditional_edges(
    "process_reason",
    route_after_reason,
    {
        "confirm": "confirm",
        END: END,
    },
)


# --------------------------------------------------
# CONFIRM
# --------------------------------------------------


builder.add_conditional_edges(
    "confirm",
    route_after_confirmation,
    {
        "create": "create",
        END: END,
    },
)


# --------------------------------------------------
# CREATE
# --------------------------------------------------


builder.add_edge(
    "create",
    END,
)


# --------------------------------------------------
# CHECKPOINT
# --------------------------------------------------


checkpointer = InMemorySaver()


graph = builder.compile(
    checkpointer=checkpointer,
)