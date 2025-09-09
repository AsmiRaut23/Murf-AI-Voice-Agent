# import os
# import asyncio
# import json
# import base64
# import subprocess
# import threading
# import traceback

# from flask import Flask, render_template, jsonify, request
# from flask_sock import Sock

# # Local modules
# from config import settings, load_config_file, save_config_file, apply_runtime_overrides
# from services.stt_service import transcribe_audio
# from services.tts_service import generate_audio
# from services.gemini_service import chat_history  # keep same global usage as your original
# # (Gemini + Murf are invoked inside STT service via callbacks/tasks)

# app = Flask(__name__)
# sock = Sock(app)


# # ---------------------------
# # Routes
# # ---------------------------
# @app.route("/")
# def index():
#     """
#     Render the main page and pass current config so your modal shows saved keys.
#     Behavior unchanged vs your original.
#     """
#     config = load_config_file()  # always show latest values
#     return render_template("index.html", config=config)


# @app.route("/save_keys", methods=["POST"])
# def save_keys():
#     """
#     Save keys to config.json and apply them at runtime (no restart needed).
#     Fully preserves your side effects and debug prints.
#     """
#     try:
#         data = request.get_json(force=True)
#         print("🔐 /save_keys called. Payload:", data, flush=True)

#         # Persist
#         cfg = load_config_file()
#         for k, v in data.items():
#             cfg[k] = v
#         save_config_file(cfg)
#         print(f"🔐 Saved config to {settings.CONFIG_FILE}", flush=True)

#         # Apply runtime overrides (reconfigures genai + module-level keys)
#         apply_runtime_overrides(cfg)
#         print("🔐 In-memory keys updated", flush=True)

#         return jsonify({"status": "success", "message": "Keys saved!"})
#     except Exception as e:
#         print("❌ /save_keys error:", e, flush=True)
#         traceback.print_exc()
#         return jsonify({"status": "error", "message": str(e)}), 500


# async def handle_transcription_and_tts(queue, ws):
#     async def send_to_client(msg):
#         ws.send(msg)

#     # Get transcription
#     text = await transcribe_audio(queue, send_to_client)

#     # Call Murf TTS
#     if text:
#         from services.tts_service import send_to_murf
#         await send_to_murf(text, client_send=send_to_client)



# # ---------------------------
# # WebSocket Handler
# # ---------------------------
# @sock.route("/ws")
# def ws_handler(ws):
#     """
#     Browser <-> Server WebSocket bridge.
#     Keeps your ffmpeg pipeline, AssemblyAI realtime loop, and message flow intact.
#     """
#     print("🎧 WS client connected (browser)", flush=True)

#     async def send_to_client(message: str):
#         try:
#             ws.send(message)
#         except Exception as e:
#             print(f"⚠ send_to_client skipped (client closed?): {e}", flush=True)

#     # Dedicated event loop/thread for async work
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     threading.Thread(target=loop.run_forever, daemon=True).start()

#     # ffmpeg to convert WebM → 16kHz mono PCM s16le
#     ffmpeg_cmd = [
#         "ffmpeg", "-loglevel", "quiet", "-i", "pipe:0",
#         "-ar", "16000", "-ac", "1", "-f", "s16le", "pipe:1"
#     ]
#     process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

#     audio_queue = asyncio.Queue()

#     # Background reader from ffmpeg → audio_queue
#     def read_pcm():
#         try:
#             while True:
#                 data = process.stdout.read(4096)
#                 if not data:
#                     break
#                 asyncio.run_coroutine_threadsafe(audio_queue.put(data), loop)
#         except Exception as e:
#             print("⚠ read_pcm error:", e, flush=True)

#     threading.Thread(target=read_pcm, daemon=True).start()

#     # Kick off the AssemblyAI realtime transcription task
#     asyncio.run_coroutine_threadsafe(
#         handle_transcription_and_tts(audio_queue, ws),
#         loop
#     )


#     # # Start reading PCM audio in a background thread
#     # threading.Thread(target=read_pcm, daemon=True).start()

#     # # Kick off the AssemblyAI realtime transcription task
#     # # transcribe_audio must be an async function
#     # loop = asyncio.get_event_loop()
#     # asyncio.run_coroutine_threadsafe(
#     #     transcribe_audio(audio_queue, send_to_client),  # async coroutine
#     #     loop
#     # )


