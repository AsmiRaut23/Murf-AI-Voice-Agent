from flask import Flask, request, Response, render_template, jsonify
from services.stt_service import upload_audio, transcribe_audio
from services.tts_service import generate_audio, fallback_audio
from services.llm_service import query_gemini
from utils.logger import logger

app = Flask(__name__)
chat_history = {}

@app.route("/")
def index():
    return render_template("index1.html")

@app.route("/agent/chat/<session_id>", methods=["POST"])
def agent_chat(session_id):
    voice_id = request.form.get("voice_id")
    transcript, ai_reply = "", ""

    try:
        audio_file = request.files.get("audio")
        if not audio_file:
            raise ValueError("No audio uploaded")

        upload_url = upload_audio(audio_file.read())
        transcript = transcribe_audio(upload_url)

        chat_history.setdefault(session_id, []).append({"role": "user", "content": transcript})
        ai_reply = query_gemini(chat_history[session_id])
        chat_history[session_id].append({"role": "assistant", "content": ai_reply})

        murf_url = generate_audio(ai_reply, voice_id) or fallback_audio(voice_id)
        if not murf_url:
            return jsonify({"error": "TTS failed"}), 500

        audio_bytes = requests.get(murf_url).content
        resp = Response(audio_bytes, mimetype="audio/mpeg")
        resp.headers["X-Transcript"] = transcript
        resp.headers["X-Reply"] = ai_reply
        return resp

    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        fb_url = fallback_audio(voice_id)
        if fb_url:
            audio_bytes = requests.get(fb_url).content
            resp = Response(audio_bytes, mimetype="audio/mpeg")
            resp.headers["X-Transcript"] = transcript
            resp.headers["X-Reply"] = "Error occurred"
            return resp
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

