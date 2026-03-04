import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from typing import List
from dotenv import load_dotenv
from .stt_service import stream_audio_to_elevenlabs

load_dotenv()

app = FastAPI()

# --------------------------------------
#  WebSocket Manager (for UI clients)
# --------------------------------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send(self, message: str):
        for conn in self.active_connections:
            try:
                await conn.send_text(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws/transcripts/{call_id}")
async def websocket_endpoint(websocket: WebSocket, call_id: str):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --------------------------------------
#  REST Endpoint to Start Transcription
# --------------------------------------
@app.post("/transcribe/start")
async def start_transcription(call_id: str, background_tasks: BackgroundTasks):
    """
    Trigger realtime transcription.
    """
    background_tasks.add_task(stream_audio_to_elevenlabs, manager, call_id)
    return {"status": "started", "call_id": call_id}