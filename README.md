# MCP Learning Projects

Hands-on projects for understanding how to build applications using [Model Context Protocol (MCP)](https://modelcontextprotocol.io/).

## Projects

### `weather/` — MCP Server + Custom Client

A weather MCP server built from the [official MCP Quickstart](https://modelcontextprotocol.io/quickstart/server), extended with a custom Python MCP client that routes tool calls through the **OpenAI Chat Completions and Responses APIs**.

### `calculator/` — MCP Server with Resources and Interactive UI

A calculator MCP server that demonstrates **MCP resources** and **MCP Apps** — an extension that renders an interactive HTML calculator widget directly inside Claude Desktop.

## Requirements

- Python 3.13+ and [`uv`](https://github.com/astral-sh/uv)
- Claude Desktop (for MCP Apps UI in the calculator project)
- OpenAI API key (for the weather client)

See each subfolder's `README.md` for setup and run instructions.
