import os
import asyncio
import json
import base64
import subprocess
import threading
import traceback

from flask import Flask, render_template, jsonify, request
from flask_sock import Sock

# Local modules
from config import settings, load_config_file, save_config_file, apply_runtime_overrides
from services.stt_service import transcribe_realtime
from services.gemini_service import chat_history  # keep same global usage as your original
# (Gemini + Murf are invoked inside STT service via callbacks/tasks)

app = Flask(__name__)
sock = Sock(app)


# ---------------------------
# Routes
# ---------------------------
@app.route("/")
def index():
    """
    Render the main page and pass current config so your modal shows saved keys.
    Behavior unchanged vs your original.
    """
    config = load_config_file()  # always show latest values
    return render_template("index.html", config=config)


@app.route("/save_keys", methods=["POST"])
def save_keys():
    """
    Save keys to config.json and apply them at runtime (no restart needed).
    Fully preserves your side effects and debug prints.
    """
    try:
        data = request.get_json(force=True)
        print("🔐 /save_keys called. Payload:", data, flush=True)

        # Persist
        cfg = load_config_file()
        for k, v in data.items():
            cfg[k] = v
        save_config_file(cfg)
        print(f"🔐 Saved config to {settings.CONFIG_FILE}", flush=True)

        # Apply runtime overrides (reconfigures genai + module-level keys)
        apply_runtime_overrides(cfg)
        print("🔐 In-memory keys updated", flush=True)

        return jsonify({"status": "success", "message": "Keys saved!"})
    except Exception as e:
        print("❌ /save_keys error:", e, flush=True)
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


# ---------------------------
# WebSocket Handler
# ---------------------------
@sock.route("/ws")
def ws_handler(ws):
    """
    Browser <-> Server WebSocket bridge.
    Keeps your ffmpeg pipeline, AssemblyAI realtime loop, and message flow intact.
    """
    print("🎧 WS client connected (browser)", flush=True)

    def send_to_client(message: str):
        try:
            ws.send(message)
        except Exception as e:
            print(f"⚠ send_to_client skipped (client closed?): {e}", flush=True)

    # Dedicated event loop/thread for async work
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    threading.Thread(target=loop.run_forever, daemon=True).start()

    # ffmpeg to convert WebM → 16kHz mono PCM s16le
    ffmpeg_cmd = [
        "ffmpeg", "-loglevel", "quiet", "-i", "pipe:0",
        "-ar", "16000", "-ac", "1", "-f", "s16le", "pipe:1"
    ]
    process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    audio_queue = asyncio.Queue()

    # Background reader from ffmpeg → audio_queue
    def read_pcm():
        try:
            while True:
                data = process.stdout.read(4096)
                if not data:
                    break
                asyncio.run_coroutine_threadsafe(audio_queue.put(data), loop)
        except Exception as e:
            print("⚠ read_pcm error:", e, flush=True)

    threading.Thread(target=read_pcm, daemon=True).start()

    # Kick off the AssemblyAI realtime transcription task
    asyncio.run_coroutine_threadsafe(
        transcribe_realtime(audio_queue, send_to_client, loop),
        loop
    )

    try:
        while True:
            try:
                msg = ws.receive()
                if msg is None:
                    print("ℹ Client disconnected cleanly", flush=True)
                    break
            except Exception as e:
                print("⚠ WS receive error:", e, flush=True)
                break

            # Parse client message
            try:
                obj = json.loads(msg)
            except Exception as e:
                print("⚠ Bad msg:", e, msg, flush=True)
                continue

            # === AUDIO CHUNKS FROM MIC ===
            if obj.get("type") == "audio_chunk":
                audio_b64 = obj.get("data")
                if audio_b64:
                    try:
                        chunk = base64.b64decode(audio_b64)
                        process.stdin.write(chunk)
                        process.stdin.flush()
                    except Exception as e:
                        print("⚠ ffmpeg write error:", e, flush=True)
                continue

            # --- (Typed text pathway was commented out in your original; preserved as-is) ---
            # elif obj.get("type") == "user_text":
            #     user_text = obj.get("text", "").strip()
            #     if not user_text:
            #         continue
            #     print(f"📝 Received typed text: {user_text}", flush=True)
            #     send_to_client(json.dumps({"type": "user_message", "text": user_text}))
            #     from services.pipeline import process_user_text  # optional split if you want
            #     asyncio.run_coroutine_threadsafe(
            #         process_user_text(user_text, send_to_client),
            #         loop
            #     )
            #     continue

    finally:
        # Cleanup
        try:
            if process.stdin:
                process.stdin.close()
        except Exception:
            pass
        try:
            process.wait(timeout=2)
        except Exception:
            process.kill()

        asyncio.run_coroutine_threadsafe(audio_queue.put(None), loop)
        print("✅ Browser connection closed cleanly", flush=True)


# Silence favicon 404
@app.route("/favicon.ico")
def favicon():
    return ("", 204)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
