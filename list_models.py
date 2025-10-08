import boto3
import os
from dotenv import load_dotenv
load_dotenv()
bedrock = boto3.client('bedrock')
response = bedrock.list_foundation_models()
for model in response['modelSummaries']:
    print(f"Model ID: {model['modelId']}, Name: {model['modelName']}")
