# VetCare AI

Servicio de inteligencia artificial para VetCare, desarrollado con
**Python, FastAPI, LangChain, LangGraph, Ollama y Qwen**, integrado con
la API real de VetCare.

El objetivo del proyecto es construir progresivamente un asistente de IA
capaz de:

-   conversar con usuarios;
-   identificar intenciones;
-   consultar información real de VetCare mediante herramientas;
-   ejecutar workflows determinísticos;
-   mantener contexto por conversación;
-   pedir aprobación humana antes de ejecutar acciones sensibles;
-   consultar una base de conocimiento mediante **RAG**;
-   evolucionar posteriormente hacia una arquitectura basada en **MCP**
    y observabilidad con **LangSmith**.

Este proyecto también funciona como laboratorio práctico para aprender
conceptos de **LLMs, prompting, structured output, tools, tool calling,
agents, LangGraph, memory, RAG, vector databases, HITL y MCP**.

------------------------------------------------------------------------

# 1. Arquitectura general

VetCare está compuesto por diferentes servicios:

``` text
                         ┌─────────────────────┐
                         │     VetCare Web      │
                         │  Next.js / React     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     VetCare API     │
                         │       NestJS        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     PostgreSQL      │
                         │       pgvector      │
                         └─────────────────────┘


                         ┌─────────────────────┐
                         │     VetCare AI      │
                         │ Python / FastAPI    │
                         │ LangChain           │
                         │ LangGraph           │
                         │ Ollama / Qwen       │
                         │ RAG                 │
                         └──────────┬──────────┘
                                    │
                                    ▼
                              VetCare API
```

La separación de responsabilidades es:

-   **VetCare Web:** interfaz de usuario.
-   **VetCare API:** lógica de negocio, autenticación y acceso a
    PostgreSQL.
-   **VetCare AI:** inteligencia artificial, agentes, workflows, tools y
    RAG.
-   **PostgreSQL:** persistencia de VetCare y almacenamiento vectorial
    mediante `pgvector`.

Una decisión importante de arquitectura es que **VetCare AI no accede
directamente a las tablas de negocio** para operar sobre mascotas o
turnos. La intención es utilizar la API de VetCare como frontera de
negocio.

------------------------------------------------------------------------

# 2. Estructura del repositorio

Actualmente la solución está organizada conceptualmente así:

``` text
VetCare
├── vetcare-web
├── vetcare-api
└── vetcare-ai
```

Y `vetcare-ai` tiene aproximadamente esta estructura:

``` text
vetcare-ai/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── ai_models.py
│   ├── prompts.py
│   │
│   ├── graph/
│   │   ├── graph.py
│   │   ├── state.py
│   │   └── booking.py
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── ingest.py
│   │   ├── retriever.py
│   │   └── answer.py
│   │
│   ├── services/
│   │   └── vetcare_api.py
│   │
│   └── tools/
│       ├── __init__.py
│       ├── appointments.py
│       ├── pets.py
│       └── knowledge.py
│
├── documents/
│   └── general/
│       ├── vacunacion.md
│       ├── turnos.md
│       └── alimentacion.md
│
├── .env
├── .env.example
├── .gitignore
└── README.md
```

------------------------------------------------------------------------

# 3. Python

Python es el lenguaje utilizado para desarrollar `vetcare-ai`.

Se eligió porque posee un ecosistema muy amplio para trabajar con:

-   inteligencia artificial;
-   machine learning;
-   LLMs;
-   embeddings;
-   RAG;
-   agentes;
-   procesamiento de lenguaje natural.

La versión utilizada actualmente es:

``` text
Python 3.12.14
```

------------------------------------------------------------------------

# 4. Entorno virtual (`venv`)

El proyecto utiliza:

``` text
.venv/
```

Un entorno virtual permite aislar las dependencias del proyecto.

Conceptualmente:

``` text
Node.js
   ↓
package.json
   ↓
node_modules
```

En Python:

``` text
Python
   ↓
pip
   ↓
.venv/
```

## Crear

``` bash
python3.12 -m venv .venv
```

## Activar

macOS/Linux:

``` bash
source .venv/bin/activate
```

------------------------------------------------------------------------

# 5. Instalación de dependencias

Con el entorno virtual activado:

``` bash
pip install fastapi
pip install "uvicorn[standard]"
pip install langchain
pip install langchain-ollama
pip install langgraph
pip install pydantic-settings
pip install httpx
```

Para RAG con PostgreSQL + pgvector:

``` bash
pip install langchain-community langchain-postgres langchain-text-splitters
pip install pgvector
pip install 'psycopg[binary]'
```

El archivo de dependencias puede generarse con:

``` bash
pip freeze > requirements.txt
```

------------------------------------------------------------------------

# 6. FastAPI

FastAPI es el framework utilizado para construir nuestra API HTTP.

