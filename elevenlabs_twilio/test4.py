
import os
import requests
import boto3
from dotenv import load_dotenv
load_dotenv()

def upload_conversation_audio_to_s3(conversation_id: str) -> dict:
    api_key = os.getenv("ELEVENLABS_API_KEY")
    bucket_name = os.getenv("AWS_S3_BUCKET_NAME")
    region = os.getenv("AWS_REGION")
    url = f"https://api.elevenlabs.io/v1/convai/conversations/{conversation_id}/audio"
    headers = {"xi-api-key": api_key}

    response = requests.get(url, headers=headers, stream=True, timeout=30)
    if response.status_code != 200:
        raise Exception("Audio fetch failed")

    s3_key = f"call-recordings/{conversation_id}.mp3"

    s3 = boto3.client("s3")

    s3.upload_fileobj(
        response.raw,
        bucket_name,
        s3_key,
        ExtraArgs={"ContentType": "audio/mpeg"},
    )

    return {
        "bucket": bucket_name,
        "key": s3_key,
        "permanent_url": f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_key}"
    }

if __name__ == "__main__":
    conversation_id = "conv_7701khny88m5fb9sgf3xfq7sbaea"
    result = upload_conversation_audio_to_s3(conversation_id)
    print(result)

# import asyncio
# import json
# import base64
# import os
# import websockets
# from dotenv import load_dotenv
# load_dotenv()
# import os
# # Your ElevenLabs API key
# ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# # WebSocket endpoint for realtime transcription
# WS_ENDPOINT = "wss://api.elevenlabs.io/v1/speech-to-text/realtime?model_id=scribe_v2_realtime"

# async def transcribe_live_call(audio_stream_generator):
#     """
#     Connect to ElevenLabs realtime STT API and stream audio.
    
#     audio_stream_generator: async generator yielding raw PCM audio bytes (e.g., 16kHz, PCM_16).
#     """

#     # WebSocket headers with API key
#     headers = {
#         "xi-api-key": ELEVENLABS_API_KEY
#     }

#     async with websockets.connect(WS_ENDPOINT, additional_headers=headers) as ws:
#         # Wait for initial handshake from ElevenLabs
#         handshake = await ws.recv()
#         print("Session started:", handshake)

#         async def send_audio():
#             # Continuously send audio as messages
#             async for pcm_chunk in audio_stream_generator():
#                 b64_audio = base64.b64encode(pcm_chunk).decode("ascii")
#                 await ws.send(json.dumps({
#                     "message_type": "input_audio_chunk",
#                     "audio_base_64": b64_audio,
#                     "commit": False  # Set to True if final segment
#                 }))
#             # Send final commit signal
#             await ws.send(json.dumps({
#                 "message_type": "input_audio_chunk",
#                 "audio_base_64": "",
#                 "commit": True
#             }))

#         async def receive_events(ws):
#             try:
#                 while True:
#                     message = await ws.recv()
#                     data = json.loads(message)

#                     if data.get("message_type") == "partial_transcript":
#                         print("Partial:", data["text"])
#                     elif data.get("message_type") == "committed_transcript":
#                         print("Final:", data["text"])
#             except websockets.exceptions.ConnectionClosedOK:
#                 print("Connection closed cleanly by server (likely due to inactivity).")

#         # Run send and receive loops concurrently
#         await asyncio.gather(send_audio(), receive_events(ws))

# # Example: mock generator (replace with real call audio frames)
# async def mock_audio():
#     for _ in range(70):
#         yield b"\x00" * 3200  # ~100ms PCM silence
#         await asyncio.sleep(0.1)

# if __name__ == "__main__":
#     asyncio.run(transcribe_live_call(mock_audio))