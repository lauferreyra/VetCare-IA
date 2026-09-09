from typing import TypedDict

from langchain_core.messages import BaseMessage


class VetCareState(TypedDict):
    messages: list[BaseMessage]

    user_id: str | None

    intent: str | None

    pet_id: str | None
    pet_name: str | None

    date: str | None
    slot_id: str | None
    reason: str | None

    appointment_id: str | None

    response: str | None