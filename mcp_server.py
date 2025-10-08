# # mcp_server.py
from mcp.server.fastmcp import FastMCP
from strands.tools import current_time
from datetime import datetime
import httpx

mcp = FastMCP("weather", stateless_http=True, host="localhost", port=8000)

# Example tool: calculator
@mcp.tool()
def calculator(expression: str) -> float:
    return eval(expression)

# Example tool: current time
@mcp.tool()
def current_time() -> str:
    return datetime.now().isoformat()

# Example tool: get weather from NWS API
@mcp.tool()
def get_weather(lat: float, lon: float) -> dict:
    url = f"https://api.weather.gov/points/{lat},{lon}/forecast"
    headers = {"User-Agent": "weather-app/1.0"}
    r = httpx.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    # Run MCP server
    mcp.run(transport="streamable-http")



