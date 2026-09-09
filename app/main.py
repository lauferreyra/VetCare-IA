from fastapi import FastAPI, Header, HTTPException

from app.graph.graph import graph
from app.schemas import ChatRequest, ChatResponse


app = FastAPI(
    title="VetCare AI",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
    }


@app.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    authorization: str | None = Header(default=None),
):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is required",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header",
        )

    access_token = authorization.replace(
        "Bearer ",
        "",
        1,
    )

    config = {
        "configurable": {
            "thread_id": request.thread_id,
            "access_token": access_token,
        }
    }

    result = graph.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": request.message,
                }
            ],
            "user_id": None,
            "intent": None,
            "pet_id": None,
            "pet_name": None,
            "date": None,
            "slot_id": None,
            "reason": None,
            "appointment_id": None,
            "response": None,
        },
        config,
    )

    final_message = result["messages"][-1]

    return {
        "response": final_message.content,
        "thread_id": request.thread_id,
    }