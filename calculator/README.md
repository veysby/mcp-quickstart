# Calculator MCP Server

A simple MCP server that provides basic arithmetic operations, calculation history, and an interactive calculator UI rendered directly inside Claude Desktop via the [MCP Apps](https://github.com/modelcontextprotocol/ext-apps) extension.

## Features

### Tools
| Tool | Description |
|---|---|
| `add(a, b)` | Add two numbers |
| `subtract(a, b)` | Subtract `b` from `a` |
| `multiply(a, b)` | Multiply two numbers |
| `divide(a, b)` | Divide `a` by `b` (raises on zero) |
| `show_calculator()` | Open the interactive calculator UI in the chat |

### Resources
| URI | Description |
|---|---|
| `calc://history` | All calculations performed in the current session |
| `calc://history/{index}` | A specific calculation by its index |
| `calc://constants` | Common mathematical constants (π, e, τ, φ) |
| `ui://calculator/app` | The interactive calculator HTML (MCP Apps resource) |

## Interactive Calculator UI

Calling `show_calculator` (or asking Claude to "show me a calculator") renders a fully interactive calculator widget inline in the conversation. Button presses call the server-side `add`, `subtract`, `multiply`, and `divide` tools — results come back from the server and appear on the display.

This uses the **MCP Apps** protocol (`text/html;profile=mcp-app`), which is supported by Claude Desktop and MCP Inspector.

## Installation

Requires Python 3.13+ and [`uv`](https://github.com/astral-sh/uv).

```bash
uv sync
```

## Running locally

```bash
uv run calculator.py
```

## Claude Desktop setup

Add the following to your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "calculator": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/calculator",
        "run",
        "calculator.py"
      ]
    }
  }
}
```

Restart Claude Desktop after editing the config. Then ask Claude:

> "Can you show me a calculator?"

## Project structure

```
calculator/
├── calculator.py         # MCP server (FastMCP)
├── calculator_ui.html    # Interactive UI (MCP Apps view)
└── pyproject.toml
```

## How the MCP Apps integration works

1. `show_calculator` is registered with `meta={"ui": {"resourceUri": "ui://calculator/app"}}`. Claude Desktop sees this in `tools/list` and knows the tool has a UI.
2. When the tool is called, Claude Desktop fetches `ui://calculator/app` from the server and renders it in a sandboxed iframe.
3. The HTML performs the `ui/initialize` handshake with the host, then reports its rendered size via `ui/notifications/size-changed` so the iframe is resized to fit.
4. Button presses in the iframe call the server tools (`add`, `subtract`, etc.) via `tools/call` over the postMessage bridge.
