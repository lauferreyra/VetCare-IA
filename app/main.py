from fastapi import FastAPI
from langchain_ollama import ChatOllama

from app.config import settings
from app.prompts import chat_prompt, intent_prompt
from app.schemas import ChatRequest
from app.ai_models import ChatIntent
from app.tools import get_available_appointments
from langchain_core.messages import ToolMessage
from app.agent import run_agent

app = FastAPI()

llm = ChatOllama(
    model=settings.llm_model,
)

chain = chat_prompt | llm

structured_llm = llm.with_structured_output(ChatIntent)

structured_chain = intent_prompt | structured_llm

llm_with_tools = llm.bind_tools(
    [get_available_appointments]
)

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest):
    response = chain.invoke(
        {
            "question": request.message,
        }
    )

    return {
        "message": response.content
    }


@app.post("/chat/intent")
def chat_intent(request: ChatRequest):
    result = structured_chain.invoke(
        {
            "question": request.message,
        }
    )

    return result.model_dump()

@app.post("/chat/tool")
def chat_tool(request: ChatRequest):
    response = llm_with_tools.invoke(
        request.message
    )

    tool_call = response.tool_calls[0]

    result = get_available_appointments.invoke(
        tool_call["args"]
    )

    final_response = llm.invoke(
        [
            ("human", request.message),
            response,
            ToolMessage(
                content=result,
                tool_call_id=tool_call["id"],
            )
        ]
    )

    return {
        "message": final_response.content
    }

@app.post("/agent")
def chat_agent(request: ChatRequest):
    return {
        "message": run_agent(request.message)
    }