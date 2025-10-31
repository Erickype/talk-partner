# app/routes/talk.py
from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.services.ai_service import generate_reply
from backend.app.services.tts_service import generate_tts
from fastapi.responses import FileResponse
import os

router = APIRouter(prefix="/talk", tags=["Talk"])

class TalkRequest(BaseModel):
    message: str  # User's message text

@router.post("/")
def talk(req: TalkRequest):
    """AI conversation: Generate reply + voice."""
    # 1. Get AI reply from Phi-3
    reply_text = generate_reply(req.message)

    # 2. Convert AI reply to speech
    audio_path = generate_tts(reply_text)

    # 3. Return both text and voice
    return {
        "reply": reply_text,
        "audio_file": os.path.basename(audio_path)
    }
