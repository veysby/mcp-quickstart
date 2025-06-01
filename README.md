# MCP Quickstart

Basic MCP server from the Model Context Protocol (MCP) [Quickstart Guide](https://modelcontextprotocol.io/quickstart/server)
adapted to work with the OpenAI chat completions and responses API's

## Notes
- MCP inspector was very helpful in troubleshooting basic configuration issues
  ```sh
  npx @modelcontextprotocol/inspector uv run weather.py
  ```
- Claude desktop works fine with this server
- I was not able to make this server work in PyCharm > AI Assistant > Model Context Protocol (MCP)
    - Constantly getting `MCP error -1: Connection closed`
    - Increasing the timeout didn't help [LLM-16647](https://youtrack.jetbrains.com/issue/LLM-16647)
    - Since JetBrains AI Assistant plugin version: 251.26094.80.11 getting `Not Started` - [LLM-17338](https://youtrack.jetbrains.com/issue/LLM-17338)

## Links:
- https://modelcontextprotocol.io/quickstart/server
- https://modelcontextprotocol.io/quickstart/client
- https://platform.openai.com/docs/api-reference/chat/create
- https://platform.openai.com/docs/api-reference/chat/object