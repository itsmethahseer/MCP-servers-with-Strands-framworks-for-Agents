import requests
import json

# ==============================
# CONFIG
# ==============================
BASE_URL = "http://localhost:8000"  
# change to your server URL if deployed
# e.g. "https://yourdomain.com"

CONVERSATION_ID = "conv_2501kh5qe7tbe45bvybq31kkgcak"
import json

def extract_store_verification_data(conversation_data):
    messages = [message for message in conversation_data]
    for message in messages:
        print("message:", message)
        tool_calls = message.get("tool_calls", [])

        for tool in tool_calls:
            if tool.get("tool_name") == "store_verification_data":

                params_string = tool.get("params_as_json")

                if not params_string:
                    continue

                try:
                    parsed_data = json.loads(params_string)
                    return parsed_data
                except json.JSONDecodeError:
                    print("Failed to parse params_as_json")
                    return None

    return None



# ==============================
# CALL API
# ==============================
def test_debug_conversation(conversation_id):
    url = f"{BASE_URL}/non-clinical-agent/debug-conversation/{conversation_id}"
    
    try:
        print(f"\n🔍 Testing: {url}\n")
        
        response = requests.get(url, timeout=15)

        print("Status Code:", response.status_code)
        print("=" * 80)

        if response.status_code == 200:
            data = response.json()
            
            print("Conversation ID:", data.get("conversation_id"))
            print("Status:", data.get("status"))
            print("Agent ID:", data.get("agent_id"))
            print("Tool Calls Found:", data.get("tool_calls_found"))
            
            # Extract verification data if available
            # verification_data = extract_store_verification_data(data)
            # print("verification_data:", verification_data)
            # if verification_data:
            #     print("\n✅ Found Verification Data:")
            #     for k, v in verification_data.items():
            #         print(f"   {k}: {v}")
            
            print("\n--- Initial Metadata ---")
            print(json.dumps(data.get("initial_metadata"), indent=2))
            
            print("\n--- Dynamic Variables ---")
            print(json.dumps(data.get("dynamic_variables"), indent=2))
            print("conversation_data:", data.get("conversation_data"))
            # print("\n--- Summary ---")
            # print(data.get("summary"))
            
            # print("\n--- Transcript Excerpt ---")
            # value = data.get("transcript_excerpt")
            # value = f"{value}"
            # fixed = value.replace("'", '"') if value else ""
            # print(fixed)
            
        else:
            print("Error Response:")
            print(response.text)

    except Exception as e:
        print("❌ Request Failed:", str(e))


if __name__ == "__main__":
    test_debug_conversation(CONVERSATION_ID)
