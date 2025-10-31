# app/services/tts_service.py
import os
import sys
import uuid
import soundfile as sf

# Add neutts-air to Python path
vendor_path = os.path.join(os.path.dirname(__file__), 'vendor', 'neutts-air')
if vendor_path not in sys.path:
    sys.path.insert(0, vendor_path)

from neuttsair.neutts import NeuTTSAir

REF_AUDIO = "ref/voice.mp3"
REF_TEXT = "ref/voice.txt"
OUTPUT_DIR = "output_audio"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Load model once ---
print("🔊 Loading custom voice...")
tts_model = NeuTTSAir(
    backbone_repo="neuphonic/neutts-air",
    backbone_device="cpu",
    codec_repo="neuphonic/neucodec",
    codec_device="cpu"
)

# Encode reference audio
ref_codes = tts_model.encode_reference(REF_AUDIO)
ref_text = open(REF_TEXT, "r", encoding="utf-8").read().strip()
print("✅ Voice loaded successfully!")

def generate_tts(text: str) -> str:
    """Generate a WAV file from text using neutts-air."""
    file_id = uuid.uuid4().hex[:8]
    output_path = os.path.join(OUTPUT_DIR, f"tts_{file_id}.wav")

    print(f"🎙️ Generating speech for: {text}")
    
    # Generate audio
    audio = tts_model.infer(text=text, ref_codes=ref_codes, ref_text=ref_text)
    
    # Save to WAV file
    sf.write(output_path, audio, tts_model.sample_rate)
    print(f"✅ Saved to: {output_path}")

    return output_path