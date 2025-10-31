# app/routes/chat.py
from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.services.ai_service import generate_reply

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str

@router.post("/")
def chat(req: ChatRequest):
    system_prompt = (
        "You are an English conversation partner helping a B2 learner. "
        "Keep your answers friendly, clear, and ask follow-up questions."
    )
    full_prompt = f"{system_prompt}\nUser: {req.message}\nAI:"
    reply = generate_reply(full_prompt)
    return {"reply": reply}
