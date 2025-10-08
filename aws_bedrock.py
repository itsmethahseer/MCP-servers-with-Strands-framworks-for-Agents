from strands import Agent
from strands.models import BedrockModel
import boto3
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()
# Access them in variables
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_DEFAULT_REGION")
bedrock_model_id = os.getenv("BEDROCK_MODEL_ID")

def get_bedrock_model():
# Create a custom boto3 session
    session = boto3.Session(
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        aws_session_token=aws_region,  # If using temporary credentials
        region_name='us-west-2'
    )
    # Create a Bedrock model instance
    bedrock_model = BedrockModel(
        model_id=bedrock_model_id,
        temperature=0.3,
        top_p=0.8,
        max_tokens=20,
        boto3_session=session
    )
    return bedrock_model

 