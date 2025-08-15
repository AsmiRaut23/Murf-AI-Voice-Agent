import requests, time
from os import getenv

ASSEMBLYAI_API_KEY = getenv("ASSEMBLYAI_API_KEY", "").strip()
UPLOAD_URL = "https://api.assemblyai.com/v2/upload"
TRANSCRIBE_URL = "https://api.assemblyai.com/v2/transcript"

def upload_audio(file_bytes: bytes) -> str:
    headers = {"authorization": ASSEMBLYAI_API_KEY}
    resp = requests.post(UPLOAD_URL, headers=headers, data=file_bytes)
    resp.raise_for_status()
    return resp.json()["upload_url"]

def transcribe_audio(audio_url: str) -> str:
    headers = {"authorization": ASSEMBLYAI_API_KEY, "content-type": "application/json"}
    create = requests.post(TRANSCRIBE_URL, headers=headers, json={"audio_url": audio_url})
    create.raise_for_status()
    tid = create.json()["id"]

    while True:
        poll = requests.get(f"{TRANSCRIBE_URL}/{tid}", headers=headers)
        poll.raise_for_status()
        data = poll.json()
        if data["status"] == "completed":
            return data["text"]
        if data["status"] == "error":
            raise RuntimeError(data.get("error", "STT error"))
        time.sleep(1)
