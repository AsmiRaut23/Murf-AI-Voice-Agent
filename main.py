# from flask import Flask, request, jsonify
# import os
# from dotenv import load_dotenv
# import google.genai as genai

# load_dotenv()
# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# app = Flask(__name__)

# @app.route("/llm/query", methods=["POST"])
# def llm_query():
#     data = request.get_json()
#     prompt = data.get("text")
#     if not prompt:
#         return jsonify({"error": "Please include 'text' in JSON body"}), 400

#     try:
#         response = client.models.generate_content(
#             model="gemini-2.0-flash",  
#             contents=prompt
#         )
#         return jsonify({"response": response.text})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":
#     app.run(debug=True)





# day 9
# import os
# import requests
# import time
# from flask import Flask, request, jsonify, render_template
# from dotenv import load_dotenv
# import google.generativeai as genai

# load_dotenv()
# app = Flask(__name__)

# # ----- Config -----
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# MURF_API_KEY = os.getenv("MURF_API_KEY")
# MURF_API_URL = os.getenv("MURF_API_URL", "https://api.murf.ai/v1/speech/generate")
# MURF_VOICE_ID = os.getenv("MURF_VOICE_ID", "en-US-natalie")

# ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
# ASSEMBLYAI_TRANSCRIBE_URL = "https://api.assemblyai.com/v2/transcript"
# ASSEMBLYAI_UPLOAD_URL = "https://api.assemblyai.com/v2/upload"

# # ----- Init Gemini -----
# gemini_model = None
# if GEMINI_API_KEY:
#     try:
#         genai.configure(api_key=GEMINI_API_KEY)
#         gemini_model = genai.GenerativeModel(GEMINI_MODEL_NAME)
#         print(f"✅ Gemini initialized with: {GEMINI_MODEL_NAME}")
#     except Exception as e:
#         print(f"❌ Failed to initialize Gemini: {e}")
# else:
#     print("❌ GEMINI_API_KEY missing.")

# # ----- Frontend -----
# @app.route("/")
# def index():
#     return render_template("index1.html")

# # ----- AssemblyAI Transcription -----
# @app.route("/transcribe", methods=["POST"])
# def transcribe_audio():
#     if "file" not in request.files:
#         return jsonify({"error": "No file uploaded"}), 400

#     file = request.files["file"]

#     # Upload file to AssemblyAI
#     headers = {"authorization": ASSEMBLYAI_API_KEY}
#     upload_res = requests.post(ASSEMBLYAI_UPLOAD_URL, headers=headers, data=file)
#     if upload_res.status_code != 200:
#         return jsonify({"error": "Upload failed", "details": upload_res.text}), 500

#     upload_url = upload_res.json().get("upload_url")

#     # Start transcription
#     transcript_req = {"audio_url": upload_url}
#     trans_res = requests.post(ASSEMBLYAI_TRANSCRIBE_URL, headers=headers, json=transcript_req)
#     if trans_res.status_code != 200:
#         return jsonify({"error": "Transcription start failed", "details": trans_res.text}), 500

#     transcript_id = trans_res.json().get("id")

#     # Poll until complete
#     while True:
#         poll_res = requests.get(f"{ASSEMBLYAI_TRANSCRIBE_URL}/{transcript_id}", headers=headers)
#         status = poll_res.json().get("status")
#         if status == "completed":
#             return jsonify({"text": poll_res.json().get("text")})
#         elif status == "error":
#             return jsonify({"error": "Transcription failed", "details": poll_res.text}), 500
#         time.sleep(2)

# # ----- LLM + Murf -----
# @app.route("/llm/query", methods=["POST"])
# def llm_query():
#     data = request.get_json(force=True, silent=True) or {}
#     user_prompt = data.get("text", "").strip()
#     if not user_prompt:
#         return jsonify({"error": "No text provided"}), 400

#     print(f"<- Received Text: '{user_prompt}'")

#     # Gemini response
#     try:
#         gemini_resp = gemini_model.generate_content(user_prompt)
#         answer_text = getattr(gemini_resp, "text", str(gemini_resp)).strip()
#     except Exception as e:
#         return jsonify({"error": f"Gemini error: {e}"}), 500

#     # Murf TTS
#     headers = {"api-key": MURF_API_KEY, "Content-Type": "application/json"}
#     payload = {"voiceId": MURF_VOICE_ID, "text": answer_text, "format": "MP3"}
#     murf_r = requests.post(MURF_API_URL, headers=headers, json=payload, timeout=40)

#     if murf_r.status_code != 200:
#         return jsonify({"error": f"Murf API Error: {murf_r.status_code}", "details": murf_r.text}), 500

