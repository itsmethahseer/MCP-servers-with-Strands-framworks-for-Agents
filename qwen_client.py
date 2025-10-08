from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.models.llamacpp import LlamaCppModel
from strands.tools.mcp.mcp_client import MCPClient


# 🔹 Step 1. Connect to Ollama running Llama 3.1
def load_llama_model():
    model = LlamaCppModel(
        base_url="http://localhost:11434",  # Ollama endpoint
        model_id="qwen3:8b",         # Your model tag from `curl /api/tags`
        params={
            "temperature": 0.7,
            "max_tokens": 500,
            "repeat_penalty": 1.1,
        },
    )
    return model

# 🔹 Step 2. Load the Llama model
llama_model = load_llama_model()

# 🔹 Step 3. Initialize MCP client
streamable_http_mcp_client = MCPClient(lambda: streamablehttp_client("http://localhost:8000/mcp"))

# 🔹 Step 4. Run the MCP context
with streamable_http_mcp_client:
    # Fetch all available tools from the MCP server
    tools = streamable_http_mcp_client.list_tools_sync()
    print(f"Loaded {len(tools)} tools from MCP server.")

    # Create the Strands agent with tools and model
    agent = Agent(model=llama_model, tools=tools)

    # 🔹 Step 5. Run the agent with a simple query
    response = agent("what is the current weather in new york with 40.7128° N, 74.0060° W as coordinates?")
    print("\n🤖 Agent Response:\n", response)
