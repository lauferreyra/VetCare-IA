from langchain_core.tools import tool


@tool
def get_my_pets() -> str:
    """
    Obtiene las mascotas del usuario.
    """

    return (
        "Tus mascotas son: "
        "Firulais, perro; "
        "Michi, gato."
    )