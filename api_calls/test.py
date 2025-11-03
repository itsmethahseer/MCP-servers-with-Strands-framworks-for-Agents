import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()
url = "https://alpha-external-api.ebsworx.dev/api/agent-invoke/"

# Example payload — replace this with your actual data
payload = {
    "agent": "customer_support",
    "messages": [
        {"role": "user", "content": "Hello, I need help with my order."}
    ]
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('TOKEN')}"
}

print("=== REQUEST PAYLOAD ===")
print(json.dumps(payload, indent=4))

response = requests.post(url, headers=headers, json=payload)

print("\n=== RESPONSE STATUS ===")
print(response.status_code)

print("\n=== RESPONSE BODY ===")
try:
    print(json.dumps(response.json(), indent=4))
except Exception:
    print(response.text)
