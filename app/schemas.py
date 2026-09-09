from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str | None = None
    thread_id: str = "default"
    resume: bool = False


class ChatResponse(BaseModel):
    response: str
    thread_id: str
    status: str
    approval: dict | None = None