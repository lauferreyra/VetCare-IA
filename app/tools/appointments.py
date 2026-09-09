from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from app.services.vetcare_api import VetCareApiService


@tool
def get_my_appointments(
    config: RunnableConfig,
) -> str:
    """
    Obtiene los turnos del usuario autenticado.
    """

    access_token = config["configurable"]["access_token"]

    api = VetCareApiService(
        access_token=access_token,
    )

    appointments = api.get_appointments()

    return str(appointments)


@tool
def get_available_appointments(
    date: str,
    config: RunnableConfig,
) -> str:
    """
    Consulta los horarios disponibles para una fecha.
    """

    access_token = config["configurable"]["access_token"]

    api = VetCareApiService(
        access_token=access_token,
    )

    appointments = api.get_available_appointments(
        date=date,
    )

    return str(appointments)


@tool
def create_appointment(
    reason: str,
    pet_id: int,
    slot_id: int,
    config: RunnableConfig,
) -> str:
    """
    Crea un turno para una mascota del usuario
    utilizando un horario disponible.
    """

    access_token = config["configurable"]["access_token"]

    api = VetCareApiService(
        access_token=access_token,
    )

    appointment = api.create_appointment(
        {
            "reason": reason,
            "petId": pet_id,
            "slotId": slot_id,
        }
    )

    return str(appointment)


@tool
def cancel_appointment(
    appointment_id: int,
    config: RunnableConfig,
) -> str:
    """
    Cancela un turno del usuario.
    """

    access_token = config["configurable"]["access_token"]

    api = VetCareApiService(
        access_token=access_token,
    )

    appointment = api.cancel_appointment(
        appointment_id,
    )

    return str(appointment)