from fastapi import FastAPI
from langchain_ollama import ChatOllama
from app.config import settings
from app.schemas import ChatRequest
from app.prompts import chat_prompt

app = FastAPI()

llm = ChatOllama(
    model=settings.llm_model,
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest):
    prompt = chat_prompt.invoke(
    {
        "question": request.message,
    }
)

    response = llm.invoke(prompt)

    return {
        "message": response.content
    }