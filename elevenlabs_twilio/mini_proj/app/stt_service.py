import os
import asyncio
import base64
import json
import websockets
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# URL for server-side realtime transcription
ELEVEN_WS_URL = (
    "wss://api.elevenlabs.io/v1/speech-to-text/realtime"
    "?model_id=scribe_v2_realtime"
)

async def audio_source_generator():
    """
    Replace this generator with your actual source:
    - Twilio Media Streams
    - WebRTC mic stream
    - File/stream URL
    Audio must be PCM data (e.g., 16kHz PCM_16).
    """
    # Example: send silence or sample audio
    for _ in range(100):
        await asyncio.sleep(0.1)
        yield b"\x00" * 3200  # ~0.1s of PCM silence

async def _run_transcription(manager, call_id):
    headers = {"xi-api-key": ELEVENLABS_API_KEY}
    async with websockets.connect(ELEVEN_WS_URL, additional_headers=headers) as ws:

        # Session handshake
        handshake = await ws.recv()
        print("Session started:", handshake)

        async def send_audio():
            async for pcm_chunk in audio_source_generator():
                # Send audio chunk
                encoded_chunk = base64.b64encode(pcm_chunk).decode("ascii")
                message = {
                    "message_type": "input_audio_chunk",
                    "audio_base_64": encoded_chunk,
                    "commit": False,
                }
                await ws.send(json.dumps(message))

            # Signal end of audio
            await ws.send(json.dumps({
                "message_type": "input_audio_chunk",
                "audio_base_64": "",
                "commit": True
            }))

        async def receive_transcripts():
            try:
                while True:
                    raw = await ws.recv()
                    event = json.loads(raw)

                    # Partial
                    if event.get("message_type") == "partial_transcript":
                        text = event.get("text", "")
                        # Send to all UI clients
                        await manager.send(f"{call_id}:{text}")

                    # Final
                    elif event.get("message_type") == "committed_transcript":
                        final_text = event.get("text", "")
                        await manager.send(f"{call_id} (final): {final_text}")

            except websockets.exceptions.ConnectionClosedOK:
                print("Session closed cleanly.")

        await asyncio.gather(send_audio(), receive_transcripts())

def stream_audio_to_elevenlabs(manager, call_id: str):
    asyncio.run(_run_transcription(manager, call_id))