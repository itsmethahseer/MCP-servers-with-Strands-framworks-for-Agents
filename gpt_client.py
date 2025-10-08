from strands import Agent
from strands.models.openai import OpenAIModel
from strands_tools import calculator
import os
from dotenv import load_dotenv
load_dotenv()
def model_giving():
    model = OpenAIModel(
        client_args={
            "api_key": os.getenv("OPENAI_API_KEY"),
        },
        # **model_config
        model_id="gpt-4o",
        params={
            "max_tokens": 20,
            "temperature": 0.7,
        }
    )
    return model