Actualmente exponemos:

``` text
GET  /health
POST /chat
```

La aplicación comienza en:

``` text
app/main.py
```

Ejemplo conceptual:

``` python
from fastapi import FastAPI

app = FastAPI()
```

FastAPI cumple un rol similar al de Express/NestJS en Node.js.

------------------------------------------------------------------------

# 7. Uvicorn

Uvicorn es el servidor ASGI que ejecuta nuestra aplicación FastAPI.

Para desarrollo:

``` bash
uvicorn app.main:app --reload
```

La expresión:

``` text
app.main:app
```

significa:

``` text
app.main
   ↓
app/main.py

:
   ↓

app
   ↓
instancia FastAPI
```

`--reload` permite reiniciar automáticamente el servidor cuando detecta
cambios.

------------------------------------------------------------------------

# 8. Health Check

Tenemos:

``` http
GET /health
```

Respuesta:

``` json
{
  "status": "ok"
}
```

Es útil para comprobar que el servicio está funcionando y posteriormente
puede ser utilizado por infraestructura, Docker, Kubernetes o sistemas
de monitoreo.

------------------------------------------------------------------------

# 9. Pydantic y Request Body

Pydantic permite definir y validar estructuras de datos.

Nuestro request de chat actualmente contempla:

``` python
class ChatRequest(BaseModel):
    message: str | None = None
    thread_id: str = "default"
    resume: bool = False
```

Ejemplo:

``` json
{
  "message": "Quiero sacar un turno para Firu",
  "thread_id": "booking-1",
  "resume": false
}
```

Conceptualmente es similar a un DTO de NestJS.

------------------------------------------------------------------------

# 10. Endpoint `/chat`

El endpoint principal es:

``` http
POST /chat
```

Además de recibir el mensaje, recibe el JWT mediante:

``` http
Authorization: Bearer <token>
```

El flujo es:

``` text
HTTP POST /chat
       ↓
FastAPI
       ↓
ChatRequest
       ↓
LangGraph
       ↓
LLM / Tools / RAG
       ↓
respuesta JSON
```

El servicio exige el header `Authorization` porque las herramientas que
consultan VetCare necesitan ejecutar operaciones en nombre del usuario
autenticado.

------------------------------------------------------------------------

# 11. Variables de entorno

Utilizamos `.env` para configuración.

Actualmente:

``` env
LLM_MODEL=qwen3:8b
VETCARE_API_URL=http://localhost:3000
```

El `.env` no debe subirse al repositorio.

`.gitignore`:

``` gitignore
.venv/
__pycache__/
*.pyc
.env
.env.*
!.env.example
```

------------------------------------------------------------------------

# 12. Pydantic Settings

La configuración se carga mediante `pydantic-settings`.

``` python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    llm_model: str
    vetcare_api_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
    )

settings = Settings()
```

Permite obtener:

``` python
settings.llm_model
settings.vetcare_api_url
```

El flujo es:

``` text
.env
 ↓
Pydantic Settings
 ↓
Settings
 ↓
configuración de la aplicación
```

------------------------------------------------------------------------

# 13. LLM

LLM significa:

**Large Language Model**

Es un modelo capaz de procesar lenguaje natural y generar respuestas.

Conceptualmente:

``` text
input
  ↓
LLM
  ↓
output
```

Un punto fundamental de arquitectura:

> El LLM no tiene automáticamente acceso a los datos reales de VetCare.

Para acceder a información externa utilizamos **Tools** y **RAG**.

------------------------------------------------------------------------

# 14. Ollama

Ollama permite ejecutar modelos de lenguaje localmente.

En nuestro proyecto:

``` text
Aplicación
    ↓
Ollama
    ↓
modelo local
```

Iniciamos el servidor con:

``` bash
ollama serve
```

Normalmente escucha en:

``` text
127.0.0.1:11434
```

------------------------------------------------------------------------

# 15. Qwen3 8B

El modelo utilizado actualmente es:

``` text
qwen3:8b
```

El `8B` representa aproximadamente 8 mil millones de parámetros.

La elección de un modelo local permite desarrollar y aprender sin
depender de una API comercial para cada prueba.

------------------------------------------------------------------------

# 16. LangChain

LangChain es un framework/ecosistema para construir aplicaciones
alrededor de LLMs.

No es el modelo.

``` text
Qwen3
   ↓
modelo

LangChain
   ↓
framework/ecosistema
```

LangChain proporciona abstracciones para:

-   modelos;
-   prompts;
-   chains;
-   structured output;
-   tools;
-   tool calling;
-   retrievers;
-   agentes;
-   RAG.

------------------------------------------------------------------------

# 17. ChatOllama

La integración con Ollama se realiza mediante:

``` python
from langchain_ollama import ChatOllama
```

Ejemplo:

