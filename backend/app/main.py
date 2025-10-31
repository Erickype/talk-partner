# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes import chat, tts

app = FastAPI(title="TalkMate Backend", version="1.0")

# Allow frontend (React/Vue) to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev, later restrict to frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(chat.router)
app.include_router(tts.router)

@app.get("/")
def home():
    return {"message": "TalkMate backend is running 🚀"}
