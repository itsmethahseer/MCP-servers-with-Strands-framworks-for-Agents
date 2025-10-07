from strands import Agent
from strands.models.openai import OpenAIModel
from strands_tools import calculator
import os
import dotenv
from dotenv import load_dotenv
load_dotenv()
openai_key = os.getenv("OPEN_AI_API_KEY")
def give_model():
    model = OpenAIModel(
        client_args={
            "api_key": openai_key,
        },
        # **model_config
        model_id="gpt-4o",
        params={
            "max_tokens": 1000,
            "temperature": 0.1,
        }
    )
    return model

# agent = Agent(model=model, tools=[calculator])
# response = agent("What is 2+2")
# print(response)