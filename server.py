import asyncio
import logging
from fastmcp import FastMCP
from fastmcp.server.auth import StaticTokenVerifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("mcp")

MAX_CONCURRENT = 50
semaphore = asyncio.Semaphore(MAX_CONCURRENT)

API_TOKEN = "3dd2f98e8fc318b0fba7861e6ffffd7c"
auth = StaticTokenVerifier(
    {
        API_TOKEN: {
            "client_id": "tigra-prod",
            "scopes": [],
        }
    }
)

mcp = FastMCP("tigra-prod", auth=auth)

@mcp.tool()
async def hello(name: str = "world") -> str:
    """Поприветствовать пользователя"""
    async with semaphore:
        return f"Hello, {name}!"

@mcp.tool()
async def ping() -> str:
    """Простой пинг"""
    async with semaphore:
        return "pong"

@mcp.tool()
async def health() -> dict:
    """Статус сервера"""
    async with semaphore:
        return {"status": "ok", "concurrency": MAX_CONCURRENT}

@mcp.tool()
async def run_command(command: str) -> str:
    """Выполнить команду в шелле сервера"""
    async with semaphore:
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=5.0)
            return f"STDOUT: {stdout.decode()}\nSTDERR: {stderr.decode()}"
        except Exception as e:
            return f"failed to run command: {str(e)}"

if __name__ == "__main__":
    logger.info("Starting tigra-prod with bearer token auth enabled")
    mcp.run(
        transport="sse",
        host="127.0.0.1",
        port=8000
    )