#     murf_json = murf_r.json()
#     audio_url = (
#         murf_json.get("audioFile") or murf_json.get("audioUrl") or
#         murf_json.get("audio_url") or murf_json.get("result_url") or
#         murf_json.get("url")
#     )

#     if not audio_url:
#         return jsonify({"error": "No audio URL in Murf response", "murf_response": murf_json}), 500

#     return jsonify({"question": user_prompt, "answer": answer_text, "audio_url": audio_url})


# if __name__ == "__main__":
#     app.run(debug=True)












# day10
# from flask import Flask, request, jsonify, render_template
# import requests
# import os
# import time

# app = Flask(__name__)

# # ===== ENVIRONMENT VARIABLES =====
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# MURF_API_KEY = os.getenv("MURF_API_KEY")
# MURF_API_URL = "https://api.murf.ai/v1/speech/generate"
# MURF_VOICE_ID = os.getenv("MURF_VOICE_ID", "en-US-natalie")

# ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
# ASSEMBLYAI_TRANSCRIBE_URL = "https://api.assemblyai.com/v2/transcript"
# ASSEMBLYAI_UPLOAD_URL = "https://api.assemblyai.com/v2/upload"

# # ===== CHAT HISTORY STORE =====
# # Stores conversation per session_id
# chat_history = {}  # { session_id: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}] }


# @app.route("/")
# def index():
#     return render_template("index1.html")


# # ===== AssemblyAI: Upload audio file =====
# def upload_audio(file_bytes):
#     headers = {"authorization": ASSEMBLYAI_API_KEY}
#     resp = requests.post(ASSEMBLYAI_UPLOAD_URL, headers=headers, data=file_bytes)
#     resp.raise_for_status()
#     return resp.json()["upload_url"]


# # ===== AssemblyAI: Transcribe uploaded audio =====
# def transcribe_audio(audio_url):
#     headers = {"authorization": ASSEMBLYAI_API_KEY, "content-type": "application/json"}
#     json_data = {"audio_url": audio_url}
#     resp = requests.post(ASSEMBLYAI_TRANSCRIBE_URL, headers=headers, json=json_data)
#     resp.raise_for_status()
#     transcript_id = resp.json()["id"]

#     # Poll until transcription completes
#     while True:
#         poll = requests.get(f"{ASSEMBLYAI_TRANSCRIBE_URL}/{transcript_id}", headers=headers)
#         status = poll.json()["status"]
#         if status == "completed":
#             return poll.json()["text"]
#         elif status == "error":
#             raise Exception(poll.json()["error"])
#         time.sleep(1)


# # ===== Gemini API: Send conversation =====
# def query_gemini(conversation):
#     """
#     conversation: list of dicts [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
#     """
#     messages = []
#     for turn in conversation:
#         messages.append({"role": turn["role"], "parts": [{"text": turn["content"]}]})

#     url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"
#     payload = {"contents": messages}
#     resp = requests.post(url, json=payload)
#     resp.raise_for_status()
#     return resp.json()["candidates"][0]["content"]["parts"][0]["text"]


# # ===== Murf API: Generate voice audio =====
# def generate_murf_audio(text, voice_id):
#     if not text:
#         return None
#     headers = {'Content-Type': 'application/json', 'api-key': MURF_API_KEY}
#     payload = {
#         "text": text,
#         "voice_id": voice_id,
#         "format": "mp3",
#         "sampleRate": "44100"
#     }
#     resp = requests.post(MURF_API_URL, headers=headers, json=payload)
#     if resp.status_code == 200:
#         return resp.json().get('audioFile')
#     else:
#         print(f"Murf API Error: {resp.status_code} - {resp.text}")
#         return None


# # ===== Chat Endpoint with History =====
# @app.route("/agent/chat/<session_id>", methods=["POST"])
# def agent_chat(session_id):
#     global chat_history
#     audio_file = request.files.get("audio")
#     if not audio_file:
#         return jsonify({"error": "No audio uploaded"}), 400

#     # Step 1: Upload + Transcribe
#     audio_url = upload_audio(audio_file.read())
#     transcript = transcribe_audio(audio_url)
#     print(f"[User - {session_id}]: {transcript}")

#     # Step 2: Initialize history if new session
#     if session_id not in chat_history:
#         chat_history[session_id] = []

#     # Step 3: Append user message
#     chat_history[session_id].append({"role": "user", "content": transcript})

#     # Step 4: Query Gemini with full history
#     ai_reply = query_gemini(chat_history[session_id])
#     print(f"[Assistant]: {ai_reply}")

#     # Step 5: Append assistant reply
#     chat_history[session_id].append({"role": "assistant", "content": ai_reply})

#     # Step 6: Generate audio with Murf
#     audio_url = generate_murf_audio(ai_reply, MURF_VOICE_ID)
#     if not audio_url:
#         return jsonify({"error": "Murf TTS failed"}), 500

