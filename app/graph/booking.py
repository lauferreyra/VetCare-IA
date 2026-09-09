import re
from datetime import date, timedelta

from langchain_ollama import ChatOllama
from langgraph.types import interrupt
from pydantic import BaseModel

from app.config import settings
from app.services.vetcare_api import VetCareApiService


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
# MESSAGE HELPER
# --------------------------------------------------


def get_last_message_content(state) -> str:
    message = state["messages"][-1]

    if isinstance(message, dict):
        return message["content"]

    return message.content


# --------------------------------------------------
# DATE EXTRACTION
# --------------------------------------------------


def extract_relative_date(message: str) -> str | None:
    """
    Convierte expresiones relativas simples a YYYY-MM-DD.

    Importante:
    las fechas relativas se procesan con Python
    y no con el LLM.
    """

    normalized = message.lower().strip()

    today = date.today()

    if re.search(r"\bhoy\b", normalized):
        return today.isoformat()

    if re.search(r"\bmañana\b", normalized):
        return (today + timedelta(days=1)).isoformat()

    if re.search(r"\bpasado mañana\b", normalized):
        return (today + timedelta(days=2)).isoformat()

    return None


# --------------------------------------------------
# BOOKING DATA EXTRACTION
# --------------------------------------------------


def extract_booking_data(
    message: str,
) -> BookingExtraction:

    structured_llm = llm.with_structured_output(
        BookingExtraction,
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

    extracted = structured_llm.invoke(prompt)

    relative_date = extract_relative_date(message)

    if relative_date:
        extracted.date = relative_date

    return extracted


# --------------------------------------------------
# START BOOKING
# --------------------------------------------------


def start_booking(state, config):

    message = get_last_message_content(state)

    extracted = extract_booking_data(message)

    access_token = config["configurable"]["access_token"]

    api = VetCareApiService(
        access_token=access_token,
    )

    pets = api.get_pets()

    if not extracted.pet_name:
        return {
            "response": (
                "¿Para qué mascota querés sacar el turno?"
            ),
            "booking_stage": "select_pet",
        }

    pet = next(
        (
            pet
            for pet in pets
            if pet["name"].lower()
            == extracted.pet_name.lower()
        ),
        None,
    )

    if not pet:

        names = ", ".join(
            pet["name"]
            for pet in pets
        )

        return {
            "response": (
                f"No encontré una mascota llamada "
                f"{extracted.pet_name}. "
                f"Tus mascotas registradas son: {names}."
            ),
            "booking_stage": "select_pet",
        }

    result = {
        "pet_id": pet["id"],
        "pet_name": pet["name"],
        "date": extracted.date,
        "reason": extracted.reason,
        "slot_time": extracted.slot_time,
    }

    # ----------------------------------------------
    # NO DATE
    # ----------------------------------------------

    if not extracted.date:

        result["response"] = (
            f"¿Para qué fecha querés sacar "
            f"el turno para {pet['name']}?"
        )

        result["booking_stage"] = "select_date"

        return result

    # ----------------------------------------------
    # DATE EXISTS
    # ----------------------------------------------

    result["booking_stage"] = "load_availability"

    return result


# --------------------------------------------------
# ASK BOOKING DATE
# --------------------------------------------------


def ask_booking_date(state):

    return {
        "response": (
            f"¿Para qué fecha querés sacar "
            f"el turno para {state['pet_name']}?"
        ),
        "booking_stage": "select_date",
    }


# --------------------------------------------------
# PROCESS DATE
# --------------------------------------------------


def process_date(state):

    message = get_last_message_content(state)

    extracted = extract_booking_data(message)

    if not extracted.date:

        return {
            "response": (
                f"No pude identificar la fecha.\n\n"
                f"¿Para qué fecha querés sacar "
                f"el turno para {state['pet_name']}?"
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


def load_availability(state, config):

    access_token = config["configurable"]["access_token"]

    api = VetCareApiService(
        access_token=access_token,
    )

    result = api.get_available_appointments(
        state["date"],
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


def show_availability(state):

    slots = state.get(
        "available_slots"
    ) or []

    available_slots = [
        slot
        for slot in slots
        if slot.get("available") is True
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


def select_slot(state):

    message = get_last_message_content(
        state
    ).strip()

    print("\n--- SELECT SLOT ---")

    print(
        "User message:",
        message,
    )

    print(
        "Available slots:",
        state.get("available_slots"),
    )

    # ----------------------------------------------
    # EXTRACT TIME DIRECTLY WITH PYTHON
    # ----------------------------------------------

    match = re.search(
        r"\b([01]?\d|2[0-3]):([0-5]\d)\b",
        message,
    )

    if not match:

        return {
            "response": (
                "No pude identificar el horario. "
                "Por favor elegí uno de los horarios disponibles."
            ),
            "booking_stage": "select_slot",
        }

    requested_time = (
        f"{int(match.group(1)):02d}:{match.group(2)}"
    )

    print(
        "Requested time:",
        requested_time,
    )

    slots = state.get(
        "available_slots"
    ) or []

    selected = next(
        (
            slot
            for slot in slots
            if slot.get("available") is True
            and slot.get("time") == requested_time
        ),
        None,
    )

    # ----------------------------------------------
    # INVALID SLOT
    # ----------------------------------------------

    if not selected:

        available = ", ".join(
            slot["time"]
            for slot in slots
            if slot.get("available") is True
        )

        return {
            "response": (
                f"El horario {requested_time} "
                f"no está disponible.\n\n"
                f"Horarios disponibles: {available}"
            ),
            "booking_stage": "select_slot",
        }

    # ----------------------------------------------
    # VALID SLOT
    # ----------------------------------------------

    print(
        "SELECTED SLOT:",
        selected,
    )

    result = {
        "slot_id": selected["id"],
        "slot_time": selected["time"],
        "booking_stage": "select_reason",
        "response": (
            f"Elegiste las {selected['time']} "
            f"para {state['pet_name']}.\n\n"
            f"¿Cuál es el motivo de la consulta?"
        ),
    }

    print(
        "--- SELECT SLOT RESULT ---"
    )

    print(result)

    return result


# --------------------------------------------------
# ASK REASON
# --------------------------------------------------


def ask_reason(state):

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


def process_reason(state):

    message = get_last_message_content(
        state
    )

    extracted = extract_booking_data(
        message
    )

    if not extracted.reason:

        return {
            "response": (
                f"¿Cuál es el motivo de la consulta "
                f"para {state['pet_name']}?"
            ),
            "booking_stage": "select_reason",
        }

    return {
        "reason": extracted.reason,
        "booking_stage": "confirm",
    }


# --------------------------------------------------
# CONFIRM BOOKING
# --------------------------------------------------


def confirm_booking(state):

    confirmation = interrupt(
        {
            "type": "booking_confirmation",
            "message": "¿Querés confirmar este turno?",
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


def create_booking(state, config):

    access_token = config["configurable"]["access_token"]

    api = VetCareApiService(
        access_token=access_token,
    )

    appointment = api.create_appointment(
        {
            "reason": state["reason"],
            "petId": state["pet_id"],
            "slotId": state["slot_id"],
        }
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