``` python
llm = ChatOllama(
    model="qwen3:8b",
    temperature=0,
)
```

La arquitectura:

``` text
LangChain
    ↓
langchain-ollama
    ↓
Ollama
    ↓
Qwen3
```

------------------------------------------------------------------------

# 18. Prompt

Un prompt es la instrucción que enviamos al modelo.

Ejemplo:

``` text
Sos el asistente virtual de VetCare.

Respondé de manera clara y profesional.

Pregunta del usuario:
¿Qué mascotas tengo?
```

El prompt puede contener:

-   instrucciones;
-   contexto;
-   datos;
-   variables;
-   reglas.

------------------------------------------------------------------------

# 19. ChatPromptTemplate

LangChain permite construir prompts estructurados.

Ejemplo:

``` python
from langchain_core.prompts import ChatPromptTemplate

chat_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Sos el asistente virtual de VetCare.",
        ),
        (
            "human",
            "{question}",
        ),
    ]
)
```

Tenemos:

``` text
SYSTEM
  ↓
comportamiento del asistente

HUMAN
  ↓
pregunta del usuario
```

------------------------------------------------------------------------

# 20. LCEL

LCEL significa:

**LangChain Expression Language**

Permite componer componentes:

``` python
chain = chat_prompt | llm
```

Conceptualmente:

``` text
Input
  ↓
Prompt
  ↓
LLM
  ↓
Output
```

El operador `|` representa el paso de salida de un componente hacia el
siguiente.

------------------------------------------------------------------------

# 21. Structured Output

Para clasificación de intención utilizamos salida estructurada.

Modelo:

``` python
class ChatIntent(BaseModel):
    intent: Literal[
        "GENERAL_CHAT",
        "BOOK_APPOINTMENT",
        "CANCEL_APPOINTMENT",
        "GET_APPOINTMENTS",
        "GET_PETS",
        "MEDICAL_QUERY",
    ]
    pet_name: str | None = None
    date: str | None = None
```

El LLM no devuelve simplemente texto libre.

Devuelve una estructura que Pydantic puede validar:

``` json
{
  "intent": "BOOK_APPOINTMENT",
  "pet_name": "Firu",
  "date": null
}
```

Esto es mucho más seguro para lógica de negocio que intentar interpretar
texto libre.

------------------------------------------------------------------------

# 22. Intent Classification

Actualmente el primer paso del grafo, para una conversación nueva, es
clasificar la intención.

Ejemplo:

``` text
Usuario:
"Quiero sacar un turno para Firu"

        ↓

LLM

        ↓

BOOK_APPOINTMENT
```

Otro ejemplo:

``` text
Usuario:
"¿Cada cuánto tengo que vacunar a mi perro?"

        ↓

LLM

        ↓

MEDICAL_QUERY
```

Las intenciones definidas actualmente son:

``` text
GENERAL_CHAT
BOOK_APPOINTMENT
CANCEL_APPOINTMENT
GET_APPOINTMENTS
GET_PETS
MEDICAL_QUERY
```

El flujo de booking y la consulta médica/RAG son los flujos funcionales
principales implementados actualmente.

------------------------------------------------------------------------

# 23. Tools

Una Tool es una capacidad que el agente puede ejecutar.

Conceptualmente:

``` text
LLM
 ↓
decide utilizar una herramienta
 ↓
Tool
 ↓
resultado
 ↓
LLM
```

En VetCare tenemos tools para:

``` text
get_my_pets
get_my_appointments
get_available_appointments
create_appointment
cancel_appointment
search_veterinary_knowledge
```

Las tools de negocio consultan la API real de VetCare.

------------------------------------------------------------------------

# 24. Tool Calling

Tool calling permite que el modelo solicite la ejecución de una
herramienta.

Por ejemplo:

``` text
Usuario:
"¿Qué turnos tengo?"

        ↓

LLM

        ↓

get_my_appointments()

        ↓

VetCare API

        ↓

resultado

        ↓

LLM

        ↓

respuesta
```

El LLM no inventa el resultado.

La aplicación ejecuta la tool y devuelve el resultado real al modelo.

------------------------------------------------------------------------

# 25. VetCareApiService

Las herramientas de negocio utilizan un servicio HTTP:

``` text
app/services/vetcare_api.py
```

Este servicio utiliza `httpx`.

Conceptualmente:

``` text
Tool
 ↓
VetCareApiService
 ↓
HTTP
 ↓
VetCare API
 ↓
PostgreSQL
```

Ejemplos de endpoints reales utilizados:

``` http
GET  /pets
GET  /appointments
GET  /appointments/availability?date=YYYY-MM-DD
POST /appointments
PATCH /appointments/:id/cancel
```

------------------------------------------------------------------------

# 26. JWT y autenticación

El usuario se autentica contra VetCare.

