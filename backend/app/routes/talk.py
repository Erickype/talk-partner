# app/routes/talk.py
from fastapi import APIRouter, UploadFile, File
from backend.app.services.ai_service import generate_reply, clean_model_output
from backend.app.services.tts_service import generate_tts
from backend.app.services.stt_service import transcribe_audio
import tempfile
import os

router = APIRouter(prefix="/talk", tags=["Talk"])


@router.post("/voice")
async def talk_voice(audio: UploadFile = File(...)):
    """
    Full conversation flow:
    1. Convert user's voice → text (STT)
    2. Generate AI reply with Phi-3
    3. Convert AI reply → voice (TTS)
    4. Return transcription, reply, and audio file
    """
    # --- Step 1: Save uploaded audio temporarily ---
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name

    try:
        # --- Step 2: Transcribe user speech ---
        print("🎤 Transcribing user voice...")
        user_text = transcribe_audio(tmp_path)
        print(f"🗣️ User said: {user_text}")

        # --- Step 3: Generate AI reply ---
        print("💬 Generating AI reply...")
        reply_raw = generate_reply(user_text)
        reply_text = clean_model_output(reply_raw)
        print(f"🤖 AI replied: {reply_text}")

        # --- Step 4: Convert reply to voice ---
        print("🔊 Generating TTS audio...")
        audio_path = generate_tts(reply_text)
        print(f"✅ Audio generated at: {audio_path}")

    finally:
        # Always clean up temporal path
        os.remove(tmp_path)

    # --- Step 5: Return everything ---
    return {
        "user_text": user_text,
        "reply_text": reply_text,
        "audio_file": os.path.basename(audio_path)
    }
