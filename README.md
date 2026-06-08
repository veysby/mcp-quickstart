# MCP Learning Projects

Hands-on projects for understanding how to build applications using [Model Context Protocol (MCP)](https://modelcontextprotocol.io/).

## Projects

### `weather/` — MCP Server + Custom Client

A weather MCP server built from the [official MCP Quickstart](https://modelcontextprotocol.io/quickstart/server), extended with a custom Python MCP client that routes tool calls through the **OpenAI Chat Completions and Responses APIs**.

### `calculator/` — MCP Server with Resources and Interactive UI

A calculator MCP server that demonstrates **MCP resources** and **MCP Apps** — an extension that renders an interactive HTML calculator widget directly inside Claude Desktop.

### `chatkit/` — Chat Web App with MCP Backend

A full-stack chat application built on [OpenAI ChatKit](https://platform.openai.com/docs/chatkit). The frontend is a React + Vite app; the backend is a FastAPI server that routes messages to MCP tool servers based on the selected composer mode.

- **Echo mode** — echoes user input back verbatim
- **Weather mode** — runs a LangChain agent backed by the `weather/` MCP server; tool calls (`get_alerts`, `get_forecast`) are streamed live to the UI as a workflow with per-step status indicators

Requires Python 3.14+ for the backend.

## Requirements

- Python 3.13+ and [`uv`](https://github.com/astral-sh/uv)
- Node.js 18+ and npm (for `chatkit/`)
- Claude Desktop (for MCP Apps UI in the calculator project)
- OpenAI API key (for the weather client and chatkit weather agent)

See each subfolder's `README.md` for setup and run instructions.
