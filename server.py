import asyncio
import logging
from fastmcp import FastMCP

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("mcp")

MAX_CONCURRENT = 50
semaphore = asyncio.Semaphore(MAX_CONCURRENT)

mcp = FastMCP("tigra-prod")

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
    mcp.run(
        transport="sse",
        host="127.0.0.1",
        port=8000
    )
