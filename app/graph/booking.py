import json
import re
from datetime import date, timedelta

from langchain_ollama import ChatOllama
from langgraph.types import interrupt
from pydantic import BaseModel

from app.config import settings
from app.mcp_client import get_mcp_tools


# --------------------------------------------------
# BOOKING EXTRACTION
# --------------------------------------------------


class BookingExtraction(BaseModel):
    pet_name: str | None = None
    date: str | None = None
    reason: str | None = None
    slot_time: str | None = None


llm = ChatOllama(
    model=settings.llm_model,
)


# --------------------------------------------------
# MCP HELPERS
# --------------------------------------------------


async def call_mcp_tool(
    tool_name: str,
    arguments: dict,
):
    """
    Ejecuta una MCP tool y normaliza su respuesta.

    MCP puede devolver el resultado como:

        [
            {
                "type": "text",
                "text": "{...JSON...}"
            }
        ]

    Por eso convertimos el contenido nuevamente
    a objetos Python.
    """

    tools = await get_mcp_tools()

    tool = next(
        (
            tool
            for tool in tools
            if tool.name == tool_name
        ),
        None,
    )

    if tool is None:
        raise RuntimeError(
            f"MCP tool '{tool_name}' was not found."
        )

    print(
        "\n================ MCP TOOL ================="
    )

    print(
        "Tool:",
        tool_name,
    )

    print(
        "Arguments:",
        arguments,
    )

    print(
        "==========================================="
    )

    raw_result = await tool.ainvoke(
        arguments
    )

    print(
        "\n================ MCP RAW RESULT ==========="
    )

    print(
        "Result:",
        raw_result,
    )

    print(
        "Result type:",
        type(raw_result),
    )

    print(
        "==========================================="
    )

    result = normalize_mcp_result(
        raw_result
    )

    print(
        "\n================ MCP NORMALIZED ============"
    )

    print(
        "Result:",
        result,
    )

    print(
        "Result type:",
        type(result),
    )

    print(
        "==========================================="
    )

    return result


# --------------------------------------------------
# MCP RESULT NORMALIZATION
# --------------------------------------------------


def normalize_mcp_result(result):
    """
    Convierte respuestas MCP de texto/JSON
    a objetos Python.
    """

    if isinstance(
        result,
        dict,
    ):
        return result

    if isinstance(
        result,
        list,
    ):

        normalized_items = []

        for item in result:

            if isinstance(
                item,
                dict,
            ):

                item_type = item.get(
                    "type"
                )

                if item_type == "text":

                    text = item.get(
                        "text",
                        "",
                    )

                    try:
                        parsed = json.loads(
                            text
                        )

                        normalized_items.append(
                            parsed
                        )

                    except json.JSONDecodeError:

                        normalized_items.append(
                            text
                        )

                    continue

            normalized_items.append(
                item
            )

        if len(
            normalized_items
        ) == 1:

            return normalized_items[0]

        return normalized_items

    if isinstance(
        result,
        str,
    ):

        try:
            return json.loads(
                result
            )

        except json.JSONDecodeError:
            return result

    return result


# --------------------------------------------------
# MESSAGE HELPER
# --------------------------------------------------


def get_last_message_content(
    state,
) -> str:

    message = state["messages"][-1]

    if isinstance(
        message,
        dict,
    ):
        return message["content"]

    return message.content


# --------------------------------------------------
# AVAILABILITY QUERY DETECTION
# --------------------------------------------------


def is_availability_query(
    message: str,
) -> bool:
    """
    Determina si el usuario solamente quiere
    consultar horarios disponibles.

    No utiliza el LLM porque es una decisión
    determinística del workflow.
    """

    normalized = (
        message
        .lower()
        .strip()
    )

    availability_patterns = [
        r"\bqué horarios\b",
        r"\bque horarios\b",
        r"\bqué horario\b",
        r"\bque horario\b",
        r"\bhorarios hay\b",
        r"\bhorarios disponibles\b",
        r"\bhorarios libre\b",
        r"\bhorarios libres\b",
        r"\bdisponibilidad\b",
        r"\bqué turnos hay\b",
        r"\bque turnos hay\b",
        r"\bqué turnos tengo disponibles\b",
        r"\bque turnos tengo disponibles\b",
    ]

    return any(
        re.search(
            pattern,
            normalized,
        )
        for pattern in availability_patterns
    )


# --------------------------------------------------
# DATE EXTRACTION
# --------------------------------------------------


