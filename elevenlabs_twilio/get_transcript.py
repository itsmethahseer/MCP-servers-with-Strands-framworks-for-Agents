import os
import requests
from dotenv import load_dotenv
load_dotenv()
def fetch_conversation_transcript(conversation_id: str) -> dict:
    """
    Fetch transcript for a given ElevenLabs conversation ID.

    Returns:
        {
            "conversation_id": str,
            "status": str,
            "transcript": list,
            "full_text": str
        }
    """

    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise {"status_code": 500, "detail": "elevenlabs_api_key not configured"}

    url = f"https://api.elevenlabs.io/v1/convai/conversations/{conversation_id}"

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers, timeout=20)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch transcript: {response.text}")

    data = response.json()

    transcript = data.get("transcript", [])

    # Flatten transcript into readable text
    lines = []
    for entry in transcript:
        role = entry.get("role", "unknown")
        message = entry.get("message", "")
        lines.append(f"{role}: {message}")

    full_text = "\n".join(lines)

    return {
        "conversation_id": conversation_id,
        "status": data.get("status"),
        "transcript": transcript,
        "full_text": full_text
    }

if __name__ == "__main__":
    conversation_id = "conv_6201khb742dqfqr9ymhpvqddpccf"
    result = fetch_conversation_transcript(conversation_id)
    print(result)
    