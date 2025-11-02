# app/services/ai_service.py
import requests
import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")


def generate_reply(user_message: str) -> str:
    """
    Sends a prompt to the local Phi-3 model through Ollama and returns the response text.
    """
    system_prompt = (
        "You are an English conversation partner helping a B2 learner. "
        "Reply naturally and casual, use short sentences, do not ask follow-up questions."
    )

    prompt = f"{system_prompt}\nUser: {user_message}\nAI:"

    payload = {
        "model": "phi3",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()

    # Ollama returns JSON lines if stream=False, otherwise NDJSON if stream=True
    data = response.json()
    return data.get("response") or data.get("text", "")