#     audio_bytes = requests.get(audio_url).content
#     return audio_bytes, 200, {'Content-Type': 'audio/mpeg'}


# if __name__ == "__main__":
#     app.run(debug=True)





# day 12 
# correct


# from flask import Flask, request, jsonify, render_template
# import requests
# import os
# import time

# app = Flask(__name__)

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# MURF_API_KEY = os.getenv("MURF_API_KEY")
# MURF_API_URL = "https://api.murf.ai/v1/speech/generate"
# MURF_VOICE_ID = os.getenv("MURF_VOICE_ID", "en-US-natalie")

# ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
# ASSEMBLYAI_TRANSCRIBE_URL = "https://api.assemblyai.com/v2/transcript"
# ASSEMBLYAI_UPLOAD_URL = "https://api.assemblyai.com/v2/upload"

# chat_history = {}

# FALLBACK_MESSAGE = "I'm having trouble connecting right now. Please try again later."

# def upload_audio(file_bytes):
#     headers = {"authorization": ASSEMBLYAI_API_KEY}
#     resp = requests.post(ASSEMBLYAI_UPLOAD_URL, headers=headers, data=file_bytes)
#     resp.raise_for_status()
#     return resp.json()["upload_url"]

# def transcribe_audio(audio_url):
#     headers = {"authorization": ASSEMBLYAI_API_KEY, "content-type": "application/json"}
#     json_data = {"audio_url": audio_url}
#     resp = requests.post(ASSEMBLYAI_TRANSCRIBE_URL, headers=headers, json=json_data)
#     resp.raise_for_status()
#     transcript_id = resp.json()["id"]

#     while True:
#         poll = requests.get(f"{ASSEMBLYAI_TRANSCRIBE_URL}/{transcript_id}", headers=headers)
#         poll.raise_for_status()
#         status = poll.json()["status"]
#         if status == "completed":
#             return poll.json()["text"]
#         elif status == "error":
#             raise Exception(poll.json()["error"])
#         time.sleep(1)

# def query_gemini(conversation):
#     messages = []
#     for turn in conversation:
#         messages.append({"role": turn["role"], "parts": [{"text": turn["content"]}]})

#     url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"
#     payload = {"contents": messages}
#     resp = requests.post(url, json=payload)
#     resp.raise_for_status()
#     return resp.json()["candidates"][0]["content"]["parts"][0]["text"]

# def generate_murf_audio(text, voice_id):
#     if not text:
#         return None
#     headers = {'Content-Type': 'application/json', 'api-key': MURF_API_KEY}
#     payload = {
#         "text": text,
#         "voice_id": voice_id,
#         "format": "mp3",
#         "sampleRate": "44100"
#     }
#     resp = requests.post(MURF_API_URL, headers=headers, json=payload)
#     if resp.status_code == 200:
#         return resp.json().get('audioFile')
#     else:
#         print(f"Murf API Error: {resp.status_code} - {resp.text}")
#         return None

# def generate_fallback_audio():
#     """Generate fallback audio if main pipeline fails."""
#     return generate_murf_audio(FALLBACK_MESSAGE, MURF_VOICE_ID)

# @app.route("/")
# def index():
#     return render_template("index1.html")

# @app.route("/agent/chat/<session_id>", methods=["POST"])
# def agent_chat(session_id):
#     global chat_history

#     try:
#         audio_file = request.files.get("audio")
#         if not audio_file:
#             raise Exception("No audio uploaded")

#         # Step 1: Upload + Transcribe
#         transcript = transcribe_audio(upload_audio(audio_file.read()))
#         print(f"[User - {session_id}]: {transcript}")

#         if session_id not in chat_history:
#             chat_history[session_id] = []

#         # Step 2: Append user message
#         chat_history[session_id].append({"role": "user", "content": transcript})

#         # Step 3: Query Gemini
#         ai_reply = query_gemini(chat_history[session_id])
#         print(f"[Assistant]: {ai_reply}")

#         # Step 4: Append assistant reply
#         chat_history[session_id].append({"role": "assistant", "content": ai_reply})

#         # Step 5: Generate audio
#         audio_url = generate_murf_audio(ai_reply, MURF_VOICE_ID)
#         if not audio_url:
#             raise Exception("Murf TTS failed")

#     except Exception as e:
#         print(f"Error in pipeline: {e}")
#         audio_url = generate_fallback_audio()
#         if not audio_url:
#             return jsonify({"error": str(e)}), 500

#     # Step 6: Return audio bytes
#     audio_bytes = requests.get(audio_url).content
#     return audio_bytes, 200, {'Content-Type': 'audio/mpeg'}

# if __name__ == "__main__":
#     app.run(debug=True)











# app.py
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