#     try:
#         while True:
#             try:
#                 msg = ws.receive()
#                 if msg is None:
#                     print("ℹ Client disconnected cleanly", flush=True)
#                     break
#             except Exception as e:
#                 print("⚠ WS receive error:", e, flush=True)
#                 break

#             # Parse client message
#             try:
#                 obj = json.loads(msg)
#             except Exception as e:
#                 print("⚠ Bad msg:", e, msg, flush=True)
#                 continue

#             # === AUDIO CHUNKS FROM MIC ===
#             if obj.get("type") == "audio_chunk":
#                 audio_b64 = obj.get("data")
#                 if audio_b64:
#                     try:
#                         chunk = base64.b64decode(audio_b64)
#                         process.stdin.write(chunk)
#                         process.stdin.flush()
#                     except Exception as e:
#                         print("⚠ ffmpeg write error:", e, flush=True)
#                 continue

#             # --- (Typed text pathway was commented out in your original; preserved as-is) ---
#             # elif obj.get("type") == "user_text":
#             #     user_text = obj.get("text", "").strip()
#             #     if not user_text:
#             #         continue
#             #     print(f"📝 Received typed text: {user_text}", flush=True)
#             #     send_to_client(json.dumps({"type": "user_message", "text": user_text}))
#             #     from services.pipeline import process_user_text  # optional split if you want
#             #     asyncio.run_coroutine_threadsafe(
#             #         process_user_text(user_text, send_to_client),
#             #         loop
#             #     )
#             #     continue

#     finally:
#         # Cleanup
#         try:
#             if process.stdin:
#                 process.stdin.close()
#         except Exception:
#             pass
#         try:
#             process.wait(timeout=2)
#         except Exception:
#             process.kill()

#         asyncio.run_coroutine_threadsafe(audio_queue.put(None), loop)
#         print("✅ Browser connection closed cleanly", flush=True)


# # Silence favicon 404
# @app.route("/favicon.ico")
# def favicon():
#     return ("", 204)


# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host="0.0.0.0", port=port, debug=False)




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






# import os
# import asyncio
# import json
# import base64
# import subprocess
# import threading
# import traceback

# from flask import Flask, render_template, jsonify, request
# from flask_sock import Sock

# # Local modules
# from config import settings, load_config_file, save_config_file, apply_runtime_overrides
# from services.stt_service import transcribe_universal_ws
# from services.tts_service import send_to_murf  # <- use streamed Murf TTS directly
# from services.gemini_service import chat_history  # keep same global usage

# app = Flask(__name__)
# sock = Sock(app)


# # ---------------------------
# # Routes
# # ---------------------------
# @app.route("/")
# def index():
#     config = load_config_file()
#     return render_template("index.html", config=config)


# @app.route("/save_keys", methods=["POST"])
# def save_keys():
#     try:
#         data = request.get_json(force=True)
#         print("🔐 /save_keys called. Payload:", data, flush=True)

#         cfg = load_config_file()
#         for k, v in data.items():
#             cfg[k] = v
#         save_config_file(cfg)
#         print(f"🔐 Saved config to {settings.CONFIG_FILE}", flush=True)

#         apply_runtime_overrides(cfg)
#         print("🔐 In-memory keys updated", flush=True)

#         return jsonify({"status": "success", "message": "Keys saved!"})
#     except Exception as e:
#         print("❌ /save_keys error:", e, flush=True)
#         traceback.print_exc()
#         return jsonify({"status": "error", "message": str(e)}), 500


# # ---------------------------
# # Transcription + TTS
# # ---------------------------
# async def handle_transcription_and_tts(queue, ws):
#     async def send_to_client(msg):
#         """Async wrapper used by STT/TTs code. Sends plain text or JSON string to the browser WS."""
#         try:
#             # ws.send is synchronous (from flask_sock) — calling it here is okay.
#             # If this thread/context ever causes issues, change to a threadsafe queuing mechanism.
#             ws.send(msg)
#         except Exception as e:
#             print("⚠ send_to_client failed:", e, flush=True)

#     try:
#         print("ℹ Starting transcription task...", flush=True)
#         text = await transcribe_universal_ws(queue, send_to_client)

#         print("✅ Transcription received:", text, flush=True)

#         if text:
#             print("ℹ Sending text to Murf TTS...", flush=True)
#             # send_to_murf expects an async client_send or sync; our send_to_client is async so send_to_murf will await safely
#             await send_to_murf(text, client_send=send_to_client)
#             print("✅ Murf TTS finished", flush=True)
#         else:
#             print("⚠ No text transcribed from audio", flush=True)

