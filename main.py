import os
import time
import requests
from flask import Flask, request, jsonify, Response, render_template

app = Flask(__name__)

# === ENV VARS ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()

MURF_API_KEY = os.getenv("MURF_API_KEY", "").strip()
MURF_API_URL = "https://api.murf.ai/v1/speech/generate"
MURF_DEFAULT_VOICE = os.getenv("MURF_VOICE_ID", "en-US-natalie").strip()

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY", "").strip()
ASSEMBLYAI_TRANSCRIBE_URL = "https://api.assemblyai.com/v2/transcript"
ASSEMBLYAI_UPLOAD_URL = "https://api.assemblyai.com/v2/upload"


# In-memory chat history
chat_history = {}  # { session_id: [ {role:'user'|'assistant', content:'...'} ] }

FALLBACK_MESSAGE = "I'm having trouble connecting right now. Please try again later."

# ---------- Helpers ----------
def upload_audio_to_assemblyai(file_bytes: bytes) -> str:
    headers = {"authorization": ASSEMBLYAI_API_KEY}
    resp = requests.post(ASSEMBLYAI_UPLOAD_URL, headers=headers, data=file_bytes)
    resp.raise_for_status()
    return resp.json()["upload_url"]

def transcribe_audio_with_assemblyai(audio_url: str) -> str:
    headers = {"authorization": ASSEMBLYAI_API_KEY, "content-type": "application/json"}
    create = requests.post(ASSEMBLYAI_TRANSCRIBE_URL, headers=headers, json={"audio_url": audio_url})
    create.raise_for_status()
    tid = create.json()["id"]

    while True:
        poll = requests.get(f"{ASSEMBLYAI_TRANSCRIBE_URL}/{tid}", headers=headers)
        poll.raise_for_status()
        data = poll.json()
        if data["status"] == "completed":
            return data["text"]
        if data["status"] == "error":
            raise RuntimeError(data.get("error", "AssemblyAI transcription error"))
        time.sleep(1)

def query_gemini(conversation):
    """
    conversation: list[{role:'user'|'assistant', content:'...'}]
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"
    contents = [{"role": turn["role"], "parts": [{"text": turn["content"]}]} for turn in conversation]
    resp = requests.post(url, json={"contents": contents})
    if resp.status_code == 429:
        # Quota exceeded - return a friendly message instead of failing
        return "[Gemini quota exceeded. Please try again later.]"
    resp.raise_for_status()
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"]

def generate_murf_audio(text: str, voice_id: str) -> str | None:
    headers = {'Content-Type': 'application/json', 'api-key': MURF_API_KEY}
    payload = {"text": text, "voice_id": voice_id, "format": "mp3", "sampleRate": "44100"}
    resp = requests.post(MURF_API_URL, headers=headers, json=payload)
    if resp.ok:
        return resp.json().get("audioFile")
    print(f"Murf API Error: {resp.status_code} - {resp.text}")
    return None

def generate_fallback_audio(voice_id: str) -> str | None:
    return generate_murf_audio(FALLBACK_MESSAGE, voice_id)

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index1.html")

@app.route("/agent/chat/<session_id>", methods=["POST"])
def agent_chat(session_id):
    """
    Accepts FormData:
      - audio: recorded blob
      - voice_id: optional Murf voice id
    Returns: MP3 bytes with headers:
      - X-Transcript: user transcript text
      - X-Reply: assistant reply text
    """
    voice_id = request.form.get("voice_id") or MURF_DEFAULT_VOICE
    transcript = ""
    ai_reply = ""

    try:
        audio_file = request.files.get("audio")
        if not audio_file:
            raise ValueError("No audio uploaded")

        # 1) STT
        try:
            upload_url = upload_audio_to_assemblyai(audio_file.read())
            transcript = transcribe_audio_with_assemblyai(upload_url)
        except Exception as e:
            # If STT fails, return fallback audio immediately
            print(f"STT error: {e}")
            ai_reply = FALLBACK_MESSAGE
            fb_url = generate_fallback_audio(voice_id)
            if not fb_url:
                return jsonify({"error": "Fallback TTS failed"}), 500
            audio_bytes = requests.get(fb_url).content
            resp = Response(audio_bytes, mimetype="audio/mpeg")
            resp.headers["X-Transcript"] = transcript or ""
            resp.headers["X-Reply"] = ai_reply
            return resp

        # 2) Maintain history
        chat_history.setdefault(session_id, [])
        chat_history[session_id].append({"role": "user", "content": transcript})

        # 3) LLM
        try:
            ai_reply = query_gemini(chat_history[session_id])
        except Exception as e:
            print(f"Gemini error: {e}")
            ai_reply = FALLBACK_MESSAGE

        # 4) Save assistant message to history
        chat_history[session_id].append({"role": "assistant", "content": ai_reply})

        # 5) TTS
        murf_url = generate_murf_audio(ai_reply, voice_id)
        if not murf_url:
            # If TTS fails, try fallback TTS
            murf_url = generate_fallback_audio(voice_id)
            if not murf_url:
                return jsonify({"error": "TTS failed"}), 500

        audio_bytes = requests.get(murf_url).content
        resp = Response(audio_bytes, mimetype="audio/mpeg")
        # resp.headers["X-Transcript"] = transcript
        # resp.headers["X-Reply"] = ai_reply
        resp.headers["X-Transcript"] = transcript.replace("\n", " ").replace("\r", " ")
        resp.headers["X-Reply"] = ai_reply.replace("\n", " ").replace("\r", " ")

        return resp

    except Exception as e:
        print(f"Pipeline error: {e}")
        # Last-resort fallback
        fb_url = generate_fallback_audio(voice_id)
        if not fb_url:
            return jsonify({"error": str(e)}), 500
        audio_bytes = requests.get(fb_url).content
        resp = Response(audio_bytes, mimetype="audio/mpeg")
        # resp.headers["X-Transcript"] = transcript or ""
        resp.headers["X-Transcript"] = transcript.replace("\n", " ").replace("\r", " ")
        resp.headers["X-Reply"] = FALLBACK_MESSAGE
        return resp


if __name__ == "__main__":
    app.run(debug=True)

