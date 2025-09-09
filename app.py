


# app.py
import os
import json
import base64
import subprocess
import threading
import traceback
import queue

from flask import Flask, render_template, jsonify, request
from flask_sock import Sock

from config import settings, load_config_file, save_config_file, apply_runtime_overrides
from services.stt_service import start_assemblyai_stream
from services.gemini_service import stream_llm_response, pirate_persona
from services.tts_service import send_to_murf  # async Murf TTS streaming


# tts_service will be imported dynamically when needed

app = Flask(__name__)
sock = Sock(app)

# =========================
# Routes
# =========================
@app.route("/")
def index():
    cfg = load_config_file()
    return render_template("index.html", config=cfg)


# @app.route("/save_keys", methods=["POST"])
# def save_keys_route():
#     try:
#         data = request.get_json(force=True)
#         print("🔐 /save_keys called. Payload:", data, flush=True)

#         cfg = load_config_file()
#         for k, v in data.items():
#             cfg[k] = v
#         save_config_file(cfg)

#         apply_runtime_overrides()
#         return jsonify({"message": "✅ Keys saved successfully!"})
#     except Exception as e:
#         traceback.print_exc()
#         return jsonify({"error": str(e)}), 500



@app.route("/save_keys", methods=["POST"])
def save_keys():
    try:
        # Always parse incoming JSON
        data = request.get_json(force=True)
        print("🔐 /save_keys called. Payload:", data, flush=True)

        # Load existing config so we don't overwrite missing keys
        cfg = load_config_file()

        # Merge new keys into existing config
        for k, v in data.items():
            if isinstance(v, str):
                cfg[k] = v.strip()  # strip spaces just in case
            else:
                cfg[k] = v

        # Save back to file
        save_config_file(cfg)

        # Apply immediately so user doesn’t need restart
        apply_runtime_overrides(cfg)

        return jsonify({
            "status": "success",
            "message": "Keys updated successfully!"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


# =========================
# WebSocket handler
# =========================
@sock.route("/ws")
def ws_handler(ws):
    print("🎧 WS client connected", flush=True)

    sdk_queue = queue.Queue()

    ffmpeg_cmd = [
        "ffmpeg", "-loglevel", "quiet", "-i", "pipe:0",
        "-ar", "16000", "-ac", "1", "-f", "s16le", "pipe:1"
    ]
    process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    transcription_thread = None
    transcription_started = False
    recording_started = False

    def read_pcm():
        try:
            while True:
                data = process.stdout.read(4096)
                if not data:
                    break
                sdk_queue.put(data)
        except Exception as e:
            print("⚠ read_pcm error:", e, flush=True)
        finally:
            try:
                sdk_queue.put(None)
            except Exception:
                pass

    threading.Thread(target=read_pcm, daemon=True).start()

    def client_send(text_or_json: str):
        try:
            ws.send(text_or_json)
        except Exception as e:
            print("⚠ client_send(ws.send) failed:", e, flush=True)

    try:
        while True:
            msg = ws.receive()
            if msg is None:
                print("ℹ Client disconnected", flush=True)
                break

            try:
                obj = json.loads(msg)
            except Exception as e:
                print("⚠ Invalid JSON:", e, msg, flush=True)
                continue

            # AUDIO CHUNKS
            if obj.get("type") == "audio_chunk":
                audio_b64 = obj.get("data")
                if audio_b64 and recording_started:
                    try:
                        chunk = base64.b64decode(audio_b64)
                        if process.stdin:
                            process.stdin.write(chunk)
                            process.stdin.flush()

                        if not transcription_started:
                            transcription_thread = threading.Thread(
                                target=start_assemblyai_stream,
                                args=(sdk_queue, client_send),
                                daemon=True,
                            )
                            transcription_thread.start()
                            transcription_started = True
                            print("ℹ Started AssemblyAI SDK transcription thread", flush=True)
                    except Exception as e:
                        print("⚠ ffmpeg write/enqueue error:", e, flush=True)
                continue

            # End-of-audio signal
            if obj.get("type") == "end_of_audio":
                if not recording_started:
                    print("⚠ Ignoring stray end_of_audio (no active recording)", flush=True)
                    continue
                print("ℹ Received end_audio signal", flush=True)
                try:
                    sdk_queue.put(None)
                except Exception:
                    pass
                continue

            # Mic control
            if obj.get("type") == "start_recording":
                print("ℹ Mic button pressed - recording started", flush=True)
                recording_started = True
                continue

            if obj.get("type") == "stop_recording":
                print("ℹ Mic button released - recording stopped", flush=True)
                recording_started = False
                try:
                    sdk_queue.put(None)
                except Exception:
                    pass
                transcription_started = False
                continue

             # ---------------------
            # TEXT COMMAND (Gemini pirate persona)
            # ---------------------
            if obj.get("type") == "text_command":
                user_text = obj.get("text", "").strip()
                if not user_text:
                    continue

                # Async Gemini processing
                import asyncio
                loop = asyncio.new_event_loop()
                threading.Thread(target=loop.run_forever, daemon=True).start()

                async def process_user_text(user_text: str):
                    try:
                        ## Generate Gemini response (normal)
                        gemini_text = await stream_llm_response(user_text)

                        # Apply pirate persona just before sending
                        pirate_text = pirate_persona(gemini_text)
                        print("🧪 Pirate persona check:", pirate_text, flush=True)

                        # Send text back to client
                        client_send(json.dumps({
                            "type": "gemini_response",
                            "text": pirate_text
                        }))

                        # DEBUG: confirm what's being sent to Murf in server logs
                        print("➡ Sending to Murf TTS (pirate):", pirate_text, flush=True)

                        # Send to Murf TTS (must use exactly pirate_text)
                        try:
                            await send_to_murf(pirate_text, client_send)
                        except Exception as e:
                            print("❌ send_to_murf error:", e, flush=True)
                            client_send(json.dumps({"type": "error", "message": "Murf TTS failed"}))

                    except Exception as e:
                        print("❌ process_user_text error:", e, flush=True)

                # asyncio.run_coroutine_threadsafe(process_user_text(final_text), loop)
                # continue

    finally:
        try:
            if process.stdin:
                process.stdin.close()
        except Exception:
            pass
        try:
            process.wait(timeout=2)
        except Exception:
            try:
                process.kill()
            except Exception:
                pass
        try:
            sdk_queue.put(None)
        except Exception:
            pass

        print("✅ Browser connection closed cleanly", flush=True)


# =========================
# Run Flask
# =========================
if __name__ == "__main__":
    cfg = load_config_file()
    apply_runtime_overrides(cfg)   # <-- pass the config
    print("🔑 GEMINI_KEY applied")
    app.run(host="0.0.0.0", port=5000, debug=False)



