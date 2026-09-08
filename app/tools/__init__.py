from app.tools.appointments import (
    get_available_appointments,
)

from app.tools.pets import (
    get_my_pets,
)

from app.tools.users import (
    get_current_user,
)


all_tools = [
    get_available_appointments,
    get_my_pets,
    get_current_user,
]