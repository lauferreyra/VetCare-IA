# VetCare AI

Servicio de inteligencia artificial para VetCare, desarrollado con **Python, FastAPI, LangChain, LangGraph y Ollama/Qwen**, integrado con la API real de VetCare.

El proyecto tiene dos objetivos:

1. Construir un asistente de IA funcional para la plataforma VetCare.
2. Utilizar el proyecto como laboratorio práctico para estudiar conceptos de **LLMs, prompting, structured output, tool calling, agents, LangGraph, memory, persistence, human-in-the-loop, RAG y observabilidad**.

> **Estado actual:** el agente ya puede ejecutarse localmente con Qwen3 8B, utilizar herramientas, mantener conversaciones mediante `thread_id`, ejecutar workflows con LangGraph, pausar mediante `interrupt` y comunicarse con `vetcare-api` utilizando el JWT del usuario.

---

# 1. Arquitectura general

VetCare está dividido en servicios con responsabilidades diferentes:

```text
                         ┌──────────────────────┐
                         │     VetCare Web      │
                         │   Next.js / React    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     VetCare API      │
                         │       NestJS         │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     PostgreSQL       │
                         │       Docker         │
                         └──────────────────────┘


                         ┌──────────────────────┐
                         │      VetCare AI      │
                         │   Python / FastAPI   │
                         └──────────┬───────────┘
                                    │
                                    │ HTTP + JWT
                                    ▼
                         ┌──────────────────────┐
                         │     VetCare API      │
                         │       NestJS         │
                         └──────────┬───────────┘
                                    │
                                    ▼
                              PostgreSQL
```

## Responsabilidades

### VetCare Web

Frontend de la aplicación.

Tecnologías principales:

- Next.js
- React
- TypeScript
- Tailwind

Responsabilidad:

- interfaz
- autenticación desde el frontend
- interacción con el usuario
- visualización de mascotas y turnos

### VetCare API

Backend principal de VetCare.

Tecnologías:

- NestJS
- Prisma
- PostgreSQL
- JWT

Responsabilidad:

- lógica de negocio
- autenticación
- autorización
- acceso a base de datos
- CRUD de mascotas
- CRUD de turnos

### VetCare AI

Microservicio independiente de inteligencia artificial.

Tecnologías:

- Python
- FastAPI
- LangChain
- LangGraph
- Ollama
- Qwen3 8B

Responsabilidad:

- interpretar lenguaje natural
- decidir qué herramienta utilizar
- consultar información mediante `vetcare-api`
- ejecutar workflows
- mantener contexto conversacional
- solicitar confirmación humana cuando corresponda

---

# 2. Arquitectura de seguridad

Una decisión importante del diseño es que **VetCare AI no accede directamente a PostgreSQL**.

El flujo es:

```text
Usuario
   │
   │ JWT
   ▼
VetCare AI
   │
   │ Authorization: Bearer JWT
   ▼
VetCare API
   │
   │ Prisma
   ▼
PostgreSQL
```

Esto mantiene a `vetcare-api` como dueño de la lógica de negocio y de los datos.

El AI service funciona como un consumidor de la API.

## ¿Por qué no acceder directamente a PostgreSQL?

Porque permitiría que el servicio de IA:

- conozca detalles internos de la base
- saltee reglas de negocio
- tenga permisos excesivos
- duplique lógica existente
- dificulte controlar autorización

La IA debe pedir:

```text
GET /pets
```

en lugar de hacer:

```sql
SELECT * FROM pets;
```

---

# 3. Python

Python es el lenguaje utilizado para `vetcare-ai`.

La versión utilizada actualmente es:

```text
Python 3.12.14
```

Python tiene un ecosistema muy amplio para:

- Inteligencia Artificial
- Machine Learning
- LLMs
- procesamiento de datos
- APIs
- automatización

Para este proyecto Python resulta especialmente conveniente por el ecosistema alrededor de LangChain, LangGraph y herramientas de IA.

---

# 4. Entorno virtual: `.venv`

El proyecto utiliza:

```text
.venv/
```

Un entorno virtual permite aislar las dependencias de Python de otros proyectos.

Conceptualmente:

```text
Proyecto A
└── .venv/

Proyecto B
└── .venv/

VetCare AI
└── .venv/
```

Esto evita depender de una instalación global de paquetes.

## Crear

```bash
python3.12 -m venv .venv
```

## Activar

```bash
source .venv/bin/activate
```

## Verificar

```bash
python --version
which python
```

---

# 5. pip

`pip` es el gestor de paquetes de Python.

Ejemplo:

```bash
pip install fastapi
```

Conceptualmente:

```text
Node.js
   ↓
npm
   ↓
package.json
   ↓
node_modules
```

En Python:

```text
Python
   ↓
pip
   ↓
dependencias
   ↓
.venv/
```

