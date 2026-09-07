from langchain_core.prompts import ChatPromptTemplate


chat_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Sos el asistente virtual de VetCare. "
            "Respondé de manera clara, profesional y amigable.",
        ),
        (
            "human",
            "{question}",
        ),
    ]
)