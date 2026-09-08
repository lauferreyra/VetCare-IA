from langchain_core.tools import tool


@tool
def get_current_user() -> str:
    """
    Obtiene información del usuario actual.
    """

    return (
        "Usuario actual: "
        "Lautaro."
    )