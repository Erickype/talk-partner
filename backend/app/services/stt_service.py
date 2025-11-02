import os
from faster_whisper import WhisperModel

model_size = "distil-large-v3"

# or run on CPU with INT8
model = WhisperModel(model_size, device="cpu", compute_type="int8")

def transcribe_audio(file_path: str) -> str:
    segments, info = model.transcribe(file_path, beam_size=5, language="en", condition_on_previous_text=False)
    transcription = " ".join([segment.text.strip() for segment in segments])
    print(f"🗣️ Transcribed: {transcription}")
    return transcription