El frontend envía el JWT a `vetcare-ai`:

``` http
Authorization: Bearer <JWT>
```

VetCare AI propaga ese token cuando necesita llamar a VetCare API:

``` text
Browser
   │
   │ Bearer JWT
   ▼
VetCare AI
   │
   │ Bearer JWT
   ▼
VetCare API
```

Esto permite que VetCare API continúe aplicando las reglas de
autorización existentes.

La IA no debe saltarse la seguridad del backend.

------------------------------------------------------------------------

# 27. LangGraph

LangGraph se utiliza para modelar workflows con estado.

La diferencia conceptual es importante:

``` text
Chain
 ↓
flujo relativamente lineal

LangGraph
 ↓
estado
 ↓
nodos
 ↓
decisiones
 ↓
ramificaciones
 ↓
loops
 ↓
interrupciones
 ↓
persistencia
```

Nuestro agente de VetCare necesita estas capacidades porque reservar un
turno no es una única llamada al LLM.

------------------------------------------------------------------------

# 28. State

Nuestro estado principal se encuentra en:

``` text
app/graph/state.py
```

Actualmente contempla información como:

``` text
messages
user_id
intent

pet_id
pet_name

date

available_slots

slot_id
slot_time

reason

appointment_id

response

approval_status
booking_stage
```

El estado permite que el grafo recuerde en qué punto se encuentra una
conversación.

------------------------------------------------------------------------

# 29. `add_messages`

El estado de mensajes utiliza:

``` python
Annotated[
    list[BaseMessage],
    add_messages,
]
```

Esto es importante para los agentes con tool calling.

Permite que LangGraph acumule correctamente:

``` text
HumanMessage
    ↓
AIMessage
    ↓
ToolMessage
    ↓
AIMessage
```

Sin esta acumulación, el modelo puede no recibir correctamente el
resultado de una tool en el siguiente paso.

------------------------------------------------------------------------

# 30. Nodes

Cada node representa una unidad de trabajo dentro del grafo.

Actualmente tenemos nodos relacionados con:

``` text
classify_intent
start_booking
process_date
availability
show_availability
select_slot
process_reason
confirm
create

knowledge_agent
knowledge_tools
```

Conceptualmente:

``` text
START
  ↓
node
  ↓
node
  ↓
node
  ↓
END
```

------------------------------------------------------------------------

# 31. Conditional Edges

Los conditional edges permiten tomar decisiones.

Ejemplo conceptual:

``` text
START
  ↓
classify_intent
  │
  ├── BOOK_APPOINTMENT → booking
  │
  └── MEDICAL_QUERY   → knowledge_agent
```

En el flujo de booking también se decide según:

``` text
booking_stage
```

Por ejemplo:

``` text
select_date
    ↓
process_date

load_availability
    ↓
availability

select_slot
    ↓
select_slot

select_reason
    ↓
process_reason

confirm
    ↓
confirm
```

------------------------------------------------------------------------

# 32. Memoria y `thread_id`

Cada conversación utiliza:

``` text
thread_id
```

Por ejemplo:

``` text
booking-123
```

El `thread_id` permite que LangGraph identifique el estado de una
conversación.

Actualmente utilizamos:

``` python
InMemorySaver()
```

Esto sirve para aprendizaje y desarrollo.

En producción debería reemplazarse por un mecanismo de persistencia
adecuado.

------------------------------------------------------------------------

# 33. Flujo completo de reserva

El workflow implementado es:

``` text
Usuario
  │
  ▼
"Quiero sacar un turno para Firu"
  │
  ▼
Intent Classification
  │
  ▼
BOOK_APPOINTMENT
  │
  ▼
Buscar mascota real
  │
  ▼
Firu → pet_id real
  │
  ▼
¿Tenemos fecha?
  │
  └── NO → preguntar fecha
  │
  ▼
"mañana"
  │
  ▼
procesar fecha
  │
  ▼
GET /appointments/availability
  │
  ▼
mostrar horarios reales
  │
  ▼
usuario elige "09:00"
  │
  ▼
buscar ese horario entre los slots reales
  │
  ▼
obtener slot_id real
  │
  ▼
pedir motivo
  │
  ▼
"Control anual"
  │
  ▼
Human-in-the-loop
  │
  ▼
"¿Querés confirmar este turno?"
  │
  ▼
resume=true
  │
  ▼
POST /appointments
  │
  ▼
Turno confirmado
```

------------------------------------------------------------------------

# 34. Selección de horarios

La API devuelve datos similares a:

``` json
{
  "date": "2026-09-09",
  "slots": [
    {
      "id": 73,
      "startTime": "2026-09-09T12:00:00.000Z",
      "time": "09:00",
      "available": true
    }
  ]
}
```

La IA no debe inventar el `slot_id`.

La regla implementada es:

