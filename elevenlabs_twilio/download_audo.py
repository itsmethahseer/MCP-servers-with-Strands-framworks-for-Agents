
import os
import requests
RECORDINGS_DIR = "recordings"
from dotenv import load_dotenv
load_dotenv()
os.makedirs(RECORDINGS_DIR, exist_ok=True)


def download_recording(conversation_id: str):

    api_key = os.getenv("elevenlabs_api_key")
    if not api_key:
        raise {"status_code": 500, "detail": "elevenlabs_api_key not configured"}

    url = f"https://api.elevenlabs.io/v1/convai/conversations/{conversation_id}/audio"
    headers = {"xi-api-key": api_key}

    response = requests.get(url, headers=headers, stream=True, timeout=30)
    print("response:", response.text)
    if response.status_code != 200:
        return {"error": f"Failed to download recording for conversation {conversation_id}"}

    file_path = os.path.join(RECORDINGS_DIR, f"{conversation_id}.mp3")

    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    return {
        "conversation_id": conversation_id,
        "file_path": file_path
    }


if __name__ == "__main__":
    conversation_id = "conv_6201khb742dqfqr9ymhpvqddpccf"
    result = download_recording(conversation_id)
    print(result)