---

# 6. Dependencias principales

El proyecto utiliza, entre otras, las siguientes:

```text
fastapi
uvicorn
langchain
langchain-ollama
langgraph
pydantic
pydantic-settings
httpx
```

Cada dependencia tiene una responsabilidad concreta:

| Dependencia | Responsabilidad |
|---|---|
| FastAPI | API HTTP |
| Uvicorn | servidor ASGI |
| Pydantic | validación y schemas |
| pydantic-settings | configuración desde `.env` |
| LangChain | abstracciones para LLMs |
| langchain-ollama | integración LangChain ↔ Ollama |
| LangGraph | workflows y agentes con estado |
| httpx | comunicación HTTP con VetCare API |

---

# 7. FastAPI

FastAPI es el framework utilizado para construir la API HTTP de `vetcare-ai`.

Actualmente tenemos:

```text
GET  /health
POST /chat
```

La estructura básica es:

```python
from fastapi import FastAPI

app = FastAPI()
```

Conceptualmente:

```text
HTTP Request
     ↓
FastAPI
     ↓
Path Operation
     ↓
Python function
     ↓
JSON Response
```

---

# 8. Uvicorn

Uvicorn es el servidor ASGI utilizado para ejecutar FastAPI.

Desarrollo:

```bash
uvicorn app.main:app --reload
```

La expresión:

```text
app.main:app
```

significa:

```text
app.main
   ↓
app/main.py

:
   ↓

app
   ↓
instancia FastAPI
```

`--reload` reinicia automáticamente el servidor cuando detecta cambios en el código.

---

# 9. Health Check

Tenemos:

```http
GET /health
```

que devuelve:

```json
{
  "status": "ok"
}
```

Un health check permite comprobar rápidamente si el servicio está vivo.

Es habitual utilizarlo junto con:

- Docker
- Kubernetes
- load balancers
- cloud platforms
- sistemas de monitoreo

---

# 10. Pydantic y Schemas

Pydantic permite definir y validar estructuras de datos.

Nuestro request:

```python
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default"
```

Esto indica:

```text
message → obligatorio → string

thread_id → opcional → string
            default = "default"
```

Conceptualmente es similar a un DTO de NestJS.

### NestJS

```typescript
export class ChatRequestDto {
  message: string;
}
```

### FastAPI

```python
class ChatRequest(BaseModel):
    message: str
```

---

# 11. Endpoint `/chat`

El endpoint principal es:

```http
POST /chat
```

Ejemplo:

```json
{
  "message": "¿Qué mascotas tengo?",
  "thread_id": "conversation-1"
}
```

La respuesta:

```json
{
  "response": "...",
  "thread_id": "conversation-1"
}
```

El endpoint también recibe:

```http
Authorization: Bearer <JWT>
```

El JWT es importante porque las herramientas necesitan realizar peticiones autenticadas a `vetcare-api`.

---

# 12. Variables de entorno

Las configuraciones que cambian entre ambientes no deberían estar hardcodeadas.

Utilizamos:

```text
.env
```

Actualmente:

```env
LLM_MODEL=qwen3:8b
VETCARE_API_URL=http://localhost:3000
```

El `.env` debe estar en `.gitignore`.

Ejemplo:

```gitignore
.venv/
__pycache__/
*.pyc
.env
.env.*
!.env.example
```

---

# 13. Pydantic Settings

Utilizamos `pydantic-settings` para cargar configuración.

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_model: str
    vetcare_api_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
    )


settings = Settings()
```

Entonces:

```python
settings.llm_model
```

obtiene:

```text
qwen3:8b
```

y:

```python
settings.vetcare_api_url
```

obtiene:

```text
http://localhost:3000
```

Ventaja:

```text
Código
  ↓
Settings
  ↓
.env
```

Podemos cambiar configuración sin modificar código.

---

# 14. LLM

LLM significa:

**Large Language Model**

Un LLM es un modelo entrenado para trabajar con lenguaje.

Conceptualmente:

```text
Input
  ↓
LLM
  ↓
Output
```

Ejemplo:

```text
Usuario:
"¿Qué mascotas tengo?"

        ↓

       LLM

        ↓

"Podés consultar tus mascotas..."
```

Pero existe una limitación fundamental:

> El LLM no conoce automáticamente los datos actuales de nuestra aplicación.

Por eso necesitamos **Tools**.

---

# 15. Ollama

Ollama permite ejecutar modelos de lenguaje localmente.

En nuestro proyecto:

```text
VetCare AI
    ↓
Ollama
    ↓
