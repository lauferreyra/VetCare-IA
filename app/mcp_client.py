from contextvars import ContextVar
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest

from app.config import settings


access_token_context: ContextVar[str | None] = ContextVar(
    "access_token_context",
    default=None,
)


async def inject_access_token(
    request: MCPToolCallRequest,
    handler,
):
    access_token = access_token_context.get()

    if not access_token:
        raise ValueError(
            "No access token available for MCP tool call."
        )

    modified_request = request.override(
        args={
            **request.args,
            "access_token": access_token,
        },
    )

    return await handler(modified_request)


def get_mcp_project_path() -> Path:
    server_path = Path(
        settings.mcp_server_path
    ).resolve()

    return server_path.parent.parent


def get_mcp_python() -> str:
    mcp_project_path = get_mcp_project_path()

    python_path = (
        mcp_project_path
        / ".venv"
        / "bin"
        / "python"
    )

    if not python_path.exists():
        raise FileNotFoundError(
            f"MCP Python interpreter not found: {python_path}"
        )

    return str(python_path)


mcp_project_path = get_mcp_project_path()
mcp_python = get_mcp_python()


mcp_client = MultiServerMCPClient(
    {
        "vetcare": {
            "command": mcp_python,
            "args": [
                "-m",
                "app.server",
            ],
            "cwd": str(mcp_project_path),
            "transport": "stdio",
        },
    },
    tool_interceptors=[
        inject_access_token,
    ],
)


async def get_mcp_tools():
    return await mcp_client.get_tools(
        server_name="vetcare",
    )