def extract_relative_date(
    message: str,
) -> str | None:

    normalized = (
        message
        .lower()
        .strip()
    )

    today = date.today()

    if re.search(
        r"\bpasado mañana\b",
        normalized,
    ):
        return (
            today + timedelta(days=2)
        ).isoformat()

    if re.search(
        r"\bmañana\b",
        normalized,
    ):
        return (
            today + timedelta(days=1)
        ).isoformat()

    if re.search(
        r"\bhoy\b",
        normalized,
    ):
        return today.isoformat()

    return None


# --------------------------------------------------
# BOOKING DATA EXTRACTION
# --------------------------------------------------


def extract_booking_data(
    message: str,
) -> BookingExtraction:

    structured_llm = (
        llm.with_structured_output(
            BookingExtraction,
        )
    )

    prompt = f"""
Sos un extractor de datos para reservas veterinarias.

Extraé únicamente información explícitamente mencionada
por el usuario.

Campos:

pet_name:
nombre de la mascota.

date:
fecha explícitamente mencionada.

reason:
motivo de la consulta.

slot_time:
horario elegido por el usuario.

REGLAS MUY IMPORTANTES:

- No inventes datos.
- Si un dato no aparece, devolvé null.
- No inventes nombres.
- No inventes fechas.
- No inventes horarios.
- No interpretes información que el usuario no dijo.
- Si el usuario solamente dice el nombre de una mascota,
  date debe ser null.
- Si el usuario solamente dice un horario,
  slot_time debe contener ese horario.
- Las expresiones "hoy", "mañana" y "pasado mañana"
  NO deben convertirse a fechas.
  Esas expresiones serán procesadas por Python.

Mensaje del usuario:

{message}
"""

    extracted = structured_llm.invoke(
        prompt
    )

    relative_date = extract_relative_date(
        message
    )

    if relative_date:
        extracted.date = relative_date

    return extracted


# --------------------------------------------------
# START AVAILABILITY
# --------------------------------------------------


async def start_availability(
    state,
    config,
):

    message = get_last_message_content(
        state
    )

    extracted = extract_booking_data(
        message
    )

    # ----------------------------------------------
    # DATE EXISTS
    # ----------------------------------------------

    if extracted.date:

        return {
            "date": extracted.date,
            "booking_stage": "load_availability_only",
        }

    # ----------------------------------------------
    # DATE DOES NOT EXIST
    # ----------------------------------------------

    return {
        "response": (
            "¿Para qué fecha querés consultar "
            "los horarios disponibles?"
        ),
        "booking_stage": "select_availability_date",
    }


# --------------------------------------------------
# PROCESS AVAILABILITY DATE
# --------------------------------------------------


def process_availability_date(
    state,
):

    message = get_last_message_content(
        state
    )

    extracted = extract_booking_data(
        message
    )

    if not extracted.date:

        return {
            "response": (
                "No pude identificar la fecha.\n\n"
                "¿Para qué fecha querés consultar "
                "los horarios disponibles?"
            ),
            "booking_stage": "select_availability_date",
        }

    return {
        "date": extracted.date,
        "booking_stage": "load_availability_only",
    }


# --------------------------------------------------
# LOAD AVAILABILITY ONLY
# --------------------------------------------------


async def load_availability_only(
    state,
    config,
):

    result = await call_mcp_tool(
        "get_available_appointments",
        {
            "date": state["date"],
        },
    )

    if not isinstance(
        result,
        dict,
    ):
        raise ValueError(
            "Unexpected availability response: "
            f"{result}"
        )

    slots = result.get(
        "slots",
        [],
    )

    return {
        "available_slots": slots,
        "booking_stage": "show_availability_only",
    }


# --------------------------------------------------
# SHOW AVAILABILITY ONLY
# --------------------------------------------------


def show_availability_only(
    state,
):

    slots = (
        state.get(
            "available_slots"
        )
        or []
    )

    available_slots = [
        slot
        for slot in slots
        if slot.get(
            "available"
        )
        is True
    ]

    if not available_slots:

        return {
            "response": (
                f"No encontré horarios disponibles "
                f"para el {state['date']}."
            ),
            "booking_stage": "completed",
        }

    lines = [
        f"- {slot['time']}"
        for slot in available_slots
    ]

    return {
        "response": (
            f"Estos son los horarios disponibles "
            f"para el {state['date']}:\n\n"
            + "\n".join(lines)
        ),
        "booking_stage": "completed",
    }


