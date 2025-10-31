# app/routes/tts.py
from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.services import tts_service

router = APIRouter(prefix="/tts", tags=["TTS"])

class TTSRequest(BaseModel):
    text: str

@router.post("/")
def text_to_speech(req: TTSRequest):
    """Convert text to speech and return file path."""
    audio_path = tts_service.generate_tts(req.text)
    return {"audio_file": audio_path}
