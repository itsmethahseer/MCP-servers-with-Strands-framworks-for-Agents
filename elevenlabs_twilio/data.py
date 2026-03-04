
import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()
def fetch_conversation_details(conversation_id: str) -> dict:
    """
    Fetch conversation details from ElevenLabs and extract:
    - Tool parameters (store_verification_data)
    - Charging usage
    - Summary
    """

    api_key = os.getenv("ELEVENLABS_API_KEY")

    url = f"https://api.elevenlabs.io/v1/convai/conversations/{conversation_id}"

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers, timeout=15)

    if response.status_code != 200:
        raise Exception(f"ElevenLabs API Error: {response.text}")

    conversation_data = response.json()
    print(json.dumps(conversation_data, indent=2))
    # ----------------------------
    # 1️⃣ Extract tool parameters
    # ----------------------------
    verification_data = None

    messages = conversation_data.get("messages", [])
    for message in messages:
        tool_calls = message.get("tool_calls", [])
        for tool in tool_calls:
            if tool.get("tool_name") == "store_verification_data":
                params_string = tool.get("params_as_json")
                if params_string:
                    try:
                        verification_data = json.loads(params_string)
                    except json.JSONDecodeError:
                        verification_data = None

    # ----------------------------
    # 2️⃣ Extract usage / cost
    # ----------------------------
    charging = conversation_data.get("charging", {})
    llm_usage = charging.get("llm_usage", {})
    irreversible = llm_usage.get("irreversible_generation", {})
    model_usage = irreversible.get("model_usage", {})

    total_cost = 0.0

    for model, usage in model_usage.items():
        input_price = usage.get("input", {}).get("price", 0)
        output_price = usage.get("output_total", {}).get("price", 0)
        total_cost += input_price + output_price

    # ----------------------------
    # 3️⃣ Extract summary
    # ----------------------------
    summary = conversation_data.get("analysis", {}).get("summary", "")

    return {
        "conversation_id": conversation_id,
        "agent_id": conversation_data.get("agent_id"),
        "status": conversation_data.get("status"),
        "verification_data": verification_data,
        "usage": {
            "tier": charging.get("tier"),
            "total_cost": total_cost,
            "model_breakdown": model_usage
        },
        "summary": summary,
        "raw": conversation_data
    }

if __name__ == "__main__":
    # conversation_id = "conv_5001khap5d5zeajvjb634tdjkt18" #for cut the call just after attend.
    conversation_id = "conv_5201kjpmgjghe3fshmz3xxjtpwa1"
    details = fetch_conversation_details(conversation_id)
    with open("conversation_details_new.json", "w") as f:
        json.dump(details, f, indent=2)
    print(json.dumps(details, indent=2))