``` text
hora elegida por usuario
        ↓
buscar en available_slots
        ↓
verificar available == true
        ↓
obtener id real
        ↓
usar ese id en POST /appointments
```

Esto es un principio importante:

> El LLM puede interpretar la intención del usuario, pero los
> identificadores de negocio deben provenir de los sistemas reales.

------------------------------------------------------------------------

# 35. Human-in-the-loop

Antes de crear un turno se utiliza una interrupción para pedir
confirmación.

El backend responde:

``` json
{
  "response": "¿Querés confirmar este turno?",
  "thread_id": "test-booking-1",
  "status": "waiting_approval",
  "approval": {
    "type": "booking_confirmation",
    "message": "¿Querés confirmar este turno?",
    "appointment": {
      "pet_name": "firu",
      "date": "2026-09-10",
      "time": "09:00",
      "reason": "Control anual"
    }
  }
}
```

El frontend puede mostrar una tarjeta de confirmación.

Para continuar actualmente:

``` json
{
  "thread_id": "test-booking-1",
  "resume": true
}
```

El backend utiliza:

``` python
Command(resume=True)
```

y el grafo continúa hasta:

``` text
create_booking
```

Este mecanismo es un ejemplo de **Human-in-the-loop (HITL)**.

> Actualmente `resume=true` representa aprobación. Una mejora futura
> será interpretar explícitamente respuestas como "sí" y "no".

------------------------------------------------------------------------

# 36. RAG

RAG significa:

**Retrieval-Augmented Generation**

Permite que el modelo responda utilizando información recuperada desde
una fuente externa.

Sin RAG:

``` text
Pregunta
   ↓
LLM
   ↓
respuesta
```

Con RAG:

``` text
Pregunta
   ↓
Retriever
   ↓
documentos relevantes
   ↓
Contexto
   ↓
LLM
   ↓
respuesta
```

En VetCare utilizamos RAG para información veterinaria general.

------------------------------------------------------------------------

# 37. Base de conocimiento

Actualmente tenemos:

``` text
documents/
└── general/
    ├── vacunacion.md
    ├── turnos.md
    └── alimentacion.md
```

Ejemplos de información:

-   vacunación;
-   turnos veterinarios;
-   alimentación de mascotas.

La base es deliberadamente pequeña porque el objetivo actual es aprender
la arquitectura.

------------------------------------------------------------------------

# 38. Embeddings

Para realizar búsqueda semántica necesitamos convertir los documentos y
consultas en vectores.

Utilizamos:

``` text
nomic-embed-text
```

mediante Ollama.

Conceptualmente:

``` text
Texto
  ↓
Embedding Model
  ↓
Vector
```

Dos textos semánticamente relacionados deberían producir vectores
cercanos.

------------------------------------------------------------------------

# 39. Vector Database

Utilizamos:

``` text
PostgreSQL
+
pgvector
```

La base de datos de VetCare utiliza una imagen compatible con pgvector:

``` text
pgvector/pgvector:pg16
```

El vector store utilizado desde Python es:

``` text
PGVector
```

La arquitectura queda:

``` text
Documento
   ↓
chunk
   ↓
embedding
   ↓
pgvector
```

------------------------------------------------------------------------

# 40. Ingestión de documentos

La ingestión está implementada en:

``` text
app/rag/ingest.py
```

Ejecutamos:

``` bash
python -m app.rag.ingest
```

El proceso es:

``` text
documents/*.md
      ↓
load_documents()
      ↓
Document
      ↓
RecursiveCharacterTextSplitter
      ↓
chunks
      ↓
OllamaEmbeddings
      ↓
vectors
      ↓
PGVector
```

Utilizamos:

``` python
chunk_size=500
chunk_overlap=50
```

El objetivo del chunking es dividir documentos grandes en unidades
manejables para recuperación semántica.

------------------------------------------------------------------------

# 41. Retriever

El retriever se encuentra en:

``` text
app/rag/retriever.py
```

Utiliza:

``` python
vector_store.similarity_search(
    query,
    k=4,
)
```

Conceptualmente:

``` text
Pregunta
   ↓
Embedding
   ↓
similarity search
   ↓
top K documentos
```

Ya se verificó que una consulta relacionada con vacunación recupera
correctamente `vacunacion.md`.

------------------------------------------------------------------------

# 42. RAG como Tool

La búsqueda de conocimiento se expone al agente mediante:

``` text
search_veterinary_knowledge
```

ubicada en:

``` text
app/tools/knowledge.py
```

Esto permite:

``` text
Usuario
  ↓
LLM
  ↓
tool call
  ↓
search_veterinary_knowledge
  ↓
Retriever
  ↓
PGVector
  ↓
documentos
  ↓
ToolMessage
  ↓
LLM
  ↓
respuesta final
```

Este punto es especialmente importante porque combina:

