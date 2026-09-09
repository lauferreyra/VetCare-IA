from typing import TypedDict

from langchain_core.messages import BaseMessage


class VetCareState(TypedDict):
    messages: list[BaseMessage]

    user_id: str | None
    intent: str | None

    pet_id: int | None
    pet_name: str | None

    date: str | None

    available_slots: list[dict] | None

    slot_id: int | None
    slot_time: str | None

    reason: str | None

    appointment_id: int | None

    response: str | None

    approval_status: str | None

    booking_stage: str | None