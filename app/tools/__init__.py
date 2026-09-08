from app.tools.appointments import (
    get_available_appointments,
    get_my_appointments,
)

from app.tools.pets import (
    get_my_pets,
)


all_tools = [
    get_available_appointments,
    get_my_appointments,
    get_my_pets,
]