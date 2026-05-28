import math
import os
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP(
    "calculator",
    instructions="A basic calculator server that supports standard arithmetic operations and provides access to calculation history and mathematical constants through resources."
)

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers."""
    result = a + b
    return result

@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    result = a - b
    return result

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    result = a * b
    return result

@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    result = a / b
    return result

@mcp.resource("calc://constants")
def get_constants() -> dict[str, float]:
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
