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

intent_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Analizá la intención del usuario relacionada con VetCare. "
"Clasificá el mensaje en una de las categorías permitidas. "
"Usá estas definiciones: "
"GENERAL_CHAT: conversación general que no corresponde a otra categoría. "
"BOOK_APPOINTMENT: el usuario quiere solicitar o reservar un nuevo turno. "
"CANCEL_APPOINTMENT: el usuario quiere cancelar un turno existente. "
"GET_APPOINTMENTS: el usuario quiere consultar sus turnos existentes. "
"GET_PETS: el usuario quiere consultar información sobre sus mascotas. "
"MEDICAL_QUERY: el usuario realiza una consulta relacionada con la salud de su mascota. "
"Extraé únicamente información explícitamente mencionada por el usuario. "
"Si el nombre de la mascota no aparece, devolvé null. "
"Si el usuario no proporciona una fecha, devolvé null. "
"Nunca inventes, supongas ni generes fechas por tu cuenta.",
        ),
        (
            "human",
            "{question}",
        ),
    ]
)