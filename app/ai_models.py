from typing import Literal

from pydantic import BaseModel


class ChatIntent(BaseModel):
    intent: Literal[
        "GENERAL_CHAT",
        "BOOK_APPOINTMENT",
        "CANCEL_APPOINTMENT",
        "GET_APPOINTMENTS",
        "GET_PETS",
        "MEDICAL_QUERY",
    ]
    pet_name: str | None = None
    date: str | None = None