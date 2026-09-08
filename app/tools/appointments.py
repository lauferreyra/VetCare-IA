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
    Consulta los turnos disponibles para una fecha.
    """

    access_token = config["configurable"]["access_token"]

    api = VetCareApiService(
        access_token=access_token,
    )

    appointments = api.get_available_appointments(
        date=date,
    )

    return str(appointments)