# --------------------------------------------------
# START BOOKING
# --------------------------------------------------


async def start_booking(
    state,
    config,
):

    message = get_last_message_content(
        state
    )

    extracted = extract_booking_data(
        message
    )

    # ----------------------------------------------
    # GET PETS THROUGH MCP
    # ----------------------------------------------

    pets_result = await call_mcp_tool(
        "get_pets",
        {},
    )

    pets = normalize_mcp_result(
        pets_result
    )

    if isinstance(
        pets,
        dict,
    ):
        pets = [pets]

    if not isinstance(
        pets,
        list,
    ):
        raise ValueError(
            "Unexpected pets response: "
            f"{pets}"
        )

    print(
        "\n================ PETS ================="
    )

    print(
        "Pets:",
        pets,
    )

    print(
        "========================================"
    )

    # ----------------------------------------------
    # NO PET SELECTED
    # ----------------------------------------------

    if not extracted.pet_name:

        return {
            "response": (
                "¿Para qué mascota querés "
                "sacar el turno?"
            ),
            "booking_stage": "select_pet",
        }

    # ----------------------------------------------
    # FIND PET
    # ----------------------------------------------

    requested_pet_name = (
        extracted.pet_name
        .strip()
        .lower()
    )

    pet = next(
        (
            pet
            for pet in pets
            if isinstance(
                pet,
                dict,
            )
            and isinstance(
                pet.get("name"),
                str,
            )
            and pet["name"]
            .strip()
            .lower()
            == requested_pet_name
        ),
        None,
    )

    # ----------------------------------------------
    # PET NOT FOUND
    # ----------------------------------------------

    if not pet:

        names = ", ".join(
            pet.get(
                "name",
                "Sin nombre",
            )
            for pet in pets
            if isinstance(
                pet,
                dict,
            )
        )

        return {
            "response": (
                f"No encontré una mascota llamada "
                f"{extracted.pet_name}. "
                f"Tus mascotas registradas son: "
                f"{names}."
            ),
            "booking_stage": "select_pet",
        }

    # ----------------------------------------------
    # PET FOUND
    # ----------------------------------------------

    result = {
        "pet_id": pet["id"],
        "pet_name": pet["name"],
        "date": extracted.date,
        "reason": extracted.reason,
        "slot_time": extracted.slot_time,
    }

    print(
        "\n================ PET FOUND ================"
    )

    print(
        "Pet:",
        pet,
    )

    print(
        "==========================================="
    )

    # ----------------------------------------------
    # NO DATE
    # ----------------------------------------------

    if not extracted.date:

        result["response"] = (
            f"¿Para qué fecha querés sacar "
            f"el turno para {pet['name']}?"
        )

        result["booking_stage"] = (
            "select_date"
        )

        return result

    # ----------------------------------------------
    # DATE EXISTS
    # ----------------------------------------------

    result["booking_stage"] = (
        "load_availability"
    )

    return result


# --------------------------------------------------
# ASK BOOKING DATE
# --------------------------------------------------


def ask_booking_date(
    state,
):

    return {
        "response": (
            f"¿Para qué fecha querés sacar "
            f"el turno para "
            f"{state['pet_name']}?"
        ),
        "booking_stage": "select_date",
    }


# --------------------------------------------------
# PROCESS DATE
# --------------------------------------------------


def process_date(
    state,
):

    message = get_last_message_content(
        state
    )

    extracted = extract_booking_data(
        message
    )

    if not extracted.date:

        return {
            "response": (
                "No pude identificar la fecha.\n\n"
                f"¿Para qué fecha querés sacar "
                f"el turno para "
                f"{state['pet_name']}?"
            ),
            "booking_stage": "select_date",
        }

    return {
        "date": extracted.date,
        "booking_stage": "load_availability",
    }


# --------------------------------------------------
# LOAD AVAILABILITY
# --------------------------------------------------


async def load_availability(
    state,
    config,
):

    result = await call_mcp_tool(
        "get_available_appointments",
        {
            "date": state["date"],
        },
    )

    if not isinstance(
        result,
        dict,
    ):
        raise ValueError(
            "Unexpected availability response: "
            f"{result}"
        )

    slots = result.get(
        "slots",
        [],
    )

    return {
        "available_slots": slots,
        "booking_stage": "select_slot",
    }


# --------------------------------------------------
# SHOW AVAILABILITY
# --------------------------------------------------