-   Agent;
-   Tool Calling;
-   LangGraph;
-   Retriever;
-   Embeddings;
-   Vector Database;
-   RAG.

------------------------------------------------------------------------

# 43. Loop Agent → Tool → Agent

El flujo implementado para RAG es:

``` text
knowledge_agent
      │
      ▼
¿hace tool call?
      │
      ├── NO ──→ END
      │
      ▼
knowledge_tools
      │
      ▼
search_veterinary_knowledge
      │
      ▼
ToolMessage
      │
      ▼
knowledge_agent
      │
      ▼
respuesta final
```

Esto es una de las razones por las que `LangGraph` resulta útil: permite
representar explícitamente estos ciclos.

------------------------------------------------------------------------

# 44. Ejemplo real de RAG

Pregunta:

``` text
¿Qué tengo que saber sobre las vacunas de mi perro?
```

El modelo puede solicitar:

``` text
search_veterinary_knowledge(
    "vacunas de perro: tipos, horarios, importancia y efectos secundarios"
)
```

La tool consulta los documentos.

La respuesta final se genera utilizando el contenido recuperado.

Si los documentos no contienen información suficiente, el asistente debe
indicarlo y no inventar datos.

------------------------------------------------------------------------

# 45. Diferencia entre Tools y RAG

Es importante distinguir ambos conceptos.

## Tool

Una tool ejecuta una capacidad:

``` text
get_my_appointments()
create_appointment()
cancel_appointment()
```

Puede interactuar con sistemas externos.

## RAG

RAG recupera información relevante:

``` text
query
 ↓
embeddings
 ↓
vector search
 ↓
context
 ↓
LLM
```

En VetCare ambos conceptos se combinan:

``` text
LLM
 │
 ├── Tools de negocio
 │      └── VetCare API
 │
 └── Tool de conocimiento
        └── RAG / pgvector
```

------------------------------------------------------------------------

# 46. Arquitectura actual del Agent

Actualmente el flujo general es:

``` text
                       POST /chat
                            │
                            ▼
                         FastAPI
                            │
                            ▼
                       LangGraph
                            │
                            ▼
                    classify_intent
                       │       │
                       │       │
        BOOK_APPOINTMENT       MEDICAL_QUERY
                       │       │
                       ▼       ▼
                  Booking    Knowledge Agent
                       │       │
                       │       ▼
                       │    RAG Tool
                       │       │
                       │       ▼
                       │    pgvector
                       │       │
                       │       ▼
                       │    ToolMessage
                       │       │
                       │       ▼
                       │    final answer
                       │
                       ▼
               Human approval
                       │
                       ▼
                create booking
```

------------------------------------------------------------------------

# 47. Arquitectura completa del proyecto

La arquitectura conceptual actual es:

``` text
┌──────────────────────────────┐
│         VetCare Web          │
│       Next.js / React        │
│                              │
│       Chat Assistant         │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│          VetCare AI          │
│                              │
│ Python / FastAPI             │
│ LangChain                    │
│ LangGraph                    │
│ Ollama / Qwen3               │
│                              │
│ Intent Classification        │
│ Tools                        │
│ Tool Calling                 │
│ Memory                       │
│ HITL                         │
│ RAG                          │
└──────────────┬───────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌──────────────┐  ┌──────────────┐
│ VetCare API  │  │  PostgreSQL  │
│    NestJS    │  │   pgvector   │
└──────┬───────┘  └──────────────┘
       │
       ▼
┌──────────────┐
│ PostgreSQL   │
│ negocio      │
└──────────────┘
```

En la arquitectura final se incorporará MCP como capa de estandarización
de herramientas.

------------------------------------------------------------------------

# 48. MCP --- próximo paso

MCP significa:

**Model Context Protocol**

La idea es estandarizar cómo una aplicación de IA descubre y utiliza
herramientas y recursos externos.

Actualmente:

``` text
VetCare AI
   ↓
Tool
   ↓
VetCare API
```

La arquitectura futura será:

``` text
VetCare AI
   ↓
MCP Client
   ↓
MCP Server
   ↓
Tools
   ↓
VetCare API
```

El MCP Server podrá exponer capacidades como:

``` text
get_pets
get_appointments
get_availability
create_appointment
cancel_appointment
```

Esto permite separar:

``` text
AI / Agent
```

de:

``` text
capabilities / tools
```

y facilita reutilizar las mismas capacidades desde diferentes agentes o
aplicaciones compatibles con MCP.

------------------------------------------------------------------------

# 49. MCP vs Tools tradicionales

Sin MCP:

``` text
Agent
  ↓
Tool
  ↓
API
```

Con MCP:

``` text
Agent
  ↓
MCP Client
  ↓
MCP Server
  ↓
Tool
  ↓
API
```

MCP no reemplaza necesariamente a una tool.