Qwen3 8B
```

Iniciamos Ollama con:

```bash
ollama serve
```

Normalmente utiliza:

```text
127.0.0.1:11434
```

La ventaja principal para este proyecto es poder desarrollar sin depender de una API comercial de LLM.

---

# 16. Qwen3 8B

El modelo utilizado actualmente es:

```text
qwen3:8b
```

`8B` hace referencia aproximadamente a 8 mil millones de parámetros.

Importante para una entrevista:

> Ollama no es el modelo.

La diferencia es:

```text
Ollama
   ↓
runtime / servidor local

Qwen3
   ↓
modelo de lenguaje
```

Ollama ejecuta y sirve el modelo.

---

# 17. LangChain

LangChain es un framework/ecosistema para construir aplicaciones alrededor de modelos de lenguaje.

No es un LLM.

La separación es:

```text
Qwen3
   ↓
modelo

LangChain
   ↓
framework para construir la aplicación
```

LangChain proporciona abstracciones para:

- Chat Models
- prompts
- structured output
- tools
- tool calling
- agents
- retrievers
- chains

---

# 18. `ChatOllama`

Utilizamos:

```python
from langchain_ollama import ChatOllama
```

Creamos:

```python
llm = ChatOllama(
    model=settings.llm_model,
)
```

El recorrido es:

```text
.env
 ↓
settings.llm_model
 ↓
ChatOllama
 ↓
Ollama
 ↓
Qwen3
```

---

# 19. `invoke()`

`invoke()` ejecuta un componente de LangChain.

Ejemplo:

```python
response = llm.invoke("Hola")
```

Conceptualmente:

```text
Input
  ↓
invoke()
  ↓
ChatOllama
  ↓
Qwen3
  ↓
AIMessage
```

El texto generado normalmente está disponible en:

```python
response.content
```

---

# 20. Prompts

Un prompt es la instrucción que enviamos al modelo.

Puede contener:

- instrucciones
- contexto
- información del usuario
- restricciones
- ejemplos
- variables dinámicas

Ejemplo:

```text
Sos el asistente virtual de VetCare.

No inventes información.

Utilizá las herramientas disponibles cuando
necesites consultar información real.
```

---

# 21. System Message

El mensaje `system` define el comportamiento general del asistente.

Ejemplo:

```text
Sos el asistente virtual de VetCare.

No inventes información.

Ayudá al usuario utilizando las herramientas disponibles.
```

Es una instrucción para orientar al modelo.

---

# 22. Human Message

El mensaje `human` representa el mensaje del usuario.

Ejemplo:

```text
¿Qué mascotas tengo?
```

Podemos tener:

```text
SYSTEM
  ↓
reglas y comportamiento

HUMAN
  ↓
pregunta del usuario
```

---

# 23. ChatPromptTemplate

LangChain permite construir prompts estructurados:

```python
from langchain_core.prompts import ChatPromptTemplate


