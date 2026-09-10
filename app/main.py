from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException
from langgraph.types import Command

import app.graph.graph as graph_module
from app.mcp_client import access_token_context
from app.schemas import ChatRequest, ChatResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n========================================")
    print("Initializing VetCare AI...")
    print("========================================")

    await graph_module.initialize_graph()

    print("\n========================================")
    print("VetCare AI initialized successfully.")
    print("========================================")

    yield

    print("\n========================================")
    print("Shutting down VetCare AI...")
    print("========================================")


app = FastAPI(
    title="VetCare AI",
    version="1.0.0",
    lifespan=lifespan,
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
async def chat(
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

    if graph_module.graph is None:
        raise HTTPException(
            status_code=503,
            detail="VetCare AI graph is not initialized",
        )

    token = access_token_context.set(
        access_token
    )

    try:
        config = {
            "configurable": {
                "thread_id": request.thread_id,
                "access_token": access_token,
            }
        }

        if request.resume:
            result = await graph_module.graph.ainvoke(
                Command(resume=True),
                config,
            )
        else:
            result = await graph_module.graph.ainvoke(
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

        response = result.get("response")

        if response:
            return {
                "response": response,
                "thread_id": request.thread_id,
                "status": "completed",
                "approval": None,
            }

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

        return {
            "response": "No pude generar una respuesta.",
            "thread_id": request.thread_id,
            "status": "completed",
            "approval": None,
        }

    finally:
        access_token_context.reset(token)