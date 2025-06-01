import asyncio
import json
import os
import sys
from abc import ABC, abstractmethod
from contextlib import AsyncExitStack
from typing import Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI


class Engine(ABC):
    @abstractmethod
    async def process_query(self, session: ClientSession, query: str) -> str:
        pass


class OpenAICompletionsEngine(Engine):
    def __init__(self):
        self.llm = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

    async def process_query(self, session: ClientSession, query: str) -> str:
        response = await session.list_tools()
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

        messages = [{"role": "user", "content": query}]
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

                result = await session.call_tool(tool_name, tool_args)
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


class OpenAIResponsesEngine(Engine):
    def __init__(self):
        self.llm = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

    async def process_query(self, session: ClientSession, query: str) -> str:
        response = await session.list_tools()
        available_tools = [{
            "type": "function",
            "name": tool.name,
            "description": tool.description,
            "strict": True,
            "parameters": {
                **tool.inputSchema,
                "additionalProperties": False
            }
        } for tool in response.tools]

        messages = [{"role": "user", "content": query}]
        response = await self.llm.responses.create(
            model="gpt-4.1-nano",
            max_output_tokens=1000,
            input=messages,
            tools=available_tools
        )
        print(response)

        # Process response and handle tool calls
        tool_results = []
        final_text = []

        for resp in response.output:
            if resp.type == "function_call":
                tool_name = resp.name
                tool_args = json.loads(resp.arguments)

                result = await session.call_tool(tool_name, tool_args)
                tool_results.append({
                    "type": "function_call_output",
                    "output": result.content[0].text,
                    "call_id": resp.call_id
                })
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                messages.append({
                    "type": "function_call",
                    "name": tool_name,
                    "arguments": resp.arguments,
                    "call_id": resp.call_id
                })
            elif resp.type == "message":
                for content in resp.content:
                    if content.type == "output_text":
                        final_text.append(content.text)

        if tool_results:
            messages.extend(tool_results)

            response = await self.llm.responses.create(
                model="gpt-4.1-nano",
                max_output_tokens=1000,
                input=messages,
                # Looks like it is ok to have tools here, but should we?
                # tools=available_tools
            )
            print(response)

            for resp in response.output:
                if resp.type == "message":
                    for content in resp.content:
                        if content.type == "output_text":
                            final_text.append(content.text)

        return "\n".join(final_text)


class MCPClient:
    def __init__(self, engine):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.engine = engine

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

    async def chat_loop(self):
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.engine.process_query(self.session, query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        await self.exit_stack.aclose()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    engine = OpenAIResponsesEngine()
    client = MCPClient(engine)
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())