#     except Exception as e:
#         print("❌ handle_transcription_and_tts error:", e, flush=True)
#         traceback.print_exc()


# # ---------------------------
# # WebSocket Handler
# # ---------------------------
# @sock.route("/ws")
# def ws_handler(ws):
#     print("🎧 WS client connected", flush=True)

#     # Create async loop in separate thread for transcription + tts tasks
#     loop = asyncio.new_event_loop()
#     threading.Thread(target=loop.run_forever, daemon=True).start()

#     # FFmpeg to convert incoming WebM (or other container) → 16kHz mono PCM s16le
#     ffmpeg_cmd = [
#         "ffmpeg", "-loglevel", "quiet", "-i", "pipe:0",
#         "-ar", "16000", "-ac", "1", "-f", "s16le", "pipe:1"
#     ]
#     process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

#     audio_queue = asyncio.Queue()
#     transcription_started = False
#     recording_started = False

#     # Background thread: read PCM from ffmpeg stdout and push to asyncio queue
#     def read_pcm():
#         try:
#             while True:
#                 data = process.stdout.read(4096)
#                 if not data:
#                     break
#                 # put bytes onto the queue in the transcription loop's event loop
#                 asyncio.run_coroutine_threadsafe(audio_queue.put(data), loop)
#         except Exception as e:
#             print("⚠ read_pcm error:", e, flush=True)

#     threading.Thread(target=read_pcm, daemon=True).start()

#     try:
#         while True:
#             msg = ws.receive()
#             if msg is None:
#                 print("ℹ Client disconnected", flush=True)
#                 break

#             try:
#                 obj = json.loads(msg)
#             except Exception as e:
#                 print("⚠ Invalid JSON:", e, msg, flush=True)
#                 continue

#             # AUDIO CHUNKS (only when recording started)
#             if obj.get("type") == "audio_chunk":
#                 audio_b64 = obj.get("data")
#                 if audio_b64 and recording_started:
#                     try:
#                         chunk = base64.b64decode(audio_b64)
#                         print(f"🔊 Received audio chunk size: {len(chunk)} bytes", flush=True)

#                         # Feed incoming chunk into ffmpeg stdin for conversion to PCM
#                         if process.stdin:
#                             process.stdin.write(chunk)
#                             process.stdin.flush()

#                         # Start transcription task only once
#                         if not transcription_started:
#                             # Start transcription coroutine on the separate loop
#                             asyncio.run_coroutine_threadsafe(
#                                 handle_transcription_and_tts(audio_queue, ws), loop
#                             )
#                             transcription_started = True
#                             print("ℹ Started transcription task", flush=True)

#                     except Exception as e:
#                         print("⚠ ffmpeg write/enqueue error:", e, flush=True)
#                 continue

#             # End-of-audio signal from client
#             if obj.get("type") == "end_of_audio":
#                 if not recording_started:
#                     print("⚠ Ignoring stray end_of_audio (no active recording)", flush=True)
#                     continue
#                 print("ℹ Received end_audio signal", flush=True)
#                 asyncio.run_coroutine_threadsafe(audio_queue.put(None), loop)
#                 continue

#             # Mic control
#             if obj.get("type") == "start_recording":
#                 print("ℹ Mic button pressed - recording started", flush=True)
#                 recording_started = True
#                 continue

#             if obj.get("type") == "stop_recording":
#                 print("ℹ Mic button released - recording stopped", flush=True)
#                 recording_started = False
#                 transcription_started = False   # reset so new press starts fresh transcription
#                 asyncio.run_coroutine_threadsafe(audio_queue.put(None), loop)
#                 continue

#     finally:
#         try:
#             if process.stdin:
#                 process.stdin.close()
#         except Exception:
#             pass
#         try:
#             process.wait(timeout=2)
#         except Exception:
#             process.kill()

#         # Ensure transcription coroutine finishes
#         try:
#             asyncio.run_coroutine_threadsafe(audio_queue.put(None), loop)
#         except Exception:
#             pass

#         print("✅ Browser connection closed cleanly", flush=True)


# # Silence favicon 404
# @app.route("/favicon.ico")
# def favicon():
#     return ("", 204)


# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host="0.0.0.0", port=port, debug=False)
