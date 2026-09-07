from langchain_core.tools import tool


@tool
def get_available_appointments(date: str) -> str:
    """Consulta los turnos disponibles para una fecha."""
    return f"Hay turnos disponibles para el {date}."