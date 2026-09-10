from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class VetCareState(TypedDict):
    messages: Annotated[
        list[BaseMessage],
        add_messages,
    ]

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