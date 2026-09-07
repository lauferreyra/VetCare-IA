# VetCare AI

Servicio de inteligencia artificial para VetCare, desarrollado con Python, FastAPI, LangChain, LangGraph y LangSmith, integrado con la API de VetCare.

El objetivo de este proyecto es construir progresivamente un servicio de IA capaz de interactuar con los usuarios de VetCare, consultar información real mediante herramientas y ejecutar workflows inteligentes.

Este proyecto también funciona como laboratorio de aprendizaje de conceptos relacionados con **LLMs, LangChain, LangGraph, LangSmith, Agents, Tools y RAG**.

---

# 1. Arquitectura general

VetCare está compuesto por diferentes servicios:

```text
                    ┌─────────────────┐
                    │   VetCare Web   │
                    │ Next.js / React │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   VetCare API   │
                    │     NestJS      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    PostgreSQL   │
                    │    Supabase     │
                    └─────────────────┘


                    ┌─────────────────┐
                    │   VetCare AI    │
                    │ Python/FastAPI  │
                    └────────┬────────┘
                             │
                             ▼
                       VetCare API
```

`vetcare-ai` es un servicio independiente especializado en funcionalidades de inteligencia artificial.

La idea es mantener separadas las responsabilidades:

* **VetCare Web:** interfaz de usuario.
* **VetCare API:** lógica de negocio y acceso a datos.
* **VetCare AI:** funcionalidades basadas en inteligencia artificial.

---

# 2. Python

Python es el lenguaje utilizado para desarrollar `vetcare-ai`.

Se eligió principalmente porque posee un ecosistema muy amplio para trabajar con inteligencia artificial, machine learning y aplicaciones basadas en LLMs.

La versión utilizada actualmente es:

```text
Python 3.12.14
```

---

# 3. Entorno virtual (`venv`)

El proyecto utiliza un entorno virtual de Python:

```text
.venv/
```

Un entorno virtual permite aislar las dependencias de un proyecto de las dependencias de otros proyectos.

Conceptualmente es similar a `node_modules` en Node.js: cada proyecto mantiene sus propias dependencias y versiones.

### Sin entorno virtual

```text
Python del sistema
│
├── proyecto A
├── proyecto B
└── vetcare-ai
```

Los proyectos podrían terminar compartiendo versiones de paquetes.

### Con entorno virtual

```text
proyecto A
└── .venv/

proyecto B
└── .venv/

vetcare-ai
└── .venv/
```

Cada proyecto tiene su propio entorno.

### Crear un entorno virtual

Utilizamos Python 3.12:

```bash
python3.12 -m venv .venv
```

### Activarlo

En macOS/Linux:

```bash
source .venv/bin/activate
```

Cuando está activo aparece:

```text
(.venv)
```

en la terminal.

---

# 4. `pip`

`pip` es el gestor de paquetes de Python.

Permite instalar las dependencias utilizadas por nuestro proyecto.

Conceptualmente:

```text
Node.js

npm
 ↓
package.json
 ↓
node_modules
```

En Python:

```text
Python

pip
 ↓
dependencias
 ↓
.venv/
```

Por ejemplo:

```bash
pip install fastapi
```

instala FastAPI dentro del entorno virtual activo.

---

# 5. FastAPI

FastAPI es el framework utilizado para construir nuestra API HTTP.

Nuestra aplicación actualmente expone:

```text
GET  /health
POST /chat
```

La estructura inicial:

```text
app/
├── main.py
├── schemas.py
└── config.py
```

---

# 6. Instancia de FastAPI

En `main.py`:

```python
from fastapi import FastAPI

app = FastAPI()
```

`FastAPI()` crea una instancia de nuestra aplicación.

Conceptualmente es similar a:

```typescript
const app = express();
```

en Express.

---

# 7. Endpoint / Path Operation

Un endpoint define una operación HTTP disponible en nuestra API.

Por ejemplo:

```python
@app.get("/health")
def health_check():
    return {"status": "ok"}
```

El decorador:

```python
@app.get("/health")
```

indica que cuando llegue una petición:

```http
GET /health
```

FastAPI debe ejecutar:

```python
health_check()
```

Y devolver:

```json
{
  "status": "ok"
}
```

En FastAPI este tipo de definición se conoce como una **path operation**.

---

# 8. Health Check

Un health check es un endpoint utilizado para comprobar si un servicio está funcionando correctamente.

Nuestro endpoint:

```http
GET /health
```

devuelve:

```json
{
  "status": "ok"
}
```

Este tipo de endpoint es muy habitual en aplicaciones desplegadas en infraestructura como Docker, Kubernetes o plataformas cloud.

---

# 9. Uvicorn

Uvicorn es el servidor ASGI que utilizamos para ejecutar nuestra aplicación FastAPI.

La relación es:

```text
Uvicorn
   ↓
ejecuta
   ↓
FastAPI
```

Para iniciar la aplicación durante el desarrollo:

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
archivo app/main.py

:
   ↓

app
   ↓
variable que contiene la instancia de FastAPI
```

---

# 10. `--reload`

Durante el desarrollo utilizamos:

```bash
uvicorn app.main:app --reload
```

La opción:

```text
--reload
```

hace que Uvicorn detecte cambios en los archivos y reinicie automáticamente la aplicación.

Por eso, mientras desarrollamos:

```text
modificar código
      ↓
guardar
      ↓
Uvicorn detecta cambio
      ↓
reinicia aplicación
```

En producción no se utiliza normalmente este modo.

---

# 11. Request Body

Cuando enviamos información a una API mediante `POST`, podemos incluir un cuerpo de la petición.

Por ejemplo:

```json
{
  "message": "¿Qué mascotas tengo?"
}
```

Este contenido es el **request body**.

---

# 12. Pydantic

FastAPI utiliza Pydantic para definir y validar estructuras de datos.

Creamos:

```python
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
```

Esto define que nuestro endpoint espera un objeto que contenga:

```text
message
```

y que ese valor sea un:

```text
str
```

Conceptualmente se parece a un DTO en NestJS.

### NestJS

```typescript
export class ChatRequestDto {
    message: string;
}
```

### FastAPI + Pydantic

```python
class ChatRequest(BaseModel):
    message: str
```

---

# 13. Endpoint `/chat`

Nuestro endpoint:

```python
@app.post("/chat")
def chat(request: ChatRequest):
    ...
```

recibe:

```json
{
  "message": "Hola"
}
```

FastAPI utiliza `ChatRequest` para interpretar y validar el request.

El flujo es:

```text
HTTP POST /chat
       ↓
FastAPI
       ↓
ChatRequest
       ↓
chat()
       ↓
respuesta JSON
```

---

# 14. Variables de entorno

La configuración que puede cambiar entre ambientes no debería estar hardcodeada en el código.

Por ejemplo:

```text
development
testing
production
```

pueden utilizar diferentes configuraciones.

Para esto utilizamos un archivo:

```text
.env
```

Actualmente configuramos:

```env
LLM_MODEL=qwen3:8b
```

El archivo `.env` no debe subirse al repositorio porque puede contener información sensible.

Nuestro `.gitignore` contiene:

```gitignore
.env
.env.*
!.env.example
```

---

# 15. Pydantic Settings

Para cargar variables de configuración utilizamos:

```text
pydantic-settings
```

Nuestro `config.py`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_model: str

    model_config = SettingsConfigDict(
        env_file=".env",
    )


settings = Settings()
```

Esto permite obtener:

```env
LLM_MODEL=qwen3:8b
```

desde:

```python
settings.llm_model
```

El flujo es:

```text
.env
 ↓
Pydantic Settings
 ↓
Settings
 ↓
settings.llm_model
```

De esta forma evitamos escribir directamente el modelo en nuestro código.

---

# 16. LLM

LLM significa:

**Large Language Model**

Es un modelo de lenguaje capaz de procesar entradas de lenguaje natural y generar respuestas.

Conceptualmente:

```text
input
  ↓
LLM
  ↓
output
```

Por ejemplo:

