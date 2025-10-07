from dotenv import load_dotenv
import os
import boto3
import json

# Load .env
load_dotenv()

bedrock = boto3.client(
    "bedrock",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)

def bedrock_llm_call(prompt: str) -> str:
    """
    Sends prompt to AWS Bedrock and returns output text.
    """
    response = bedrock.invoke_model(
        modelId="anthropic.claude-v2",  # or any Bedrock model
        contentType="application/json",
        body={
            "input": prompt,
            "temperature": 0.7,
            "max_tokens_to_sample": 500
        }
    )
    body = json.loads(response["body"].read())
    return body.get("outputText", str(body))


# Wrapper for Strands streaming interface
class BedrockModelWrapper:
    def __init__(self, llm_func):
        self.llm_func = llm_func

    def stream(self, messages, tool_specs=None, system_prompt=None):
        # Concatenate messages into a single prompt
        prompt = "\n".join([m["content"] for m in messages])
        yield self.llm_func(prompt)
