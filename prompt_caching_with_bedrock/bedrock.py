from strands import Agent
from strands.models import Bedrock
from strands import tool

@tool
def get_user_profile(user_id: str) -> dict:
    return {
        "user_id": user_id,
        "tier": "premium",
        "region": "IN"
    }

@tool
def fetch_order_status(order_id: str) -> dict:
    return {
        "order_id": order_id,
        "status": "Delivered",
        "date": "2025-01-02"
    }

STATIC_AGENT_PROMPT = """
You are a reliable enterprise assistant.

### Conversation Flow
1. Understand user intent
2. Decide if a tool is needed
3. Call the tool if required
4. Respond clearly and concisely

### Rules
- Never hallucinate tool outputs
- Ask clarifying questions only if required
- Prefer tools over assumptions
- Output JSON only when explicitly asked

### Input Details
- User may ask about orders, profile, or general info
"""



model = Bedrock(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
    region="us-east-1",
    temperature=0,
    max_tokens=512
)

agent = Agent(
    model=model,
    system_prompt=STATIC_AGENT_PROMPT,   # 🔥 Cached once
    tools=[get_user_profile, fetch_order_status]
)


def infer_with_strands(dynamic_user_query: str):
    response = agent.run(dynamic_user_query)
    return response

print("=== Example 1: User Profile Query ===")
user_query_1 = "Can you provide the profile details for user ID U12345?"
response_1 = infer_with_strands(user_query_1)
print(response_1)