```text
Usuario:
¿Qué es una API REST?

        ↓

      LLM

        ↓

Respuesta generada
```

Un punto fundamental:

> Un LLM no tiene automáticamente acceso a la información de nuestra base de datos de VetCare.

Más adelante utilizaremos Tools para permitirle consultar información real.

---

# 17. Ollama

Ollama permite ejecutar modelos de lenguaje localmente.

En nuestro proyecto utilizamos Ollama para evitar depender de una API comercial durante el aprendizaje.

La arquitectura es:

```text
Aplicación
    ↓
Ollama
    ↓
modelo local
```

Ollama actúa como runtime/servidor para ejecutar el modelo.

---

# 18. Modelo local

Utilizamos:

```text
Qwen3 8B
```

El `8B` hace referencia aproximadamente a:

```text
8 billion parameters
```

Es decir, aproximadamente 8.000 millones de parámetros.

El tamaño real en disco y memoria depende también de la cuantización utilizada.

Elegimos un modelo de este tamaño porque nuestro objetivo inicial es aprender el ecosistema de LLMs localmente.

---

# 19. Ollama Server

Ollama funciona mediante un servidor local.

Podemos iniciarlo con:

```bash
ollama serve
```

El flujo conceptual es:

```text
Aplicación
    ↓
Ollama Server
    ↓
Qwen3 8B
```

El servidor normalmente escucha en:

```text
127.0.0.1:11434
```

---

# 20. LangChain

LangChain es un framework/ecosistema para construir aplicaciones basadas en LLMs.

LangChain **no es el modelo de IA**.

Por ejemplo:

```text
Qwen3
   ↓
es el modelo

LangChain
   ↓
nos proporciona componentes
para construir la aplicación alrededor del modelo
```

LangChain permite trabajar con conceptos como:

* modelos
* prompts
* tools
* agents
* retrievers
* output estructurado
* cadenas

---

# 21. `langchain-ollama`

Para conectar LangChain con Ollama utilizamos:

```text
langchain-ollama
```

La arquitectura queda:

```text
LangChain
    ↓
langchain-ollama
    ↓
Ollama
    ↓
Qwen3
```

Esto permite que nuestra aplicación utilice un modelo servido localmente por Ollama a través de las abstracciones de LangChain.

---

# 22. `ChatOllama`

En nuestro código:

```python
from langchain_ollama import ChatOllama
```

Creamos el modelo:

```python
llm = ChatOllama(
    model=settings.llm_model,
)
```

El modelo concreto viene de:

```env
LLM_MODEL=qwen3:8b
```

Por lo tanto:

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

# 23. `invoke()`

`invoke()` permite ejecutar un componente de LangChain con una entrada.

Por ejemplo:

```python
response = llm.invoke("Hola")
```

Conceptualmente:

```text
input
  ↓
invoke()
  ↓
ChatModel
  ↓
LLM
  ↓
output
```

La respuesta de un modelo de chat puede ser un `AIMessage`.

Para obtener el texto:

```python
response.content
```

---

# 24. Prompt

Un prompt es la entrada/instrucción que proporcionamos al modelo para indicarle qué queremos que haga.

Por ejemplo:

```text
Sos el asistente virtual de VetCare.

Respondé de manera clara, profesional y amigable.

Pregunta del usuario:
¿Qué mascotas tengo?
```

El prompt puede contener instrucciones y datos dinámicos.

---

# 25. ChatPromptTemplate

LangChain permite construir prompts estructurados mediante:

```python
ChatPromptTemplate
```

Creamos:

```python
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
```

Tenemos dos mensajes:

```text
SYSTEM
  ↓
define el comportamiento del asistente

HUMAN
  ↓
contiene la pregunta del usuario
```

---

# 26. System Message

El mensaje `system` contiene instrucciones generales sobre el comportamiento del modelo.

Ejemplo:

```text
Sos el asistente virtual de VetCare.
Respondé de manera clara, profesional y amigable.
```

Conceptualmente:

```text
SYSTEM
   ↓
cómo debe comportarse el asistente
```

