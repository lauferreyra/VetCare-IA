from fastapi import FastAPI
from langchain_ollama import ChatOllama

from app.config import settings
from app.prompts import chat_prompt
from app.schemas import ChatRequest

app = FastAPI()

llm = ChatOllama(
    model=settings.llm_model,
)

chain = chat_prompt | llm


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