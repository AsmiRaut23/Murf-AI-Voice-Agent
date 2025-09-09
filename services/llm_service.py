import requests
from os import getenv

GEMINI_API_KEY = getenv("GEMINI_API_KEY", "").strip()
MODEL_NAME = getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()

def query_gemini(conversation):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"
    contents = [{"role": turn["role"], "parts": [{"text": turn["content"]}]} for turn in conversation]
    resp = requests.post(url, json={"contents": contents})
    if resp.status_code == 429:
        return "[Gemini quota exceeded. Please try again later.]"
    resp.raise_for_status()
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
