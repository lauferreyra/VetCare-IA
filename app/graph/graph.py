from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from app.ai_models import ChatIntent
from app.graph.booking import (
    confirm_booking,
    create_booking,
    is_availability_query,
    load_availability,
    load_availability_only,
    process_availability_date,
    process_date,
    process_reason,
    select_slot,
    show_availability,
    show_availability_only,
    start_availability,
    start_booking,
)
from app.graph.state import VetCareState
from app.mcp_client import get_mcp_tools
from app.prompts import intent_prompt
from app.tools.knowledge import search_veterinary_knowledge


# ==================================================
# MODELOS
# ==================================================


intent_llm = ChatOllama(
    model="qwen3:8b",
    temperature=0,
)


agent_llm = ChatOllama(
    model="qwen3:8b",
    temperature=0,
)


# ==================================================
# MCP TOOLS
# ==================================================


async def load_tools():

    mcp_tools = await get_mcp_tools()

    print(
        "\n================ MCP TOOLS ================="
    )

    for tool in mcp_tools:
        print(
            "Tool:",
            tool.name,
        )

    print(
        "============================================="
    )

    return mcp_tools


# ==================================================
# KNOWLEDGE TOOLS
# ==================================================


knowledge_tools = [
    search_veterinary_knowledge,
]


# ==================================================
# GRAPH BUILDER
# ==================================================


