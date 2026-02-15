import requests
from typing import Optional

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3:mini"

def ollama_generate(prompt: str, system: Optional[str] = None, temperature: float = 0.2) -> str:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": 300   #  limit output tokens
        }
    }

    if system:
        payload["system"] = system

    r = requests.post(OLLAMA_URL, json=payload, timeout=180)
    r.raise_for_status()
    return r.json().get("response", "").strip()
