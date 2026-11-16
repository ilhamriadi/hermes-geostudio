"""MCP Server entrypoint for Hermes GeoStudio."""
import sys
import os

# Ensure src is in path
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from mcp.server.fastmcp import FastMCP
from .tools import mcp
from .gee.client import check_connection, is_initialized

def main():
    """Main entry point for the MCP server."""
    print("Starting Hermes GeoStudio MCP Server...", file=sys.stderr)

    # Pre-flight checks
    result = check_connection()
    if result.get("success"):
        print(f"GEE Connection OK ({result.get('method')})", file=sys.stderr)
    else:
        print(f"GEE Warning: {result.get('error', 'not connected')}", file=sys.stderr)
        print("Run gee_authenticate tool first, or set GEE_CREDENTIALS_FILE env var.", file=sys.stderr)

    # Run the MCP server via stdio
    mcp.run(transport="stdio")

def register_tools():
    """Register tools with Hermes Agent (for plugin mode)."""
    from .tools import mcp
    return mcp.tool_names

if __name__ == "__main__":
    main()
