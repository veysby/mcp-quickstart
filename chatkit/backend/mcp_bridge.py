from __future__ import annotations

from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


class MCPBridge:
    def __init__(self) -> None:
        self._stack = AsyncExitStack()
        self.session: ClientSession | None = None

    async def connect(self, params: StdioServerParameters) -> None:
        read, write = await self._stack.enter_async_context(stdio_client(params))
        self.session = await self._stack.enter_async_context(ClientSession(read, write))
        await self.session.initialize()

    async def close(self) -> None:
        await self._stack.aclose()