MCP define un protocolo estandarizado para descubrir y utilizar
capacidades.

Una forma simple de pensarlo:

``` text
Tool = capacidad

MCP = protocolo para exponer/descubrir/utilizar capacidades
```

------------------------------------------------------------------------

# 50. LangSmith --- próximo paso

LangSmith será utilizado para observabilidad y evaluación.

Conceptualmente:

``` text
User
 ↓
Agent
 ↓
Tool
 ↓
LLM
 ↓
Response
```

LangSmith permitirá observar:

-   prompts;
-   llamadas al LLM;
-   tool calls;
-   tiempos;
-   errores;
-   trazas;
-   ejecuciones del grafo;
-   evaluaciones.

La idea será poder responder preguntas como:

``` text
¿Por qué el agente eligió esta tool?

¿Qué prompt recibió?

¿Cuánto tardó?

¿Qué documentos recuperó?

¿Dónde falló el workflow?
```

------------------------------------------------------------------------

# 51. Seguridad

Principios importantes del proyecto:

### No confiar en el LLM para identificadores

Nunca debería inventar:

``` text
pet_id
slot_id
appointment_id
```

Los IDs deben provenir de los sistemas reales.

### Mantener autorización en VetCare API

La IA no debería reemplazar los Guards del backend.

``` text
VetCare AI
    ↓
Authorization: Bearer JWT
    ↓
VetCare API
    ↓
JwtAuthGuard / autorización
```

### Human approval para acciones sensibles

Acciones como crear o cancelar turnos deberían requerir controles
apropiados.

### No subir secretos

Nunca subir:

``` text
.env
tokens
API keys
passwords
```

------------------------------------------------------------------------

# 52. Flujo completo de una conversación

Ejemplo:

``` text
Usuario
"Quiero sacar un turno para Firu"

        ↓

FastAPI

        ↓

LangGraph

        ↓

Intent Classification

        ↓

BOOK_APPOINTMENT

        ↓

buscar mascotas

        ↓

Firu → pet_id real

        ↓

preguntar fecha

        ↓

"mañana"

        ↓

consultar disponibilidad real

        ↓

mostrar horarios

        ↓

"09:00"

        ↓

buscar slot_id real

        ↓

"Control anual"

        ↓

Human approval

        ↓

"¿Querés confirmar?"

        ↓

resume=true

        ↓

POST /appointments

        ↓

"Turno confirmado"
```

------------------------------------------------------------------------

# 53. Flujo de una consulta médica con RAG

Ejemplo:

``` text
Usuario
"¿Qué tengo que saber sobre las vacunas?"

        ↓

FastAPI

        ↓

LangGraph

        ↓

Intent Classification

        ↓

MEDICAL_QUERY

        ↓

knowledge_agent

        ↓

search_veterinary_knowledge

        ↓

Retriever

        ↓

Embedding

        ↓

pgvector

        ↓

Documentos relevantes

        ↓

ToolMessage

        ↓

knowledge_agent

        ↓

respuesta basada en contexto
```

------------------------------------------------------------------------

# 54. Cómo ejecutar el proyecto

## 54.1 Activar entorno

``` bash
source .venv/bin/activate
```

## 54.2 Iniciar Ollama

En otra terminal:

``` bash
ollama serve
```

Verificar que el modelo exista:

``` bash
ollama list
```

Deberíamos tener:

``` text
qwen3:8b
nomic-embed-text
```

## 54.3 Iniciar VetCare API

La API de VetCare debe estar funcionando en:

``` text
http://localhost:3000
```

## 54.4 PostgreSQL

El proyecto utiliza PostgreSQL con pgvector.

El contenedor de VetCare utiliza:

``` text
pgvector/pgvector:pg16
```

El volumen debe conservarse.

**No utilizar `docker compose down -v` si se quiere conservar la base de
datos.**

## 54.5 Ingerir documentos RAG

``` bash
python -m app.rag.ingest
```

## 54.6 Iniciar VetCare AI

``` bash
uvicorn app.main:app --reload
```

Por defecto FastAPI estará disponible en:

``` text
http://127.0.0.1:8000
```

Swagger:

``` text
http://127.0.0.1:8000/docs
```

------------------------------------------------------------------------

# 55. Prueba básica

Health check:

``` bash
curl http://127.0.0.1:8000/health
```

Respuesta:

``` json
{
  "status": "ok"
}
```

Chat:

``` bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_JWT" \
  -d '{
    "message": "¿Qué tengo que saber sobre las vacunas de mi perro?",
    "thread_id": "rag-test-1"
  }'
```

------------------------------------------------------------------------

# 56. Estado actual del proyecto

Actualmente ya tenemos implementados y probados:

