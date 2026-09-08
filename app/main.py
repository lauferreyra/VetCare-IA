from fastapi import FastAPI

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
def chat(request: ChatRequest):

    config = {
        "configurable": {
            "thread_id": request.thread_id,
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