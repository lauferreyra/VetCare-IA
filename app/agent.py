from langchain.agents import create_agent

from app.config import settings
from app.tools import get_available_appointments
from langchain_ollama import ChatOllama


llm = ChatOllama(
    model=settings.llm_model,
)

agent = create_agent(
    model=llm,
    tools=[get_available_appointments],
)

def run_agent(message: str):
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": message,
                }
            ]
        }
    )

    return result["messages"][-1].content