prompt = ChatPromptTemplate.from_messages(
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

La variable:

```text
{question}
```

se reemplaza al ejecutar el prompt.

---

# 24. LCEL

LCEL significa:

**LangChain Expression Language**

Permite componer componentes.

Ejemplo:

```python
chain = prompt | llm
```

El operador:

```text
|
```

representa el paso de la salida de un componente al siguiente.

```text
Input
  ↓
Prompt
  ↓
LLM
  ↓
Output
```

Una distinción importante:

```python
chain = prompt | llm
```

construye la chain.

Mientras que:

```python
chain.invoke(...)
```

la ejecuta.

---

# 25. Structured Output

Uno de los primeros pasos importantes fue dejar de depender únicamente de texto libre.

En lugar de pedir:

```text
Decime qué intención tiene el usuario.
```

y recibir:

```text
Creo que el usuario quiere reservar un turno...
```

podemos definir una estructura.

Creamos:

```python
from typing import Literal
from pydantic import BaseModel


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

El modelo debe producir una estructura compatible con ese schema.

Conceptualmente:

```text
Usuario
  ↓
LLM
  ↓
Structured Output
  ↓
ChatIntent
```

Esto es mucho más útil para código que interpretar texto libre.

---

# 26. `with_structured_output()`

LangChain permite:

```python
structured_llm = llm.with_structured_output(ChatIntent)
```

Luego:

```python
result = structured_llm.invoke(...)
```

La salida se transforma en una estructura validada por Pydantic.

Ejemplo conceptual:

```json
{
  "intent": "BOOK_APPOINTMENT",
  "pet_name": "Firulais",
  "date": "2026-09-08"
}
```

Esto permite que nuestro código trabaje con datos estructurados.

---

# 27. Tools

Una Tool es una función que el LLM puede solicitar ejecutar.

Ejemplo:

```python
from langchain_core.tools import tool


@tool
def get_my_pets():
    """Obtiene las mascotas del usuario autenticado."""
    ...
```

La idea fundamental es:

> El LLM decide cuándo necesita una herramienta, pero la ejecución real de la función la realiza nuestra aplicación.

Flujo:

```text
Usuario
   ↓
LLM
   ↓
"Necesito consultar mascotas"
   ↓
Tool Call
   ↓
Python ejecuta la Tool
   ↓
resultado
   ↓
LLM
```

---

# 28. Tool Calling

Para permitir que el modelo conozca las herramientas:

```python
llm_with_tools = llm.bind_tools(all_tools)
```

Ahora el modelo puede generar una solicitud de herramienta.

Ejemplo conceptual:

```json
{
  "name": "get_my_pets",
  "arguments": {}
}
```

El modelo no ejecuta directamente Python.

Genera una intención estructurada de ejecutar una herramienta.

---

# 29. ToolNode

LangGraph proporciona:

```python
ToolNode
```

para ejecutar Tools.

Ejemplo:

```python
builder.add_node(
    "tools",
    ToolNode(all_tools),
)
```

El flujo:

```text
LLM
 ↓
tool_call
 ↓
ToolNode
 ↓
Tool
 ↓
ToolMessage
 ↓
LLM
```

Esto es fundamental para entender Agents.

---

# 30. Tools reales de VetCare

Creamos Tools para consultar información real.

Actualmente:

```text
app/tools/
├── __init__.py
├── appointments.py
├── pets.py
└── users.py
```

Las herramientas de usuario disponibles incluyen:

```text
get_my_pets
get_my_appointments
get_available_appointments
```

Las rutas administrativas no deben ser utilizadas por el agente normal.

---

# 31. API real de VetCare

El backend NestJS expone actualmente:

## Pets

```http
GET    /pets
GET    /pets/:id
POST   /pets
PATCH  /pets/:id
DELETE /pets/:id
```

## Appointments

```http
GET    /appointments
GET    /appointments/:id
GET    /appointments/availability?date=YYYY-MM-DD
POST   /appointments
PATCH  /appointments/:id
PATCH  /appointments/:id/cancel
DELETE /appointments/:id
```

El AI service utiliza estas rutas a través de HTTP.

---

# 32. `httpx`

Utilizamos `httpx` para que Python pueda comunicarse con `vetcare-api`.

Ejemplo:

```python
response = client.get(
    f"{self.base_url}/pets",
    headers=self._headers(),
)
```

Conceptualmente:

```text
Python
  ↓
HTTP request
  ↓
NestJS
  ↓
Prisma
  ↓
PostgreSQL
```

---

# 33. `VetCareApiService`

Centralizamos la comunicación HTTP en:

```text
app/services/vetcare_api.py
```

La clase recibe el JWT:

```python
class VetCareApiService:

    def __init__(self, access_token: str):
        self.base_url = settings.vetcare_api_url
        self.access_token = access_token
```

Y construye:

```python
def _headers(self):
    return {
        "Authorization": f"Bearer {self.access_token}",
    }
```

Así todas las peticiones utilizan el JWT del usuario.

---

# 34. JWT Propagation

Este es uno de los conceptos más importantes de la arquitectura actual.

El usuario inicia sesión en `vetcare-api`.

Obtiene:

```text
JWT
```

Luego llama:

```http
POST /chat
Authorization: Bearer <JWT>
```

FastAPI extrae el token y lo coloca en la configuración del grafo:

```python
config = {
    "configurable": {
        "thread_id": request.thread_id,
        "access_token": access_token,
    }
}
```

La Tool obtiene el token:

```python
access_token = config["configurable"]["access_token"]
```

Y finalmente:

```text
Tool
 ↓
VetCareApiService
 ↓
Authorization: Bearer JWT
 ↓
VetCare API
```

---

# 35. Contexto del runtime vs datos generados por el LLM

Una distinción muy importante:

## Datos que puede generar el LLM

Por ejemplo:

```text
date
pet_id
appointment_id
```

## Datos que NO debería generar el LLM

Por ejemplo:

```text
access_token
user identity
permissions
```

El JWT pertenece al contexto de ejecución de la aplicación.

Por eso no lo ponemos en el prompt.

```text
LLM-generated arguments
        ↓
date / pet_id / appointment_id

Runtime context
        ↓
access_token
```

Esto mejora seguridad y evita que el modelo tenga responsabilidad sobre credenciales.

---

# 36. LangGraph

LangGraph se utiliza para construir workflows con estado.

A diferencia de una chain simple:

```text
Prompt
 ↓
LLM
 ↓
Response
```

LangGraph permite:

- estado
- nodos
- edges
- conditional edges
- loops
- persistence
- interrupts
- human-in-the-loop

---

# 37. State

Nuestro estado:

```python
class VetCareState(TypedDict):
    messages: list[BaseMessage]
    user_id: str | None
    intent: str | None
    pet_id: str | None
    pet_name: str | None
    date: str | None
    appointment_id: str | None
    response: str | None
```

El State representa la información que circula por el workflow.

Conceptualmente:

```text
State
  ↓
Node
  ↓
State actualizado
  ↓
Node
  ↓
State actualizado
```

---

# 38. ¿Por qué usar State?

Porque un workflow complejo necesita recordar información.

Ejemplo:

```text
Usuario:
"Quiero sacar un turno para Firulais"

       ↓

intent = BOOK_APPOINTMENT

pet_name = Firulais

       ↓

preguntar fecha

       ↓

date = 2026-09-08

       ↓

buscar disponibilidad

       ↓

mostrar horarios
```

Sin State tendríamos que pasar toda la información manualmente entre funciones.

---

# 39. Nodes

Un Node es una función que procesa el State.

Ejemplo:

```python
def call_agent(state):
    ...
    return {
        "messages": [response]
    }
```

Conceptualmente:

```text
State
  ↓
Node
  ↓
nuevo State
```

En nuestro proyecto tenemos un nodo principal de agente.

---

# 40. Edges

Un Edge conecta nodos.

Ejemplo:

```python
builder.add_edge(
    START,
    "agent",
)
```

Significa:

```text
START
  ↓
agent
```

Otro:

```python
builder.add_edge(
    "tools",
    "agent",
)
```

significa:

```text
tools
  ↓
agent
```

---

# 41. Conditional Edges

No siempre queremos ejecutar el mismo camino.

Podemos decidir el siguiente nodo según el estado.

Utilizamos:

```python
builder.add_conditional_edges(
    "agent",
    route_agent,
    {
        "tools": "tools",
        END: END,
    },
)
```

El agente puede producir:

```text
tool call
```

o:

```text
respuesta final
```

Entonces:

```text
                    ┌──→ tools
                    │
agent ── router ────┤
                    │
                    └──→ END
```

---

# 42. `tools_condition`

LangGraph incluye una condición preconstruida:

```python
from langgraph.prebuilt import tools_condition
```

Nuestro router:

```python
def route_agent(state):
    return tools_condition(state)
```

Esta función analiza la última respuesta del agente y determina si hay Tool Calls.

Conceptualmente:

```text
AIMessage
   │
   ├── tiene tool call → tools
   │
   └── no tiene tool call → END
```

---

# 43. Loops en LangGraph

Una de las diferencias importantes entre un workflow lineal y un agente es que el agente puede necesitar varios ciclos.

Nuestro grafo permite:

```text
LLM
 ↓
Tool
 ↓
LLM
 ↓
Tool
 ↓
LLM
 ↓
END
```

Por ejemplo, Qwen puede:

1. pedir disponibilidad
2. recibir el resultado
3. decidir que necesita otra consulta
4. ejecutar otra Tool
5. generar la respuesta final

Esto es un **loop controlado por el grafo**.

---

# 44. Arquitectura actual del Agent

El flujo principal es:

```text
                ┌───────────────┐
                │    START      │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │     Agent     │
                │     Qwen      │
                └───────┬───────┘
                        │
                 ¿Tool Call?
                   /       \
                 Sí         No
                 │           │
                 ▼           ▼
            ┌────────┐      END
            │ Tools  │
            └────┬───┘
                 │
                 ▼
               Agent
```

Esta arquitectura permite que el modelo decida cuándo utilizar herramientas.

---

# 45. Memory

Una conversación necesita mantener contexto.

Utilizamos:

```python
from langgraph.checkpoint.memory import InMemorySaver
```

y:

```python
checkpointer = InMemorySaver()
```

Esto permite guardar checkpoints en memoria.

---

# 46. `thread_id`

Para identificar una conversación usamos:

```python
config = {
    "configurable": {
        "thread_id": "conversation-1"
    }
}
```

El `thread_id` identifica el hilo conversacional.

Conceptualmente:

```text
thread_id = conversation-1
       ↓
mensajes de esa conversación
       ↓
checkpoint
       ↓
siguiente request
```

Si otro usuario utiliza:

```text
conversation-2
```

se trata de otro hilo.

---

# 47. InMemorySaver vs Persistencia real

`InMemorySaver` guarda información en RAM.

Ventaja:

- muy simple
- ideal para aprender
- no necesita infraestructura adicional

Desventaja:

```text
reiniciar proceso
      ↓
se pierde la memoria
```

No es una solución adecuada para producción.

En producción podríamos utilizar un checkpointer persistente, por ejemplo PostgreSQL.

---

# 48. Interrupts

LangGraph permite pausar un workflow y esperar información externa.

Utilizamos:

```python
from langgraph.types import interrupt
```

Ejemplo conceptual:

```python
def ask_name(state):
    name = interrupt(
        "¿Cuál es tu nombre?"
    )

    return {
        "name": name
    }
```

El workflow queda pausado.

---

# 49. Resume

Una vez que el usuario responde podemos continuar:

```python
from langgraph.types import Command

graph.invoke(
    Command(resume="Lautaro"),
    config,
)
```

Conceptualmente:

```text
Graph
  ↓
interrupt()
  ↓
PAUSA
  ↓
usuario responde
  ↓
Command(resume=...)
  ↓
Graph continúa
```

Esto permite implementar **Human-in-the-loop**.

---

# 50. Human-in-the-loop

Human-in-the-loop significa que una persona participa en una parte del workflow.

Es especialmente útil antes de operaciones importantes.

Por ejemplo:

```text
Usuario:
"Reservame un turno mañana a las 10"

        ↓

AI
        ↓

consulta disponibilidad

        ↓

"Hay disponibilidad a las 10:00.
¿Confirmás?"

        ↓

interrupt

        ↓

Usuario:
"Sí"

        ↓

resume

        ↓

crear turno
```

Esto evita que el agente ejecute acciones sensibles automáticamente sin confirmación.

---

# 51. Diferencia entre consulta y escritura

Una decisión arquitectónica importante es diferenciar:

## Operaciones de lectura

Ejemplos:

```text
GET /pets
GET /appointments
GET /appointments/availability
```

Normalmente pueden ejecutarse directamente.

## Operaciones de escritura

Ejemplos:

```text
POST /appointments
PATCH /appointments/:id/cancel
DELETE /appointments/:id
```

Son más sensibles.

Una estrategia recomendada es:

```text
LLM
 ↓
preparar acción
 ↓
mostrar qué va a hacer
 ↓
Human approval
 ↓
Tool
 ↓
API
```

---

# 52. Flujo completo de reserva de turno

El objetivo del agente es poder realizar un flujo como:

```text
Usuario
"Quiero sacar un turno para Firulais"
          ↓
        Agent
          ↓
identifica intención
          ↓
busca mascota
          ↓
pregunta/obtiene fecha
          ↓
consulta disponibilidad
          ↓
muestra horarios
          ↓
usuario confirma
          ↓
Human approval
          ↓
POST /appointments
          ↓
VetCare API
          ↓
Prisma
          ↓
PostgreSQL
          ↓
respuesta final
```

La IA no debería inventar:

- mascotas
- turnos
- horarios
- IDs
- disponibilidad

Debe obtenerlos mediante herramientas.

---

# 53. Agente vs Chain

Una pregunta típica de entrevista:

**¿Cuál es la diferencia entre una Chain y un Agent?**

## Chain

Tiene un flujo relativamente definido:

```text
Prompt
 ↓
LLM
 ↓
Parser
 ↓
Output
```

El desarrollador define el camino.

## Agent

El LLM puede decidir qué acción necesita:

```text
LLM
 ↓
decide
 ↓
Tool A
Tool B
Tool C
```

El agente es más dinámico.

En nuestro proyecto:

```text
Chain
   ↓
útil para procesamiento definido

Agent
   ↓
útil cuando debe decidir qué herramienta utilizar
```

---

# 54. Agent + LangGraph

LangGraph nos permite controlar el comportamiento del Agent.

El LLM decide:

```text
"Necesito get_my_pets"
```

LangGraph controla:

```text
¿Hay Tool Call?
        ↓
sí
        ↓
ToolNode
        ↓
volver al Agent
```

Por eso:

> El LLM toma decisiones semánticas y LangGraph controla el workflow.

Esta separación es muy importante conceptualmente.

---

# 55. Autenticación de VetCare

El backend utiliza JWT.

El flujo de login:

```text
POST /auth/login
        ↓
NestJS
        ↓
valida usuario
        ↓
genera JWT
        ↓
access_token
```

Luego:

```http
Authorization: Bearer <JWT>
```

Ese mismo JWT se propaga desde `vetcare-ai` hacia `vetcare-api`.

---

# 56. PostgreSQL local con Docker

Inicialmente el proyecto utilizaba Supabase para PostgreSQL.

Para desarrollo local decidimos utilizar PostgreSQL mediante Docker Compose.

Arquitectura:

```text
Docker Compose
      ↓
PostgreSQL
      ↓
vetcare-api
      ↓
Prisma
```

Esto permite tener una base reproducible localmente.

Ejemplo de servicio:

```yaml
services:
  postgres:
    image: postgres:16
    container_name: vetcare-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: vetcare
    ports:
      - "5432:5432"
    volumes:
      - vetcare_postgres_data:/var/lib/postgresql/data

volumes:
  vetcare_postgres_data:
```

---

# 57. Prisma

Prisma es el ORM utilizado por `vetcare-api`.

La arquitectura:

```text
NestJS
  ↓
Prisma
  ↓
PostgreSQL
```

El AI service no utiliza Prisma.

Esto es importante:

```text
vetcare-ai
    ↓ HTTP
vetcare-api
    ↓ Prisma
PostgreSQL
```

---

# 58. Por qué Docker para PostgreSQL

Utilizar PostgreSQL en Docker tiene varias ventajas:

- entorno reproducible
- instalación simple
- aislamiento
- fácil eliminación/recreación
- misma versión para todos los desarrolladores
- facilita CI/CD

Comandos básicos:

```bash
docker compose up -d
```

Ver servicios:

```bash
docker compose ps
```

Ver logs:

```bash
docker compose logs -f postgres
```

Detener:

```bash
docker compose down
```

---

# 59. Flujo real implementado hasta ahora

Actualmente tenemos esta integración:

```text
                  Usuario
                     │
                     │
                     ▼
              POST /chat
              + JWT
                     │
                     ▼
              ┌─────────────┐
              │  FastAPI    │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │  LangGraph  │
              └──────┬──────┘
                     │
                     ▼
                ┌─────────┐
                │  Qwen   │
                └────┬────┘
                     │
                 Tool Call
                     │
                     ▼
              ┌─────────────┐
              │  ToolNode   │
              └──────┬──────┘
                     │
                     ▼
             VetCareApiService
                     │
                     │ HTTP + JWT
                     ▼
              ┌─────────────┐
              │ VetCare API │
              │   NestJS    │
              └──────┬──────┘
                     │
                     ▼
                  Prisma
                     │
                     ▼
                PostgreSQL
```

---

# 60. Estructura actual del proyecto

La estructura principal es:

```text
vetcare-ai/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── ai_models.py
│   ├── prompts.py
│   │
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── state.py
│   │   ├── nodes.py
│   │   ├── routers.py
│   │   └── graph.py
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── appointments.py
│   │   ├── pets.py
│   │   └── users.py
│   │
│   └── services/
│       └── vetcare_api.py
│
├── .env
├── .gitignore
├── README.md
└── .venv/
```

---

# 61. Responsabilidad de cada módulo

## `main.py`

Entrada HTTP.

```text
FastAPI
 ↓
/health
/chat
```

## `schemas.py`

Modelos de request/response.

```text
ChatRequest
ChatResponse
```

## `config.py`

Configuración del sistema.

```text
LLM_MODEL
VETCARE_API_URL
```

## `ai_models.py`

Schemas relacionados con IA.

```text
ChatIntent
```

## `prompts.py`

Prompts reutilizables.

## `tools/`

Herramientas que puede utilizar el agente.

## `services/vetcare_api.py`

Cliente HTTP contra `vetcare-api`.

## `graph/`

Workflow del agente.

```text
state
nodes
routers
graph
```

---

# 62. Lo que ya aprendimos

Hasta este checkpoint ya trabajamos con:

```text
Python
   ↓
venv
   ↓
FastAPI
   ↓
Pydantic
   ↓
Settings
   ↓
LLM
   ↓
Ollama
   ↓
Qwen
   ↓
LangChain
   ↓
Prompts
   ↓
LCEL
   ↓
Structured Output
   ↓
Tools
   ↓
Tool Calling
   ↓
ToolNode
   ↓
Agents
   ↓
LangGraph
   ↓
State
   ↓
Nodes
   ↓
Edges
   ↓
Conditional Edges
   ↓
Loops
   ↓
Persistence / Checkpoints
   ↓
Thread ID
   ↓
Interrupt
   ↓
Human-in-the-loop
   ↓
JWT propagation
   ↓
HTTP integration
   ↓
VetCare API
   ↓
PostgreSQL
```

---

# 63. Conceptos que todavía faltan

El roadmap continúa con:

```text
LangSmith
   ├── tracing
   ├── debugging
   ├── datasets
   └── evaluation

RAG
   ├── embeddings
   ├── vector database
   ├── documents
   ├── chunking
   ├── retrieval
   └── context injection

Production
   ├── persistent checkpointer
   ├── error handling
   ├── retries
   ├── timeouts
   ├── logging
   ├── security
   ├── Docker
   └── deployment
```

Estos conceptos forman parte del siguiente nivel del proyecto y **no deben considerarse ya implementados** hasta que se incorporen al código.

---

# 64. RAG: objetivo futuro

RAG significa:

**Retrieval-Augmented Generation**

La idea es permitir que el LLM responda utilizando información externa.

Arquitectura:

```text
Documentos
    ↓
Chunking
    ↓
Embeddings
    ↓
Vector Database
    ↓
Retriever
    ↓
Contexto relevante
    ↓
LLM
    ↓
Respuesta
```

En VetCare, un caso de uso podría ser:

```text
Usuario:
"¿Qué cuidados necesita un perro después de una cirugía?"

       ↓

Retriever

       ↓

documentación veterinaria relevante

       ↓

LLM

       ↓

respuesta basada en la documentación
```

RAG es diferente de Tool Calling:

```text
Tool Calling
    ↓
consulta/acción sobre un sistema

RAG
    ↓
recuperación de conocimiento/documentos
```

---

# 65. LangSmith: objetivo futuro

LangSmith es una plataforma del ecosistema LangChain orientada a observabilidad y evaluación.

Permite analizar:

- prompts
- respuestas
- tool calls
- traces
- latencias
- errores
- evaluaciones

Conceptualmente:

```text
Usuario
   ↓
Agent
   ↓
Tool
   ↓
LLM
   ↓
Response

        ↓

    LangSmith
        ↓
   Trace completo
```

En un sistema real esto permite entender por qué un agente tomó una decisión.

---

# 66. Preguntas típicas de entrevista

## ¿Qué es un LLM?

Un Large Language Model es un modelo de lenguaje entrenado para comprender y generar texto.

## ¿Qué es Ollama?

Un runtime/servidor que permite ejecutar modelos de lenguaje localmente.

## ¿Qwen es Ollama?

No.

```text
Qwen = modelo
Ollama = runtime/servidor
```

## ¿Qué es LangChain?

Un framework/ecosistema para construir aplicaciones alrededor de LLMs.

## ¿Qué es LangGraph?

Una librería para construir workflows/agentes con estado, branching, loops, persistence e interrupts.

## ¿Qué es una Tool?

Una función que un agente puede solicitar ejecutar.

## ¿El LLM ejecuta directamente la Tool?

No necesariamente. El LLM genera un Tool Call y nuestra aplicación ejecuta la herramienta.

## ¿Qué es Tool Calling?

La capacidad del modelo de generar una llamada estructurada a una herramienta.

## ¿Qué diferencia hay entre Chain y Agent?

Una Chain sigue un flujo definido. Un Agent puede decidir dinámicamente qué herramientas utilizar.

## ¿Por qué LangGraph?

Porque necesitamos controlar un workflow con estado, decisiones, loops, checkpoints e interacción humana.

## ¿Qué es `thread_id`?

Un identificador de una conversación/workflow que permite asociar checkpoints y memoria.

## ¿Qué es `interrupt`?

Un mecanismo para pausar un workflow y esperar información externa, por ejemplo aprobación del usuario.

## ¿Qué es Human-in-the-loop?

Un patrón donde una persona participa antes o durante una acción del sistema.

## ¿Por qué no poner el JWT en el prompt?

Porque es una credencial sensible y pertenece al contexto de ejecución de la aplicación, no al contexto semántico que debe manejar el LLM.

## ¿Por qué el AI service no accede directamente a PostgreSQL?

Para mantener separación de responsabilidades, autorización y reglas de negocio centralizadas en `vetcare-api`.

## ¿Qué es Structured Output?

Es obligar/orientar al modelo a devolver datos con una estructura definida, en lugar de texto libre.

## ¿Qué es RAG?

Retrieval-Augmented Generation: recuperar información relevante desde una fuente externa y utilizarla como contexto para generar una respuesta.

---

# 67. Comandos principales

## Activar entorno

```bash
source .venv/bin/activate
```

## Ejecutar FastAPI

```bash
uvicorn app.main:app --reload
```

## Ejecutar Ollama

```bash
ollama serve
```

## Ver modelos

```bash
ollama list
```

## Ejecutar Qwen

```bash
ollama run qwen3:8b
```

## PostgreSQL

```bash
docker compose up -d
```

```bash
docker compose ps
```

```bash
docker compose logs -f postgres
```

---

# 68. Checkpoint actual

```text
┌─────────────────────────────────────────────┐
│              VETCARE AI                     │
├─────────────────────────────────────────────┤
│                                             │
│ Python 3.12                                 │
│ FastAPI                                     │
│ Pydantic                                    │
│ Ollama                                      │
│ Qwen3 8B                                    │
│ LangChain                                   │
│ Structured Output                           │
│ Tools                                       │
│ Tool Calling                                │
│ Agent                                       │
│ LangGraph                                   │
│ State                                       │
│ Nodes                                       │
│ Conditional Routing                         │
│ Loops                                       │
│ InMemorySaver                               │
│ Thread ID                                   │
│ Interrupts                                  │
│ Human-in-the-loop                           │
│ JWT propagation                             │
│ HTTP integration                            │
│ VetCare API                                 │
│ PostgreSQL + Docker                         │
│                                             │
└─────────────────────────────────────────────┘
```

El siguiente objetivo es evolucionar este agente hacia un sistema más cercano a producción:

```text
Agent
  │
  ├── Pets Tools
  ├── Appointment Tools
  ├── Human Approval
  ├── Memory Persistence
  ├── RAG
  └── Observability / LangSmith
```

La prioridad es mantener **un solo agente con múltiples herramientas**, evitando una arquitectura multi-agent innecesariamente compleja para este proyecto.
