from fastapi import FastAPI
from langchain_ollama import ChatOllama

from app.config import settings
from app.prompts import chat_prompt, intent_prompt
from app.schemas import ChatRequest
from app.ai_models import ChatIntent

app = FastAPI()

llm = ChatOllama(
    model=settings.llm_model,
)

chain = chat_prompt | llm

structured_llm = llm.with_structured_output(ChatIntent)

structured_chain = intent_prompt | structured_llm

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