from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.tools.mcp.mcp_client import MCPClient
from dotenv import load_dotenv
import os
load_dotenv()
streamable_http_mcp_client = MCPClient(lambda: streamablehttp_client("http://localhost:8000/mcp"))

with streamable_http_mcp_client:
    # Get the tools from the MCP server
    tools = streamable_http_mcp_client.list_tools_sync()

    # Create an agent with these tools
    agent = Agent(tools=tools)
    
    # ✨ THIS IS WHAT'S MISSING ✨
    # You need to actually invoke the agent with a task
    response = agent("who is the president of india?")  # or agent.chat(), agent.execute(), etc.
    print(response)