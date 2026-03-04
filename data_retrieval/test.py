import boto3
import os
from dotenv import load_dotenv
load_dotenv()
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
)
bucket = "alpha-amazon-connect-call"
instance_id = "65e33559-a7fe-407b-b447-c82914f35738"


{'recording_file_name': 'connect://recording/601a423b-26c7-4af0-b0c4-0054aadd1949', 'transcript_file_name': 'connect://transcript/601a423b-26c7-4af0-b0c4-0054aadd1949'}


def parse_connect_ref(ref):
    # ref = connect://recording/<contact_id>
    parts = ref.replace("connect://", "").split("/")
    return {
        "type": parts[0],       # recording | transcript
        "contact_id": parts[1]
    }
def find_call_recording(s3, bucket, instance_id, contact_id):
    prefix = f"{instance_id}/CallRecordings/"
    paginator = s3.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            if contact_id in obj["Key"]:
                return obj["Key"]

    return None
def find_transcript(s3, bucket, instance_id, contact_id):
    prefix = f"{instance_id}/Analysis/Voice/"
    paginator = s3.get_paginator("list_objects_v2")
    print("Searching for transcript with prefix:", prefix)
    print("paginator:", paginator)
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            if contact_id in obj["Key"]:
                return obj["Key"]

    return None


key = find_call_recording(s3, bucket, instance_id, contact_id="e582a49c-f6a0-439b-95b3-5c133467a0d7")
key2 = find_transcript(s3, bucket, instance_id, contact_id="e582a49c-f6a0-439b-95b3-5c133467a0d7")
print("Recording Key:", key)
print("Transcript Key:", key2)
if key:
    # ensure s3 client exists
    try:
        s3
    except NameError:
        s3 = boto3.client("s3")

    os.makedirs("/tmp", exist_ok=True)
    s3.download_file(bucket, key, "/tmp/recording.wav")
if key2:
    # ensure s3 client exists
    try:
        s3
    except NameError:
        s3 = boto3.client("s3")

    os.makedirs("/tmp", exist_ok=True)
    s3.download_file(bucket, key2, "/tmp/transcript.json")
