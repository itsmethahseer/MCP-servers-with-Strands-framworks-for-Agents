import os
from anthropic import Anthropic
from dotenv import load_dotenv
load_dotenv()

client = Anthropic(
    # Defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

message = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Explain Machine learning in details"}
    ]
)
print(message.content[0].text)
