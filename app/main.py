from fastapi import FastAPI, Header, HTTPException
from langgraph.types import Command

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

    # --------------------------------------------------
    # VALIDATE AUTHORIZATION
    # --------------------------------------------------

    if not authorization:

        raise HTTPException(
            status_code=401,
            detail="Authorization header is required",
        )

    if not authorization.startswith(
        "Bearer "
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header",
        )

    access_token = authorization.replace(
        "Bearer ",
        "",
        1,
    )

    # --------------------------------------------------
    # LANGGRAPH CONFIG
    # --------------------------------------------------

    config = {
        "configurable": {
            "thread_id": request.thread_id,
            "access_token": access_token,
        }
    }

    # --------------------------------------------------
    # RESUME INTERRUPT
    # --------------------------------------------------

    if request.resume:

        result = graph.invoke(
            Command(
                resume=True,
            ),
            config,
        )

    # --------------------------------------------------
    # NEW / CONTINUING MESSAGE
    # --------------------------------------------------

    else:

        result = graph.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": request.message or "",
                    }
                ],
            },
            config,
        )

    # --------------------------------------------------
    # INTERRUPT
    # --------------------------------------------------

    if "__interrupt__" in result:

        interrupt_data = result[
            "__interrupt__"
        ][0].value

        return {
            "response": interrupt_data.get(
                "message",
                "Necesito tu confirmación para continuar.",
            ),
            "thread_id": request.thread_id,
            "status": "waiting_approval",
            "approval": interrupt_data,
        }

    # --------------------------------------------------
    # RESPONSE FROM CURRENT GRAPH EXECUTION
    # --------------------------------------------------

    response = result.get(
        "response"
    )

    if response:

        return {
            "response": response,
            "thread_id": request.thread_id,
            "status": "completed",
            "approval": None,
        }

    # --------------------------------------------------
    # FALLBACK TO LAST MESSAGE
    # --------------------------------------------------

    messages = result.get(
        "messages",
        [],
    )

    if messages:

        final_message = messages[-1]

        if isinstance(
            final_message,
            dict,
        ):

            content = final_message.get(
                "content",
                "",
            )

        else:

            content = final_message.content

        return {
            "response": content,
            "thread_id": request.thread_id,
            "status": "completed",
            "approval": None,
        }

    # --------------------------------------------------
    # EMPTY RESPONSE
    # --------------------------------------------------

    return {
        "response": "No pude generar una respuesta.",
        "thread_id": request.thread_id,
        "status": "completed",
        "approval": None,
    }