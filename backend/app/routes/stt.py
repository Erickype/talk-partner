# app/routes/stt.py
from fastapi import APIRouter, UploadFile, File
from backend.app.services.stt_service import transcribe_audio
import os
import tempfile

router = APIRouter(prefix="/stt", tags=["Speech to Text"])

@router.post("/")
async def speech_to_text(audio: UploadFile = File(...)):
    """Transcribe uploaded audio (WAV, MP3, etc.) into text."""
    # Save temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name

    text = transcribe_audio(tmp_path)
    os.remove(tmp_path)
    return {"transcription": text}
