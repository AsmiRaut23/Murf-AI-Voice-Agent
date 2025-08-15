import requests
from os import getenv

MURF_API_KEY = getenv("MURF_API_KEY", "").strip()
MURF_URL = "https://api.murf.ai/v1/speech/generate"
FALLBACK_MESSAGE = "I'm having trouble connecting right now. Please try again later."

def generate_audio(text: str, voice_id: str) -> str | None:
    headers = {'Content-Type': 'application/json', 'api-key': MURF_API_KEY}
    payload = {"text": text, "voice_id": voice_id, "format": "mp3", "sampleRate": "44100"}
    resp = requests.post(MURF_URL, headers=headers, json=payload)
    if resp.ok:
        return resp.json().get("audioFile")
    return None

def fallback_audio(voice_id: str) -> str | None:
    return generate_audio(FALLBACK_MESSAGE, voice_id)
