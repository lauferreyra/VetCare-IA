from langchain_core.tools import tool


@tool
def get_available_appointments(date: str) -> str:
    """
    Consulta los turnos disponibles para una fecha.
    """

    appointments = {
        "2026-09-08": [
            "10:00",
            "11:30",
            "15:00",
            "16:30",
        ],
    }

    available = appointments.get(date)

    if not available:
        return f"No hay turnos disponibles para {date}."

    return (
        f"Turnos disponibles para {date}: "
        + ", ".join(available)
    )