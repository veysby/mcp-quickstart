# ChatKit App

A chat web app powered by [OpenAI ChatKit](https://platform.openai.com/docs/chatkit).

**Reference**: [openai-chatkit-starter-app](https://github.com/openai/openai-chatkit-starter-app) — official starter app this project is based on. [Python SDK docs](https://openai.github.io/chatkit-python/).

**Backend**: Python (FastAPI) — handles ChatKit requests and routes them to MCP tool servers.  
**Frontend**: Node.js, Vite, React, TypeScript — renders the ChatKit UI.

## Prerequisites

- Python 3.14+ and [uv](https://docs.astral.sh/uv/)
- Node.js 18+ and npm
- OpenAI API key

## Configuration

Copy `.env.sample` to `.env` and fill in the values:

```bash
cp .env.sample .env
```

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key — used by the LangChain weather agent |
| `WEATHER_MCP_SERVER` | Path to the weather MCP server script (e.g. `../weather/weather.py`) |

## Running the backend

```bash
uv run uvicorn backend.server:app --reload
```

The server starts at `http://localhost:8000`. Health check: `GET /health`.

## Running the frontend dev server

```bash
npm run dev
```

The UI starts at `http://localhost:5173`. The Vite dev server proxies `/chatkit` requests to the Python backend at `http://localhost:8000`.

Start the backend first, then the frontend.

