#!/usr/bin/env python3
"""Simple test MCP server"""
from mcp.server.fastmcp import FastMCP

server = FastMCP('test-server')

@server.tool()
def hello(name: str = "World") -> str:
    """Say hello"""
    return f"Hello {name}!"

if __name__ == '__main__':
    print("🧪 Starting test MCP server on port 8765...")
    server.run()