def show_availability(
    state,
):

    slots = (
        state.get(
            "available_slots"
        )
        or []
    )

    available_slots = [
        slot
        for slot in slots
        if slot.get(
            "available"
        )
        is True
    ]

    if not available_slots:

        return {
            "response": (
                f"No encontré horarios disponibles "
                f"para el {state['date']}."
            ),
            "booking_stage": "completed",
        }

    lines = [
        f"- {slot['time']}"
        for slot in available_slots
    ]

    return {
        "response": (
            f"Estos son los horarios disponibles "
            f"para {state['pet_name']} "
            f"el {state['date']}:\n\n"
            + "\n".join(lines)
            + "\n\n¿Cuál preferís?"
        ),
        "booking_stage": "select_slot",
    }


# --------------------------------------------------
# SELECT SLOT
# --------------------------------------------------


def select_slot(
    state,
):

    message = get_last_message_content(
        state
    ).strip()

    print(
        "\n--- SELECT SLOT ---"
    )

    print(
        "User message:",
        message,
    )

    print(
        "Available slots:",
        state.get(
            "available_slots"
        ),
    )

    match = re.search(
        r"\b([01]?\d|2[0-3]):([0-5]\d)\b",
        message,
    )

    if not match:

        return {
            "response": (
                "No pude identificar el horario. "
                "Por favor elegí uno de los "
                "horarios disponibles."
            ),
            "booking_stage": "select_slot",
        }

    requested_time = (
        f"{int(match.group(1)):02d}:"
        f"{match.group(2)}"
    )

    print(
        "Requested time:",
        requested_time,
    )

    slots = (
        state.get(
            "available_slots"
        )
        or []
    )

    selected = next(
        (
            slot
            for slot in slots
            if slot.get(
                "available"
            ) is True
            and slot.get(
                "time"
            ) == requested_time
        ),
        None,
    )

    if not selected:

        available = ", ".join(
            slot["time"]
            for slot in slots
            if slot.get(
                "available"
            ) is True
        )

        return {
            "response": (
                f"El horario {requested_time} "
                f"no está disponible.\n\n"
                f"Horarios disponibles: "
                f"{available}"
            ),
            "booking_stage": "select_slot",
        }

    print(
        "SELECTED SLOT:",
        selected,
    )

    result = {
        "slot_id": selected["id"],
        "slot_time": selected["time"],
        "booking_stage": "select_reason",
        "response": (
            f"Elegiste las "
            f"{selected['time']} "
            f"para {state['pet_name']}.\n\n"
            f"¿Cuál es el motivo de la consulta?"
        ),
    }

    return result


# --------------------------------------------------
# ASK REASON
# --------------------------------------------------


def ask_reason(
    state,
):

    return {
        "response": (
            f"¿Cuál es el motivo de la consulta "
            f"para {state['pet_name']}?"
        ),
        "booking_stage": "select_reason",
    }


# --------------------------------------------------
# PROCESS REASON
# --------------------------------------------------


def process_reason(
    state,
):

    message = get_last_message_content(
        state
    ).strip()

    if not message:

        return {
            "response": (
                f"¿Cuál es el motivo de la consulta "
                f"para {state['pet_name']}?"
            ),
            "booking_stage": "select_reason",
        }

    return {
        "reason": message,
        "booking_stage": "confirm",
    }


# --------------------------------------------------
# CONFIRM BOOKING
# --------------------------------------------------


def confirm_booking(
    state,
):

    confirmation = interrupt(
        {
            "type": "booking_confirmation",
            "message": (
                "¿Querés confirmar este turno?"
            ),
            "appointment": {
                "pet_name": state["pet_name"],
                "date": state["date"],
                "time": state["slot_time"],
                "reason": state["reason"],
            },
        }
    )

    return {
        "approval_status": (
            "approved"
            if confirmation is True
            else "denied"
        ),
    }


# --------------------------------------------------
# CREATE BOOKING
# --------------------------------------------------


async def create_booking(
    state,
    config,
):

    appointment = await call_mcp_tool(
        "create_appointment",
        {
            "reason": state["reason"],
            "pet_id": state["pet_id"],
            "slot_id": state["slot_id"],
        },
    )

    if not isinstance(
        appointment,
        dict,
    ):
        raise ValueError(
            "Unexpected appointment response: "
            f"{appointment}"
        )

    return {
        "appointment_id": appointment["id"],
        "response": (
            f"Turno confirmado para "
            f"{state['pet_name']} "
            f"el {state['date']} "
            f"a las {state['slot_time']}."
        ),
        "booking_stage": "completed",
    }