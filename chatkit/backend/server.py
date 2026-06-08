from __future__ import annotations

import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncIterator

from chatkit.server import ChatKitServer, StreamingResult
from chatkit.types import (
    AssistantMessageContent,
    AssistantMessageItem,
    CustomTask,
    ThreadItemAddedEvent,
    ThreadItemDoneEvent,
    ThreadItemUpdatedEvent,
    ThreadMetadata,
    ThreadStreamEvent,
    UserMessageItem,
    UserMessageTextContent,
    Workflow,
    WorkflowItem,
    WorkflowTaskAdded,
    WorkflowTaskUpdated,
)
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse
from langchain.agents import create_agent
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from mcp.client.stdio import StdioServerParameters

from .memory_store import MemoryStore
from .mcp_bridge import MCPBridge

load_dotenv()

bridge = MCPBridge()


@asynccontextmanager
async def lifespan(app: FastAPI):
    server_path = os.environ["WEATHER_MCP_SERVER"]
    await bridge.connect(StdioServerParameters(command="uv", args=["run", "python", server_path]))
    yield
    await bridge.close()


app = FastAPI(lifespan=lifespan)


class EchoChatServer(ChatKitServer[dict[str, Any]]):
    def __init__(self) -> None:
        self.store: MemoryStore = MemoryStore()
        super().__init__(self.store)

    async def respond(
        self,
        thread: ThreadMetadata,
        item: UserMessageItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        user_text = " ".join(
            part.text for part in (item.content if item else [])
            if isinstance(part, UserMessageTextContent)
        )
        tool_id = (
            item.inference_options.tool_choice.id
            if item and item.inference_options and item.inference_options.tool_choice
            else None
        )

        if tool_id == "weather":
            workflow_id = str(uuid.uuid4())
            created_at = datetime.now(timezone.utc)
            tasks: list[CustomTask] = []
            run_id_to_idx: dict[str, int] = {}

            workflow_item = WorkflowItem(
                id=workflow_id,
                thread_id=thread.id,
                created_at=created_at,
                workflow=Workflow(type="custom", tasks=[]),
            )
            yield ThreadItemAddedEvent(item=workflow_item)

            llm = ChatOpenAI(model="gpt-4.1-nano")
            mcp_tools = await load_mcp_tools(bridge.session)
            agent = create_agent(llm, mcp_tools)

            reply = ""
            async for event in agent.astream_events(
                {"messages": [{"role": "user", "content": user_text}]},
                version="v2",
            ):
                kind = event["event"]
                run_id = event.get("run_id", "")

                if kind == "on_tool_start":
                    task = CustomTask(
                        title=event["name"],
                        icon="bolt",
                        status_indicator="loading",
                    )
                    run_id_to_idx[run_id] = len(tasks)
                    tasks.append(task)
                    yield ThreadItemUpdatedEvent(
                        item_id=workflow_id,
                        update=WorkflowTaskAdded(task_index=len(tasks) - 1, task=task),
                    )

                elif kind == "on_tool_end":
                    idx = run_id_to_idx.get(run_id, 0)
                    task = CustomTask(
                        title=event["name"],
                        icon="bolt",
                        status_indicator="complete",
                    )
                    tasks[idx] = task
                    yield ThreadItemUpdatedEvent(
                        item_id=workflow_id,
                        update=WorkflowTaskUpdated(task_index=idx, task=task),
                    )

                elif kind == "on_chain_end":
                    output = event["data"].get("output", {})
                    if isinstance(output, dict) and "messages" in output:
                        msgs = output["messages"]
                        if msgs:
                            content = getattr(msgs[-1], "content", None)
                            if content and isinstance(content, str):
                                reply = content

            yield ThreadItemDoneEvent(
                item=WorkflowItem(
                    id=workflow_id,
                    thread_id=thread.id,
                    created_at=created_at,
                    workflow=Workflow(type="custom", tasks=tasks),
                )
            )

            msg = AssistantMessageItem(
                id=str(uuid.uuid4()),
                thread_id=thread.id,
                created_at=datetime.now(timezone.utc),
                content=[AssistantMessageContent(text=reply)],
            )
            yield ThreadItemAddedEvent(item=msg)
            yield ThreadItemDoneEvent(item=msg)

        else:
            msg = AssistantMessageItem(
                id=str(uuid.uuid4()),
                thread_id=thread.id,
                created_at=datetime.now(timezone.utc),
                content=[AssistantMessageContent(text=user_text)],
            )
            yield ThreadItemAddedEvent(item=msg)
            yield ThreadItemDoneEvent(item=msg)


chatkit_server = EchoChatServer()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chatkit")
async def chatkit_endpoint(request: Request) -> Response:
    payload = await request.body()
    result = await chatkit_server.process(payload, {"request": request})

    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    if hasattr(result, "json"):
        return Response(content=result.json, media_type="application/json")
    return JSONResponse(result)
