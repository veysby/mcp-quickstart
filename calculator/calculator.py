import math
import os
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP(
    "calculator",
    instructions="A basic calculator server that supports standard arithmetic operations and provides access to calculation history and mathematical constants through resources."
)

# In-memory storage for calculation history
history: List[Dict[str, Any]] = []

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers."""
    result = a + b
    history.append({"operation": "add", "a": a, "b": b, "result": result})
    return result

@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    result = a - b
    history.append({"operation": "subtract", "a": a, "b": b, "result": result})
    return result

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    result = a * b
    history.append({"operation": "multiply", "a": a, "b": b, "result": result})
    return result

@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    result = a / b
    history.append({"operation": "divide", "a": a, "b": b, "result": result})
    return result

@mcp.resource("calc://history")
def get_history() -> str:
    """Get the history of all calculations performed in this session."""
    if not history:
        return "No calculations performed yet."
    
    lines = []
    for i, entry in enumerate(history):
        lines.append(f"{i}: {entry['a']} {entry['operation']} {entry['b']} = {entry['result']}")
    return "\n".join(lines)

@mcp.resource("calc://history/{index}")
def get_history_entry(index: int) -> str:
    """Get a specific calculation from history by its index."""
    try:
        entry = history[index]
        return f"Calculation {index}:\nOperation: {entry['operation']}\nInput A: {entry['a']}\nInput B: {entry['b']}\nResult: {entry['result']}"
    except IndexError:
        return f"Error: No calculation found at index {index}"
    except ValueError:
        return "Error: Index must be an integer"

@mcp.resource("calc://constants")
def get_constants() -> Dict[str, float]:
    """Get a list of common mathematical constants."""
    return {
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
        "phi": (1 + 5**0.5) / 2
    }

@mcp.resource("ui://calculator/app", mime_type="text/html;profile=mcp-app")
def get_ui() -> str:
    """Get the interactive calculator UI."""
    ui_path = os.path.join(os.path.dirname(__file__), "calculator_ui.html")
    with open(ui_path, "r") as f:
        return f.read()

@mcp.tool(meta={"ui": {"resourceUri": "ui://calculator/app"}})
def show_calculator() -> str:
    """Display an interactive calculator with buttons in the chat."""
    return "I've opened the interactive calculator for you."

if __name__ == "__main__":
    mcp.run()
