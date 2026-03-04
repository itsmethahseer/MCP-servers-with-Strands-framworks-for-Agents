import json
import requests
import boto3
import logging
import os
from dotenv import load_dotenv
load_dotenv()
from concurrent.futures import ThreadPoolExecutor
from botocore.exceptions import ClientError
connect = boto3.client("connect", 
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
)
executor = ThreadPoolExecutor(max_workers=1)
instance_id = "65e33559-a7fe-407b-b447-c82914f35738"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
def describe_contact(contact_data):
    contact_id = contact_data["contact_id"]
    logger.info(f"describe_contact {contact_id}")

    try:
        resp = connect.describe_contact(InstanceId=instance_id, ContactId=contact_id)
        logger.info("describe contact response:",resp)
        print("DescribeContact response:", resp)
        return {"statusCode": 200, "body": resp}
    except ClientError as e:
        print("Error calling DescribeContact:", e)
        return {"statusCode": 500, "body": {"error": str(e)}}

print(describe_contact({"contact_id": "e582a49c-f6a0-439b-95b3-5c133467a0d7"}))