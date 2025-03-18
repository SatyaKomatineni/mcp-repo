#*************************************************
#* Import FastMCP from the fastmcp module
#* This is from the mcp Python SDK which is at: https://github.com/modelcontextprotocol/python-sdk
#*************************************************
# server.py
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Demo")

#*************************************************
#* Create Tools
#*************************************************

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def echo_tool(message: str) -> str:
    """Echo a message as a tool"""
    return f"Tool echo: {message}"


#*************************************************
#* Create resources
#* These are like documents and files returned by a web server
#*************************************************
@mcp.resource("hello://world")
def get_hello_message() -> str:
    """Return a simple hello world message."""
    return "Hello, World! This is my first MCP resource."
    
# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

@mcp.resource("echo://{message}")
def echo_resource(message: str) -> str:
    """Echo a message as a resource"""
    return f"Resource echo: {message}"

#*************************************************
# Prompts
#*************************************************

@mcp.prompt()
def echo_prompt(message: str) -> str:
    """Create an echo prompt"""
    return f"Please process this message: {message}"


