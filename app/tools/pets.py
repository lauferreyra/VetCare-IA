from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from app.services.vetcare_api import VetCareApiService


@tool
def get_my_pets(
    config: RunnableConfig,
) -> str:
    """
    Obtiene las mascotas del usuario autenticado.
    """

    access_token = config["configurable"]["access_token"]

    api = VetCareApiService(
        access_token=access_token,
    )

    pets = api.get_pets()

    return str(pets)