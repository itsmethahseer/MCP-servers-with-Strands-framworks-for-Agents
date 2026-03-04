import boto3
import json
import time
import logging
from dotenv import load_dotenv

# ---------------------------
# Setup & Debug Logging
# ---------------------------

load_dotenv()

# Enable low-level AWS debug logs
boto3.set_stream_logger("botocore", level=logging.DEBUG)

bedrock = boto3.client(
    "bedrock-runtime",
    region_name="us-east-1"
)

MODEL_ID = "us.anthropic.claude-sonnet-4-20250514-v1:0"

# ---------------------------
# Tool Implementations
# ---------------------------

def top_song(sign: str):
    return {
        "song": "Bohemian Rhapsody",
        "artist": "Queen",
        "station": sign
    }

def weather_info(city: str):
    return {
        "city": city,
        "weather": "Sunny",
        "temperature": "30°C"
    }

TOOL_FUNCTIONS = {
    "top_song": top_song,
    "weather_info": weather_info
}

# ---------------------------
# Cached System Prompt
# ---------------------------

SYSTEM_PROMPT = [
    {
        "text": (
            "You are a helpful AI agent. "
            "You may call tools when required. "
            "Respond concisely and accurately."
        )
    },
    {
        # 🔥 Cached once per model/region
        "cachePoint": {"type": "default"}
    }
]

# ---------------------------
# Cached Tool Definitions
# ---------------------------

TOOL_CONFIG = {
    "tools": [
        {
            "toolSpec": {
                "name": "top_song",
                "description": "Get the most popular song from a radio station",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "sign": {"type": "string"}
                        },
                        "required": ["sign"]
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "weather_info",
                "description": "Get current weather of a city",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "city": {"type": "string"}
                        },
                        "required": ["city"]
                    }
                }
            }
        },
        {
            # 🔥 Cache tools schema
            "cachePoint": {"type": "default"}
        }
    ]
}

# ---------------------------
# Agent Converse Call
# ---------------------------

def run_agent(user_input, conversation_history):
    messages = conversation_history + [
        {
            "role": "user",
            "content": [
                {"text": user_input}
            ]
        }
    ]

    start = time.time()

    response = bedrock.converse(
        modelId=MODEL_ID,
        system=SYSTEM_PROMPT,
        messages=messages,
        toolConfig=TOOL_CONFIG
    )

    latency = time.time() - start
    print(f"\n⏱️ Converse latency: {latency:.3f}s")

    return response

# ---------------------------
# Tool Routing (Strands-Style)
# ---------------------------

def handle_response(response, conversation_history):
    output_message = response["output"]["message"]
    conversation_history.append(output_message)

    for block in output_message["content"]:
        if "toolUse" in block:
            tool_name = block["toolUse"]["name"]
            tool_args = block["toolUse"]["input"]
            tool_id = block["toolUse"]["toolUseId"]

            print(f"\n🔧 Tool invoked: {tool_name}")
            print(f"📥 Tool args: {tool_args}")

            tool_result = TOOL_FUNCTIONS[tool_name](**tool_args)

            tool_message = {
                "role": "user",
                "content": [
                    {
                        "toolResult": {
                            "toolUseId": tool_id,
                            "content": [{"json": tool_result}]
                        }
                    }
                ]
            }

            conversation_history.append(tool_message)

            # Follow-up call after tool result
            start = time.time()

            followup = bedrock.converse(
                modelId=MODEL_ID,
                system=SYSTEM_PROMPT,
                messages=conversation_history,
                toolConfig=TOOL_CONFIG
            )

            latency = time.time() - start
            print(f"⏱️ Follow-up latency: {latency:.3f}s")

            return followup, conversation_history

    return response, conversation_history

# ---------------------------
# Example Run
# ---------------------------

if __name__ == "__main__":
    history = []

    print("\n====== FIRST CALL (CACHE MISS EXPECTED) ======")
    response = run_agent("What is the most popular song on WZPZ?", history)
    response, history = handle_response(response, history)

    print(json.dumps(response["output"]["message"], indent=2))

    print("\n====== SECOND CALL (CACHE HIT EXPECTED) ======")
    response = run_agent("What is the most popular song on WZPZ?", history)
    response, history = handle_response(response, history)

    print(json.dumps(response["output"]["message"], indent=2))