---

# 27. Human Message

El mensaje `human` representa el mensaje del usuario.

En nuestro template:

```python
(
    "human",
    "{question}",
)
```

`{question}` es una variable.

Si el usuario envía:

```text
¿Qué mascotas tengo?
```

el template genera:

```text
HUMAN:
¿Qué mascotas tengo?
```

---

# 28. Variables en Prompts

Las variables permiten reutilizar un mismo template.

Tenemos:

```text
{question}
```

y al ejecutar:

```python
chat_prompt.invoke(
    {
        "question": request.message,
    }
)
```

LangChain reemplaza la variable.

Conceptualmente:

```text
Template:

Pregunta:
{question}

        ↓

question = "¿Qué mascotas tengo?"

        ↓

Prompt final:

Pregunta:
¿Qué mascotas tengo?
```

---

# 29. LCEL

LCEL significa:

**LangChain Expression Language**

Permite componer componentes de LangChain.

Por ejemplo:

```python
chain = chat_prompt | llm
```

El operador:

```text
|
```

representa el paso de la salida de un componente hacia el siguiente.

Conceptualmente:

```text
Input
  ↓
Prompt
  ↓
LLM
  ↓
Output
```

---

# 30. Chain

Una chain es una composición de componentes.

Nuestro ejemplo:

```python
chain = chat_prompt | llm
```

representa:

```text
ChatPromptTemplate
        ↓
     ChatOllama
```

Luego ejecutamos:

```python
response = chain.invoke(
    {
        "question": request.message,
    }
)
```

Importante:

```python
chain = chat_prompt | llm
```

construye la cadena.

Mientras que:

```python
chain.invoke(...)
```

la ejecuta.

---

# 31. Arquitectura actual

Actualmente nuestro servicio funciona conceptualmente así:

```text
                  POST /chat
                       │
                       ▼
                    FastAPI
                       │
                       ▼
                  ChatRequest
                       │
                       ▼
                 ChatPromptTemplate
                       │
                       ▼
                    ChatOllama
                       │
                       ▼
                     Ollama
                       │
                       ▼
                    Qwen3 8B
                       │
                       ▼
                    AIMessage
                       │
                       ▼
                response.content
```

---

# 32. Conceptos que todavía vamos a aprender

El proyecto todavía está en una etapa inicial.

Los siguientes conceptos serán incorporados progresivamente:

```text
LangChain
│
├── Structured Output
├── Tools
├── Tool Calling
├── Agents
├── Memory
├── Retrievers
└── RAG
        │
        ▼
    LangGraph
        │
        ├── State
        ├── Nodes
        ├── Edges
        ├── Conditional Edges
        ├── Loops
        ├── Persistence
        └── Human-in-the-loop
                │
                ▼
            LangSmith
                │
                ├── Tracing
                ├── Debugging
                ├── Datasets
                └── Evaluation
```

Estos conceptos se irán incorporando al proyecto a medida que los estudiemos y utilicemos.

---

# 33. Objetivo final

El objetivo es evolucionar desde:

```text
POST /chat
    ↓
Prompt
    ↓
LLM
    ↓
respuesta
```

hasta una arquitectura capaz de:

```text
Usuario
   │
   ▼
VetCare AI
   │
   ▼
LLM
   │
   ├───────────────┐
   │               │
   ▼               ▼
Tools           LangGraph
   │               │
   ▼               ▼
VetCare API     Workflows
   │               │
   ▼               ▼
Datos reales   decisiones
                   │
                   ▼
             Human approval
                   │
                   ▼
              acción final
```

Un ejemplo futuro será:

```text
Usuario:
"Quiero sacar un turno para Firulais"

             ↓

            LLM

             ↓

       identifica intención

             ↓

       busca mascota

             ↓

       consulta disponibilidad

             ↓

       propone horarios

             ↓

       usuario confirma

             ↓

       crea appointment

             ↓

       respuesta final
```

El objetivo principal es que el LLM **no invente información de VetCare**, sino que utilice herramientas para consultar y operar sobre los datos reales de la aplicación.
