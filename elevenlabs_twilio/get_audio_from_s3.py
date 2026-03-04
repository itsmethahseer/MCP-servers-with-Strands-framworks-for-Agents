import os
import json
import logging
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger(__name__)
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

def get_audio_from_s3(conversation_id: str) -> dict:
    try:
        bucket_name = os.getenv("AWS_S3_BUCKET_NAME")
        region = os.getenv("AWS_REGION")
        s3_key = f"call-recordings/{conversation_id}.mp3"

        s3 = boto3.client("s3", region_name=region, aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

        # Check if object exists
        s3.head_object(Bucket=bucket_name, Key=s3_key)

        # Generate presigned URL (valid for 1 hour)
        presigned_url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": s3_key},
            ExpiresIn=3600
        )

        return {
            "bucket": bucket_name,
            "key": s3_key,
            "permanent_url": f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_key}",
            "presigned_url": presigned_url
        }

    except s3.exceptions.NoSuchKey:
        logger.warning(f"Audio not found in S3 for {conversation_id}")
        return {}
    except Exception as e:
        logger.error(f"Failed to get audio from S3 for {conversation_id}: {e}")
        return {}
    
if __name__ == "__main__":
    conversation_id = "conv_5101kjpykg8qf968x1jk707htzrm"
    audio_info = get_audio_from_s3(conversation_id)
    print(json.dumps(audio_info, indent=2))