from fastapi import FastAPI, Request
from fastapi.responses import Response,FileResponse
from twilio.twiml.voice_response import VoiceResponse
from elevenlabs.client import ElevenLabs
import boto3
import os
from datetime import datetime
import uvicorn
from dotenv import load_dotenv
load_dotenv()
app = FastAPI()

# Initialize ElevenLabs client
client = ElevenLabs(api_key=os.getenv("elevenlabs_api_key"))

# Create local audio directory
AUDIO_DIR = "audio_files"
os.makedirs(AUDIO_DIR, exist_ok=True)
@app.post('/voice')
async def voice(request: Request):
    form_data = await request.form()
    
    response = VoiceResponse()
    
    # Generate audio using ElevenLabs SDK
    audio = client.text_to_speech.convert(
        voice_id=os.getenv("VOICE_ID"),  # Rachel
        text="Hello! This is a call powered by ElevenLabs and Twilio.",
        model_id=os.getenv("MODEL_ID")
    )
    
    # Save audio locally
    filename = f"welcome_{datetime.now().timestamp()}.mp3"
    file_path = os.path.join(AUDIO_DIR, filename)
    
    with open(file_path, 'wb') as f:
        for chunk in audio:
            f.write(chunk)
    
    print(f"✅ Audio saved to: {file_path}")
    
    # Get the base URL from the request
    base_url = str(request.base_url).rstrip('/')
    audio_url = f"{base_url}/audio/{filename}"
    
    # Play in Twilio
    response.play(audio_url)
    
    return Response(content=str(response), media_type='text/xml')

@app.get('/audio/{filename}')
async def serve_audio(filename: str):
    """Serve audio files"""
    file_path = os.path.join(AUDIO_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='audio/mpeg')
    return {"error": "File not found"}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)