``` text
✅ Python 3.12
✅ venv
✅ FastAPI
✅ Uvicorn
✅ Pydantic
✅ Pydantic Settings
✅ Ollama
✅ Qwen3 8B
✅ LangChain
✅ ChatPromptTemplate
✅ LCEL
✅ Structured Output
✅ Intent Classification
✅ LangGraph
✅ State
✅ Nodes
✅ Conditional Routing
✅ Loops
✅ InMemorySaver
✅ thread_id
✅ Tools
✅ Tool Calling
✅ ToolNode
✅ JWT propagation
✅ VetCare API integration
✅ Appointment workflow
✅ Real pet lookup
✅ Real availability lookup
✅ Real slot selection
✅ Human-in-the-loop
✅ RAG
✅ Embeddings
✅ nomic-embed-text
✅ PostgreSQL
✅ pgvector
✅ Document ingestion
✅ Vector similarity search
✅ RAG exposed as a Tool
```

La combinación más importante implementada hasta ahora es:

``` text
LangGraph
   +
Tool Calling
   +
VetCare API
   +
RAG
   +
pgvector
   +
Human-in-the-loop
```

------------------------------------------------------------------------

# 57. Próximos pasos

El roadmap previsto es:

``` text
                    VETCARE AI
                        │
                        ▼
              ┌──────────────────┐
              │ Intent Detection │
              └────────┬─────────┘
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
        Booking Flow          RAG Agent
             │                   │
             ▼                   ▼
        VetCare API          pgvector
             │                   │
             └─────────┬─────────┘
                       │
                       ▼
                 Human Approval
                       │
                       ▼
                    MCP
                       │
                       ▼
                  LangSmith
                       │
                       ▼
              Evaluation / Tests
                       │
                       ▼
              Production / Cloud
```

Orden recomendado:

1.  **MCP Server**
2.  Integrar MCP Client en `vetcare-ai`.
3.  Migrar las tools de negocio detrás de MCP.
4.  Mejorar el manejo explícito de aprobación `sí/no`.
5.  Incorporar LangSmith tracing.
6.  Agregar tests de workflows.
7.  Mejorar RAG: metadata, filtros, fuentes y evaluación.
8.  Agregar streaming.
9.  Integrar el chat en `vetcare-web`.
10. Dockerizar `vetcare-ai`.
11. Preparar despliegue.

------------------------------------------------------------------------

# 58. Conceptos importantes para entrevistas

Este proyecto permite explicar en una entrevista:

### LLM

> Modelo de lenguaje utilizado para interpretar lenguaje natural y
> generar respuestas.

### Prompt

> Instrucciones y contexto enviados al modelo.

### Structured Output

> Técnica para obtener una respuesta con una estructura definida y
> validable.

### Tool

> Función que permite al agente ejecutar una capacidad externa.

### Tool Calling

> Mecanismo mediante el cual el modelo decide solicitar la ejecución de
> una tool.

### Agent

> Sistema que combina un modelo con herramientas y lógica para decidir
> qué acciones realizar.

### LangGraph

> Framework para construir workflows de agentes con estado, nodos,
> decisiones, ciclos e interrupciones.

### Memory

> Persistencia del estado/conversación para continuar workflows entre
> mensajes.

### RAG

> Arquitectura que recupera información relevante desde una fuente
> externa y la incorpora al contexto del LLM.

### Embedding

> Representación vectorial de texto utilizada para comparar similitud
> semántica.

### Vector Database

> Base de datos optimizada para almacenar y buscar vectores.

### pgvector

> Extensión de PostgreSQL para almacenar y consultar embeddings.

### Human-in-the-loop

> Incorporación de una aprobación humana antes de continuar con una
> acción.

### MCP

> Protocolo estandarizado para conectar aplicaciones de IA con
> herramientas y recursos externos.

### LangSmith

> Plataforma para tracing, debugging y evaluación de aplicaciones
> basadas en LLMs.

------------------------------------------------------------------------

# 59. Objetivo final

El objetivo del proyecto es evolucionar desde:

``` text
POST /chat
    ↓
Prompt
    ↓
LLM
    ↓
respuesta
```

hasta:

``` text
                         Usuario
                            │
                            ▼
                      VetCare Web
                            │
                            ▼
                       VetCare AI
                            │
                            ▼
                        LangGraph
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
          Intent / Agent              RAG
                │                       │
                ▼                       ▼
              MCP                    pgvector
                │
                ▼
             Tools
                │
                ▼
          VetCare API
                │
                ▼
           PostgreSQL
                │
                ▼
        Human Approval
                │
                ▼
          acción final
```

El principio fundamental es:

> **El LLM interpreta y decide, pero las fuentes reales y las reglas de
> negocio deben permanecer bajo control de los sistemas de la
> aplicación.**

Esto permite construir un asistente de IA más confiable, trazable y
preparado para evolucionar hacia una arquitectura de producción.
