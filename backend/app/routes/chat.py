# app/routes/chat.py
from fastapi import APIRouter
from pydantic import BaseModel
import requests

router = APIRouter(prefix="/chat", tags=["Chat"])

OLLAMA_URL = "http://localhost:11434/api/generate"  # Ollama API endpoint

class ChatRequest(BaseModel):
    message: str

@router.post("/")
def chat(req: ChatRequest):
    """Send message to local Phi-3 model and return AI reply."""
    payload = {
        "model": "phi3",
        "prompt": f"You are an English conversation partner for a B2 learner. "
                  f"Be friendly and concise.\nUser: {req.message}\nAI:"
    }

    # Stream response from Ollama
    response = requests.post(OLLAMA_URL, json=payload, stream=True)
    output = ""
    for line in response.iter_lines():
        if line:
            data = line.decode("utf-8")
            output += data

    return {"reply": output}