async def build_graph():

    mcp_tools = await load_tools()

    agent_tools = [
        *mcp_tools,
        *knowledge_tools,
    ]

    agent_llm_with_tools = agent_llm.bind_tools(
        agent_tools,
        tool_choice="required",
    )

    # ----------------------------------------------
    # GET PETS TOOL
    # ----------------------------------------------

    get_pets_tool = next(
        (
            tool
            for tool in mcp_tools
            if tool.name == "get_pets"
        ),
        None,
    )

    if get_pets_tool is None:
        raise RuntimeError(
            "MCP tool 'get_pets' was not found."
        )

    get_pets_llm = agent_llm.bind_tools(
        [get_pets_tool],
        tool_choice="required",
    )

    # ==================================================
    # INTENT
    # ==================================================

    def classify_intent(state):

        messages = state.get(
            "messages",
            [],
        )

        if not messages:

            return {
                "intent": "GENERAL_CHAT",
            }

        last_message = messages[-1]

        if isinstance(
            last_message,
            dict,
        ):

            content = last_message.get(
                "content",
                "",
            )

        else:

            content = last_message.content

        chain = (
            intent_prompt
            | intent_llm.with_structured_output(
                ChatIntent
            )
        )

        result = chain.invoke(
            {
                "question": content,
            }
        )

        print(
            "\n================ INTENT ================="
        )

        print(
            "Message:",
            content,
        )

        print(
            "Intent:",
            result.intent,
        )

        print(
            "========================================="
        )

        return {
            "intent": result.intent,
        }

    # ==================================================
    # INITIAL ROUTER
    # ==================================================

    def route_initial_intent(state):

        intent = state.get(
            "intent"
        )

        print(
            "\n================ ROUTING ================="
        )

        print(
            "Intent:",
            intent,
        )

        # ----------------------------------------------
        # BOOKING
        # ----------------------------------------------

        if intent == "BOOK_APPOINTMENT":

            messages = state.get(
                "messages",
                [],
            )

            last_message = (
                messages[-1]
                if messages
                else None
            )

            if isinstance(
                last_message,
                dict,
            ):

                content = last_message.get(
                    "content",
                    "",
                )

            else:

                content = (
                    last_message.content
                    if last_message
                    else ""
                )

            # ------------------------------------------
            # AVAILABILITY QUERY
            # ------------------------------------------

            if is_availability_query(
                content
            ):

                print(
                    "→ availability_query"
                )

                return "availability_query"

            # ------------------------------------------
            # NORMAL BOOKING
            # ------------------------------------------

            print(
                "→ booking"
            )

            return "booking"

        # ----------------------------------------------
        # MEDICAL
        # ----------------------------------------------

        if intent == "MEDICAL_QUERY":

            print(
                "→ knowledge_agent"
            )

            return "knowledge_agent"

        print(
            "→ knowledge_agent"
        )

        return "knowledge_agent"

    # ==================================================
    # BOOKING ROUTER
    # ==================================================

    def route_booking_stage(state):

        stage = state.get(
            "booking_stage"
        )

        print(
            "\n================ ROUTING BOOKING ================"
        )

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
            bool(
                state.get("available_slots")
            ),
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
        # NORMAL BOOKING
        # ----------------------------------------------

        if stage == "select_date":

            print(
                "→ process_date"
            )

            return "process_date"

        if stage == "load_availability":

            print(
                "→ availability"
            )

            return "availability"

        if stage == "select_slot":

            print(
                "→ select_slot"
            )

            return "select_slot"

        if stage == "select_reason":

            print(
                "→ process_reason"
            )

            return "process_reason"

        if stage == "confirm":

            print(
                "→ confirm"
            )

            return "confirm"

        # ----------------------------------------------
        # AVAILABILITY ONLY
        # ----------------------------------------------

        if stage == "select_availability_date":

            print(
                "→ process_availability_date"
            )

            return "process_availability_date"

        if stage == "load_availability_only":

            print(
                "→ availability_only"
            )

            return "availability_only"

        if stage == "show_availability_only":

            print(
                "→ show_availability_only"
            )

            return "show_availability_only"

        # ----------------------------------------------
        # DEFAULT
        # ----------------------------------------------

        print(
            "→ start_booking"
        )

        return "start_booking"

    # ==================================================
    # BOOKING ROUTERS
    # ==================================================

    def route_after_start(state):

        stage = state.get(
            "booking_stage"
        )

        if stage == "load_availability":

            return "availability"

        return END

    def route_after_date(state):

        if (
            state.get(
                "booking_stage"
            )
            == "load_availability"
        ):

            return "availability"

        return END

    def route_after_reason(state):

        if (
            state.get(
                "booking_stage"
            )
            == "confirm"
        ):

            return "confirm"

        return END

    def route_after_confirmation(state):

        if (
            state.get(
                "approval_status"
            )
            == "approved"
        ):

            return "create"

        return END

    # ==================================================
    # AVAILABILITY ROUTERS
    # ==================================================

    def route_after_availability_start(
        state
    ):

        stage = state.get(
            "booking_stage"
        )

        if stage == "load_availability_only":

            return "availability_only"

        return END

    def route_after_availability_date(
        state
    ):

        stage = state.get(
            "booking_stage"
        )

        if stage == "load_availability_only":

            return "availability_only"

        return END

    # ==================================================
    # KNOWLEDGE AGENT
    # ==================================================

    def knowledge_agent(state):

        messages = state.get(
            "messages",
            [],
        )

        intent = state.get(
            "intent"
        )

        last_message = (
            messages[-1]
            if messages
            else None
        )

        is_tool_result = (
            last_message is not None
            and getattr(
                last_message,
                "type",
                None,
            )
            == "tool"
        )

        system_message = {
            "role": "system",
            "content": """
Sos el asistente virtual de VetCare.

Podés utilizar herramientas para obtener información
real de VetCare.

También podés utilizar la herramienta
search_veterinary_knowledge para consultar la base
de conocimiento veterinaria.

No inventes información.

Para información de mascotas o turnos,
utilizá las herramientas de VetCare.

Para información veterinaria general,
utilizá search_veterinary_knowledge.

Nunca inventes IDs, mascotas, turnos ni horarios.

Cuando una herramienta ya devolvió información,
utilizá ese resultado para responder al usuario.
No vuelvas a solicitar la misma información.
""",
        }

        # ----------------------------------------------
        # FINAL RESPONSE AFTER TOOL
        # ----------------------------------------------

        if is_tool_result:

            response = agent_llm.invoke(
                [
                    system_message,
                    *messages,
                ]
            )

            print(
                "\n================ KNOWLEDGE AGENT ================"
            )

            print(
                "Tool result received."
            )

            print(
                "Final response:",
                response,
            )

            print(
                "Tool calls:",
                getattr(
                    response,
                    "tool_calls",
                    [],
                ),
            )

            print(
                "=================================================="
            )

            return {
                "messages": [
                    response,
                ],
                "response": response.content,
            }

        # ----------------------------------------------
        # GET PETS
        # ----------------------------------------------

        if intent == "GET_PETS":

            response = get_pets_llm.invoke(
                [
                    system_message,
                    *messages,
                ]
            )

        # ----------------------------------------------
        # OTHER INTENTS
        # ----------------------------------------------

        else:

            response = agent_llm_with_tools.invoke(
                [
                    system_message,
                    *messages,
                ]
            )

        print(
            "\n================ KNOWLEDGE AGENT ================"
        )

        print(
            "Response:",
            response,
        )

        print(
            "Tool calls:",
            getattr(
                response,
                "tool_calls",
                [],
            ),
        )

        print(
            "=================================================="
        )

        return {
            "messages": [
                response,
            ],
        }

    # ==================================================
    # KNOWLEDGE ROUTER
    # ==================================================

    def route_after_knowledge_agent(state):

        messages = state.get(
            "messages",
            [],
        )

        if not messages:
            return END

        last_message = messages[-1]

        tool_calls = getattr(
            last_message,
            "tool_calls",
            [],
        )

        if tool_calls:

            print(
                "→ agent_tools"
            )

            return "agent_tools"

        print(
            "→ END"
        )

        return END

    # ==================================================
    # GRAPH
    # ==================================================

    builder = StateGraph(
        VetCareState
    )

    # ==================================================
    # BOOKING NODES
    # ==================================================

    builder.add_node(
        "classify_intent",
        classify_intent,
    )

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

    # ==================================================
    # AVAILABILITY ONLY NODES
    # ==================================================

    builder.add_node(
        "start_availability",
        start_availability,
    )

    builder.add_node(
        "process_availability_date",
        process_availability_date,
    )

    builder.add_node(
        "availability_only",
        load_availability_only,
    )

    builder.add_node(
        "show_availability_only",
        show_availability_only,
    )

    # ==================================================
    # AGENT NODES
    # ==================================================

    builder.add_node(
        "knowledge_agent",
        knowledge_agent,
    )

    builder.add_node(
        "agent_tools",
        ToolNode(
            agent_tools,
        ),
    )

    # ==================================================
    # START
    # ==================================================

    def route_start(state):

        messages = state.get(
            "messages",
            [],
        )

        if not messages:
            return "classify_intent"

        last_message = messages[-1]

        if isinstance(
            last_message,
            dict,
        ):
            content = last_message.get(
                "content",
                "",
            )
        else:
            content = last_message.content

        print(
            "\n================ START ROUTING ================="
        )

        print(
            "Message:",
            content,
        )

        print(
            "Current booking_stage:",
            state.get(
                "booking_stage"
            ),
        )

        # --------------------------------------------------
        # NEW AVAILABILITY QUERY
        # --------------------------------------------------

        if is_availability_query(
            content
        ):

            print(
                "→ new availability query"
            )

            return "start_availability"

        # --------------------------------------------------
        # ACTIVE BOOKING
        # --------------------------------------------------

        if state.get(
            "booking_stage"
        ):

            print(
                "→ continue booking"
            )

            return route_booking_stage(
                state
            )

        # --------------------------------------------------
        # NEW CONVERSATION
        # --------------------------------------------------

        print(
            "→ classify intent"
        )

        return "classify_intent"

    builder.add_conditional_edges(
        START,
        route_start,
        {
            "classify_intent": "classify_intent",
            "start_booking": "start_booking",
            "process_date": "process_date",
            "availability": "availability",
            "select_slot": "select_slot",
            "process_reason": "process_reason",
            "confirm": "confirm",
            "start_availability": "start_availability",
            "process_availability_date": "process_availability_date",
            "availability_only": "availability_only",
            "show_availability_only": "show_availability_only",
            END: END,
        },
    )

    # ==================================================
    # INTENT
    # ==================================================

    builder.add_conditional_edges(
        "classify_intent",
        route_initial_intent,
        {
            "booking": "start_booking",
            "availability_query": "start_availability",
            "knowledge_agent": "knowledge_agent",
        },
    )

    # ==================================================
    # START BOOKING
    # ==================================================

    builder.add_conditional_edges(
        "start_booking",
        route_after_start,
        {
            "availability": "availability",
            END: END,
        },
    )

    # ==================================================
    # PROCESS DATE
    # ==================================================

    builder.add_conditional_edges(
        "process_date",
        route_after_date,
        {
            "availability": "availability",
            END: END,
        },
    )

    # ==================================================
    # AVAILABILITY
    # ==================================================

    builder.add_edge(
        "availability",
        "show_availability",
    )

    builder.add_edge(
        "show_availability",
        END,
    )

    # ==================================================
    # SELECT SLOT
    # ==================================================

    builder.add_edge(
        "select_slot",
        END,
    )

    # ==================================================
    # PROCESS REASON
    # ==================================================

    builder.add_conditional_edges(
        "process_reason",
        route_after_reason,
        {
            "confirm": "confirm",
            END: END,
        },
    )

    # ==================================================
    # CONFIRM
    # ==================================================

    builder.add_conditional_edges(
        "confirm",
        route_after_confirmation,
        {
            "create": "create",
            END: END,
        },
    )

    # ==================================================
    # CREATE
    # ==================================================

    builder.add_edge(
        "create",
        END,
    )

    # ==================================================
    # AVAILABILITY ONLY
    # ==================================================

    builder.add_conditional_edges(
        "start_availability",
        route_after_availability_start,
        {
            "availability_only": "availability_only",
            END: END,
        },
    )

    builder.add_conditional_edges(
        "process_availability_date",
        route_after_availability_date,
        {
            "availability_only": "availability_only",
            END: END,
        },
    )

    builder.add_edge(
        "availability_only",
        "show_availability_only",
    )

    builder.add_edge(
        "show_availability_only",
        END,
    )

    # ==================================================
    # KNOWLEDGE AGENT
    # ==================================================

    builder.add_conditional_edges(
        "knowledge_agent",
        route_after_knowledge_agent,
        {
            "agent_tools": "agent_tools",
            END: END,
        },
    )

    # ==================================================
    # TOOLS → AGENT
    # ==================================================

    builder.add_edge(
        "agent_tools",
        "knowledge_agent",
    )

    # ==================================================
    # CHECKPOINT
    # ==================================================

    checkpointer = InMemorySaver()

    return builder.compile(
        checkpointer=checkpointer,
    )


# ==================================================
# GRAPH INSTANCE
# ==================================================


graph = None


async def initialize_graph():

    global graph

    graph = await build_graph()