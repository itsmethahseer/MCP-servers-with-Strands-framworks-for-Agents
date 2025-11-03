from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import asyncio
from livekit.agents import JobContext, AgentSession, WorkerOptions
from livekit import agents
from livekit.plugins import google, silero, elevenlabs

# Define your Agent class (using Gemini)
class Assistant(agents.Agent):
    def __init__(self) -> None:
        llm = google.LLM(model="gemini-2.0-flash", temperature=0.7,api_key="AIzaSyD-pT2WudsPuYm1Lc3lY6J86S8a_jc2G_o")
        stt = google.STT()
        tts = elevenlabs.TTS()
        vad = silero.VAD.load()
        super().__init__(
            instructions="You are a helpful voice assistant via voice.",
            stt=stt,
            llm=llm,
            tts=tts,
            vad=vad,
        )

# Pydantic payload schema for API request
class StartAgentPayload(BaseModel):
    room_name: str
    user_identity: str
    # add other fields as needed

app = FastAPI()

@app.post("/start_agent")
async def start_agent(payload: StartAgentPayload, request: Request):
    try:
        # Note: Here we start a session for the agent and return info to caller
        session = AgentSession()
        # You might want to run this in background so the API returns quickly
        asyncio.create_task(session.start(
            room=payload.room_name,
            agent=Assistant()
        ))
        return {"status": "started", "room": payload.room_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
