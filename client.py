import os
import asyncio
import sys
import json
from contextlib import AsyncExitStack
from typing import Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from openai import AsyncOpenAI


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.llm = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

    async def connect_to_server(self, server_script_path: str):
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])
        print("\nSchema:", json.dumps([{
            "name": tool.name,
            "description": tool.description,
            "inputSchema": tool.inputSchema
        } for tool in tools], indent=2))

    async def process_query(self, query: str) -> str:
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        response = await self.session.list_tools()
        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "strict": True,
                "parameters": {
                    **tool.inputSchema,
                    "additionalProperties": False
                }
            }
        } for tool in response.tools]

        response = await self.llm.chat.completions.create(
            model="gpt-4.1-nano",
            max_tokens=1000,
            messages=messages,
            tools=available_tools
        )
        print(response)

        # Process response and handle tool calls
        tool_results = []
        final_text = []

        message = response.choices[0].message
        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                result = await self.session.call_tool(tool_name, tool_args)
                tool_results.append({
                    "role": "tool",
                    "content": result.content,
                    "tool_call_id": tool_call.id
                })
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

            messages.append({
                "role": "assistant",
                "tool_calls": message.tool_calls,
            })
            messages.extend(tool_results)

            response = await self.llm.chat.completions.create(
                model="gpt-4.1-nano",
                max_tokens=1000,
                messages=messages,
            )
            print(response)

            final_text.append(response.choices[0].message.content)
        elif message.content:
            final_text.append(message.content)

        return "\n".join(final_text)

    async def chat_loop(self):
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        await self.exit_stack.aclose()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())