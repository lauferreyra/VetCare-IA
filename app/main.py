from fastapi import FastAPI
from app.schemas import ChatRequest

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/chat")
def chat(request: ChatRequest):
    return {
        "message": f"Recibí tu mensaje: {request.message}"
    }