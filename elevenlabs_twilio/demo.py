# app.py
import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from elevenlabs import RealtimeUrlOptions, speech_to_text

# Load API key from environment
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
speech_to_text.api_key = ELEVENLABS_API_KEY

app = FastAPI()


@app.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    await websocket.accept()
    try:
        # Example live stream URL (can be replaced by client)
        stream_url = "https://npr-ice.streamguys1.com/live.mp3"

        # Connect to ElevenLabs Realtime transcription
        connection = await speech_to_text.realtime.connect(
            RealtimeUrlOptions(
                model_id="scribe_v2_realtime",
                url=stream_url,
                include_timestamps=True,
            )
        )

        async for message in connection:
            # message is a dict containing the transcript
            # Example: {'text': 'hello world', 'timestamps': [...]}
            text = message.get("text")
            if text:
                await websocket.send_text(text)

    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        await connection.close()