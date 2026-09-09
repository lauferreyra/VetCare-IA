from app.tools.appointments import (
    cancel_appointment,
    create_appointment,
    get_available_appointments,
    get_my_appointments,
)
from app.tools.pets import get_my_pets


read_tools = [
    get_available_appointments,
    get_my_appointments,
    get_my_pets,
]

write_tools = [
    create_appointment,
    cancel_appointment,
]

all_tools = [
    *read_tools,
    *write_tools,
]