# app/routes/talk.py
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
from backend.app.services.ai_service import generate_reply, clean_model_output
from backend.app.services.tts_service import stream_tts
from backend.app.services.stt_service import transcribe_audio
import tempfile
import os
import io
import wave

router = APIRouter(prefix="/talk", tags=["Talk"])


@router.post("/voice")
async def talk_voice(audio: UploadFile = File(...)):
    """
    Full conversation flow with streaming TTS:
    1. Convert user's voice → text (STT)
    2. Generate AI reply with Phi-3
    3. Stream AI reply as voice (TTS)
    4. Return audio stream with metadata in headers
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
        print(f"🤖 AI replied: {reply_raw}")
        print(f"🤖 Cleaned up: {reply_text}")

    finally:
        # Always clean up temporal path
        os.remove(tmp_path)

    # --- Step 4: Stream TTS audio ---
    print("🔊 Streaming TTS audio...")
    
    # --- Step 5: Return streaming response with metadata in headers ---
    return StreamingResponse(
        stream_tts(reply_text),
        media_type="audio/raw",
        headers={
            "X-User-Text": user_text,
            "X-Reply-Text": reply_text,
            "Content-Disposition": "inline; filename=response.wav"
        }
    )
