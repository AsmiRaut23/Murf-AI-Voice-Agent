# day15

# from flask import Flask
# from flask_sock import Sock

# app = Flask(__name__)
# sock = Sock(app)

# @sock.route('/ws')
# def ws_handler(ws):
#     while True:
#         data = ws.receive()
#         if data is None:
#             break
#         print(f"Received via WS: {data}")
#         ws.send(f"Echo: {data}")

# # if __name__ == "__main__":
# #     app.run(debug=True)

# if __name__ == "__main__":
#     app.run(debug=True, host='0.0.0.0')



#  day 16

# from flask import Flask, render_template
# from flask_sock import Sock
# import os
# from datetime import datetime
# import subprocess  # for ffmpeg conversion

# app = Flask(__name__)
# sock = Sock(app)

# # Ensure a recordings/ folder exists
# RECORDINGS_DIR = "recordings"
# os.makedirs(RECORDINGS_DIR, exist_ok=True)

# def new_filename(ext=".webm"):
#     ts = datetime.now().strftime("%Y%m%d-%H%M%S")
#     return os.path.join(RECORDINGS_DIR, f"recording-{ts}{ext}")

# # ---------- Routes ----------
# @app.route("/")
# def index():
#     return render_template("WebSocket.html")

# @sock.route('/ws')
# def ws_handler(ws):
#     print("WS client connected")

#     # Default: save as .webm
#     filepath = new_filename(".webm")
#     f = open(filepath, "wb")
#     print(f"Saving audio to: {filepath}")

#     try:
#         while True:
#             msg = ws.receive()
#             if msg is None:
#                 print("WS client disconnected")
#                 break

#             # Handle text messages
#             if isinstance(msg, str):
#                 print(f"WS text received: {msg}")

#                 # Client can tell us its MIME type
#                 if msg.startswith("mime:"):
#                     mime = msg.split(":", 1)[1].strip()
#                     if f.tell() == 0:  # only switch if file still empty
#                         f.close()
#                         ext = ".webm"
#                         if "ogg" in mime:
#                             ext = ".ogg"
#                         elif "wav" in mime:
#                             ext = ".wav"
#                         elif "mp3" in mime:
#                             ext = ".mp3"
#                         filepath = new_filename(ext)
#                         f = open(filepath, "wb")
#                         print(f"Switched file type, saving to: {filepath}")
#                 else:
#                     ws.send(f"Echo: {msg}")

#             # Handle binary messages (audio chunks)
#             else:
#                 f.write(msg)
#                 f.flush()
#                 print(f"Received {len(msg)} bytes of audio")

#     finally:
#         f.close()
#         print(f"Closed file: {filepath}")

#         # Auto-convert to WAV if it’s a .webm
#         if filepath.endswith(".webm"):
#             wav_path = filepath.replace(".webm", ".wav")
#             try:
#                 subprocess.run(
#                     ["ffmpeg", "-y", "-i", filepath, wav_path],
#                     stdout=subprocess.DEVNULL,
#                     stderr=subprocess.DEVNULL
#                 )
#                 print(f"Converted to WAV: {wav_path}")
#             except Exception as e:
#                 print(f"FFmpeg conversion failed: {e}")

# if __name__ == "__main__":
#     # app.run(debug=True, host='0.0.0.0', port=5000)
#     app.run(debug=True)





#  day 17
# import os
# import asyncio
# import websockets
# import subprocess
# import threading
# from flask import Flask, render_template
# from flask_sock import Sock
# from dotenv import load_dotenv

# load_dotenv()
# ASSEMBLYAI_KEY = os.getenv("ASSEMBLYAI_API_KEY")
# ASSEMBLYAI_URL = "wss://streaming.assemblyai.com/v3/ws"

# app = Flask(__name__)
# sock = Sock(app)

# @app.route("/")
# def index():
#     return render_template("WebSocket.html")

# async def transcribe_realtime(audio_queue, client_ws, loop):
#     async with websockets.connect(
#         ASSEMBLYAI_URL,
#         extra_headers={"Authorization": ASSEMBLYAI_KEY}
#     ) as aai_ws:
#         print("✅ Connected to AssemblyAI Realtime API")

#         async def send_audio():
#             while True:
#                 pcm_chunk = await audio_queue.get()
#                 if pcm_chunk is None:
#                     break
#                 await aai_ws.send(pcm_chunk)

#         async def recv_transcripts():
#             async for msg in aai_ws:
#                 print("📝 Transcript:", msg)
#                 # Forward transcript back to browser client
#                 try:
#                     client_ws.send(msg)
#                 except Exception as e:
#                     print("⚠️ Could not send to browser:", e)

#         await asyncio.gather(send_audio(), recv_transcripts())

# def start_transcriber(audio_queue, client_ws, loop):
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(transcribe_realtime(audio_queue, client_ws, loop))

# @sock.route('/ws')
# def ws_handler(ws):
#     print("🎧 WS client connected")

#     ffmpeg_cmd = [
#         "ffmpeg", "-loglevel", "quiet", "-i", "pipe:0",
#         "-ar", "16000", "-ac", "1", "-f", "s16le", "pipe:1"
#     ]
#     process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

#     audio_queue = asyncio.Queue()
#     loop = asyncio.new_event_loop()

#     def read_pcm():
#         while True:
#             data = process.stdout.read(4096)
#             if not data:
#                 break
#             asyncio.run_coroutine_threadsafe(audio_queue.put(data), loop)

#     threading.Thread(target=read_pcm, daemon=True).start()
#     threading.Thread(target=start_transcriber, args=(audio_queue, ws, loop), daemon=True).start()

#     try:
#         while True:
#             msg = ws.receive()
#             if msg is None:
#                 break
#             if isinstance(msg, str):
#                 print("Text message:", msg)
#             else:
#                 process.stdin.write(msg)
#                 process.stdin.flush()
#     finally:
#         process.stdin.close()
#         process.wait()
#         asyncio.run_coroutine_threadsafe(audio_queue.put(None), loop)
#         print("❌ WS client disconnected")

# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5000)




# day 18
# import os
# import asyncio
# import websockets
# import subprocess
# import threading
# import json
# from flask import Flask, render_template
# from flask_sock import Sock
# from dotenv import load_dotenv

# load_dotenv()
# ASSEMBLYAI_KEY = os.getenv("ASSEMBLYAI_API_KEY")
# ASSEMBLYAI_URL = "wss://streaming.assemblyai.com/v3/ws"

# app = Flask(__name__)
# sock = Sock(app)

# @app.route("/")
# def index():
#     return render_template("WebSocket.html")

# async def transcribe_realtime(audio_queue, client_ws, loop):
#     async with websockets.connect(
#         ASSEMBLYAI_URL,
#         extra_headers={"Authorization": ASSEMBLYAI_KEY}
#     ) as aai_ws:
#         print("✅ Connected to AssemblyAI Realtime API")

#         async def send_audio():
#             while True:
#                 pcm_chunk = await audio_queue.get()
#                 if pcm_chunk is None:
#                     break
#                 await aai_ws.send(pcm_chunk)

#         async def recv_transcripts():
#             async for msg in aai_ws:
#                 try:
#                     data = json.loads(msg)
#                     if data.get("type") == "Turn":
#                         print(f"\n📝 Transcript (Turn {data.get('turn_order')}): {data.get('transcript')}")
#                         if "words" in data:
#                             for w in data["words"]:
#                                 print(f"  start={w['start']}, end={w['end']}, text='{w['text']}', "
#                                       f"confidence={w['confidence']:.2f}, word_is_final={w['word_is_final']}")
#                         if data.get("end_of_turn"):
#                             print("✅ End of Turn Reached\n")
#                     else:
#                         print("📝 Transcript:", data)

#                     # still forward the raw JSON to browser
#                     client_ws.send(msg)

#                 except Exception as e:
#                     print("⚠️ Could not process message:", e)
#                     print("📝 Raw:", msg)

#         await asyncio.gather(send_audio(), recv_transcripts())

# def start_transcriber(audio_queue, client_ws, loop):
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(transcribe_realtime(audio_queue, client_ws, loop))

# @sock.route('/ws')
# def ws_handler(ws):
#     print("🎧 WS client connected")

#     ffmpeg_cmd = [
#         "ffmpeg", "-loglevel", "quiet", "-i", "pipe:0",
#         "-ar", "16000", "-ac", "1", "-f", "s16le", "pipe:1"
#     ]
#     process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

#     audio_queue = asyncio.Queue()
#     loop = asyncio.new_event_loop()

#     def read_pcm():
#         while True:
#             data = process.stdout.read(4096)
#             if not data:
#                 break
#             asyncio.run_coroutine_threadsafe(audio_queue.put(data), loop)

#     threading.Thread(target=read_pcm, daemon=True).start()
#     threading.Thread(target=start_transcriber, args=(audio_queue, ws, loop), daemon=True).start()

#     try:
#         while True:
#             msg = ws.receive()
#             if msg is None:
#                 break
#             if isinstance(msg, str):
#                 print("Text message:", msg)
#             else:
#                 process.stdin.write(msg)
#                 process.stdin.flush()
#     finally:
#         process.stdin.close()
#         process.wait()
#         asyncio.run_coroutine_threadsafe(audio_queue.put(None), loop)
#         print("❌ WS client disconnected")

# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5000)












# day 19
# import os
# import asyncio
# import websockets
# import subprocess
# import threading
# import json
# from flask import Flask, render_template
# from flask_sock import Sock
# from dotenv import load_dotenv
# import google.generativeai as genai  # ✅ Gemini SDK

# load_dotenv()
# ASSEMBLYAI_KEY = os.getenv("ASSEMBLYAI_API_KEY")
# ASSEMBLYAI_URL = "wss://streaming.assemblyai.com/v3/ws"

# GEMINI_KEY = os.getenv("GEMINI_API_KEY")   # ✅ your Gemini API key
# genai.configure(api_key=GEMINI_KEY)

# app = Flask(__name__)
# sock = Sock(app)

# @app.route("/")
# def index():
#     return render_template("WebSocket.html")

# async def stream_llm_response(prompt: str):
#     """Send transcript to Gemini and stream back response."""
#     model = genai.GenerativeModel("gemini-1.5-flash")
#     response = model.generate_content(prompt, stream=True)
#     print("\n🤖 LLM Response:")
#     full_text = ""
#     for chunk in response:
#         if chunk.text:
#             print(chunk.text, end="", flush=True)
#             full_text += chunk.text
#     print("\n✅ End of LLM Response\n")
#     return full_text

# async def transcribe_realtime(audio_queue, client_ws, loop):
#     async with websockets.connect(
#         ASSEMBLYAI_URL,
#         extra_headers={"Authorization": ASSEMBLYAI_KEY}
#     ) as aai_ws:
#         print("✅ Connected to AssemblyAI Realtime API")

#         async def send_audio():
#             while True:
#                 pcm_chunk = await audio_queue.get()
#                 if pcm_chunk is None:
#                     break
#                 await aai_ws.send(pcm_chunk)

#         async def recv_transcripts():
#             async for msg in aai_ws:
#                 try:
#                     data = json.loads(msg)
#                     if data.get("type") == "Turn":
#                         print(f"\n📝 Transcript (Turn {data.get('turn_order')}): {data.get('transcript')}")
                        
#                         if data.get("end_of_turn"):
#                             print("✅ End of Turn Reached")
#                             # ✅ Send transcript to Gemini
#                             asyncio.create_task(stream_llm_response(data["transcript"]))
#                     # forward raw JSON to browser
#                     client_ws.send(msg)

#                 except Exception as e:
#                     print("⚠️ Could not process message:", e)
#                     print("📝 Raw:", msg)

#         await asyncio.gather(send_audio(), recv_transcripts())

# def start_transcriber(audio_queue, client_ws, loop):
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(transcribe_realtime(audio_queue, client_ws, loop))

# @sock.route('/ws')
# def ws_handler(ws):
#     print("🎧 WS client connected")

#     ffmpeg_cmd = [
#         "ffmpeg", "-loglevel", "quiet", "-i", "pipe:0",
#         "-ar", "16000", "-ac", "1", "-f", "s16le", "pipe:1"
#     ]
#     process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

#     audio_queue = asyncio.Queue()
#     loop = asyncio.new_event_loop()

#     def read_pcm():
#         while True:
#             data = process.stdout.read(4096)
#             if not data:
#                 break
#             asyncio.run_coroutine_threadsafe(audio_queue.put(data), loop)

#     threading.Thread(target=read_pcm, daemon=True).start()
#     threading.Thread(target=start_transcriber, args=(audio_queue, ws, loop), daemon=True).start()

#     try:
#         while True:
#             msg = ws.receive()
#             if msg is None:
#                 break
#             if isinstance(msg, str):
#                 print("Text message:", msg)
#             else:
#                 process.stdin.write(msg)
#                 process.stdin.flush()
#     finally:
#         process.stdin.close()
#         process.wait()
#         asyncio.run_coroutine_threadsafe(audio_queue.put(None), loop)
#         print("❌ WS client disconnected")

# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5000)









# day 20
# import os
# import asyncio
# import websockets
# import subprocess
# import threading
# import json
# from flask import Flask, render_template
# from flask_sock import Sock
# from dotenv import load_dotenv
# import google.generativeai as genai  # ✅ Gemini SDK
# # import uuid
# import traceback


# load_dotenv()
# ASSEMBLYAI_KEY = os.getenv("ASSEMBLYAI_API_KEY")
# ASSEMBLYAI_URL = "wss://streaming.assemblyai.com/v3/ws"

# GEMINI_KEY = os.getenv("GEMINI_API_KEY")   # ✅ Gemini API key
# genai.configure(api_key=GEMINI_KEY)

# MURF_KEY = os.getenv("MURF_API_KEY").strip()       # ✅ Murf API key
# print(f"MURF_KEY loaded:")

# MURF_URL = "wss://api.murf.ai/v1/speech/stream-input"   # ✅ Murf WebSocket TTS endpoint
# # MURF_CONTEXT_ID = f"day20-{uuid.uuid4()}"   # ✅ Static context_id

# app = Flask(__name__)
# sock = Sock(app)

# @app.route("/")
# def index():
#     return render_template("WebSocket.html")

# # ---------------------------
# # Gemini LLM (streaming text)
# # ---------------------------
# async def stream_llm_response(prompt: str):
#     model = genai.GenerativeModel("gemini-1.5-flash")
#     response = model.generate_content(prompt, stream=True)
#     print("\n🤖 LLM Response:")
#     full_text = ""
#     for chunk in response:
#         if chunk.text:
#             print(chunk.text, end="", flush=True)
#             full_text += chunk.text
#     print("\n✅ End of LLM Response\n")
#     return full_text

# # ---------------------------
# # Murf WebSocket TTS
# # ---------------------------
# async def send_to_murf(text: str, client_ws=None):
#     """Send Gemini's response to Murf, get back base64 audio."""

#     # ✅ Generate a new context_id per session (fixes exceeded context limit)
#     context_id = "day20-STATIC-12345"  # Use any fixed value
#     print(f"🎯 Using Murf context_id: {context_id}")

#     ws_url = f"{MURF_URL}?api-key={MURF_KEY}&sample_rate=16000&channel_type=MONO&format=mp3"
#     # ws_url = f"{MURF_URL}?api-key={MURF_KEY}&channel_type=MONO"
#     async with websockets.connect(ws_url) as ws:

#     # async with websockets.connect(
#     #     MURF_URL,
#     #     extra_headers={"Authorization": f"Bearer {MURF_KEY}"}
#     # ) as murf_ws:
#         # ✅ Step 1: Send config
#         await ws.send(json.dumps({
#             "type": "config",
#             "context_id": context_id,
#             "voice_config": {
#             "voiceId": "en-US-natalie",
#             "voice_gender": "female",
#             "language": "en-US"
#             },
#             "format": "mp3",          # Use compressed format!
#             "sample_rate": 16000,      # Lower sample rate
#         }))


#         # await asyncio.sleep(0.2)
   

#         # ✅ Step 2: Send text (use "speak")
#         await ws.send(json.dumps({
#             "type": "speak",
#             "context_id": context_id,
#             "text": text
#         }))

#         print("\n🎤 Murf Audio Response (base64 chunks):")
#         async for msg in ws:
#             print("🔎(base64 chunks):", msg)
#             data = json.loads(msg)

#             if data.get("type") == "audio" and "audio" in data:
#                 print(data["audio"])
#                 if client_ws:
#                     await client_ws.send(json.dumps({
#                         "type": "murf_audio",
#                         "audio": data["audio"]
#                     }))

#             elif data.get("type") == "speak_end":
#                 print("✅ End of Murf Audio Response\n")
#                 break










# # ---------------------------
# # AssemblyAI Streaming (Speech → Text)
# # ---------------------------
# async def transcribe_realtime(audio_queue, client_ws, loop):
#     async with websockets.connect(
#         ASSEMBLYAI_URL,
#         extra_headers={"Authorization": ASSEMBLYAI_KEY}
#     ) as aai_ws:
#         print("✅ Connected to AssemblyAI Realtime API")

#         async def send_audio():
#             while True:
#                 pcm_chunk = await audio_queue.get()
#                 if pcm_chunk is None:
#                     break
#                 await aai_ws.send(pcm_chunk)

#         async def recv_transcripts():
#             async for msg in aai_ws:
#                 try:
#                     data = json.loads(msg)
#                     if data.get("type") == "Turn":
#                         print(f"\n📝 Transcript (Turn {data.get('turn_order')}): {data.get('transcript')}")
                        
#                         if data.get("end_of_turn"):
#                             print("✅ End of Turn Reached")
#                             # ✅ Send transcript to Gemini → then to Murf
#                             async def process_turn():
#                                 llm_text = await stream_llm_response(data["transcript"])
#                                 await send_to_murf(llm_text, client_ws)

#                             asyncio.create_task(process_turn())
                    
#                     # Forward raw JSON to browser
                 
#                     if client_ws is not None:
#                         client_ws.send(msg)

#                 except Exception as e:
#                     print("⚠️ Could not process message:", e)
#                     print("📝 Raw:", msg)
#                     traceback.print_exc()

#         await asyncio.gather(send_audio(), recv_transcripts())

# # ---------------------------
# # Flask WebSocket Handler
# # ---------------------------
# def start_transcriber(audio_queue, client_ws, loop):
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(transcribe_realtime(audio_queue, client_ws, loop))

# @sock.route('/ws')
# def ws_handler(ws):
#     print("🎧 WS client connected")

#     ffmpeg_cmd = [
#         "ffmpeg", "-loglevel", "quiet", "-i", "pipe:0",
#         "-ar", "16000", "-ac", "1", "-f", "s16le", "pipe:1"
#     ]
#     process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

#     audio_queue = asyncio.Queue()
#     loop = asyncio.new_event_loop()

#     def read_pcm():
#         while True:
#             data = process.stdout.read(4096)
#             if not data:
#                 break
#             asyncio.run_coroutine_threadsafe(audio_queue.put(data), loop)

#     threading.Thread(target=read_pcm, daemon=True).start()
#     threading.Thread(target=start_transcriber, args=(audio_queue, ws, loop), daemon=True).start()

#     try:
#         while True:
#             msg = ws.receive()
#             if msg is None:
#                 break
#             if isinstance(msg, str):
#                 print("Text message:", msg)
#             else:
#                 process.stdin.write(msg)
#                 process.stdin.flush()
#     finally:
#         process.stdin.close()
#         process.wait()
#         asyncio.run_coroutine_threadsafe(audio_queue.put(None), loop)
#         print(" Connection closed")

# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5000)





# day 21
# import os
# import asyncio
# import websockets
# import subprocess
# import threading
# import json
# from flask import Flask, render_template
# from flask_sock import Sock
# from dotenv import load_dotenv
# import google.generativeai as genai
# import traceback

# load_dotenv()
# ASSEMBLYAI_KEY = os.getenv("ASSEMBLYAI_API_KEY")
# ASSEMBLYAI_URL = "wss://streaming.assemblyai.com/v3/ws"

# GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# genai.configure(api_key=GEMINI_KEY)

# MURF_KEY = os.getenv("MURF_API_KEY").strip()
# print(f"MURF_KEY loaded:")

# MURF_URL = "wss://api.murf.ai/v1/speech/stream-input"

# app = Flask(__name__)
# sock = Sock(app)

# @app.route("/")
# def index():
#     return render_template("WebSocket.html")

# # ---------------------------
# # Gemini LLM (streaming text)
# # ---------------------------
# async def stream_llm_response(prompt: str):
#     model = genai.GenerativeModel("gemini-1.5-flash")
#     response = model.generate_content(prompt, stream=True)
#     print("\n🤖 LLM Response:")
#     full_text = ""
#     for chunk in response:
#         if chunk.text:
#             print(chunk.text, end="", flush=True)
#             full_text += chunk.text
#     print("\n✅ End of LLM Response\n")
#     return full_text

# # ---------------------------
# # Murf WebSocket TTS
# # ---------------------------
# async def send_to_murf(text: str, client_ws=None):
#     """Send Gemini's response to Murf, get back base64 audio."""

#     if not text.strip():
#         print("⚠️ Empty text, skipping Murf TTS")
#         return
#     # Generate a static context_id
#     context_id = "day21-STATIC-12345"  # Updated for Day 21
#     print(f"🎯 Using Murf context_id: {context_id}")

#     ws_url = f"{MURF_URL}?api-key={MURF_KEY}&sample_rate=16000&channel_type=MONO&format=mp3"
#     async with websockets.connect(ws_url) as ws:
#         # Step 1: Send config
#         await ws.send(json.dumps({
#             "type": "config",
#             "context_id": context_id,
#             "voice_config": {
#                 "voiceId": "en-US-natalie",
#                 "voice_gender": "female",
#                 "language": "en-US"
#             },
#             "format": "mp3",
#             "sample_rate": 16000,
#         }))

#         # Step 2: Send text (use "speak")
#         await ws.send(json.dumps({
#             "type": "speak",
#             "context_id": context_id,
#             "text": text
#         }))

#         print("\n🎤 Murf Audio Response (base64 chunks):")
#         async for msg in ws:
#             print("🔎(base64 chunks):", msg)
#             data = json.loads(msg)
#             print("🔎 Murf raw message keys:", list(data.keys())) # ✅ Debugging print

#             if data.get("type") == "audio" and "audio" in data:
#             # if "audio" in data:
#                 # print(data["audio"])
#                 audio_b64 = data["audio"]
#                 # 🔽 Break into smaller chunks (e.g., 4 KB each)
#                 chunk_size = 100  
#                 for i in range(0, len(audio_b64), chunk_size):
#                     chunk = audio_b64[i:i+chunk_size]

#                     print("🔊 Got audio chunk from Murf")  # ✅ Debugging print
#                     if client_ws:
#                         print("➡️ Forwarding audio chunk to client")
#                         client_ws.send(json.dumps({
#                             "type": "murf_audio",
#                             "audio": chunk
#                             # "audio": data["audio"]
#                     }))
#                 print(f"🔎 Murf audio split into {len(audio_b64)//chunk_size + 1} chunks")

#             elif data.get("type") == "speak_end":
#                 print("✅ End of Murf Audio Response\n")
#                 if client_ws:
#                     client_ws.send(json.dumps({
#                         "type": "murf_audio_end"
#                     }))
#                 break

# # ---------------------------
# # AssemblyAI Streaming (Speech → Text)
# # ---------------------------
# async def transcribe_realtime(audio_queue, client_ws, loop):
#     async with websockets.connect(
#         ASSEMBLYAI_URL,
#         extra_headers={"Authorization": ASSEMBLYAI_KEY}
#     ) as aai_ws:
#         print("✅ Connected to AssemblyAI Realtime API")

#         async def send_audio():
#             while True:
#                 pcm_chunk = await audio_queue.get()
#                 if pcm_chunk is None:
#                     break
#                 await aai_ws.send(pcm_chunk)

#         async def recv_transcripts():
#             async for msg in aai_ws:
#                 try:
#                     data = json.loads(msg)
#                     if data.get("type") == "Turn":
#                         print(f"\n📝 Transcript (Turn {data.get('turn_order')}): {data.get('transcript')}")
                        
#                         if data.get("end_of_turn"):
#                             print("✅ End of Turn Reached")
#                             # Send transcript to Gemini → then to Murf
#                             async def process_turn():
#                                 llm_text = await stream_llm_response(data["transcript"])
#                                 await send_to_murf(llm_text, client_ws)

#                             asyncio.create_task(process_turn())
                    
#                     # Forward raw JSON to browser
#                     if client_ws is not None:
#                         client_ws.send(msg)

#                 except Exception as e:
#                     print("⚠️ Could not process message:", e)
#                     print("📝 Raw:", msg)
#                     traceback.print_exc()

#         await asyncio.gather(send_audio(), recv_transcripts())

# # ---------------------------
# # Flask WebSocket Handler
# # ---------------------------
# def start_transcriber(audio_queue, client_ws, loop):
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(transcribe_realtime(audio_queue, client_ws, loop))

# @sock.route('/ws')
# def ws_handler(ws):
#     print("🎧 WS client connected")

#     ffmpeg_cmd = [
#         "ffmpeg", "-loglevel", "quiet", "-i", "pipe:0",
#         "-ar", "16000", "-ac", "1", "-f", "s16le", "pipe:1"
#     ]
#     process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

#     audio_queue = asyncio.Queue()
#     loop = asyncio.new_event_loop()

#     def read_pcm():
#         while True:
#             data = process.stdout.read(4096)
#             if not data:
#                 break
#             asyncio.run_coroutine_threadsafe(audio_queue.put(data), loop)

#     threading.Thread(target=read_pcm, daemon=True).start()
#     threading.Thread(target=start_transcriber, args=(audio_queue, ws, loop), daemon=True).start()

#     try:
#         while True:
#             try:
#                 msg = ws.receive() 
#             except Exception as e:
#                 print("⚠️ WS receive error (likely client closed):", e)
#                 break
#             if msg is None:
#                 break
            
#             if isinstance(msg, (bytes, bytearray)):   # <-- Binary audio chunks
#                 process.stdin.write(msg)
#                 process.stdin.flush()
#             else:
#                 print("Text message:", msg)
#     finally:
#         try:
#             process.stdin.close()
#         except:
#             pass
#         process.wait()
#         asyncio.run_coroutine_threadsafe(audio_queue.put(None), loop)
#         print("✅ Connection closed cleanly")

# if __name__ == "__main__":
#     app.run(debug=False, host="0.0.0.0", port=5000)








# day 22
# import os
# import asyncio
# import websockets
# import subprocess
# import threading
# import json
# import base64
# import traceback
# from flask import Flask, render_template
# from flask_sock import Sock
# from dotenv import load_dotenv
# import google.generativeai as genai

# load_dotenv()

# ASSEMBLYAI_KEY = os.getenv("ASSEMBLYAI_API_KEY")
# ASSEMBLYAI_URL = "wss://streaming.assemblyai.com/v3/ws"

# GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# genai.configure(api_key=GEMINI_KEY)

# MURF_KEY = os.getenv("MURF_API_KEY").strip()
# MURF_URL = "wss://api.murf.ai/v1/speech/stream-input"

# app = Flask(__name__)
# sock = Sock(app)

# @app.route("/")
# def index():
#     return render_template("WebSocket.html")

# # ---------------------------
# # Gemini LLM (streaming text)
# # ---------------------------
# async def stream_llm_response(prompt: str):
#     model = genai.GenerativeModel("gemini-1.5-flash")
#     response = model.generate_content(prompt, stream=True)
#     print("\n🤖 Gemini Response:")
#     full_text = ""
#     for chunk in response:
#         if chunk.text:
#             print(chunk.text, end="", flush=True)
#             full_text += chunk.text
#     print("\n✅ End of Gemini Response\n")
#     return full_text

# def safe_send(ws, message: str):
#     try:
#         ws.send(message)
#     except Exception as e:
#         print("❌ send failed:", e)

# # ---------------------------
# # Murf TTS (streamed)
# # ---------------------------
# async def send_to_murf(text: str, client_ws=None):
#     if not text.strip():
#         print("⚠️ Empty text, skipping Murf TTS")
#         return

#     print(f"\n🚀 send_to_murf CALLED with text: {text}\n")
#     ws_url = f"{MURF_URL}?api-key={MURF_KEY}&sample_rate=16000&channel_type=MONO&format=mp3"

#     sent_end = False
#     try:
#         async with websockets.connect(ws_url) as ws:
#             print("✅ Connected to Murf WS")

#             await ws.send(json.dumps({
#                 "type": "config",
#                 "context_id": "day22-demo",
#                 "voice_config": {
#                     "voiceId": "en-US-natalie",
#                     "voice_gender": "female",
#                     "language": "en-US"
#                 },
#                 "format": "mp3",
#                 "sample_rate": 16000,
#             }))
#             print("📨 Sent Murf config")

#             await ws.send(json.dumps({
#                 "type": "speak",
#                 "context_id": "day22-demo",
#                 "text": text
#             }))
#             print("📨 Sent speak text to Murf")

#             async for msg in ws:
#                 try:
#                     data = json.loads(msg)

#                     if "audio" in data:
#                         audio_b64 = data["audio"]
#                         print(f"🔊 Got Murf audio chunk, size={len(audio_b64)}")
#                         if client_ws:
#                             threading.Thread(
#                                 target=safe_send,
#                                 args=(client_ws, json.dumps({"type": "murf_audio","audio": audio_b64})),
#                                 daemon=True
#                             ).start()

#                     elif data.get("type") in (
#                         "speak_end", "completed", "response_end", "audio_end", "end"
#                     ):
#                         print("✅ End of Murf Audio Response\n")
#                         if client_ws:
#                             threading.Thread(
#                                 target=safe_send,
#                                 args=(client_ws, json.dumps({"type": "murf_audio_end"})),
#                                 daemon=True
#                             ).start()
#                         sent_end = True
#                         break

#                 except Exception as e:
#                     print("⚠️ Error parsing Murf msg:", e, msg)

#     except websockets.ConnectionClosed as e:
#         print("ℹ️ Murf WS closed:", e)
#     except Exception as e:
#         print("❌ Murf error:", e)
#     finally:
#         # Guarantee the client always receives a terminator
#         if client_ws and not sent_end:
#             threading.Thread(
#                 target=safe_send,
#                 args=(client_ws, json.dumps({"type": "murf_audio_end"})),
#                 daemon=True
#             ).start()

# # ---------------------------
# # AssemblyAI Streaming
# # ---------------------------
# async def transcribe_realtime(audio_queue, client_ws, loop):
#     async with websockets.connect(
#         ASSEMBLYAI_URL,
#         extra_headers={"Authorization": ASSEMBLYAI_KEY}
#     ) as aai_ws:
#         print("✅ Connected to AssemblyAI Realtime API")

#         async def send_audio():
#             while True:
#                 pcm_chunk = await audio_queue.get()
#                 if pcm_chunk is None:
#                     break
#                 await aai_ws.send(pcm_chunk)

#         async def recv_transcripts():
#             async for msg in aai_ws:
#                 try:
#                     data = json.loads(msg)
#                     if data.get("type") == "Turn":
#                         print(f"\n📝 Transcript (Turn {data.get('turn_order')}): {data.get('transcript')}")
#                         if data.get("end_of_turn"):
#                             print("✅ End of Turn Reached")
#                             async def process_turn():
#                                 llm_text = await stream_llm_response(data["transcript"])
#                                 await send_to_murf(llm_text, client_ws)
#                             asyncio.create_task(process_turn())

#                     if client_ws:
#                         try:
#                             client_ws.send(msg)
#                         except Exception as e:
#                             print("❌ WS send failed:", e)

#                 except Exception as e:
#                     print("⚠️ Could not process AAI msg:", e)
#                     traceback.print_exc()

#         await asyncio.gather(send_audio(), recv_transcripts())

# def start_transcriber(audio_queue, client_ws, loop):
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(transcribe_realtime(audio_queue, client_ws, loop))

# # ---------------------------
# # Flask WebSocket Handler
# # ---------------------------
# @sock.route('/ws')
# def ws_handler(ws):
#     print("🎧 WS client connected")

#     ffmpeg_cmd = [
#         "ffmpeg", "-loglevel", "quiet", "-i", "pipe:0",
#         "-ar", "16000", "-ac", "1", "-f", "s16le", "pipe:1"
#     ]
#     process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

#     audio_queue = asyncio.Queue()
#     loop = asyncio.new_event_loop()

#     def read_pcm():
#         while True:
#             data = process.stdout.read(4096)
#             if not data:
#                 break
#             asyncio.run_coroutine_threadsafe(audio_queue.put(data), loop)

#     threading.Thread(target=read_pcm, daemon=True).start()
#     threading.Thread(target=start_transcriber, args=(audio_queue, ws, loop), daemon=True).start()

#     try:
#         while True:
#             try:
#                 msg = ws.receive()
#             except Exception as e:
#                 print("⚠️ WS receive error:", e)
#                 break
#             if msg is None:
#                 break

#             try:
#                 obj = json.loads(msg)
#                 if obj.get("type") == "audio_chunk":
#                     chunk = base64.b64decode(obj["data"])
#                     process.stdin.write(chunk)
#                     process.stdin.flush()
#             except Exception as e:
#                 print("⚠️ Bad msg:", e, msg)

#     finally:
#         try:
#             process.stdin.close()
#         except:
#             pass
#         process.wait()
#         asyncio.run_coroutine_threadsafe(audio_queue.put(None), loop)
#         print("✅ Connection closed cleanly")

# # (optional) silence favicon 404
# @app.route('/favicon.ico')
# def favicon():
#     return ('', 204)

# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5000)












# import os
# import asyncio
# import websockets
# import subprocess
# import threading
# import json
# import base64
# import traceback
# import uuid
# from flask import Flask, render_template
# from flask_sock import Sock
# from dotenv import load_dotenv
# import google.generativeai as genai

# load_dotenv()

# ASSEMBLYAI_KEY = os.getenv("ASSEMBLYAI_API_KEY")
# ASSEMBLYAI_URL = "wss://streaming.assemblyai.com/v3/ws"

# GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# genai.configure(api_key=GEMINI_KEY)

# MURF_KEY = os.getenv("MURF_API_KEY").strip()
# MURF_URL = "wss://api.murf.ai/v1/speech/stream-input"

# app = Flask(__name__)
# sock = Sock(app)

# # ---------------------------
# # Conversation history
# # ---------------------------
# # NOTE: this is per-process memory. For production use a db or per-session store.
# chat_history = []  # list of {"role": "user"|"assistant", "text": "..."} 

# @app.route("/")
# def index():
#     return render_template("WebSocket.html")

# # ---------------------------
# # Gemini LLM (streaming text) - uses chat_history
# # ---------------------------
# async def stream_llm_response(prompt_text: str):
#     """
#     Append user prompt to chat_history, stream LLM response, append assistant reply,
#     and return full reply text.
#     """
#     global chat_history
#     chat_history.append({"role": "user", "text": prompt_text})

#     model = genai.GenerativeModel("gemini-1.5-flash")

#     # Build a single prompt string from the chat history (simple format)
#     prompt = ""
#     for turn in chat_history:
#         role = "User" if turn["role"] == "user" else "Assistant"
#         prompt += f"{role}: {turn['text']}\n"
#     prompt += "Assistant:"  # hint to LLM

#     print("\n🤖 Gemini Response (streaming):")
#     full_text = ""
#     response = model.generate_content(prompt, stream=True)
#     for chunk in response:
#         if getattr(chunk, "text", None):
#             print(chunk.text, end="", flush=True)
#             full_text += chunk.text
#     print("\n✅ End of Gemini Response\n")

#     # Save assistant reply into history
#     chat_history.append({"role": "assistant", "text": full_text})
#     return full_text

# def safe_send(ws, message: str):
#     """Send to client WS in a thread to avoid blocking async loops."""
#     try:
#         ws.send(message)
#     except Exception as e:
#         print("❌ safe_send failed:", e)

# # ---------------------------
# # Murf TTS (streamed)
# # ---------------------------
# async def send_to_murf(text: str, client_ws=None):
#     """Stream text to Murf TTS and forward audio chunks to client_ws."""
#     if not text or not text.strip():
#         print("⚠️ Empty text, skipping Murf TTS")
#         return

#     ctx = f"day23-{uuid.uuid4().hex[:8]}"
#     print(f"\n🚀 send_to_murf CALLED (ctx={ctx}) text len={len(text)}\n")
#     ws_url = f"{MURF_URL}?api-key={MURF_KEY}&sample_rate=16000&channel_type=MONO&format=mp3"

#     sent_end = False
#     try:
#         async with websockets.connect(ws_url, max_size=None) as ws:
#             print("✅ Connected to Murf WS")

#             # config
#             await ws.send(json.dumps({
#                 "type": "config",
#                 "context_id": ctx,
#                 "voice_config": {
#                     "voiceId": "en-US-natalie",
#                     "voice_gender": "female",
#                     "language": "en-US"
#                 },
#                 "format": "mp3",
#                 "sample_rate": 16000
#             }))
#             print("📨 Sent Murf config")

#             # speak
#             await ws.send(json.dumps({
#                 "type": "speak",
#                 "context_id": ctx,
#                 "text": text
#             }))
#             print("📨 Sent speak text to Murf")

#             # stream messages from Murf and forward audio chunks to client_ws
#             async for msg in ws:
#                 try:
#                     data = json.loads(msg)
#                 except Exception:
#                     # Murf sometimes sends non-json or binary; skip if parse fail
#                     print("⚠️ Non-json Murf message (skipping)")
#                     continue

#                 # If audio chunk present (Murf uses "audio" field)
#                 if "audio" in data:
#                     audio_b64 = data["audio"]
#                     # forward to client
#                     if client_ws:
#                         threading.Thread(
#                             target=safe_send,
#                             args=(client_ws, json.dumps({"type": "murf_audio", "audio": audio_b64})),
#                             daemon=True
#                         ).start()
#                     print("🔊 forwarded Murf chunk, size=", len(audio_b64))

#                 # end events
#                 elif data.get("type") in ("speak_end", "completed", "response_end", "audio_end", "end"):
#                     print("✅ Murf signalled end of response")
#                     if client_ws:
#                         threading.Thread(
#                             target=safe_send,
#                             args=(client_ws, json.dumps({"type": "murf_audio_end"})),
#                             daemon=True
#                         ).start()
#                     sent_end = True
#                     break

#     except websockets.ConnectionClosed as e:
#         print("ℹ️ Murf WS closed:", e)
#     except Exception as e:
#         print("❌ Murf error:", e)
#         traceback.print_exc()
#     finally:
#         # ensure client always receives a terminator
#         if client_ws and not sent_end:
#             try:
#                 threading.Thread(
#                     target=safe_send,
#                     args=(client_ws, json.dumps({"type": "murf_audio_end"})),
#                     daemon=True
#                 ).start()
#             except Exception as e:
#                 print("❌ failed to send murf_audio_end in finally:", e)

# # ---------------------------
# # AssemblyAI Streaming (transcribe realtime)
# # ---------------------------
# async def transcribe_realtime(audio_queue, client_ws, loop):
#     """
#     Connects to AssemblyAI Realtime and forwards audio (PCM) from audio_queue.
#     For each 'Turn' (interim/final) received, forward to client_ws.
#     On final turn (end_of_turn) call the LLM and TTS pipeline.
#     """
#     async with websockets.connect(
#         ASSEMBLYAI_URL,
#         extra_headers={"Authorization": ASSEMBLYAI_KEY},
#         max_size=None
#     ) as aai_ws:
#         print("✅ Connected to AssemblyAI Realtime API")

#         async def send_audio():
#             while True:
#                 pcm_chunk = await audio_queue.get()
#                 if pcm_chunk is None:
#                     break
#                 # AssemblyAI expects base64 audio frames (depending on API spec).
#                 # The user's previous code sent raw PCM bytes directly; keep the same:
#                 try:
#                     await aai_ws.send(pcm_chunk)
#                 except Exception as e:
#                     print("❌ Failed to send audio to AssemblyAI:", e)
#                     break

#         async def recv_transcripts():
#             async for msg in aai_ws:
#                 try:
#                     data = json.loads(msg)
#                 except Exception:
#                     continue

#                 # Forward raw AAI message to client (so frontend can display interim/final)
#                 if client_ws:
#                     try:
#                         client_ws.send(msg)
#                     except Exception as e:
#                         print("❌ WS send to client failed:", e)

#                 # When AAI sends a Turn object, handle end_of_turn
#                 if data.get("type") == "Turn":
#                     transcript = data.get("transcript", "")
#                     print(f"\n📝 Transcript (Turn): {transcript}")

#                     if data.get("end_of_turn"):
#                         print("✅ End of Turn Reached - processing")
#                         # Process turn: send to Gemini, then send its output to Murf TTS
#                         async def process_turn():
#                             try:
#                                 llm_text = await stream_llm_response(transcript)

#                                 # *** NEW: Send Gemini text back to browser so UI can show it ***
#                                 if client_ws:
#                                     threading.Thread(
#                                         target=safe_send,
#                                         args=(client_ws, json.dumps({"type": "gemini_response", "text": llm_text})),
#                                         daemon=True
#                                     ).start()

#                                 # send to Murf and forward audio to client
#                                 await send_to_murf(llm_text, client_ws)
#                             except Exception as e:
#                                 print("❌ process_turn error:", e)
#                                 traceback.print_exc()
#                         # schedule (do not block recv_transcripts)
#                         asyncio.create_task(process_turn())

#         await asyncio.gather(send_audio(), recv_transcripts())

# def start_transcriber(audio_queue, client_ws, loop):
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(transcribe_realtime(audio_queue, client_ws, loop))

# # ---------------------------
# # Flask WebSocket Handler (client ↔ server)
# # ---------------------------
# @sock.route('/ws')
# def ws_handler(ws):
#     print("🎧 WS client connected (browser)")

#     # start ffmpeg to convert incoming webm chunks to s16le PCM for AssemblyAI
#     ffmpeg_cmd = [
#         "ffmpeg", "-loglevel", "quiet", "-i", "pipe:0",
#         "-ar", "16000", "-ac", "1", "-f", "s16le", "pipe:1"
#     ]
#     process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

#     audio_queue = asyncio.Queue()
#     loop = asyncio.new_event_loop()

#     # thread to read PCM from ffmpeg stdout and push to audio_queue
#     def read_pcm():
#         try:
#             while True:
#                 data = process.stdout.read(4096)
#                 if not data:
#                     break
#                 asyncio.run_coroutine_threadsafe(audio_queue.put(data), loop)
#         except Exception as e:
#             print("⚠️ read_pcm error:", e)

#     threading.Thread(target=read_pcm, daemon=True).start()
#     threading.Thread(target=start_transcriber, args=(audio_queue, ws, loop), daemon=True).start()

#     try:
#         while True:
#             try:
#                 msg = ws.receive()
#             except Exception as e:
#                 print("⚠️ WS receive error:", e)
#                 break
#             if msg is None:
#                 break

#             try:
#                 obj = json.loads(msg)
#                 if obj.get("type") == "audio_chunk":
#                     # msgs from client contain base64 webm chunks
#                     chunk = base64.b64decode(obj["data"])
#                     # feed ffmpeg stdin
#                     try:
#                         process.stdin.write(chunk)
#                         process.stdin.flush()
#                     except Exception as e:
#                         print("⚠️ ffmpeg write error:", e)
#             except Exception as e:
#                 print("⚠️ Bad msg:", e, msg)

#     finally:
#         try:
#             process.stdin.close()
#         except:
#             pass
#         process.wait()
#         asyncio.run_coroutine_threadsafe(audio_queue.put(None), loop)
#         print("✅ Browser connection closed cleanly")

# # silence favicon 404
# @app.route('/favicon.ico')
# def favicon():
#     return ('', 204)

# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5000)

















# day 23
# import os
# import asyncio
# import websockets
# import subprocess
# import threading
# import json
# import base64
# import traceback
# from flask import Flask, render_template
# from flask_sock import Sock
# from dotenv import load_dotenv
# import google.generativeai as genai

# load_dotenv()

# ASSEMBLYAI_KEY = os.getenv("ASSEMBLYAI_API_KEY")
# ASSEMBLYAI_URL = "wss://streaming.assemblyai.com/v3/ws"

# GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# genai.configure(api_key=GEMINI_KEY)

# MURF_KEY = os.getenv("MURF_API_KEY").strip()
# MURF_URL = "wss://api.murf.ai/v1/speech/stream-input"

# app = Flask(__name__)
# sock = Sock(app)

# # ---------------------------
# # Conversation history
# # ---------------------------
# chat_history = []  # list of {"role": "user"|"assistant", "text": "..."}

# @app.route("/")
# def index():
#     # keep your filename
#     return render_template("WebSocket.html")

# # ---------------------------
# # Gemini LLM (streaming text) - uses chat_history
# # ---------------------------
# async def stream_llm_response(prompt_text: str):
#     """
#     Append user prompt to chat_history, stream LLM response, append assistant reply,
#     and return full reply text.
#     """
#     global chat_history
#     chat_history.append({"role": "user", "text": prompt_text})

#     model = genai.GenerativeModel("gemini-1.5-flash")

#     # Build a single prompt string from the chat history (simple format)
#     # AGENT_NAME = "Kampra AI"

#     # prompt = (
#     #     f"You are {AGENT_NAME}, a helpful and friendly AI assistant. "
#     #     f"If the user asks for your name, always say: 'My name is {AGENT_NAME}.'\n\n"
#     # )





#     for turn in chat_history:
#         role = "User" if turn["role"] == "user" else "Assistant"
#         prompt += f"{role}: {turn['text']}\n"
#     prompt += "Assistant:"

#     print("\n🤖 Gemini Response (streaming):")
#     full_text = ""
#     response = model.generate_content(prompt, stream=True)
#     for chunk in response:
#         if getattr(chunk, "text", None):
#             print(chunk.text, end="", flush=True)
#             full_text += chunk.text
#     print("\n✅ End of Gemini Response\n", flush=True)

#     # Save assistant reply into history
#     chat_history.append({"role": "assistant", "text": full_text})
#     return full_text

# def safe_send(ws, message: str):
#     """Send to client WS safely (skip if closed)."""
#     try:
#         # Some ws objects (Flask-Sock) don't have .closed attribute, so check
#         if hasattr(ws, "connected") and not ws.connected:
#             return
#         ws.send(message)
#     except Exception as e:
#         print(f"⚠️ safe_send skipped (client closed?): {e}", flush=True)



# # ---------------------------
# # Murf TTS (streamed)  — REPLACE THIS WHOLE FUNCTION
# # ---------------------------
# async def send_to_murf(text: str, client_ws=None):
#     """
#     Stream text to Murf TTS and forward audio chunks to client_ws.
#     Ensures a terminator (murf_audio_end) is always sent, even if Murf
#     does not send an explicit completion message.
#     """
#     if not text or not text.strip():
#         print("⚠️ Empty text, skipping Murf TTS", flush=True)
#         return

#     ctx = "day23-demo"  # static as requested
#     print(f"\n🚀 send_to_murf CALLED (ctx={ctx}) text len={len(text)}\n", flush=True)
#     ws_url = f"{MURF_URL}?api-key={MURF_KEY}&sample_rate=16000&channel_type=MONO&format=mp3"

#     sent_end = False
#     got_any_audio = False

#     try:
#         # Disable ping timeouts; we manage our own idle timeout
#         async with websockets.connect(ws_url, max_size=None, ping_interval=None) as ws:
#             print("✅ Connected to Murf WS", flush=True)

#             # config
#             await ws.send(json.dumps({
#                 "type": "config",
#                 "context_id": ctx,
#                 "voice_config": {
                    # "voiceId": "en-US-natalie",
                    # "voice_gender": "female",
                    # "language": "en-US"
#                 },
#                 "format": "mp3",
#                 "sample_rate": 16000
#             }))
#             print("📨 Sent Murf config", flush=True)

#             # speak
#             await ws.send(json.dumps({
#                 "type": "speak",
#                 "context_id": ctx,
#                 "text": text
#             }))
#             print("📨 Sent speak text to Murf", flush=True)

#             # Read loop with idle timeout to force-end if Murf is silent
#             IDLE_TIMEOUT = 2  # seconds with no messages => end turn
#             while True:
#                 try:
#                     msg = await asyncio.wait_for(ws.recv(), timeout=IDLE_TIMEOUT)
#                 except asyncio.TimeoutError:
#                     # If we already received audio and now idle => end the turn
#                     if got_any_audio:
#                         print("⏱️ Murf idle timeout after audio — ending turn", flush=True)
#                         if client_ws:
#                             threading.Thread(
#                                 target=safe_send,
#                                 args=(client_ws, json.dumps({"type": "murf_audio_end"})),
#                                 daemon=True
#                             ).start()
#                         sent_end = True
#                         # Close Murf socket to free resources
#                         try:
#                             await ws.close()
#                         except:
#                             pass
#                         break
#                     else:
#                         # No audio yet; keep waiting
#                         continue
#                 except websockets.ConnectionClosed:
#                     print("ℹ️ Murf WS closed by server", flush=True)
#                     break

#                 # (Optional) peek at raw message for debugging
#                 if isinstance(msg, (bytes, bytearray)):
#                     # Some providers send binary; skip here
#                     continue
#                 if isinstance(msg, str):
#                     # Try to parse JSON messages
#                     try:
#                         data = json.loads(msg)
#                     except Exception:
#                         # Non-JSON text; ignore
#                         continue
#                 else:
#                     # Unknown type
#                     continue

#                 # Audio chunk?
#                 if "audio" in data:
#                     audio_b64 = data["audio"]
#                     got_any_audio = True

#                     # Forward to client
#                     if client_ws:
#                         threading.Thread(
#                             target=safe_send,
#                             args=(client_ws, json.dumps({"type": "murf_audio", "audio": audio_b64})),
#                             daemon=True
#                         ).start()

#                     # Your requested log format
#                     print(f"🔊 forwarded Murf chunk, size= {len(audio_b64)}", flush=True)
#                     continue

#                 # Explicit end signals (handle all we know)
#                 if data.get("type") in ("speak_end", "completed", "response_end", "audio_end", "end"):
#                     print("✅ Murf signalled end of response", flush=True)
#                     if client_ws:
#                         threading.Thread(
#                             target=safe_send,
#                             args=(client_ws, json.dumps({"type": "murf_audio_end"})),
#                             daemon=True
#                         ).start()
#                     sent_end = True
#                     break

#     except Exception as e:
#         print("❌ Murf error:", e, flush=True)
#         traceback.print_exc()
#     finally:
#         # Last-resort terminator (if we never emitted end above)
#         if client_ws and not sent_end and got_any_audio:
#             try:
#                 print("🛟 Forcing murf_audio_end in finally()", flush=True)
#                 threading.Thread(
#                     target=safe_send,
#                     args=(client_ws, json.dumps({"type": "murf_audio_end"})),
#                     daemon=True
#                 ).start()
#             except Exception as e:
#                 print("❌ failed to send murf_audio_end in finally:", e, flush=True)



# # ---------------------------
# # AssemblyAI Streaming (transcribe realtime)
# # ---------------------------
# async def transcribe_realtime(audio_queue, client_ws, loop):
#     """
#     Connects to AssemblyAI Realtime and forwards audio (PCM) from audio_queue.
#     For each 'Turn' (interim/final) received, forward to client_ws.
#     On final turn (end_of_turn) call the LLM and TTS pipeline.
#     """
#     async with websockets.connect(
#         ASSEMBLYAI_URL,
#         extra_headers={"Authorization": ASSEMBLYAI_KEY},
#         max_size=None
#     ) as aai_ws:
#         print("✅ Connected to AssemblyAI Realtime API", flush=True)

#         async def send_audio():
#             while True:
#                 pcm_chunk = await audio_queue.get()
#                 if pcm_chunk is None:
#                     break
#                 try:
#                     await aai_ws.send(pcm_chunk)
#                 except Exception as e:
#                     print("❌ Failed to send audio to AssemblyAI:", e, flush=True)
#                     break

#         async def recv_transcripts():
#             async for msg in aai_ws:
#                 try:
#                     data = json.loads(msg)
#                 except Exception:
#                     continue

#                 # Forward raw AAI message to client (frontend expects transcript/end_of_turn)
#                 if client_ws:
#                     try:
#                         client_ws.send(msg)
#                     except Exception as e:
#                         print("❌ WS send to client failed:", e, flush=True)

#                 if data.get("type") == "Turn":
#                     transcript = data.get("transcript", "")
#                     print(f"\n📝 Transcript (Turn): {transcript}", flush=True)

#                     if data.get("end_of_turn"):
#                         print("✅ End of Turn Reached - processing", flush=True)

#                         async def process_turn():
#                             try:
#                                 llm_text = await stream_llm_response(transcript)

#                                 # Send AI text to browser for chat transcript
#                                 if client_ws:
#                                     threading.Thread(
#                                         target=safe_send,
#                                         args=(client_ws, json.dumps({"type": "gemini_response", "text": llm_text})),
#                                         daemon=True
#                                     ).start()

#                                 # Then send to Murf and forward audio chunks to browser
#                                 await send_to_murf(llm_text, client_ws)
#                             except Exception as e:
#                                 print("❌ process_turn error:", e, flush=True)
#                                 traceback.print_exc()

#                         asyncio.create_task(process_turn())

#         await asyncio.gather(send_audio(), recv_transcripts())

# def start_transcriber(audio_queue, client_ws, loop):
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(transcribe_realtime(audio_queue, client_ws, loop))

# # ---------------------------
# # Flask WebSocket Handler (client ↔ server)
# # ---------------------------
# @sock.route('/ws')
# def ws_handler(ws):
#     print("🎧 WS client connected (browser)", flush=True)

#     # start ffmpeg to convert incoming webm chunks to s16le PCM for AssemblyAI
#     ffmpeg_cmd = [
#         "ffmpeg", "-loglevel", "quiet", "-i", "pipe:0",
#         "-ar", "16000", "-ac", "1", "-f", "s16le", "pipe:1"
#     ]
#     process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

#     audio_queue = asyncio.Queue()
#     loop = asyncio.new_event_loop()

#     # thread to read PCM from ffmpeg stdout and push to audio_queue
#     def read_pcm():
#         try:
#             while True:
#                 data = process.stdout.read(4096)
#                 if not data:
#                     break
#                 asyncio.run_coroutine_threadsafe(audio_queue.put(data), loop)
#         except Exception as e:
#             print("⚠️ read_pcm error:", e, flush=True)

#     threading.Thread(target=read_pcm, daemon=True).start()
#     threading.Thread(target=start_transcriber, args=(audio_queue, ws, loop), daemon=True).start()

#     try:
#         while True:
#             try:
#                 msg = ws.receive()
#                 if msg is None:

#                     print("ℹ️ Client disconnected cleanly", flush=True)
#                     break  # end loop if browser closed
#             except Exception as e:
#                 print("⚠️ WS receive error:", e, flush=True)
#                 # break  # end loop if fatal error (don’t spin forever)
#                 break

#             try:
#                 obj = json.loads(msg)
#             except Exception as e:
#                 print("⚠️ Bad msg:", e, msg, flush=True)
#                 continue

#             if obj.get("type") == "audio_chunk":
#                     # msgs from client contain base64 webm chunks

#                     # feed ffmpeg stdin
#                 try:
#                     chunk = base64.b64decode(obj["data"])
#                     process.stdin.write(chunk)
#                     process.stdin.flush()
#                 except Exception as e:
#                     print("⚠️ ffmpeg write error:", e, flush=True)
#                 continue
            

#     finally:
#         try:
#             if process.stdin:
#                 process.stdin.close()
#         except:
#             pass
#         try:
#             process.wait(timeout=2)
#         except Exception:
#             process.kill()
        
#         asyncio.run_coroutine_threadsafe(audio_queue.put(None), loop)
#         print("✅ Browser connection closed cleanly", flush=True)

# # silence favicon 404
# @app.route('/favicon.ico')
# def favicon():
#     return ('', 204)

# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5000)








# day24
# import os
# import asyncio
# import websockets
# import subprocess
# import threading
# import json
# import base64
# import traceback
# from flask import Flask, render_template
# from flask_sock import Sock
# from dotenv import load_dotenv
# import google.generativeai as genai

# load_dotenv()

# ASSEMBLYAI_KEY = os.getenv("ASSEMBLYAI_API_KEY")
# ASSEMBLYAI_URL = "wss://streaming.assemblyai.com/v3/ws"
# GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# genai.configure(api_key=GEMINI_KEY)
# MURF_KEY = os.getenv("MURF_API_KEY").strip()
# MURF_URL = "wss://api.murf.ai/v1/speech/stream-input"

# app = Flask(__name__)
# sock = Sock(app)

# # ---------------------------
# # Conversation history
# # ---------------------------
# chat_history = []


# @app.route("/")
# def index():
#     return render_template("WebSocket.html")


# # ---------------------------
# # Gemini LLM (streaming text)
# # ---------------------------
# async def stream_llm_response(prompt_text: str):
#     """Append user prompt to chat_history, stream LLM response, append assistant reply."""
#     global chat_history
#     chat_history.append({"role": "user", "text": prompt_text})

#     model = genai.GenerativeModel("gemini-1.5-flash")

#     # AGENT_NAME = "Munna Bhai AI"
#     # prompt = (
#     #     f"You are {AGENT_NAME}, inspired by the character Munna Bhai from the 2003 movie 'Munna Bhai MBBS'. "
#     #     f"Speak in a friendly, playful, and desi Mumbaiya style. Use casual Hinglish, call people 'mamu', "
#     #     f"and sometimes mention 'Circuit' and 'Jadoo ki Jhappi 🤗'. "
#     #     f"Keep responses short, fun, and in character. "
#     #     f"If the user asks your name, always say: 'Arre mamu, mera naam hai {AGENT_NAME}.'\n\n"
#     # )


#     # AGENT_NAME = "Munna Bhai"
#     # prompt = (
#     #     f"You are {AGENT_NAME}, a fun and lovable Mumbaiya don inspired by Sanjay Dutt’s character from the movie "
#     #     f"'Munna Bhai MBBS'. Speak in a true tapori Mumbai style: use casual Hinglish, lots of 'arre mamu', 'bhai', "
#     #     f"'bolo kya scene hai', and emotional filmy lines. Be playful, warm, and street-smart. "
#     #     f"Sometimes tease the user like a friend, sometimes give a heartwarming 'Jadoo ki Jhappi 🤗', "
#     #     f"and sometimes call out to 'Circuit' for help. "
#     #     f"Keep responses short (1–3 sentences), funny, and filmy. "
#     #     f"If the user asks your name, always say: 'Arre mamu, mera naam hai {AGENT_NAME}.' "
#     #     f"Stay in full character at all times, like you’re actually Munna Bhai talking."
#     # )




#     AGENT_NAME = "Captain"
#     prompt = (
#         f"You are {AGENT_NAME}, a friendly pirate. "
#         f"- Always keep answers very short — never more than 4 sentences. "
#         f"Always speak in pirate slang, using words like: "
#         f"'Ahoy' (hello), 'Arrr' (excitement),"
#         f"'Yo-ho-ho' (happy shout)'"
#         f"\n\nDo NOT use these words at all: "
#         f"'booty', 'shiver me timbers', 'savvy', 'Davy Jones', or any confusing old pirate phrases. "
#         f"\n\nPirate rules for talking: "
#         f"- Roll your 'R's and use 'Arrr!' "
#         f"- Drop the 'G' in words (say 'sailin'' not 'sailing'). "
#         f"- Use 'ye' instead of 'you' (say 'Are ye ready?'). "
#         f"- Keep it short, fun, and playful. "
#         f"\n\nIf someone asks your name or to introduce yourself, always reply: "
#         f"'Ahoy! I be {AGENT_NAME}, the jolliest pirate of the seas!' "
#         f"Keep the mood light, funny, and easy for everyone to enjoy.\n\n"
#     )

#     for turn in chat_history:
#         role = "User" if turn["role"] == "user" else "Assistant"
#         prompt += f"{role}: {turn['text']}\n"
#     prompt += "Assistant:"

#     print("\n🤖 Gemini Response (streaming):")
#     full_text = ""
#     response = model.generate_content(prompt, stream=True)
#     for chunk in response:
#         if getattr(chunk, "text", None):
#             print(chunk.text, end="", flush=True)
#             full_text += chunk.text
#     print("\n✅ End of Gemini Response\n", flush=True)

#     chat_history.append({"role": "assistant", "text": full_text})
#     return full_text


# # ---------------------------
# # Murf TTS (streamed)
# # ---------------------------
# async def send_to_murf(text: str, client_send=None):
#     """Stream text to Murf TTS and forward audio chunks to client_send."""
#     if not text or not text.strip():
#         print("⚠️ Empty text, skipping Murf TTS", flush=True)
#         return

#     ctx = "day23-demo"
#     print(f"\n🚀 send_to_murf CALLED (ctx={ctx}) text len={len(text)}\n", flush=True)

#     ws_url = f"{MURF_URL}?api-key={MURF_KEY}&sample_rate=16000&channel_type=MONO&format=mp3"
#     sent_end = False
#     got_any_audio = False

#     try:
#         async with websockets.connect(ws_url, max_size=None, ping_interval=None) as ws:
#             print("✅ Connected to Murf WS", flush=True)

#             # config
#             await ws.send(json.dumps({
#                 "type": "config",
#                 "context_id": ctx,
#                 "voice_config": {
#                     "voiceId": "en-UK-freddie",
#                     "voice_gender": "male",
#                     "language": "en-UK"
#                 },
#                 "format": "mp3",
#                 "sample_rate": 16000
#             }))
#             print("📨 Sent Murf config", flush=True)

#             # speak
#             await ws.send(json.dumps({
#                 "type": "speak",
#                 "context_id": ctx,
#                 "text": text
#             }))
#             print("📨 Sent speak text to Murf", flush=True)

#             # idle timeout after audio
#             IDLE_TIMEOUT = 2
#             while True:
#                 try:
#                     msg = await asyncio.wait_for(ws.recv(), timeout=IDLE_TIMEOUT)
#                 except asyncio.TimeoutError:
#                     if got_any_audio:
#                         print("⏱️ Murf idle timeout after audio — ending turn", flush=True)
#                         if client_send:
#                             client_send(json.dumps({"type": "murf_audio_end"}))
#                         sent_end = True
#                         try:
#                             await ws.close()
#                         except:
#                             pass
#                         break
#                     else:
#                         continue
#                 except websockets.ConnectionClosed:
#                     print("ℹ️ Murf WS closed by server", flush=True)
#                     break

#                 if isinstance(msg, str):
#                     try:
#                         data = json.loads(msg)
#                     except Exception:
#                         continue
#                 else:
#                     continue

#                 # Audio chunk
#                 if "audio" in data:
#                     audio_b64 = data["audio"]
#                     got_any_audio = True
#                     if client_send:
#                         client_send(json.dumps({"type": "murf_audio", "audio": audio_b64}))
#                     print(f"🔊 forwarded Murf chunk, size= {len(audio_b64)}", flush=True)
#                     continue

#                 # End of response
#                 if data.get("type") in ("speak_end", "completed", "response_end", "audio_end", "end"):
#                     print("✅ Murf signalled end of response", flush=True)
#                     if client_send:
#                         client_send(json.dumps({"type": "murf_audio_end"}))
#                     sent_end = True
#                     break

#     except Exception as e:
#         print("❌ Murf error:", e, flush=True)
#         traceback.print_exc()
#     finally:
#         if client_send and not sent_end and got_any_audio:
#             try:
#                 print("🛟 Forcing murf_audio_end in finally()", flush=True)
#                 client_send(json.dumps({"type": "murf_audio_end"}))
#             except Exception as e:
#                 print("❌ failed to send murf_audio_end in finally:", e, flush=True)


# # ---------------------------
# # AssemblyAI Streaming
# # ---------------------------
# async def transcribe_realtime(audio_queue, client_send, loop):
#     """Connects to AssemblyAI Realtime and forwards audio and transcripts."""
#     async with websockets.connect(
#         ASSEMBLYAI_URL,
#         extra_headers={"Authorization": ASSEMBLYAI_KEY},
#         max_size=None
#     ) as aai_ws:
#         print("✅ Connected to AssemblyAI Realtime API", flush=True)

#         async def send_audio():
#             while True:
#                 pcm_chunk = await audio_queue.get()
#                 if pcm_chunk is None:
#                     break
#                 try:
#                     await aai_ws.send(pcm_chunk)
#                 except Exception as e:
#                     print("❌ Failed to send audio to AssemblyAI:", e, flush=True)
#                     break

#         async def recv_transcripts():
#             async for msg in aai_ws:
#                 try:
#                     data = json.loads(msg)
#                 except Exception:
#                     continue

#                 if client_send:
#                     client_send(msg)

#                 if data.get("type") == "Turn":
#                     transcript = data.get("transcript", "")
#                     print(f"\n📝 Transcript (Turn): {transcript}", flush=True)

#                     if data.get("end_of_turn"):
#                         print("✅ End of Turn Reached - processing", flush=True)

#                         async def process_turn():
#                             try:
#                                 llm_text = await stream_llm_response(transcript)
#                                 if client_send:
#                                     client_send(json.dumps({"type": "gemini_response", "text": llm_text}))
#                                 await send_to_murf(llm_text, client_send)
#                             except Exception as e:
#                                 print("❌ process_turn error:", e, flush=True)
#                                 traceback.print_exc()

#                         asyncio.create_task(process_turn())

#         await asyncio.gather(send_audio(), recv_transcripts())


# def start_transcriber(audio_queue, client_send, loop):
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(transcribe_realtime(audio_queue, client_send, loop))


# # ---------------------------
# # Flask WebSocket Handler
# # ---------------------------
# @sock.route('/ws')
# def ws_handler(ws):
#     print("🎧 WS client connected (browser)", flush=True)

#     # thread-safe sender bound to this ws
#     send_lock = threading.Lock()

#     def send_to_client(message: str):
#         try:
#             with send_lock:
#                 if hasattr(ws, "connected") and not ws.connected:
#                     return
#                 ws.send(message)
#         except Exception as e:
#             print(f"⚠️ send_to_client skipped (client closed?): {e}", flush=True)

#     # ffmpeg process
#     ffmpeg_cmd = [
#         "ffmpeg", "-loglevel", "quiet", "-i", "pipe:0",
#         "-ar", "16000", "-ac", "1", "-f", "s16le", "pipe:1"
#     ]
#     process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

#     audio_queue = asyncio.Queue()
#     loop = asyncio.new_event_loop()

#     def read_pcm():
#         try:
#             while True:
#                 data = process.stdout.read(4096)
#                 if not data:
#                     break
#                 asyncio.run_coroutine_threadsafe(audio_queue.put(data), loop)
#         except Exception as e:
#             print("⚠️ read_pcm error:", e, flush=True)

#     threading.Thread(target=read_pcm, daemon=True).start()
#     threading.Thread(target=start_transcriber, args=(audio_queue, send_to_client, loop), daemon=True).start()

#     try:
#         while True:
#             try:
#                 msg = ws.receive()
#                 if msg is None:
#                     print("ℹ️ Client disconnected cleanly", flush=True)
#                     break
#             except Exception as e:
#                 print("⚠️ WS receive error:", e, flush=True)
#                 break

#             try:
#                 obj = json.loads(msg)
#             except Exception as e:
#                 print("⚠️ Bad msg:", e, msg, flush=True)
#                 continue

#             if obj.get("type") == "audio_chunk":
#                 try:
#                     chunk = base64.b64decode(obj["data"])
#                     process.stdin.write(chunk)
#                     process.stdin.flush()
#                 except Exception as e:
#                     print("⚠️ ffmpeg write error:", e, flush=True)
#                 continue
#     finally:
#         try:
#             if process.stdin:
#                 process.stdin.close()
#         except:
#             pass
#         try:
#             process.wait(timeout=2)
#         except Exception:
#             process.kill()

#         asyncio.run_coroutine_threadsafe(audio_queue.put(None), loop)
#         print("✅ Browser connection closed cleanly", flush=True)


# # silence favicon 404
# @app.route('/favicon.ico')
# def favicon():
#     return ('', 204)


# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)





# day 25  moon skill default is mumbai

# import os
# import asyncio
# import websockets
# import subprocess
# import threading
# import json
# import base64
# import traceback
# from flask import Flask, render_template
# from flask_sock import Sock
# from dotenv import load_dotenv
# import google.generativeai as genai
# import requests   # === Day 25 CHANGE: to fetch weather ===
# import re         # === Day 25 CHANGE: to detect city name ===

# load_dotenv()

# ASSEMBLYAI_KEY = os.getenv("ASSEMBLYAI_API_KEY")
# ASSEMBLYAI_URL = "wss://streaming.assemblyai.com/v3/ws"

# GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# genai.configure(api_key=GEMINI_KEY)

# MURF_KEY = os.getenv("MURF_API_KEY").strip()
# MURF_URL = "wss://api.murf.ai/v1/speech/stream-input"

# OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")  # ✅ Weather API key

# IPGEO_KEY = os.getenv("IPGEO_KEY") 

# app = Flask(__name__)
# sock = Sock(app)

# # ---------------------------
# # Conversation history
# # ---------------------------
# chat_history = []


# @app.route("/")
# def index():
#     return render_template("WebSocket.html")


# # ---------------------------
# # Weather skill function
# # ---------------------------
# def get_weather(city: str):
#     """Fetch weather for a given city using OpenWeather API"""
#     try:
#         url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric"
#         resp = requests.get(url)
#         data = resp.json()
#         if data.get("cod") != 200:
#             return f"Arrr! I couldn't find weather for {city}. ⚠️"
#         temp = data["main"]["temp"]
#         desc = data["weather"][0]["description"]
#         return f"{temp}°C with {desc}"
#     except Exception as e:
#         return f"⚠️ Weather API error: {str(e)}"



# # ---------------------------
# # Moon skill function
# # ---------------------------
# def get_moon_position(lat: float, lon: float):
#     """Fetch moon data from IPGeolocation Astronomy API"""
#     try:
#         url = f"https://api.ipgeolocation.io/astronomy?apiKey={IPGEO_KEY}&lat={lat}&long={lon}"
#         resp = requests.get(url, timeout=10)
#         data = resp.json()

#         return {
#             "rise": data.get("moonrise"),
#             "set": data.get("moonset"),
#             "altitude": data.get("moon_altitude"),
#             "azimuth": data.get("moon_azimuth"),
#             "distance": data.get("moon_distance"),
#             "phase": data.get("moon_status")
#         }
#     except Exception as e:
#         print("⚠️ Moon API error:", e)
#         return None



# # ---------------------------
# # Gemini LLM (streaming text) + Weather Skill
# # ---------------------------
# async def stream_llm_response(prompt_text: str):
#     """Append user prompt to chat_history, process skill if needed, otherwise use Gemini."""
#     global chat_history
#     chat_history.append({"role": "user", "text": prompt_text})

#     model = genai.GenerativeModel("gemini-1.5-flash")

#     AGENT_NAME = "Captain"
#     base_prompt = (
#         f"You are {AGENT_NAME}, a friendly pirate. "
#         f"- Always keep answers very short — never more than 4 sentences. "
#         f"Always speak in pirate slang, using words like: "
#         f"'Ahoy' (hello), 'Arrr' (excitement), 'Yo-ho-ho' (happy shout)' "
#         f"\n\nDo NOT use these words at all: "
#         f"'booty', 'shiver me timbers', 'savvy', 'Davy Jones', or any confusing old pirate phrases. "
#         f"\n\nPirate rules for talking: "
#         f"- Roll your 'R's and use 'Arrr!' "
#         f"- Drop the 'G' in words (say 'sailin'' not 'sailing'). "
#         f"- Use 'ye' instead of 'you' (say 'Are ye ready?'). "
#         f"- Keep it short, fun, and playful. "
#         f"\n\nIf someone asks your name or to introduce yourself, always reply: "
#         f"'Ahoy! I be {AGENT_NAME}, the jolliest pirate of the seas!' "
#         f"Keep the mood light, funny, and easy for everyone to enjoy.\n\n"
#     )

#     # === Weather Skill ===
#     if "weather" in prompt_text.lower() or "whether" in prompt_text.lower():
#         try:
#             # Extract city from user’s text (basic regex for capitalized words)
#             match = re.search(r"(?:in|of)\s+([A-Za-z\s]+)", prompt_text, re.IGNORECASE)
#             if match:
#                 city = match.group(1).strip() 
#                 # remove common trailing words
#                 city = re.sub(r"\b(today|now|right now|please|tomorrow)\b", "", city, flags=re.IGNORECASE).strip()
#                 if city:
#                     weather_info = get_weather(city)
#                     # Pirate-style weather report
#                     pirate_weather = f"Arrr! 🌤️ In {city}, it be {weather_info}, matey!"
#                     chat_history.append({"role": "assistant", "text": pirate_weather})
#                     return pirate_weather
                    
#             # If no city found
#             pirate_fail = "⚓ Arrr! Ye forgot to tell me the city for the weather, matey!"
#             chat_history.append({"role": "assistant", "text": pirate_fail})
#             return pirate_fail

#         except Exception as e:
#             pirate_fail = "⚓ Arrr, me compass be broken! Can't fetch the weather right now."
#             chat_history.append({"role": "assistant", "text": pirate_fail})
#             return pirate_fail
#     # === End Weather Skill ===


#      # 🌙 Moon Skill
#     if "moon" in prompt_text.lower():
#         try:
#             # Default: use a fixed location (can later use user’s IP/geo if needed)
#             lat, lon = 19.0760, 72.8777  # Example: Mumbai
#             moon = get_moon_position(lat, lon)
#             if moon:
#                 pirate_moon = (
#                     f"Arrr! 🌙 The moon be {moon['altitude']}° high at azimuth {moon['azimuth']}°. "
#                     f"She rises at {moon['rise']} and sets at {moon['set']}. "
#                     f"Phase be {moon['phase']}, 'n distance {moon['distance']} km."
#                 )
#                 chat_history.append({"role": "assistant", "text": pirate_moon})
#                 return pirate_moon
#             else:
#                 fail_msg = "⚓ Arrr! I can't find where the moon be lurkin', matey!"
#                 chat_history.append({"role": "assistant", "text": fail_msg})
#                 return fail_msg
#         except Exception:
#             fail_msg = "⚓ Arrr, the moon map be broken!"
#             chat_history.append({"role": "assistant", "text": fail_msg})
#             return fail_msg


#     # Normal Gemini flow if no special skill triggered
#     prompt = base_prompt
#     for turn in chat_history:
#         role = "User" if turn["role"] == "user" else "Assistant"
#         prompt += f"{role}: {turn['text']}\n"
#     prompt += "Assistant:"

#     print("\n🤖 Gemini Response (streaming):")
#     full_text = ""
#     response = model.generate_content(prompt, stream=True)
#     for chunk in response:
#         if getattr(chunk, "text", None):
#             print(chunk.text, end="", flush=True)
#             full_text += chunk.text
#     print("\n✅ End of Gemini Response\n", flush=True)

#     chat_history.append({"role": "assistant", "text": full_text})
#     return full_text


# # ---------------------------
# # Murf TTS (streamed)
# # ---------------------------
# async def send_to_murf(text: str, client_send=None):
#     """Stream text to Murf TTS and forward audio chunks to client_send."""
#     if not text or not text.strip():
#         print("⚠️ Empty text, skipping Murf TTS", flush=True)
#         return

#     ctx = "day25-demo"  # === Day 25 CHANGE: updated context name ===
#     print(f"\n🚀 send_to_murf CALLED (ctx={ctx}) text len={len(text)}\n", flush=True)

#     ws_url = f"{MURF_URL}?api-key={MURF_KEY}&sample_rate=16000&channel_type=MONO&format=mp3"
#     sent_end = False
#     got_any_audio = False

#     try:
#         async with websockets.connect(ws_url, max_size=None, ping_interval=None) as ws:
#             print("✅ Connected to Murf WS", flush=True)

#             # config
#             await ws.send(json.dumps({
#                 "type": "config",
#                 "context_id": ctx,
#                 "voice_config": {
#                     "voiceId": "en-UK-freddie",
#                     "voice_gender": "male",
#                     "language": "en-UK"
#                 },
#                 "format": "mp3",
#                 "sample_rate": 16000
#             }))
#             print("📨 Sent Murf config", flush=True)

#             # speak
#             await ws.send(json.dumps({
#                 "type": "speak",
#                 "context_id": ctx,
#                 "text": text
#             }))
#             print("📨 Sent speak text to Murf", flush=True)

#             # idle timeout after audio
#             IDLE_TIMEOUT = 2
#             while True:
#                 try:
#                     msg = await asyncio.wait_for(ws.recv(), timeout=IDLE_TIMEOUT)
#                 except asyncio.TimeoutError:
#                     if got_any_audio:
#                         print("⏱️ Murf idle timeout after audio — ending turn", flush=True)
#                         if client_send:
#                             client_send(json.dumps({"type": "murf_audio_end"}))
#                         sent_end = True
#                         try:
#                             await ws.close()
#                         except:
#                             pass
#                         break
#                     else:
#                         continue
#                 except websockets.ConnectionClosed:
#                     print("ℹ️ Murf WS closed by server", flush=True)
#                     break

#                 if isinstance(msg, str):
#                     try:
#                         data = json.loads(msg)
#                     except Exception:
#                         continue
#                 else:
#                     continue

#                 # Audio chunk
#                 if "audio" in data:
#                     audio_b64 = data["audio"]
#                     got_any_audio = True
#                     if client_send:
#                         client_send(json.dumps({"type": "murf_audio", "audio": audio_b64}))
#                     print(f"🔊 forwarded Murf chunk, size= {len(audio_b64)}", flush=True)
#                     continue

#                 # End of response
#                 if data.get("type") in ("speak_end", "completed", "response_end", "audio_end", "end"):
#                     print("✅ Murf signalled end of response", flush=True)
#                     if client_send:
#                         client_send(json.dumps({"type": "murf_audio_end"}))
#                     sent_end = True
#                     break

#     except Exception as e:
#         print("❌ Murf error:", e, flush=True)
#         traceback.print_exc()
#     finally:
#         if client_send and not sent_end and got_any_audio:
#             try:
#                 print("🛟 Forcing murf_audio_end in finally()", flush=True)
#                 client_send(json.dumps({"type": "murf_audio_end"}))
#             except Exception as e:
#                 print("❌ failed to send murf_audio_end in finally:", e, flush=True)


# # ---------------------------
# # AssemblyAI Streaming
# # ---------------------------
# async def transcribe_realtime(audio_queue, client_send, loop):
#     """Connects to AssemblyAI Realtime and forwards audio and transcripts."""
#     async with websockets.connect(
#         ASSEMBLYAI_URL,
#         extra_headers={"Authorization": ASSEMBLYAI_KEY},
#         max_size=None
#     ) as aai_ws:
#         print("✅ Connected to AssemblyAI Realtime API", flush=True)

#         async def send_audio():
#             while True:
#                 pcm_chunk = await audio_queue.get()
#                 if pcm_chunk is None:
#                     break
#                 try:
#                     await aai_ws.send(pcm_chunk)
#                 except Exception as e:
#                     print("❌ Failed to send audio to AssemblyAI:", e, flush=True)
#                     break

#         async def recv_transcripts():
#             async for msg in aai_ws:
#                 try:
#                     data = json.loads(msg)
#                 except Exception:
#                     continue

#                 if client_send:
#                     client_send(msg)

#                 if data.get("type") == "Turn":
#                     transcript = data.get("transcript", "")
#                     print(f"\n📝 Transcript (Turn): {transcript}", flush=True)

#                     if data.get("end_of_turn"):
#                         print("✅ End of Turn Reached - processing", flush=True)

#                         async def process_turn():
#                             try:
#                                 llm_text = await stream_llm_response(transcript)
#                                 if client_send:
#                                     client_send(json.dumps({"type": "gemini_response", "text": llm_text}))
#                                 await send_to_murf(llm_text, client_send)
#                             except Exception as e:
#                                 print("❌ process_turn error:", e, flush=True)
#                                 traceback.print_exc()

#                         asyncio.create_task(process_turn())

#         await asyncio.gather(send_audio(), recv_transcripts())


# def start_transcriber(audio_queue, client_send, loop):
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(transcribe_realtime(audio_queue, client_send, loop))


# # ---------------------------
# # Flask WebSocket Handler
# # ---------------------------
# @sock.route('/ws')
# def ws_handler(ws):
#     print("🎧 WS client connected (browser)", flush=True)

#     # thread-safe sender bound to this ws
#     send_lock = threading.Lock()

#     def send_to_client(message: str):
#         try:
#             with send_lock:
#                 if hasattr(ws, "connected") and not ws.connected:
#                     return
#                 ws.send(message)
#         except Exception as e:
#             print(f"⚠️ send_to_client skipped (client closed?): {e}", flush=True)

#     # ffmpeg process
#     ffmpeg_cmd = [
#         "ffmpeg", "-loglevel", "quiet", "-i", "pipe:0",
#         "-ar", "16000", "-ac", "1", "-f", "s16le", "pipe:1"
#     ]
#     process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

#     audio_queue = asyncio.Queue()
#     loop = asyncio.new_event_loop()

#     def read_pcm():
#         try:
#             while True:
#                 data = process.stdout.read(4096)
#                 if not data:
#                     break
#                 asyncio.run_coroutine_threadsafe(audio_queue.put(data), loop)
#         except Exception as e:
#             print("⚠️ read_pcm error:", e, flush=True)

#     threading.Thread(target=read_pcm, daemon=True).start()
#     threading.Thread(target=start_transcriber, args=(audio_queue, send_to_client, loop), daemon=True).start()

#     try:
#         while True:
#             try:
#                 msg = ws.receive()
#                 if msg is None:
#                     print("ℹ️ Client disconnected cleanly", flush=True)
#                     break
#             except Exception as e:
#                 print("⚠️ WS receive error:", e, flush=True)
#                 break

#             try:
#                 obj = json.loads(msg)
#             except Exception as e:
#                 print("⚠️ Bad msg:", e, msg, flush=True)
#                 continue

#             if obj.get("type") == "audio_chunk":
#                 try:
#                     chunk = base64.b64decode(obj["data"])
#                     process.stdin.write(chunk)
#                     process.stdin.flush()
#                 except Exception as e:
#                     print("⚠️ ffmpeg write error:", e, flush=True)
#                 continue
#     finally:
#         try:
#             if process.stdin:
#                 process.stdin.close()
#         except:
#             pass
#         try:
#             process.wait(timeout=2)
#         except Exception:
#             process.kill()

#         asyncio.run_coroutine_threadsafe(audio_queue.put(None), loop)
#         print("✅ Browser connection closed cleanly", flush=True)


# # silence favicon 404
# @app.route('/favicon.ico')
# def favicon():
#     return ('', 204)


# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)









# day 25 final

# import os
# import asyncio
# import websockets
# import subprocess
# import threading
# import json
# import base64
# import traceback
# from flask import Flask, render_template
# from flask_sock import Sock
# from dotenv import load_dotenv
# import google.generativeai as genai
# import requests   # === Day 25 CHANGE: to fetch weather ===
# import re         # === Day 25 CHANGE: to detect city name ===

# load_dotenv()

# ASSEMBLYAI_KEY = os.getenv("ASSEMBLYAI_API_KEY")
# ASSEMBLYAI_URL = "wss://streaming.assemblyai.com/v3/ws"

# GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# genai.configure(api_key=GEMINI_KEY)

# MURF_KEY = os.getenv("MURF_API_KEY").strip()
# MURF_URL = "wss://api.murf.ai/v1/speech/stream-input"

# OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")  # ✅ Weather API key

# IPGEO_KEY = os.getenv("IPGEO_KEY") 

# app = Flask(__name__)
# sock = Sock(app)

# # ---------------------------
# # Conversation history
# # ---------------------------
# chat_history = []


# @app.route("/")
# def index():
#     return render_template("WebSocket.html")



# # ---------------------------
# # Weather skill function
# # ---------------------------
# def get_weather(city: str):
#     """Fetch weather for a given city using OpenWeather API"""
#     try:
#         url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric"
#         resp = requests.get(url)
#         data = resp.json()
#         if data.get("cod") != 200:
#             return f"Arrr! I couldn't find weather for {city}. ⚠"
#         temp = data["main"]["temp"]
#         desc = data["weather"][0]["description"]
#         return f"{temp}°C with {desc}"
#     except Exception as e:
#         return f"⚠ Weather API error: {str(e)}"


# # -----------------------------------
# # Helper: Convert azimuth degrees → direction (N, NE, E, SE, S, SW, W, NW)
# # -----------------------------------
# def azimuth_to_direction(degrees):
#     directions = [
#         "North", "North-East", "East", "South-East",
#         "South", "South-West", "West", "North-West"
#     ]
#     idx = round(degrees / 45) % 8
#     return directions[idx]


# # -----------------------------------
# # Special Skill: Get User Location (IP-based)
# # -----------------------------------
# def get_user_location():
#     """
#     Uses IPGeolocation IP API to detect user's city + lat/lon automatically.
#     This makes the Moon skill work anywhere without hardcoding coordinates.
#     """
#     try:
#         if not IPGEO_KEY:
#             return None, None, "Unknown city", "Unknown country"
#         url = f"https://api.ipgeolocation.io/ipgeo?apiKey={IPGEO_KEY}"
#         res = requests.get(url, timeout=6).json()
#         lat = res.get("latitude")
#         lon = res.get("longitude")
#         city = res.get("city", "Unknown city")
#         country = res.get("country_name", "Unknown country")
#         # Convert to floats if present
#         lat = float(lat) if lat is not None else None
#         lon = float(lon) if lon is not None else None
#         return lat, lon, city, country
#     except Exception as e:
#         print("⚠️ IP location error:", e, flush=True)
#         return None, None, "Unknown city", "Unknown country"


# # ---------------------------
# # Moon skill function
# # ---------------------------
# def get_moon_position():
#     """
#     Fetch moon data from IPGeolocation Astronomy API for the user's current IP-based location.
#     Returns pirate-styled, short, friendly string including altitude, azimuth, direction,
#     rise/set times, phase, and distance.
#     """
#     try:
#         # Step 1: Detect user’s location (auto via IP)
#         lat, lon, city, country = get_user_location()

#         if not IPGEO_KEY:
#             return "⚓ Arrr! Me spyglass be empty — set IPGEO_KEY in yer .env, matey!"
#         if lat is None or lon is None:
#             return "⚓ Arrr! I can't spy yer location. Try again later, matey!"

#         # Step 2: Fetch Moon position from Astronomy API (JSON output)
#         url = f"https://api.ipgeolocation.io/astronomy?apiKey={IPGEO_KEY}&lat={lat}&long={lon}"
#         res = requests.get(url, timeout=6).json()

#         altitude = res.get("moon_altitude")     # degrees above horizon
#         azimuth = res.get("moon_azimuth")       # degrees clockwise from North
#         distance = res.get("moon_distance")     # km
#         phase = res.get("moon_phase")           # e.g., "Waxing Gibbous"
#         rise = res.get("moonrise")              # local time HH:MM
#         set_time = res.get("moonset")           # local time HH:MM

#         # Convert azimuth to cardinal direction
#         direction = azimuth_to_direction(azimuth)

#         # Speech-friendly, short pirate style + clear meaning of azimuth
#         return (
#             f"Arrr! 🌙 From {city}, {country}, the moon be {altitude}° high, "
#             f"azimuth {azimuth}° toward {direction}. "
#             f"It rises at {rise} and sets at {set_time}. "
#             f"Phase be {phase}, 'n distance {distance} km."
#         )
#     except Exception as e:
#         print("⚠️ Moon API error:", e, flush=True)
#         return "⚓ Arrr, me star charts be tangled! Can't fetch the moon right now."




# # ---------------------------
# # Gemini LLM (streaming text) + Weather Skill
# # ---------------------------
# async def stream_llm_response(prompt_text: str):
#     """Append user prompt to chat_history, process skill if needed, otherwise use Gemini."""
#     global chat_history
#     chat_history.append({"role": "user", "text": prompt_text})

#     model = genai.GenerativeModel("gemini-1.5-flash")

#     AGENT_NAME = "Captain"
#     base_prompt = (
#         f"You are {AGENT_NAME}, a friendly pirate. "
#         f"- Always keep answers very short — never more than 4 sentences. "
#         f"Always speak in pirate slang, using words like: "
#         f"'Ahoy' (hello), 'Arrr' (excitement), 'Yo-ho-ho' (happy shout)' "
#         f"\n\nDo NOT use these words at all: "
#         f"'booty', 'shiver me timbers', 'savvy', 'Davy Jones', or any confusing old pirate phrases. "
#         f"\n\nPirate rules for talking: "
#         f"- Roll your 'R's and use 'Arrr!' "
#         f"- Drop the 'G' in words (say 'sailin'' not 'sailing'). "
#         f"- Use 'ye' instead of 'you' (say 'Are ye ready?'). "
#         f"- Keep it short, fun, and playful. "
#         f"\n\nIf someone asks your name or to introduce yourself, always reply: "
#         f"'Ahoy! I be {AGENT_NAME}, the jolliest pirate of the seas!' "
#         f"Keep the mood light, funny, and easy for everyone to enjoy.\n\n"
#     )

#     # === Weather Skill ===
#     if "weather" in prompt_text.lower() or "whether" in prompt_text.lower():
#         try:
#             # Extract city from user’s text (basic regex for capitalized words)
#             match = re.search(r"(?:in|of)\s+([A-Za-z\s]+)", prompt_text, re.IGNORECASE)
#             if match:
#                 city = match.group(1).strip() 
#                 # remove common trailing words
#                 city = re.sub(r"\b(today|now|right now|please|tomorrow)\b", "", city, flags=re.IGNORECASE).strip()
#                 if city:
#                     weather_info = get_weather(city)
#                     # Pirate-style weather report
#                     pirate_weather = f"Arrr! 🌤 In {city}, it be {weather_info}, matey!"
#                     chat_history.append({"role": "assistant", "text": pirate_weather})
#                     return pirate_weather
                    
#             # If no city found
#             pirate_fail = "⚓ Arrr! Ye forgot to tell me the city for the weather, matey!"
#             chat_history.append({"role": "assistant", "text": pirate_fail})
#             return pirate_fail

#         except Exception as e:
#             pirate_fail = "⚓ Arrr, me compass be broken! Can't fetch the weather right now."
#             chat_history.append({"role": "assistant", "text": pirate_fail})
#             return pirate_fail
#     # === End Weather Skill ===


#      # === 🌙 Moon Skill (IP-based auto location via IPGeolocation) ===
#     if "moon" in prompt_text.lower():
#         try:
#             pirate_moon = get_moon_position()
#             chat_history.append({"role": "assistant", "text": pirate_moon})
#             return pirate_moon
#         except Exception:
#             fail_msg = "⚓ Arrr, the moon map be broken!"
#             chat_history.append({"role": "assistant", "text": fail_msg})
#             return fail_msg
#     # === End Moon Skill ===


#     # Normal Gemini flow if no special skill triggered
#     prompt = base_prompt
#     for turn in chat_history:
#         role = "User" if turn["role"] == "user" else "Assistant"
#         prompt += f"{role}: {turn['text']}\n"
#     prompt += "Assistant:"

#     print("\n🤖 Gemini Response (streaming):")
#     full_text = ""
#     response = model.generate_content(prompt, stream=True)
#     for chunk in response:
#         if getattr(chunk, "text", None):
#             print(chunk.text, end="", flush=True)
#             full_text += chunk.text
#     print("\n✅ End of Gemini Response\n", flush=True)

#     chat_history.append({"role": "assistant", "text": full_text})
#     return full_text


# # ---------------------------
# # Murf TTS (streamed)
# # ---------------------------
# async def send_to_murf(text: str, client_send=None):
#     """Stream text to Murf TTS and forward audio chunks to client_send."""
#     if not text or not text.strip():
#         print("⚠ Empty text, skipping Murf TTS", flush=True)
#         return

#     ctx = "day25-demo"  # === Day 25 CHANGE: updated context name ===
#     print(f"\n🚀 send_to_murf CALLED (ctx={ctx}) text len={len(text)}\n", flush=True)

#     ws_url = f"{MURF_URL}?api-key={MURF_KEY}&sample_rate=16000&channel_type=MONO&format=mp3"
#     sent_end = False
#     got_any_audio = False

#     try:
#         async with websockets.connect(ws_url, max_size=None, ping_interval=None) as ws:
#             print("✅ Connected to Murf WS", flush=True)

#             # config
#             await ws.send(json.dumps({
#                 "type": "config",
#                 "context_id": ctx,
#                 "voice_config": {
#                     "voiceId": "en-UK-freddie",
#                     "voice_gender": "male",
#                     "language": "en-UK"
#                 },
#                 "format": "mp3",
#                 "sample_rate": 16000
#             }))
#             print("📨 Sent Murf config", flush=True)

#             # speak
#             await ws.send(json.dumps({
#                 "type": "speak",
#                 "context_id": ctx,
#                 "text": text
#             }))
#             print("📨 Sent speak text to Murf", flush=True)

#             # idle timeout after audio
#             IDLE_TIMEOUT = 2
#             while True:
#                 try:
#                     msg = await asyncio.wait_for(ws.recv(), timeout=IDLE_TIMEOUT)
#                 except asyncio.TimeoutError:
#                     if got_any_audio:
#                         print("⏱ Murf idle timeout after audio — ending turn", flush=True)
#                         if client_send:
#                             client_send(json.dumps({"type": "murf_audio_end"}))
#                         sent_end = True
#                         try:
#                             await ws.close()
#                         except:
#                             pass
#                         break
#                     else:
#                         continue
#                 except websockets.ConnectionClosed:
#                     print("ℹ Murf WS closed by server", flush=True)
#                     break

#                 if isinstance(msg, str):
#                     try:
#                         data = json.loads(msg)
#                     except Exception:
#                         continue
#                 else:
#                     continue

#                 # Audio chunk
#                 if "audio" in data:
#                     audio_b64 = data["audio"]
#                     got_any_audio = True
#                     if client_send:
#                         client_send(json.dumps({"type": "murf_audio", "audio": audio_b64}))
#                     print(f"🔊 forwarded Murf chunk, size= {len(audio_b64)}", flush=True)
#                     continue

#                 # End of response
#                 if data.get("type") in ("speak_end", "completed", "response_end", "audio_end", "end"):
#                     print("✅ Murf signalled end of response", flush=True)
#                     if client_send:
#                         client_send(json.dumps({"type": "murf_audio_end"}))
#                     sent_end = True
#                     break

#     except Exception as e:
#         print("❌ Murf error:", e, flush=True)
#         traceback.print_exc()
#     finally:
#         if client_send and not sent_end and got_any_audio:
#             try:
#                 print("🛟 Forcing murf_audio_end in finally()", flush=True)
#                 client_send(json.dumps({"type": "murf_audio_end"}))
#             except Exception as e:
#                 print("❌ failed to send murf_audio_end in finally:", e, flush=True)


# # ---------------------------
# # AssemblyAI Streaming
# # ---------------------------
# async def transcribe_realtime(audio_queue, client_send, loop):
#     """Connects to AssemblyAI Realtime and forwards audio and transcripts."""
#     async with websockets.connect(
#         ASSEMBLYAI_URL,
#         extra_headers={"Authorization": ASSEMBLYAI_KEY},
#         max_size=None
#     ) as aai_ws:
#         print("✅ Connected to AssemblyAI Realtime API", flush=True)

#         async def send_audio():
#             while True:
#                 pcm_chunk = await audio_queue.get()
#                 if pcm_chunk is None:
#                     break
#                 try:
#                     await aai_ws.send(pcm_chunk)
#                 except Exception as e:
#                     print("❌ Failed to send audio to AssemblyAI:", e, flush=True)
#                     break

#         async def recv_transcripts():
#             async for msg in aai_ws:
#                 try:
#                     data = json.loads(msg)
#                 except Exception:
#                     continue

#                 if client_send:
#                     client_send(msg)

#                 if data.get("type") == "Turn":
#                     transcript = data.get("transcript", "")
#                     print(f"\n📝 Transcript (Turn): {transcript}", flush=True)

#                     if data.get("end_of_turn"):
#                         print("✅ End of Turn Reached - processing", flush=True)

#                         async def process_turn():
#                             try:
#                                 llm_text = await stream_llm_response(transcript)
#                                 if client_send:
#                                     client_send(json.dumps({"type": "gemini_response", "text": llm_text}))
#                                 await send_to_murf(llm_text, client_send)
#                             except Exception as e:
#                                 print("❌ process_turn error:", e, flush=True)
#                                 traceback.print_exc()

#                         asyncio.create_task(process_turn())

#         await asyncio.gather(send_audio(), recv_transcripts())


# def start_transcriber(audio_queue, client_send, loop):
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(transcribe_realtime(audio_queue, client_send, loop))


# # ---------------------------
# # Flask WebSocket Handler
# # ---------------------------
# @sock.route('/ws')
# def ws_handler(ws):
#     print("🎧 WS client connected (browser)", flush=True)

#     # thread-safe sender bound to this ws
#     send_lock = threading.Lock()

#     def send_to_client(message: str):
#         try:
#             with send_lock:
#                 if hasattr(ws, "connected") and not ws.connected:
#                     return
#                 ws.send(message)
#         except Exception as e:
#             print(f"⚠ send_to_client skipped (client closed?): {e}", flush=True)

#     # ffmpeg process
#     ffmpeg_cmd = [
#         "ffmpeg", "-loglevel", "quiet", "-i", "pipe:0",
#         "-ar", "16000", "-ac", "1", "-f", "s16le", "pipe:1"
#     ]
#     process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

#     audio_queue = asyncio.Queue()
#     loop = asyncio.new_event_loop()

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
#     threading.Thread(target=start_transcriber, args=(audio_queue, send_to_client, loop), daemon=True).start()

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

#             try:
#                 obj = json.loads(msg)
#             except Exception as e:
#                 print("⚠ Bad msg:", e, msg, flush=True)
#                 continue

#             if obj.get("type") == "audio_chunk":
#                 try:
#                     chunk = base64.b64decode(obj["data"])
#                     process.stdin.write(chunk)
#                     process.stdin.flush()
#                 except Exception as e:
#                     print("⚠ ffmpeg write error:", e, flush=True)
#                 continue
#     finally:
#         try:
#             if process.stdin:
#                 process.stdin.close()
#         except:
#             pass
#         try:
#             process.wait(timeout=2)
#         except Exception:
#             process.kill()

#         asyncio.run_coroutine_threadsafe(audio_queue.put(None), loop)
#         print("✅ Browser connection closed cleanly", flush=True)


# # silence favicon 404
# @app.route('/favicon.ico')
# def favicon():
#     return ('', 204)


# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)






# day26_updated_with_horoscope_debug.py
# import os
# import asyncio
# import websockets
# import subprocess
# import threading
# import json
# import base64
# import traceback
# from flask import Flask, render_template
# from flask_sock import Sock
# from dotenv import load_dotenv
# import google.generativeai as genai
# import requests   # === Day 25 CHANGE: to fetch weather ===
# import re         # === Day 25 CHANGE: to detect city name ===

# load_dotenv()

# ASSEMBLYAI_KEY = os.getenv("ASSEMBLYAI_API_KEY")
# ASSEMBLYAI_URL = "wss://streaming.assemblyai.com/v3/ws"

# GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# genai.configure(api_key=GEMINI_KEY)

# # Defensive: handle missing murf env gracefully
# MURF_KEY = os.getenv("MURF_API_KEY")
# MURF_KEY = MURF_KEY.strip() if isinstance(MURF_KEY, str) else None
# MURF_URL = "wss://api.murf.ai/v1/speech/stream-input"

# OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")  # ✅ Weather API key

# IPGEO_KEY = os.getenv("IPGEO_KEY") 

# API_NINJAS_KEY = os.getenv("API_NINJAS_KEY")
# # ASTROLOGY_URL = f"https://api.api-ninjas.com/v1/horoscope?zodiac={sign.lower()}"

# app = Flask(__name__)
# sock = Sock(app)

# # ---------------------------
# # Conversation history
# # ---------------------------
# chat_history = []


# @app.route("/")
# def index():
#     return render_template("WebSocket.html")



# # ---------------------------
# # Weather skill function
# # ---------------------------
# def get_weather(city: str):
#     """Fetch weather for a given city using OpenWeather API"""
#     try:
#         url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric"
#         resp = requests.get(url, timeout=8)
#         data = resp.json()
#         if data.get("cod") != 200:
#             return f"Arrr! I couldn't find weather for {city}. ⚠"
#         temp = data["main"]["temp"]
#         desc = data["weather"][0]["description"]
#         return f"{temp}°C with {desc}"
#     except Exception as e:
#         return f"⚠ Weather API error: {str(e)}"


# # -----------------------------------
# # Helper: Convert azimuth degrees → direction (N, NE, E, SE, S, SW, W, NW)
# # -----------------------------------
# def azimuth_to_direction(degrees):
#     directions = [
#         "North", "North-East", "East", "South-East",
#         "South", "South-West", "West", "North-West"
#     ]
#     idx = round(degrees / 45) % 8
#     return directions[idx]


# # -----------------------------------
# # Special Skill: Get User Location (IP-based)
# # -----------------------------------
# def get_user_location():
#     """
#     Uses IPGeolocation IP API to detect user's city + lat/lon automatically.
#     This makes the Moon skill work anywhere without hardcoding coordinates.
#     """
#     try:
#         if not IPGEO_KEY:
#             return None, None, "Unknown city", "Unknown country"
#         url = f"https://api.ipgeolocation.io/ipgeo?apiKey={IPGEO_KEY}"
#         res = requests.get(url, timeout=6).json()
#         lat = res.get("latitude")
#         lon = res.get("longitude")
#         city = res.get("city", "Unknown city")
#         country = res.get("country_name", "Unknown country")
#         # Convert to floats if present
#         lat = float(lat) if lat is not None else None
#         lon = float(lon) if lon is not None else None
#         return lat, lon, city, country
#     except Exception as e:
#         print("⚠️ IP location error:", e, flush=True)
#         return None, None, "Unknown city", "Unknown country"


# # ---------------------------
# # Moon skill function
# # ---------------------------
# def get_moon_position():
#     """
#     Fetch moon data from IPGeolocation Astronomy API for the user's current IP-based location.
#     Returns pirate-styled, short, friendly string including altitude, azimuth, direction,
#     rise/set times, phase, and distance.
#     """
#     try:
#         # Step 1: Detect user’s location (auto via IP)
#         lat, lon, city, country = get_user_location()

#         if not IPGEO_KEY:
#             return "⚓ Arrr! Me spyglass be empty — set IPGEO_KEY in yer .env, matey!"
#         if lat is None or lon is None:
#             return "⚓ Arrr! I can't spy yer location. Try again later, matey!"

#         # Step 2: Fetch Moon position from Astronomy API (JSON output)
#         url = f"https://api.ipgeolocation.io/astronomy?apiKey={IPGEO_KEY}&lat={lat}&long={lon}"
#         res = requests.get(url, timeout=6).json()

#         altitude = res.get("moon_altitude")     # degrees above horizon
#         azimuth = res.get("moon_azimuth")       # degrees clockwise from North
#         distance = res.get("moon_distance")     # km
#         phase = res.get("moon_phase")           # e.g., "Waxing Gibbous"
#         rise = res.get("moonrise")              # local time HH:MM
#         set_time = res.get("moonset")           # local time HH:MM

#         # Convert azimuth to cardinal direction
#         direction = azimuth_to_direction(azimuth)

#         # Speech-friendly, short pirate style + clear meaning of azimuth
#         return (
#             f"Arrr! 🌙 From {city}, {country}, the moon be {altitude}° high, "
#             f"azimuth {azimuth}° toward {direction}. "
#             f"It rises at {rise} and sets at {set_time}. "
#             f"Phase be {phase}, 'n distance {distance} km."
#         )
#     except Exception as e:
#         print("⚠️ Moon API error:", e, flush=True)
#         return "⚓ Arrr, me star charts be tangled! Can't fetch the moon right now."


# # ---------------------------
# # ADDED: Horoscope skill function (FIXED & DEBUGGED)
# # ---------------------------
# def get_horoscope(sign: str):
#     """
#     Fetch daily horoscope for a given zodiac sign using API Ninjas (API_NINJAS_KEY).
#     - Uses param `zodiac=` per the documentation you shared.
#     - Stronger error handling and debug prints so you can see what's coming back.
#     """
#     if not API_NINJAS_KEY:
#         # Helpful debug message if env var not set
#         print("⚠️ API_NINJAS_KEY not set in .env", flush=True)
#         return "⚠ Arrr! The astrology key be missin' in yer .env."

#     if not sign:
#         return "⚓ Arrr! Tell me yer zodiac sign, matey (like Aries or Leo)!"

#     try:
#         # Use 'zodiac' param name (per docs you pasted)
#         url = f"https://api.api-ninjas.com/v1/horoscope?zodiac={sign.lower()}"
#         headers = {"X-Api-Key": API_NINJAS_KEY}

#         # Make request with timeout
#         resp = requests.get(url, headers=headers, timeout=10)

#         # Debug output — ALWAYS print status/body so you can see API answers in server logs
#         print(f"🛰 Horoscope API status: {resp.status_code}", flush=True)
#         print(f"🛰 Horoscope API body: {resp.text}", flush=True)

#         if resp.status_code == 200:
#             # API Ninjas returns JSON normally; attempt to parse
#             try:
#                 data = resp.json()
#             except Exception:
#                 data = None

#             horoscope_text = None
#             if isinstance(data, dict):
#                 # prefer 'horoscope' key per docs; fallback to other likely keys
#                 horoscope_text = data.get("horoscope") or data.get("text") or None

#             if not horoscope_text:
#                 # fallback to raw response body (handles plain-text responses)
#                 horoscope_text = resp.text.strip()

#             # Pirate-styled friendly message (single source of truth)
#             return f"Arrr! 🔮 Fer {sign.capitalize()}, today, it be sayin': {horoscope_text}"
#         else:
#             # Provide a debug-friendly pirate message
#             return f"⚠ Arrr! I couldn't fetch yer horoscope (API {resp.status_code})."
#     except Exception as e:
#         print("❌ Horoscope error:", e, flush=True)
#         traceback.print_exc()
#         return f"⚠ Arrr! Somethin' went wrong fetchin' the stars: {str(e)}"
# # --------------------------- END horoscope function --------------------


# # ---------------------------
# # Gemini LLM (streaming text) + Weather Skill
# # (kept behaviour: stream_llm_response returns a string; rest of your pipeline expects string)
# # ---------------------------
# async def stream_llm_response(prompt_text: str):
#     """Append user prompt to chat_history, process skill if needed, otherwise use Gemini."""
#     global chat_history
#     chat_history.append({"role": "user", "text": prompt_text})

#     model = genai.GenerativeModel("gemini-1.5-flash")

#     AGENT_NAME = "Captain"
#     base_prompt = (
#         f"You are {AGENT_NAME}, a friendly pirate. "
#         f"- Always keep answers very short — never more than 4 sentences. "
#         f"Always speak in pirate slang, using words like: "
#         f"'Ahoy' (hello), 'Arrr' (excitement), 'Yo-ho-ho' (happy shout)' "
#         f"\n\nDo NOT use these words at all: "
#         f"'booty', 'shiver me timbers', 'savvy', 'Davy Jones', or any confusing old pirate phrases. "
#         f"\n\nPirate rules for talking: "
#         f"- Roll your 'R's and use 'Arrr!' "
#         f"- Drop the 'G' in words (say 'sailin'' not 'sailing'). "
#         f"- Use 'ye' instead of 'you' (say 'Are ye ready?'). "
#         f"- Keep it short, fun, and playful. "
#         f"\n\nIf someone asks your name or to introduce yourself, always reply: "
#         f"'Ahoy! I be {AGENT_NAME}, the jolliest pirate of the seas!' "
#         f"Keep the mood light, funny, and easy for everyone to enjoy.\n\n"
#     )

#     # === Weather Skill ===
#     if "weather" in prompt_text.lower() or "whether" in prompt_text.lower():
#         try:
#             # Extract city from user’s text (basic regex for capitalized words)
#             match = re.search(r"(?:in|of)\s+([A-Za-z\s]+)", prompt_text, re.IGNORECASE)
#             if match:
#                 city = match.group(1).strip() 
#                 # remove common trailing words
#                 city = re.sub(r"\b(today|now|right now|please|tomorrow)\b", "", city, flags=re.IGNORECASE).strip()
#                 if city:
#                     weather_info = get_weather(city)
#                     # Pirate-style weather report
#                     pirate_weather = f"Arrr! 🌤 In {city}, it be {weather_info}, matey!"
#                     chat_history.append({"role": "assistant", "text": pirate_weather})
#                     return pirate_weather
                    
#             # If no city found
#             pirate_fail = "⚓ Arrr! Ye forgot to tell me the city for the weather, matey!"
#             chat_history.append({"role": "assistant", "text": pirate_fail})
#             return pirate_fail

#         except Exception as e:
#             pirate_fail = "⚓ Arrr, me compass be broken! Can't fetch the weather right now."
#             chat_history.append({"role": "assistant", "text": pirate_fail})
#             return pirate_fail
#     # === End Weather Skill ===


#      # === 🌙 Moon Skill (IP-based auto location via IPGeolocation) ===
#     if "moon" in prompt_text.lower():
#         try:
#             pirate_moon = get_moon_position()
#             chat_history.append({"role": "assistant", "text": pirate_moon})
#             return pirate_moon
#         except Exception:
#             fail_msg = "⚓ Arrr, the moon map be broken!"
#             chat_history.append({"role": "assistant", "text": fail_msg})
#             return fail_msg
#     # === End Moon Skill ===

#     # === 🔮 Horoscope Skill (NEW) ===
#     if "horoscope" in prompt_text.lower() or "zodiac" in prompt_text.lower():
#         try:
#             # Extract zodiac sign (basic regex for common signs)
#             signs = ["aries","taurus","gemini","cancer","leo","virgo",
#                      "libra","scorpio","sagittarius","capricorn","aquarius","pisces"]
#             chosen_sign = None

#             for s in signs:
#                 if s in prompt_text.lower():
#                     chosen_sign = s
#                     break

#             if chosen_sign:
#                 # get_horoscope returns a pirate-styled string (or an error message)
#                 pirate_horo = get_horoscope(chosen_sign)
#                 chat_history.append({"role": "assistant", "text": pirate_horo})
#                 return pirate_horo
#             else:
#                 msg = "⚓ Arrr! Tell me yer zodiac sign, matey (like Aries or Leo)!"
#                 chat_history.append({"role": "assistant", "text": msg})
#                 return msg
#         except Exception:
#             fail_msg = "⚓ Arrr, the stars be cloudy! Can't fetch horoscope now."
#             chat_history.append({"role": "assistant", "text": fail_msg})
#             return fail_msg
#     # === End Horoscope Skill ===


#     # Normal Gemini flow if no special skill triggered
#     prompt = base_prompt
#     for turn in chat_history:
#         role = "User" if turn["role"] == "user" else "Assistant"
#         prompt += f"{role}: {turn['text']}\n"
#     prompt += "Assistant:"

#     print("\n🤖 Gemini Response (streaming):")
#     full_text = ""
#     response = model.generate_content(prompt, stream=True)
#     for chunk in response:
#         if getattr(chunk, "text", None):
#             print(chunk.text, end="", flush=True)
#             full_text += chunk.text
#     print("\n✅ End of Gemini Response\n", flush=True)

#     chat_history.append({"role": "assistant", "text": full_text})
#     return full_text



# # ---------------------------
# # Murf TTS (streamed)
# # ---------------------------
# async def send_to_murf(text: str, client_send=None):
#     """Stream text to Murf TTS and forward audio chunks to client_send."""
#     if not text or not text.strip():
#         print("⚠ Empty text, skipping Murf TTS", flush=True)
#         return

#     ctx = "day25-demo"  # === Day 25 CHANGE: updated context name ===
#     print(f"\n🚀 send_to_murf CALLED (ctx={ctx}) text len={len(text)}\n", flush=True)

#     if not MURF_KEY:
#         print("⚠️ MURF_KEY missing — cannot stream TTS", flush=True)
#         return

#     ws_url = f"{MURF_URL}?api-key={MURF_KEY}&sample_rate=16000&channel_type=MONO&format=mp3"
#     sent_end = False
#     got_any_audio = False

#     try:
#         async with websockets.connect(ws_url, max_size=None, ping_interval=None) as ws:
#             print("✅ Connected to Murf WS", flush=True)

#             # config
#             await ws.send(json.dumps({
#                 "type": "config",
#                 "context_id": ctx,
#                 "voice_config": {
#                     "voiceId": "en-UK-freddie",
#                     "voice_gender": "male",
#                     "language": "en-UK"
#                 },
#                 "format": "mp3",
#                 "sample_rate": 16000
#             }))
#             print("📨 Sent Murf config", flush=True)

#             # speak
#             await ws.send(json.dumps({
#                 "type": "speak",
#                 "context_id": ctx,
#                 "text": text
#             }))
#             print("📨 Sent speak text to Murf", flush=True)

#             # idle timeout after audio
#             IDLE_TIMEOUT = 4
#             while True:
#                 try:
#                     msg = await asyncio.wait_for(ws.recv(), timeout=IDLE_TIMEOUT)
#                 except asyncio.TimeoutError:
#                     if got_any_audio:
#                         print("⏱ Murf idle timeout after audio — ending turn", flush=True)
#                         if client_send:
#                             client_send(json.dumps({"type": "murf_audio_end"}))
#                         sent_end = True
#                         try:
#                             await ws.close()
#                         except:
#                             pass
#                         break
#                     else:
#                         continue
#                 except websockets.ConnectionClosed:
#                     print("ℹ Murf WS closed by server", flush=True)
#                     break

#                 if isinstance(msg, str):
#                     try:
#                         data = json.loads(msg)
#                     except Exception:
#                         continue
#                 else:
#                     continue

#                 # Audio chunk
#                 if "audio" in data:
#                     audio_b64 = data["audio"]
#                     got_any_audio = True
#                     if client_send:
#                         client_send(json.dumps({"type": "murf_audio", "audio": audio_b64}))
#                     print(f"🔊 forwarded Murf chunk, size= {len(audio_b64)}", flush=True)
#                     continue

#                 # End of response
#                 if data.get("type") in ("speak_end", "completed", "response_end", "audio_end", "end"):
#                     print("✅ Murf signalled end of response", flush=True)
#                     if client_send:
#                         client_send(json.dumps({"type": "murf_audio_end"}))
#                     sent_end = True
#                     break

#     except Exception as e:
#         print("❌ Murf error:", e, flush=True)
#         traceback.print_exc()
#     finally:
#         if client_send and not sent_end and got_any_audio:
#             try:
#                 print("🛟 Forcing murf_audio_end in finally()", flush=True)
#                 client_send(json.dumps({"type": "murf_audio_end"}))
#             except Exception as e:
#                 print("❌ failed to send murf_audio_end in finally:", e, flush=True)


# # ---------------------------
# # AssemblyAI Streaming
# # ---------------------------
# async def transcribe_realtime(audio_queue, client_send, loop):
#     """Connects to AssemblyAI Realtime and forwards audio and transcripts."""
#     async with websockets.connect(
#         ASSEMBLYAI_URL,
#         extra_headers={"Authorization": ASSEMBLYAI_KEY},
#         max_size=None
#     ) as aai_ws:
#         print("✅ Connected to AssemblyAI Realtime API", flush=True)

#         async def send_audio():
#             while True:
#                 pcm_chunk = await audio_queue.get()
#                 if pcm_chunk is None:
#                     break
#                 try:
#                     await aai_ws.send(pcm_chunk)
#                 except Exception as e:
#                     print("❌ Failed to send audio to AssemblyAI:", e, flush=True)
#                     break

#         async def recv_transcripts():
#             async for msg in aai_ws:
#                 try:
#                     data = json.loads(msg)
#                 except Exception:
#                     continue

#                 if client_send:
#                     client_send(msg)

#                 if data.get("type") == "Turn":
#                     transcript = data.get("transcript", "")
#                     print(f"\n📝 Transcript (Turn): {transcript}", flush=True)

#                     if data.get("end_of_turn"):
#                         print("✅ End of Turn Reached - processing", flush=True)

#                         async def process_turn():
#                             try:
#                                 llm_text = await stream_llm_response(transcript)
#                                 if client_send:
#                                     client_send(json.dumps({"type": "gemini_response", "text": llm_text}))
#                                 await send_to_murf(llm_text, client_send)
#                             except Exception as e:
#                                 print("❌ process_turn error:", e, flush=True)
#                                 traceback.print_exc()

#                         asyncio.create_task(process_turn())

#         await asyncio.gather(send_audio(), recv_transcripts())


# def start_transcriber(audio_queue, client_send, loop):
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(transcribe_realtime(audio_queue, client_send, loop))


# # ---------------------------
# # Flask WebSocket Handler
# # ---------------------------
# @sock.route('/ws')
# def ws_handler(ws):
#     print("🎧 WS client connected (browser)", flush=True)

#     # thread-safe sender bound to this ws
#     send_lock = threading.Lock()

#     def send_to_client(message: str):
#         try:
#             with send_lock:
#                 if hasattr(ws, "connected") and not ws.connected:
#                     return
#                 ws.send(message)
#         except Exception as e:
#             print(f"⚠ send_to_client skipped (client closed?): {e}", flush=True)

#     # ffmpeg process
#     ffmpeg_cmd = [
#         "ffmpeg", "-loglevel", "quiet", "-i", "pipe:0",
#         "-ar", "16000", "-ac", "1", "-f", "s16le", "pipe:1"
#     ]
#     process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

#     audio_queue = asyncio.Queue()
#     loop = asyncio.new_event_loop()

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
#     threading.Thread(target=start_transcriber, args=(audio_queue, send_to_client, loop), daemon=True).start()

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

#             try:
#                 obj = json.loads(msg)
#             except Exception as e:
#                 print("⚠ Bad msg:", e, msg, flush=True)
#                 continue

#             if obj.get("type") == "audio_chunk":
#                 try:
#                     chunk = base64.b64decode(obj["data"])
#                     process.stdin.write(chunk)
#                     process.stdin.flush()
#                 except Exception as e:
#                     print("⚠ ffmpeg write error:", e, flush=True)
#                 continue
#     finally:
#         try:
#             if process.stdin:
#                 process.stdin.close()
#         except:
#             pass
#         try:
#             process.wait(timeout=2)
#         except Exception:
#             process.kill()

#         asyncio.run_coroutine_threadsafe(audio_queue.put(None), loop)
#         print("✅ Browser connection closed cleanly", flush=True)


# # silence favicon 404
# @app.route('/favicon.ico')
# def favicon():
#     return ('', 204)


# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)






# day 27
# import os
# import asyncio
# import websockets
# import subprocess
# import threading
# import json
# import base64
# import traceback
# from flask import Flask, render_template, jsonify, request
# from flask_sock import Sock
# from dotenv import load_dotenv
# import google.generativeai as genai
# import requests   # === Day 25 CHANGE: to fetch weather ===
# import re         # === Day 25 CHANGE: to detect city name ===

# load_dotenv()

# ASSEMBLYAI_KEY = os.getenv("ASSEMBLYAI_API_KEY")
# ASSEMBLYAI_URL = "wss://streaming.assemblyai.com/v3/ws"

# GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# genai.configure(api_key=GEMINI_KEY)

# # Defensive: handle missing murf env gracefully
# MURF_KEY = os.getenv("MURF_API_KEY")
# MURF_KEY = MURF_KEY.strip() if isinstance(MURF_KEY, str) else None
# MURF_URL = "wss://api.murf.ai/v1/speech/stream-input"

# OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")  # ✅ Weather API key

# IPGEO_KEY = os.getenv("IPGEO_KEY") 

# API_NINJAS_KEY = os.getenv("API_NINJAS_KEY")
# # ASTROLOGY_URL = f"https://api.api-ninjas.com/v1/horoscope?zodiac={sign.lower()}"

# CONFIG_FILE = "config.json"

# app = Flask(__name__)
# sock = Sock(app)

# # ---------------------------
# # Conversation history
# # ---------------------------
# chat_history = []

# # Load saved keys
# def load_config():
#     try:
#         with open(CONFIG_FILE, "r") as f:
#             return json.load(f)
#     except FileNotFoundError:
#         return {
#             "MURF_KEY": "",
#             "GEMINI_KEY": "",
#             "ASSEMBLY_KEY": "",
#             "WEATHER_KEY": "",
#             "MOON_KEY": "",
#             "HOROSCOPE_KEY": ""
#         }

# # Save keys
# def save_config(config):
#     with open(CONFIG_FILE, "w") as f:
#         json.dump(config, f, indent=4)

# config = load_config()


# @app.route("/")
# def index():
#     return render_template("WebSocket.html", config=config)


# @app.route("/save_keys", methods=["POST"])
# def save_keys():
#     data = request.json
#     for key, value in data.items():
#         config[key] = value
#     save_config(config)
#     return jsonify({"status": "success", "message": "Keys saved!"})


# # ---------------------------
# # Weather skill function
# # ---------------------------
# def get_weather(city: str):
#     """Fetch weather for a given city using OpenWeather API"""
#     try:
#         url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric"
#         resp = requests.get(url, timeout=8)
#         data = resp.json()
#         if data.get("cod") != 200:
#             return f"Arrr! I couldn't find weather for {city}. ⚠"
#         temp = data["main"]["temp"]
#         desc = data["weather"][0]["description"]
#         return f"{temp}°C with {desc}"
#     except Exception as e:
#         return f"⚠ Weather API error: {str(e)}"


# # -----------------------------------
# # Helper: Convert azimuth degrees → direction (N, NE, E, SE, S, SW, W, NW)
# # -----------------------------------
# def azimuth_to_direction(degrees):
#     directions = [
#         "North", "North-East", "East", "South-East",
#         "South", "South-West", "West", "North-West"
#     ]
#     idx = round(degrees / 45) % 8
#     return directions[idx]


# # -----------------------------------
# # Special Skill: Get User Location (IP-based)
# # -----------------------------------
# def get_user_location():
#     """
#     Uses IPGeolocation IP API to detect user's city + lat/lon automatically.
#     This makes the Moon skill work anywhere without hardcoding coordinates.
#     """
#     try:
#         if not IPGEO_KEY:
#             return None, None, "Unknown city", "Unknown country"
#         url = f"https://api.ipgeolocation.io/ipgeo?apiKey={IPGEO_KEY}"
#         res = requests.get(url, timeout=6).json()
#         lat = res.get("latitude")
#         lon = res.get("longitude")
#         city = res.get("city", "Unknown city")
#         country = res.get("country_name", "Unknown country")
#         # Convert to floats if present
#         lat = float(lat) if lat is not None else None
#         lon = float(lon) if lon is not None else None
#         return lat, lon, city, country
#     except Exception as e:
#         print("⚠️ IP location error:", e, flush=True)
#         return None, None, "Unknown city", "Unknown country"


# # ---------------------------
# # Moon skill function
# # ---------------------------
# def get_moon_position():
#     """
#     Fetch moon data from IPGeolocation Astronomy API for the user's current IP-based location.
#     Returns pirate-styled, short, friendly string including altitude, azimuth, direction,
#     rise/set times, phase, and distance.
#     """
#     try:
#         # Step 1: Detect user’s location (auto via IP)
#         lat, lon, city, country = get_user_location()

#         if not IPGEO_KEY:
#             return "⚓ Arrr! Me spyglass be empty — set IPGEO_KEY in yer .env, matey!"
#         if lat is None or lon is None:
#             return "⚓ Arrr! I can't spy yer location. Try again later, matey!"

#         # Step 2: Fetch Moon position from Astronomy API (JSON output)
#         url = f"https://api.ipgeolocation.io/astronomy?apiKey={IPGEO_KEY}&lat={lat}&long={lon}"
#         res = requests.get(url, timeout=6).json()

#         altitude = res.get("moon_altitude")     # degrees above horizon
#         azimuth = res.get("moon_azimuth")       # degrees clockwise from North
#         distance = res.get("moon_distance")     # km
#         phase = res.get("moon_phase")           # e.g., "Waxing Gibbous"
#         rise = res.get("moonrise")              # local time HH:MM
#         set_time = res.get("moonset")           # local time HH:MM

#         # Convert azimuth to cardinal direction
#         direction = azimuth_to_direction(azimuth)

#         # Speech-friendly, short pirate style + clear meaning of azimuth
#         return (
#             f"Arrr! 🌙 From {city}, {country}, the moon be {altitude}° high, "
#             f"azimuth {azimuth}° toward {direction}. "
#             f"It rises at {rise} and sets at {set_time}. "
#             f"Phase be {phase}, 'n distance {distance} km."
#         )
#     except Exception as e:
#         print("⚠️ Moon API error:", e, flush=True)
#         return "⚓ Arrr, me star charts be tangled! Can't fetch the moon right now."


# # ---------------------------
# # ADDED: Horoscope skill function (FIXED & DEBUGGED)
# # ---------------------------
# def get_horoscope(sign: str):
#     """
#     Fetch daily horoscope for a given zodiac sign using API Ninjas (API_NINJAS_KEY).
#     - Uses param `zodiac=` per the documentation you shared.
#     - Stronger error handling and debug prints so you can see what's coming back.
#     """
#     if not API_NINJAS_KEY:
#         # Helpful debug message if env var not set
#         print("⚠️ API_NINJAS_KEY not set in .env", flush=True)
#         return "⚠ Arrr! The astrology key be missin' in yer .env."

#     if not sign:
#         return "⚓ Arrr! Tell me yer zodiac sign, matey (like Aries or Leo)!"

#     try:
#         # Use 'zodiac' param name (per docs you pasted)
#         url = f"https://api.api-ninjas.com/v1/horoscope?zodiac={sign.lower()}"
#         headers = {"X-Api-Key": API_NINJAS_KEY}

#         # Make request with timeout
#         resp = requests.get(url, headers=headers, timeout=10)

#         # Debug output — ALWAYS print status/body so you can see API answers in server logs
#         print(f"🛰 Horoscope API status: {resp.status_code}", flush=True)
#         print(f"🛰 Horoscope API body: {resp.text}", flush=True)

#         if resp.status_code == 200:
#             # API Ninjas returns JSON normally; attempt to parse
#             try:
#                 data = resp.json()
#             except Exception:
#                 data = None

#             horoscope_text = None
#             if isinstance(data, dict):
#                 # prefer 'horoscope' key per docs; fallback to other likely keys
#                 horoscope_text = data.get("horoscope") or data.get("text") or None

#             if not horoscope_text:
#                 # fallback to raw response body (handles plain-text responses)
#                 horoscope_text = resp.text.strip()

#             # Pirate-styled friendly message (single source of truth)
#             return f"Arrr! 🔮 Fer {sign.capitalize()}, today, it be sayin': {horoscope_text}"
#         else:
#             # Provide a debug-friendly pirate message
#             return f"⚠ Arrr! I couldn't fetch yer horoscope (API {resp.status_code})."
#     except Exception as e:
#         print("❌ Horoscope error:", e, flush=True)
#         traceback.print_exc()
#         return f"⚠ Arrr! Somethin' went wrong fetchin' the stars: {str(e)}"
# # --------------------------- END horoscope function --------------------


# # ---------------------------
# # Gemini LLM (streaming text) + Weather Skill
# # (kept behaviour: stream_llm_response returns a string; rest of your pipeline expects string)
# # ---------------------------
# async def stream_llm_response(prompt_text: str):
#     """Append user prompt to chat_history, process skill if needed, otherwise use Gemini."""
#     global chat_history
#     chat_history.append({"role": "user", "text": prompt_text})

#     model = genai.GenerativeModel("gemini-1.5-flash")

#     AGENT_NAME = "Captain"
#     base_prompt = (
#         f"You are {AGENT_NAME}, a friendly pirate. "
#         f"- Always keep answers very short — never more than 4 sentences. "
#         f"Always speak in pirate slang, using words like: "
#         f"'Ahoy' (hello), 'Arrr' (excitement), 'Yo-ho-ho' (happy shout)' "
#         f"\n\nDo NOT use these words at all: "
#         f"'booty', 'shiver me timbers', 'savvy', 'Davy Jones', or any confusing old pirate phrases. "
#         f"\n\nPirate rules for talking: "
#         f"- Roll your 'R's and use 'Arrr!' "
#         f"- Drop the 'G' in words (say 'sailin'' not 'sailing'). "
#         f"- Use 'ye' instead of 'you' (say 'Are ye ready?'). "
#         f"- Keep it short, fun, and playful. "
#         f"\n\nIf someone asks your name or to introduce yourself, always reply: "
#         f"'Ahoy! I be {AGENT_NAME}, the jolliest pirate of the seas!' "
#         f"Keep the mood light, funny, and easy for everyone to enjoy.\n\n"
#     )

#     # === Weather Skill ===
#     if "weather" in prompt_text.lower() or "whether" in prompt_text.lower():
#         try:
#             # Extract city from user’s text (basic regex for capitalized words)
#             match = re.search(r"(?:in|of)\s+([A-Za-z\s]+)", prompt_text, re.IGNORECASE)
#             if match:
#                 city = match.group(1).strip() 
#                 # remove common trailing words
#                 city = re.sub(r"\b(today|now|right now|please|tomorrow)\b", "", city, flags=re.IGNORECASE).strip()
#                 if city:
#                     weather_info = get_weather(city)
#                     # Pirate-style weather report
#                     pirate_weather = f"Arrr! 🌤 In {city}, it be {weather_info}, matey!"
#                     chat_history.append({"role": "assistant", "text": pirate_weather})
#                     return pirate_weather
                    
#             # If no city found
#             pirate_fail = "⚓ Arrr! Ye forgot to tell me the city for the weather, matey!"
#             chat_history.append({"role": "assistant", "text": pirate_fail})
#             return pirate_fail

#         except Exception as e:
#             pirate_fail = "⚓ Arrr, me compass be broken! Can't fetch the weather right now."
#             chat_history.append({"role": "assistant", "text": pirate_fail})
#             return pirate_fail
#     # === End Weather Skill ===


#      # === 🌙 Moon Skill (IP-based auto location via IPGeolocation) ===
#     if "moon" in prompt_text.lower():
#         try:
#             pirate_moon = get_moon_position()
#             chat_history.append({"role": "assistant", "text": pirate_moon})
#             return pirate_moon
#         except Exception:
#             fail_msg = "⚓ Arrr, the moon map be broken!"
#             chat_history.append({"role": "assistant", "text": fail_msg})
#             return fail_msg
#     # === End Moon Skill ===

#     # === 🔮 Horoscope Skill (NEW) ===
#     if "horoscope" in prompt_text.lower() or "zodiac" in prompt_text.lower():
#         try:
#             # Extract zodiac sign (basic regex for common signs)
#             signs = ["aries","taurus","gemini","cancer","leo","virgo",
#                      "libra","scorpio","sagittarius","capricorn","aquarius","pisces"]
#             chosen_sign = None

#             for s in signs:
#                 if s in prompt_text.lower():
#                     chosen_sign = s
#                     break

#             if chosen_sign:
#                 # get_horoscope returns a pirate-styled string (or an error message)
#                 pirate_horo = get_horoscope(chosen_sign)
#                 chat_history.append({"role": "assistant", "text": pirate_horo})
#                 return pirate_horo
#             else:
#                 msg = "⚓ Arrr! Tell me yer zodiac sign, matey (like Aries or Leo)!"
#                 chat_history.append({"role": "assistant", "text": msg})
#                 return msg
#         except Exception:
#             fail_msg = "⚓ Arrr, the stars be cloudy! Can't fetch horoscope now."
#             chat_history.append({"role": "assistant", "text": fail_msg})
#             return fail_msg
#     # === End Horoscope Skill ===


#     # Normal Gemini flow if no special skill triggered
#     prompt = base_prompt
#     for turn in chat_history:
#         role = "User" if turn["role"] == "user" else "Assistant"
#         prompt += f"{role}: {turn['text']}\n"
#     prompt += "Assistant:"

#     print("\n🤖 Gemini Response (streaming):")
#     full_text = ""
#     response = model.generate_content(prompt, stream=True)
#     for chunk in response:
#         if getattr(chunk, "text", None):
#             print(chunk.text, end="", flush=True)
#             full_text += chunk.text
#     print("\n✅ End of Gemini Response\n", flush=True)

#     chat_history.append({"role": "assistant", "text": full_text})
#     return full_text



# # ---------------------------
# # Murf TTS (streamed)
# # ---------------------------
# async def send_to_murf(text: str, client_send=None):
#     """Stream text to Murf TTS and forward audio chunks to client_send."""
#     if not text or not text.strip():
#         print("⚠ Empty text, skipping Murf TTS", flush=True)
#         return

#     ctx = "day25-demo"  # === Day 25 CHANGE: updated context name ===
#     print(f"\n🚀 send_to_murf CALLED (ctx={ctx}) text len={len(text)}\n", flush=True)

#     if not MURF_KEY:
#         print("⚠️ MURF_KEY missing — cannot stream TTS", flush=True)
#         return

#     ws_url = f"{MURF_URL}?api-key={MURF_KEY}&sample_rate=16000&channel_type=MONO&format=mp3"
#     sent_end = False
#     got_any_audio = False

#     try:
#         async with websockets.connect(ws_url, max_size=None, ping_interval=None) as ws:
#             print("✅ Connected to Murf WS", flush=True)

#             # config
#             await ws.send(json.dumps({
#                 "type": "config",
#                 "context_id": ctx,
#                 "voice_config": {
#                     "voiceId": "en-UK-freddie",
#                     "voice_gender": "male",
#                     "language": "en-UK"
#                 },
#                 "format": "mp3",
#                 "sample_rate": 16000
#             }))
#             print("📨 Sent Murf config", flush=True)

#             # speak
#             await ws.send(json.dumps({
#                 "type": "speak",
#                 "context_id": ctx,
#                 "text": text
#             }))
#             print("📨 Sent speak text to Murf", flush=True)

#             # idle timeout after audio
#             IDLE_TIMEOUT = 4
#             while True:
#                 try:
#                     msg = await asyncio.wait_for(ws.recv(), timeout=IDLE_TIMEOUT)
#                 except asyncio.TimeoutError:
#                     if got_any_audio:
#                         print("⏱ Murf idle timeout after audio — ending turn", flush=True)
#                         if client_send:
#                             client_send(json.dumps({"type": "murf_audio_end"}))
#                         sent_end = True
#                         try:
#                             await ws.close()
#                         except:
#                             pass
#                         break
#                     else:
#                         continue
#                 except websockets.ConnectionClosed:
#                     print("ℹ Murf WS closed by server", flush=True)
#                     break

#                 if isinstance(msg, str):
#                     try:
#                         data = json.loads(msg)
#                     except Exception:
#                         continue
#                 else:
#                     continue

#                 # Audio chunk
#                 if "audio" in data:
#                     audio_b64 = data["audio"]
#                     got_any_audio = True
#                     if client_send:
#                         client_send(json.dumps({"type": "murf_audio", "audio": audio_b64}))
#                     print(f"🔊 forwarded Murf chunk, size= {len(audio_b64)}", flush=True)
#                     continue

#                 # End of response
#                 if data.get("type") in ("speak_end", "completed", "response_end", "audio_end", "end"):
#                     print("✅ Murf signalled end of response", flush=True)
#                     if client_send:
#                         client_send(json.dumps({"type": "murf_audio_end"}))
#                     sent_end = True
#                     break

#     except Exception as e:
#         print("❌ Murf error:", e, flush=True)
#         traceback.print_exc()
#     finally:
#         if client_send and not sent_end and got_any_audio:
#             try:
#                 print("🛟 Forcing murf_audio_end in finally()", flush=True)
#                 client_send(json.dumps({"type": "murf_audio_end"}))
#             except Exception as e:
#                 print("❌ failed to send murf_audio_end in finally:", e, flush=True)


# # ---------------------------
# # AssemblyAI Streaming
# # ---------------------------
# async def transcribe_realtime(audio_queue, client_send, loop):
#     """Connects to AssemblyAI Realtime and forwards audio and transcripts."""
#     async with websockets.connect(
#         ASSEMBLYAI_URL,
#         extra_headers={"Authorization": ASSEMBLYAI_KEY},
#         max_size=None
#     ) as aai_ws:
#         print("✅ Connected to AssemblyAI Realtime API", flush=True)

#         async def send_audio():
#             while True:
#                 pcm_chunk = await audio_queue.get()
#                 if pcm_chunk is None:
#                     break
#                 try:
#                     await aai_ws.send(pcm_chunk)
#                 except Exception as e:
#                     print("❌ Failed to send audio to AssemblyAI:", e, flush=True)
#                     break

#         async def recv_transcripts():
#             async for msg in aai_ws:
#                 try:
#                     data = json.loads(msg)
#                 except Exception:
#                     continue

#                 if client_send:
#                     client_send(msg)

#                 if data.get("type") == "Turn":
#                     transcript = data.get("transcript", "")
#                     print(f"\n📝 Transcript (Turn): {transcript}", flush=True)

#                     if data.get("end_of_turn"):
#                         print("✅ End of Turn Reached - processing", flush=True)

#                         async def process_turn():
#                             try:
#                                 llm_text = await stream_llm_response(transcript)
#                                 if client_send:
#                                     client_send(json.dumps({"type": "gemini_response", "text": llm_text}))
#                                 await send_to_murf(llm_text, client_send)
#                             except Exception as e:
#                                 print("❌ process_turn error:", e, flush=True)
#                                 traceback.print_exc()

#                         asyncio.create_task(process_turn())

#         await asyncio.gather(send_audio(), recv_transcripts())


# def start_transcriber(audio_queue, client_send, loop):
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(transcribe_realtime(audio_queue, client_send, loop))


# # ---------------------------
# # Flask WebSocket Handler
# # ---------------------------
# @sock.route('/ws')
# def ws_handler(ws):
#     print("🎧 WS client connected (browser)", flush=True)

#     # thread-safe sender bound to this ws
#     send_lock = threading.Lock()

#     def send_to_client(message: str):
#         try:
#             with send_lock:
#                 if hasattr(ws, "connected") and not ws.connected:
#                     return
#                 ws.send(message)
#         except Exception as e:
#             print(f"⚠ send_to_client skipped (client closed?): {e}", flush=True)

#     # ffmpeg process
#     ffmpeg_cmd = [
#         "ffmpeg", "-loglevel", "quiet", "-i", "pipe:0",
#         "-ar", "16000", "-ac", "1", "-f", "s16le", "pipe:1"
#     ]
#     process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

#     audio_queue = asyncio.Queue()
#     loop = asyncio.new_event_loop()

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
#     threading.Thread(target=start_transcriber, args=(audio_queue, send_to_client, loop), daemon=True).start()

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

#             try:
#                 obj = json.loads(msg)
#             except Exception as e:
#                 print("⚠ Bad msg:", e, msg, flush=True)
#                 continue

#             if obj.get("type") == "audio_chunk":
#                 try:
#                     chunk = base64.b64decode(obj["data"])
#                     process.stdin.write(chunk)
#                     process.stdin.flush()
#                 except Exception as e:
#                     print("⚠ ffmpeg write error:", e, flush=True)
#                 continue
#     finally:
#         try:
#             if process.stdin:
#                 process.stdin.close()
#         except:
#             pass
#         try:
#             process.wait(timeout=2)
#         except Exception:
#             process.kill()

#         asyncio.run_coroutine_threadsafe(audio_queue.put(None), loop)
#         print("✅ Browser connection closed cleanly", flush=True)


# # silence favicon 404
# @app.route('/favicon.ico')
# def favicon():
#     return ('', 204)


# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)










# import os
# import asyncio
# import websockets
# import subprocess
# import threading
# import json
# import base64
# import traceback
# from flask import Flask, render_template, jsonify, request
# from flask_sock import Sock
# from dotenv import load_dotenv
# import google.generativeai as genai
# import requests   # === Day 25 CHANGE: to fetch weather ===
# import re         # === Day 25 CHANGE: to detect city name ===

# load_dotenv()

# ASSEMBLYAI_KEY = os.getenv("ASSEMBLYAI_API_KEY")
# ASSEMBLYAI_URL = "wss://streaming.assemblyai.com/v3/ws"

# GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# genai.configure(api_key=GEMINI_KEY)

# # Defensive: handle missing murf env gracefully
# MURF_KEY = os.getenv("MURF_API_KEY")
# MURF_KEY = MURF_KEY.strip() if isinstance(MURF_KEY, str) else None
# MURF_URL = "wss://api.murf.ai/v1/speech/stream-input"

# OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")  # ✅ Weather API key

# IPGEO_KEY = os.getenv("IPGEO_KEY") 

# API_NINJAS_KEY = os.getenv("API_NINJAS_KEY")
# # ASTROLOGY_URL = f"https://api.api-ninjas.com/v1/horoscope?zodiac={sign.lower()}"

# CONFIG_FILE = "config.json"

# app = Flask(__name__)
# sock = Sock(app)

# # ---------------------------
# # Conversation history
# # ---------------------------
# chat_history = []

# # Load saved keys
# def load_config():
#     try:
#         with open(CONFIG_FILE, "r") as f:
#             return json.load(f)
#     except FileNotFoundError:
#         return {
#             "MURF_KEY": "",
#             "GEMINI_KEY": "",
#             "ASSEMBLY_KEY": "",
#             "WEATHER_KEY": "",
#             "MOON_KEY": "",
#             "HOROSCOPE_KEY": ""
#         }

# # Save keys
# def save_config(config):
#     with open(CONFIG_FILE, "w") as f:
#         json.dump(config, f, indent=4)

# config = load_config()

# # ---------------------------
# # Day 27 minimal change:
# # If the user has provided keys via the UI (config.json), prefer them over .env
# # (Only this override is added; rest of your logic unchanged.)
# # ---------------------------
# try:
#     if isinstance(config.get("GEMINI_KEY"), str) and config.get("GEMINI_KEY").strip():
#         GEMINI_KEY = config.get("GEMINI_KEY").strip()
#         # re-configure genai with user-provided key
#         try:
#             genai.configure(api_key=GEMINI_KEY)
#         except Exception as _e:
#             # keep the previous configure if reconfigure fails
#             print("⚠️ genai.configure failed with user key:", _e, flush=True)
#     if isinstance(config.get("MURF_KEY"), str) and config.get("MURF_KEY").strip():
#         MURF_KEY = config.get("MURF_KEY").strip()
#     if isinstance(config.get("ASSEMBLY_KEY"), str) and config.get("ASSEMBLY_KEY").strip():
#         ASSEMBLYAI_KEY = config.get("ASSEMBLY_KEY").strip()
#     if isinstance(config.get("WEATHER_KEY"), str) and config.get("WEATHER_KEY").strip():
#         OPENWEATHER_KEY = config.get("WEATHER_KEY").strip()
#     if isinstance(config.get("MOON_KEY"), str) and config.get("MOON_KEY").strip():
#         IPGEO_KEY = config.get("MOON_KEY").strip()
#     if isinstance(config.get("HOROSCOPE_KEY"), str) and config.get("HOROSCOPE_KEY").strip():
#         API_NINJAS_KEY = config.get("HOROSCOPE_KEY").strip()
# except Exception as e:
#     print("⚠️ Error applying config overrides:", e, flush=True)

# @app.route("/")
# def index():
#     # Day 27 minimal change: pass `config` into template so the modal values show saved keys
#     return render_template("WebSocket.html", config=config)


# @app.route("/save_keys", methods=["POST"])
# def save_keys():
#     data = request.json
#     for key, value in data.items():
#         config[key] = value
#     save_config(config)
#     return jsonify({"status": "success", "message": "Keys saved!"})


# # ---------------------------
# # Weather skill function
# # ---------------------------
# def get_weather(city: str):
#     """Fetch weather for a given city using OpenWeather API"""
#     try:
#         url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric"
#         resp = requests.get(url, timeout=8)
#         data = resp.json()
#         if data.get("cod") != 200:
#             return f"Arrr! I couldn't find weather for {city}. ⚠"
#         temp = data["main"]["temp"]
#         desc = data["weather"][0]["description"]
#         return f"{temp}°C with {desc}"
#     except Exception as e:
#         return f"⚠ Weather API error: {str(e)}"


# # -----------------------------------
# # Helper: Convert azimuth degrees → direction (N, NE, E, SE, S, SW, W, NW)
# # -----------------------------------
# def azimuth_to_direction(degrees):
#     directions = [
#         "North", "North-East", "East", "South-East",
#         "South", "South-West", "West", "North-West"
#     ]
#     idx = round(degrees / 45) % 8
#     return directions[idx]


# # -----------------------------------
# # Special Skill: Get User Location (IP-based)
# # -----------------------------------
# def get_user_location():
#     """
#     Uses IPGeolocation IP API to detect user's city + lat/lon automatically.
#     This makes the Moon skill work anywhere without hardcoding coordinates.
#     """
#     try:
#         if not IPGEO_KEY:
#             return None, None, "Unknown city", "Unknown country"
#         url = f"https://api.ipgeolocation.io/ipgeo?apiKey={IPGEO_KEY}"
#         res = requests.get(url, timeout=6).json()
#         lat = res.get("latitude")
#         lon = res.get("longitude")
#         city = res.get("city", "Unknown city")
#         country = res.get("country_name", "Unknown country")
#         # Convert to floats if present
#         lat = float(lat) if lat is not None else None
#         lon = float(lon) if lon is not None else None
#         return lat, lon, city, country
#     except Exception as e:
#         print("⚠️ IP location error:", e, flush=True)
#         return None, None, "Unknown city", "Unknown country"


# # ---------------------------
# # Moon skill function
# # ---------------------------
# def get_moon_position():
#     """
#     Fetch moon data from IPGeolocation Astronomy API for the user's current IP-based location.
#     Returns pirate-styled, short, friendly string including altitude, azimuth, direction,
#     rise/set times, phase, and distance.
#     """
#     try:
#         # Step 1: Detect user’s location (auto via IP)
#         lat, lon, city, country = get_user_location()

#         if not IPGEO_KEY:
#             return "⚓ Arrr! Me spyglass be empty — set IPGEO_KEY in yer .env, matey!"
#         if lat is None or lon is None:
#             return "⚓ Arrr! I can't spy yer location. Try again later, matey!"

#         # Step 2: Fetch Moon position from Astronomy API (JSON output)
#         url = f"https://api.ipgeolocation.io/astronomy?apiKey={IPGEO_KEY}&lat={lat}&long={lon}"
#         res = requests.get(url, timeout=6).json()

#         altitude = res.get("moon_altitude")     # degrees above horizon
#         azimuth = res.get("moon_azimuth")       # degrees clockwise from North
#         distance = res.get("moon_distance")     # km
#         phase = res.get("moon_phase")           # e.g., "Waxing Gibbous"
#         rise = res.get("moonrise")              # local time HH:MM
#         set_time = res.get("moonset")           # local time HH:MM

#         # Convert azimuth to cardinal direction
#         direction = azimuth_to_direction(azimuth)

#         # Speech-friendly, short pirate style + clear meaning of azimuth
#         return (
#             f"Arrr! 🌙 From {city}, {country}, the moon be {altitude}° high, "
#             f"azimuth {azimuth}° toward {direction}. "
#             f"It rises at {rise} and sets at {set_time}. "
#             f"Phase be {phase}, 'n distance {distance} km."
#         )
#     except Exception as e:
#         print("⚠️ Moon API error:", e, flush=True)
#         return "⚓ Arrr, me star charts be tangled! Can't fetch the moon right now."


# # ---------------------------
# # ADDED: Horoscope skill function (FIXED & DEBUGGED)
# # ---------------------------
# def get_horoscope(sign: str):
#     """
#     Fetch daily horoscope for a given zodiac sign using API Ninjas (API_NINJAS_KEY).
#     - Uses param `zodiac=` per the documentation you shared.
#     - Stronger error handling and debug prints so you can see what's coming back.
#     """
#     if not API_NINJAS_KEY:
#         # Helpful debug message if env var not set
#         print("⚠️ API_NINJAS_KEY not set in .env", flush=True)
#         return "⚠ Arrr! The astrology key be missin' in yer .env."

#     if not sign:
#         return "⚓ Arrr! Tell me yer zodiac sign, matey (like Aries or Leo)!"

#     try:
#         # Use 'zodiac' param name (per docs you pasted)
#         url = f"https://api.api-ninjas.com/v1/horoscope?zodiac={sign.lower()}"
#         headers = {"X-Api-Key": API_NINJAS_KEY}

#         # Make request with timeout
#         resp = requests.get(url, headers=headers, timeout=10)

#         # Debug output — ALWAYS print status/body so you can see API answers in server logs
#         print(f"🛰 Horoscope API status: {resp.status_code}", flush=True)
#         print(f"🛰 Horoscope API body: {resp.text}", flush=True)

#         if resp.status_code == 200:
#             # API Ninjas returns JSON normally; attempt to parse
#             try:
#                 data = resp.json()
#             except Exception:
#                 data = None

#             horoscope_text = None
#             if isinstance(data, dict):
#                 # prefer 'horoscope' key per docs; fallback to other likely keys
#                 horoscope_text = data.get("horoscope") or data.get("text") or None

#             if not horoscope_text:
#                 # fallback to raw response body (handles plain-text responses)
#                 horoscope_text = resp.text.strip()

#             # Pirate-styled friendly message (single source of truth)
#             return f"Arrr! 🔮 Fer {sign.capitalize()}, today, it be sayin': {horoscope_text}"
#         else:
#             # Provide a debug-friendly pirate message
#             return f"⚠ Arrr! I couldn't fetch yer horoscope (API {resp.status_code})."
#     except Exception as e:
#         print("❌ Horoscope error:", e, flush=True)
#         traceback.print_exc()
#         return f"⚠ Arrr! Somethin' went wrong fetchin' the stars: {str(e)}"
# # --------------------------- END horoscope function --------------------


# # ---------------------------
# # Gemini LLM (streaming text) + Weather Skill
# # (kept behaviour: stream_llm_response returns a string; rest of your pipeline expects string)
# # ---------------------------
# async def stream_llm_response(prompt_text: str):
#     """Append user prompt to chat_history, process skill if needed, otherwise use Gemini."""
#     global chat_history
#     chat_history.append({"role": "user", "text": prompt_text})

#     model = genai.GenerativeModel("gemini-1.5-flash")

#     AGENT_NAME = "Captain"
#     base_prompt = (
#         f"You are {AGENT_NAME}, a friendly pirate. "
#         f"- Always keep answers very short — never more than 4 sentences. "
#         f"Always speak in pirate slang, using words like: "
#         f"'Ahoy' (hello), 'Arrr' (excitement), 'Yo-ho-ho' (happy shout)' "
#         f"\n\nDo NOT use these words at all: "
#         f"'booty', 'shiver me timbers', 'savvy', 'Davy Jones', or any confusing old pirate phrases. "
#         f"\n\nPirate rules for talking: "
#         f"- Roll your 'R's and use 'Arrr!' "
#         f"- Drop the 'G' in words (say 'sailin'' not 'sailing'). "
#         f"- Use 'ye' instead of 'you' (say 'Are ye ready?'). "
#         f"- Keep it short, fun, and playful. "
#         f"\n\nIf someone asks your name or to introduce yourself, always reply: "
#         f"'Ahoy! I be {AGENT_NAME}, the jolliest pirate of the seas!' "
#         f"Keep the mood light, funny, and easy for everyone to enjoy.\n\n"
#     )

#     # === Weather Skill ===
#     if "weather" in prompt_text.lower() or "whether" in prompt_text.lower():
#         try:
#             # Extract city from user’s text (basic regex for capitalized words)
#             match = re.search(r"(?:in|of)\s+([A-Za-z\s]+)", prompt_text, re.IGNORECASE)
#             if match:
#                 city = match.group(1).strip() 
#                 # remove common trailing words
#                 city = re.sub(r"\b(today|now|right now|please|tomorrow)\b", "", city, flags=re.IGNORECASE).strip()
#                 if city:
#                     weather_info = get_weather(city)
#                     # Pirate-style weather report
#                     pirate_weather = f"Arrr! 🌤 In {city}, it be {weather_info}, matey!"
#                     chat_history.append({"role": "assistant", "text": pirate_weather})
#                     return pirate_weather
                    
#             # If no city found
#             pirate_fail = "⚓ Arrr! Ye forgot to tell me the city for the weather, matey!"
#             chat_history.append({"role": "assistant", "text": pirate_fail})
#             return pirate_fail

#         except Exception as e:
#             pirate_fail = "⚓ Arrr, me compass be broken! Can't fetch the weather right now."
#             chat_history.append({"role": "assistant", "text": pirate_fail})
#             return pirate_fail
#     # === End Weather Skill ===


#      # === 🌙 Moon Skill (IP-based auto location via IPGeolocation) ===
#     if "moon" in prompt_text.lower():
#         try:
#             pirate_moon = get_moon_position()
#             chat_history.append({"role": "assistant", "text": pirate_moon})
#             return pirate_moon
#         except Exception:
#             fail_msg = "⚓ Arrr, the moon map be broken!"
#             chat_history.append({"role": "assistant", "text": fail_msg})
#             return fail_msg
#     # === End Moon Skill ===

#     # === 🔮 Horoscope Skill (NEW) ===
#     if "horoscope" in prompt_text.lower() or "zodiac" in prompt_text.lower():
#         try:
#             # Extract zodiac sign (basic regex for common signs)
#             signs = ["aries","taurus","gemini","cancer","leo","virgo",
#                      "libra","scorpio","sagittarius","capricorn","aquarius","pisces"]
#             chosen_sign = None

#             for s in signs:
#                 if s in prompt_text.lower():
#                     chosen_sign = s
#                     break

#             if chosen_sign:
#                 # get_horoscope returns a pirate-styled string (or an error message)
#                 pirate_horo = get_horoscope(chosen_sign)
#                 chat_history.append({"role": "assistant", "text": pirate_horo})
#                 return pirate_horo
#             else:
#                 msg = "⚓ Arrr! Tell me yer zodiac sign, matey (like Aries or Leo)!"
#                 chat_history.append({"role": "assistant", "text": msg})
#                 return msg
#         except Exception:
#             fail_msg = "⚓ Arrr, the stars be cloudy! Can't fetch horoscope now."
#             chat_history.append({"role": "assistant", "text": fail_msg})
#             return fail_msg
#     # === End Horoscope Skill ===


#     # Normal Gemini flow if no special skill triggered
#     prompt = base_prompt
#     for turn in chat_history:
#         role = "User" if turn["role"] == "user" else "Assistant"
#         prompt += f"{role}: {turn['text']}\n"
#     prompt += "Assistant:"

#     print("\n🤖 Gemini Response (streaming):")
#     full_text = ""
#     response = model.generate_content(prompt, stream=True)
#     for chunk in response:
#         if getattr(chunk, "text", None):
#             print(chunk.text, end="", flush=True)
#             full_text += chunk.text
#     print("\n✅ End of Gemini Response\n", flush=True)

#     chat_history.append({"role": "assistant", "text": full_text})
#     return full_text



# # ---------------------------
# # Murf TTS (streamed)
# # ---------------------------
# async def send_to_murf(text: str, client_send=None):
#     """Stream text to Murf TTS and forward audio chunks to client_send."""
#     if not text or not text.strip():
#         print("⚠ Empty text, skipping Murf TTS", flush=True)
#         return

#     ctx = "day25-demo"  # === Day 25 CHANGE: updated context name ===
#     print(f"\n🚀 send_to_murf CALLED (ctx={ctx}) text len={len(text)}\n", flush=True)

#     if not MURF_KEY:
#         print("⚠️ MURF_KEY missing — cannot stream TTS", flush=True)
#         return

#     ws_url = f"{MURF_URL}?api-key={MURF_KEY}&sample_rate=16000&channel_type=MONO&format=mp3"
#     sent_end = False
#     got_any_audio = False

#     try:
#         async with websockets.connect(ws_url, max_size=None, ping_interval=None) as ws:
#             print("✅ Connected to Murf WS", flush=True)

#             # config
#             await ws.send(json.dumps({
#                 "type": "config",
#                 "context_id": ctx,
#                 "voice_config": {
#                     "voiceId": "en-UK-freddie",
#                     "voice_gender": "male",
#                     "language": "en-UK"
#                 },
#                 "format": "mp3",
#                 "sample_rate": 16000
#             }))
#             print("📨 Sent Murf config", flush=True)

#             # speak
#             await ws.send(json.dumps({
#                 "type": "speak",
#                 "context_id": ctx,
#                 "text": text
#             }))
#             print("📨 Sent speak text to Murf", flush=True)

#             # idle timeout after audio
#             IDLE_TIMEOUT = 4
#             while True:
#                 try:
#                     msg = await asyncio.wait_for(ws.recv(), timeout=IDLE_TIMEOUT)
#                 except asyncio.TimeoutError:
#                     if got_any_audio:
#                         print("⏱ Murf idle timeout after audio — ending turn", flush=True)
#                         if client_send:
#                             client_send(json.dumps({"type": "murf_audio_end"}))
#                         sent_end = True
#                         try:
#                             await ws.close()
#                         except:
#                             pass
#                         break
#                     else:
#                         continue
#                 except websockets.ConnectionClosed:
#                     print("ℹ Murf WS closed by server", flush=True)
#                     break

#                 if isinstance(msg, str):
#                     try:
#                         data = json.loads(msg)
#                     except Exception:
#                         continue
#                 else:
#                     continue

#                 # Audio chunk
#                 if "audio" in data:
#                     audio_b64 = data["audio"]
#                     got_any_audio = True
#                     if client_send:
#                         client_send(json.dumps({"type": "murf_audio", "audio": audio_b64}))
#                     print(f"🔊 forwarded Murf chunk, size= {len(audio_b64)}", flush=True)
#                     continue

#                 # End of response
#                 if data.get("type") in ("speak_end", "completed", "response_end", "audio_end", "end"):
#                     print("✅ Murf signalled end of response", flush=True)
#                     if client_send:
#                         client_send(json.dumps({"type": "murf_audio_end"}))
#                     sent_end = True
#                     break

#     except Exception as e:
#         print("❌ Murf error:", e, flush=True)
#         traceback.print_exc()
#     finally:
#         if client_send and not sent_end and got_any_audio:
#             try:
#                 print("🛟 Forcing murf_audio_end in finally()", flush=True)
#                 client_send(json.dumps({"type": "murf_audio_end"}))
#             except Exception as e:
#                 print("❌ failed to send murf_audio_end in finally:", e, flush=True)


# # ---------------------------
# # AssemblyAI Streaming
# # ---------------------------
# async def transcribe_realtime(audio_queue, client_send, loop):
#     """Connects to AssemblyAI Realtime and forwards audio and transcripts."""
#     async with websockets.connect(
#         ASSEMBLYAI_URL,
#         extra_headers={"Authorization": ASSEMBLYAI_KEY},
#         max_size=None
#     ) as aai_ws:
#         print("✅ Connected to AssemblyAI Realtime API", flush=True)

#         async def send_audio():
#             while True:
#                 pcm_chunk = await audio_queue.get()
#                 if pcm_chunk is None:
#                     break
#                 try:
#                     await aai_ws.send(pcm_chunk)
#                 except Exception as e:
#                     print("❌ Failed to send audio to AssemblyAI:", e, flush=True)
#                     break

#         async def recv_transcripts():
#             async for msg in aai_ws:
#                 try:
#                     data = json.loads(msg)
#                 except Exception:
#                     continue

#                 if client_send:
#                     client_send(msg)

#                 if data.get("type") == "Turn":
#                     transcript = data.get("transcript", "")
#                     print(f"\n📝 Transcript (Turn): {transcript}", flush=True)

#                     if data.get("end_of_turn"):
#                         print("✅ End of Turn Reached - processing", flush=True)

#                         async def process_turn():
#                             try:
#                                 llm_text = await stream_llm_response(transcript)

#                                 # Send Gemini text
#                                 if client_send:
#                                     client_send(json.dumps({"type": "gemini_response", "text": llm_text}))

#                                 # Send Murf audio
#                                 for chunk in murf_stream(llm_text):
#                                     client_send(json.dumps({"type": "murf_audio", "audio": chunk}))
#                                 client_send(json.dumps({"type": "murf_audio_end"}))

#                             except Exception as e:
#                                 print("❌ process_turn error:", e, flush=True)
#                                 traceback.print_exc()



# def start_transcriber(audio_queue, client_send, loop):
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(transcribe_realtime(audio_queue, client_send, loop))


# async def process_user_text(text: str, send_to_client):
#     try:
#         print(f"💬 process_user_text called with: {text}", flush=True)

#         # 1. Gemini
#         reply = await stream_llm_response(text)
#         print(f"🤖 Gemini reply: {reply}", flush=True)

#         # 2. Send Gemini reply as text
#         send_to_client(json.dumps({
#             "type": "gemini_response",
#             "text": reply
#         }))

#         # 3. Send Murf audio chunks (using your old murf_stream)
#         for chunk in murf_stream(reply):
#             send_to_client(json.dumps({
#                 "type": "murf_audio",
#                 "audio": chunk
#             }))

#         # Mark audio end
#         send_to_client(json.dumps({"type": "murf_audio_end"}))

#         print("✅ Murf pipeline finished", flush=True)

#     except Exception as e:
#         print("❌ process_user_text error:", e, flush=True)
#         traceback.print_exc()




# # # ---------------------------
# # # Gemini Response
# # # ---------------------------
# # def get_gemini_response(user_text: str) -> str:
# #     """
# #     Send user text to Gemini and return the reply.
# #     Replace this with your actual Gemini API call.
# #     """
# #     try:
# #         url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
# #         headers = {"Content-Type": "application/json"}
# #         payload = {
# #             "contents": [{
# #                 "parts": [{"text": user_text}]
# #             }]
# #         }
# #         params = {"key": GEMINI_KEY}
# #         resp = requests.post(url, headers=headers, params=params, json=payload, timeout=30)
# #         data = resp.json()

# #         return data["candidates"][0]["content"]["parts"][0]["text"]
# #     except Exception as e:
# #         print("⚠ Gemini error:", e, flush=True)
# #         return "Sorry, I had trouble thinking of a response."


# # # ---------------------------
# # # Murf Streaming
# # # ---------------------------
# # ---------------------------
# # Murf Streaming (OLD WORKING)
# # ---------------------------
# def murf_stream(text: str):
#     """
#     Stream audio chunks from Murf TTS for a given text.
#     Yields base64-encoded audio chunks.
#     """
#     try:
#         url = "https://api.murf.ai/v1/speech/generate/async"
#         headers = {
#             "accept": "application/json",
#             "content-type": "application/json",
#             "api-key": MURF_KEY,
#         }
#         payload = {
#             "voiceId": "en-US-1",  # change voice if you want
#             "format": "mp3",
#             "text": text
#         }

#         resp = requests.post(url, headers=headers, json=payload, timeout=30)
#         resp.raise_for_status()

#         # Example: Murf may return a job ID → poll for chunks
#         data = resp.json()
#         audio_url = data.get("audioFile")

#         if not audio_url:
#             print("⚠ Murf API did not return audio URL", flush=True)
#             return

#         # Fetch audio file (blocking, not true streaming)
#         audio_resp = requests.get(audio_url, timeout=60)
#         b64_chunk = base64.b64encode(audio_resp.content).decode("utf-8")
#         yield b64_chunk

#     except Exception as e:
#         print("⚠ Murf error:", e, flush=True)
#         return


# # ---------------------------
# # Flask WebSocket Handler
# # ---------------------------
# @sock.route('/ws')
# def ws_handler(ws):
#     print("🎧 WS client connected (browser)", flush=True)

#     # thread-safe sender bound to this ws
#     send_lock = threading.Lock()

#     def send_to_client(message: str):
#         try:
#             with send_lock:
#                 if hasattr(ws, "connected") and not ws.connected:
#                     return
#                 ws.send(message)
#         except Exception as e:
#             print(f"⚠ send_to_client skipped (client closed?): {e}", flush=True)

#     # ffmpeg process for mic input
#     ffmpeg_cmd = [
#         "ffmpeg", "-loglevel", "quiet", "-i", "pipe:0",
#         "-ar", "16000", "-ac", "1", "-f", "s16le", "pipe:1"
#     ]
#     process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

#     audio_queue = asyncio.Queue()
#     loop = asyncio.new_event_loop()

#     # background reader from ffmpeg → audio_queue
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
#     threading.Thread(
#         target=start_transcriber,
#         args=(audio_queue, send_to_client, loop),
#         daemon=True
#     ).start()

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

#             try:
#                 obj = json.loads(msg)
#             except Exception as e:
#                 print("⚠ Bad msg:", e, msg, flush=True)
#                 continue

#             # === AUDIO CHUNKS FROM MIC ===
#             if obj.get("type") == "audio_chunk":
#                 try:
#                     chunk = base64.b64decode(obj["data"])
#                     process.stdin.write(chunk)
#                     process.stdin.flush()
#                 except Exception as e:
#                     print("⚠ ffmpeg write error:", e, flush=True)
#                 continue

#             # === TYPED TEXT FROM USER ===

#             elif obj.get("type") == "user_text":
#                 user_text = obj.get("text", "").strip()
#                 if not user_text:
#                     continue

#                 print(f"📝 Received typed text: {user_text}", flush=True)

#                 # Echo transcript back to frontend
#                 send_to_client(json.dumps({
#                     "transcript": user_text,
#                     "end_of_turn": True
#                 }))

#                 # Run AI pipeline async
#                 asyncio.run_coroutine_threadsafe(
#                     process_user_text(user_text, send_to_client),
#                     loop
#                 )
#                 continue


#     finally:
#         try:
#             if process.stdin:
#                 process.stdin.close()
#         except:
#             pass
#         try:
#             process.wait(timeout=2)
#         except Exception:
#             process.kill()

#         asyncio.run_coroutine_threadsafe(audio_queue.put(None), loop)
#         print("✅ Browser connection closed cleanly", flush=True)


# # silence favicon 404
# @app.route('/favicon.ico')
# def favicon():
#     return ('', 204)


# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)











import os
import asyncio
import websockets
import subprocess
import threading
import json
import base64
import traceback
from flask import Flask, render_template, jsonify, request
from flask_sock import Sock
from dotenv import load_dotenv
import google.generativeai as genai
import requests   # === Day 25 CHANGE: to fetch weather ===
import re         # === Day 25 CHANGE: to detect city name ===

load_dotenv()

ASSEMBLYAI_KEY = os.getenv("ASSEMBLYAI_API_KEY")
ASSEMBLYAI_URL = "wss://streaming.assemblyai.com/v3/ws"

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_KEY)

# Defensive: handle missing murf env gracefully
MURF_KEY = os.getenv("MURF_API_KEY")
MURF_KEY = MURF_KEY.strip() if isinstance(MURF_KEY, str) else None
MURF_URL = "wss://api.murf.ai/v1/speech/stream-input"

OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")  # ✅ Weather API key

IPGEO_KEY = os.getenv("IPGEO_KEY") 

API_NINJAS_KEY = os.getenv("API_NINJAS_KEY")
# ASTROLOGY_URL = f"https://api.api-ninjas.com/v1/horoscope?zodiac={sign.lower()}"

CONFIG_FILE = "config.json"

app = Flask(__name__)
sock = Sock(app)

# ---------------------------
# Conversation history
# ---------------------------
chat_history = []

# Load saved keys
def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "MURF_KEY": "",
            "GEMINI_KEY": "",
            "ASSEMBLY_KEY": "",
            "WEATHER_KEY": "",
            "MOON_KEY": "",
            "HOROSCOPE_KEY": ""
        }

# Save keys
def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

config = load_config()

# ---------------------------
# Day 27 minimal change:
# If the user has provided keys via the UI (config.json), prefer them over .env
# (Only this override is added; rest of your logic unchanged.)
# ---------------------------
try:
    if isinstance(config.get("GEMINI_KEY"), str) and config.get("GEMINI_KEY").strip():
        GEMINI_KEY = config.get("GEMINI_KEY").strip()
        # re-configure genai with user-provided key
        try:
            genai.configure(api_key=GEMINI_KEY)
        except Exception as _e:
            # keep the previous configure if reconfigure fails
            print("⚠️ genai.configure failed with user key:", _e, flush=True)
    if isinstance(config.get("MURF_KEY"), str) and config.get("MURF_KEY").strip():
        MURF_KEY = config.get("MURF_KEY").strip()
    if isinstance(config.get("ASSEMBLY_KEY"), str) and config.get("ASSEMBLY_KEY").strip():
        ASSEMBLYAI_KEY = config.get("ASSEMBLY_KEY").strip()
    if isinstance(config.get("WEATHER_KEY"), str) and config.get("WEATHER_KEY").strip():
        OPENWEATHER_KEY = config.get("WEATHER_KEY").strip()
    if isinstance(config.get("MOON_KEY"), str) and config.get("MOON_KEY").strip():
        IPGEO_KEY = config.get("MOON_KEY").strip()
    if isinstance(config.get("HOROSCOPE_KEY"), str) and config.get("HOROSCOPE_KEY").strip():
        API_NINJAS_KEY = config.get("HOROSCOPE_KEY").strip()
except Exception as e:
    print("⚠️ Error applying config overrides:", e, flush=True)

@app.route("/")
def index():
    # Day 27 minimal change: pass `config` into template so the modal values show saved keys
    return render_template("WebSocket.html", config=config)


# @app.route("/save_keys", methods=["POST"])
# def save_keys():
#     data = request.json
#     for key, value in data.items():
#         config[key] = value
#     save_config(config)
#     return jsonify({"status": "success", "message": "Keys saved!"})


@app.route("/save_keys", methods=["POST"])
def save_keys():
    try:
        data = request.get_json(force=True)
        print("🔐 /save_keys called. Payload:", data, flush=True)

        # update config + persist
        for key, value in data.items():
            config[key] = value
        save_config(config)
        print(f"🔐 Saved config to {CONFIG_FILE}", flush=True)

        # runtime apply (so no restart needed)
        global MURF_KEY, ASSEMBLYAI_KEY, OPENWEATHER_KEY, IPGEO_KEY, API_NINJAS_KEY
        if config.get("GEMINI_KEY"):
            genai.configure(api_key=config.get("GEMINI_KEY").strip())
            print("🔑 GEMINI_KEY applied", flush=True)
        if config.get("MURF_KEY"): MURF_KEY = config.get("MURF_KEY").strip()
        if config.get("ASSEMBLY_KEY"): ASSEMBLYAI_KEY = config.get("ASSEMBLY_KEY").strip()
        if config.get("WEATHER_KEY"): OPENWEATHER_KEY = config.get("WEATHER_KEY").strip()
        if config.get("MOON_KEY"): IPGEO_KEY = config.get("MOON_KEY").strip()
        if config.get("HOROSCOPE_KEY"): API_NINJAS_KEY = config.get("HOROSCOPE_KEY").strip()

        print("🔐 In-memory keys updated", flush=True)
        return jsonify({"status": "success", "message": "Keys saved!"})

    except Exception as e:
        print("❌ /save_keys error:", e, flush=True)
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


# ---------------------------
# Weather skill function
# ---------------------------
def get_weather(city: str):
    """Fetch weather for a given city using OpenWeather API"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric"
        resp = requests.get(url, timeout=8)
        data = resp.json()
        if data.get("cod") != 200:
            return f"Arrr! I couldn't find weather for {city}. ⚠"
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        return f"{temp}°C with {desc}"
    except Exception as e:
        return f"⚠ Weather API error: {str(e)}"


# -----------------------------------
# Helper: Convert azimuth degrees → direction (N, NE, E, SE, S, SW, W, NW)
# -----------------------------------
def azimuth_to_direction(degrees):
    directions = [
        "North", "North-East", "East", "South-East",
        "South", "South-West", "West", "North-West"
    ]
    idx = round(degrees / 45) % 8
    return directions[idx]


# -----------------------------------
# Special Skill: Get User Location (IP-based)
# -----------------------------------
def get_user_location():
    """
    Uses IPGeolocation IP API to detect user's city + lat/lon automatically.
    This makes the Moon skill work anywhere without hardcoding coordinates.
    """
    try:
        if not IPGEO_KEY:
            return None, None, "Unknown city", "Unknown country"
        url = f"https://api.ipgeolocation.io/ipgeo?apiKey={IPGEO_KEY}"
        res = requests.get(url, timeout=6).json()
        lat = res.get("latitude")
        lon = res.get("longitude")
        city = res.get("city", "Unknown city")
        country = res.get("country_name", "Unknown country")
        # Convert to floats if present
        lat = float(lat) if lat is not None else None
        lon = float(lon) if lon is not None else None
        return lat, lon, city, country
    except Exception as e:
        print("⚠️ IP location error:", e, flush=True)
        return None, None, "Unknown city", "Unknown country"


# ---------------------------
# Moon skill function
# ---------------------------
def get_moon_position():
    """
    Fetch moon data from IPGeolocation Astronomy API for the user's current IP-based location.
    Returns pirate-styled, short, friendly string including altitude, azimuth, direction,
    rise/set times, phase, and distance.
    """
    try:
        # Step 1: Detect user’s location (auto via IP)
        lat, lon, city, country = get_user_location()

        if not IPGEO_KEY:
            return "⚓ Arrr! Me spyglass be empty — set IPGEO_KEY in yer .env, matey!"
        if lat is None or lon is None:
            return "⚓ Arrr! I can't spy yer location. Try again later, matey!"

        # Step 2: Fetch Moon position from Astronomy API (JSON output)
        url = f"https://api.ipgeolocation.io/astronomy?apiKey={IPGEO_KEY}&lat={lat}&long={lon}"
        res = requests.get(url, timeout=6).json()

        altitude = res.get("moon_altitude")     # degrees above horizon
        azimuth = res.get("moon_azimuth")       # degrees clockwise from North
        distance = res.get("moon_distance")     # km
        phase = res.get("moon_phase")           # e.g., "Waxing Gibbous"
        rise = res.get("moonrise")              # local time HH:MM
        set_time = res.get("moonset")           # local time HH:MM

        # Convert azimuth to cardinal direction
        direction = azimuth_to_direction(azimuth)

        # Speech-friendly, short pirate style + clear meaning of azimuth
        return (
            f"Arrr! 🌙 From your location, the moon be {altitude}° high, "
            f"azimuth {azimuth}° toward {direction}. "
            f"It rises at {rise} and sets at {set_time}. "
            f"Phase be {phase}, 'n distance {distance} km."
        )
    except Exception as e:
        print("⚠️ Moon API error:", e, flush=True)
        return "⚓ Arrr, me star charts be tangled! Can't fetch the moon right now."


# ---------------------------
# ADDED: Horoscope skill function (FIXED & DEBUGGED)
# ---------------------------
def get_horoscope(sign: str):
    """
    Fetch daily horoscope for a given zodiac sign using API Ninjas (API_NINJAS_KEY).
    - Uses param `zodiac=` per the documentation you shared.
    - Stronger error handling and debug prints so you can see what's coming back.
    """
    if not API_NINJAS_KEY:
        # Helpful debug message if env var not set
        print("⚠️ API_NINJAS_KEY not set in .env", flush=True)
        return "⚠ Arrr! The astrology key be missin' in yer .env."

    if not sign:
        return "⚓ Arrr! Tell me yer zodiac sign, matey (like Aries or Leo)!"

    try:
        # Use 'zodiac' param name (per docs you pasted)
        url = f"https://api.api-ninjas.com/v1/horoscope?zodiac={sign.lower()}"
        headers = {"X-Api-Key": API_NINJAS_KEY}

        # Make request with timeout
        resp = requests.get(url, headers=headers, timeout=10)

        # Debug output — ALWAYS print status/body so you can see API answers in server logs
        print(f"🛰 Horoscope API status: {resp.status_code}", flush=True)
        print(f"🛰 Horoscope API body: {resp.text}", flush=True)

        if resp.status_code == 200:
            # API Ninjas returns JSON normally; attempt to parse
            try:
                data = resp.json()
            except Exception:
                data = None

            horoscope_text = None
            if isinstance(data, dict):
                # prefer 'horoscope' key per docs; fallback to other likely keys
                horoscope_text = data.get("horoscope") or data.get("text") or None

            if not horoscope_text:
                # fallback to raw response body (handles plain-text responses)
                horoscope_text = resp.text.strip()

            # Pirate-styled friendly message (single source of truth)
            return f"Arrr! 🔮 Fer {sign.capitalize()}, today, it be sayin': {horoscope_text}"
        else:
            # Provide a debug-friendly pirate message
            return f"⚠ Arrr! I couldn't fetch yer horoscope (API {resp.status_code})."
    except Exception as e:
        print("❌ Horoscope error:", e, flush=True)
        traceback.print_exc()
        return f"⚠ Arrr! Somethin' went wrong fetchin' the stars: {str(e)}"
# --------------------------- END horoscope function --------------------


# ---------------------------
# Gemini LLM (streaming text) + Weather Skill
# (kept behaviour: stream_llm_response returns a string; rest of your pipeline expects string)
# ---------------------------
async def stream_llm_response(prompt_text: str):
    """Append user prompt to chat_history, process skill if needed, otherwise use Gemini."""
    global chat_history
    chat_history.append({"role": "user", "text": prompt_text})

    model = genai.GenerativeModel("gemini-1.5-flash")

    AGENT_NAME = "Captain"
    base_prompt = (
        f"You are {AGENT_NAME}, a friendly pirate. "
        f"- Always keep answers very short — never more than 4 sentences. "
        f"Always speak in pirate slang, using words like: "
        f"'Ahoy' (hello), 'Arrr' (excitement), 'Yo-ho-ho' (happy shout)' "
        f"\n\nDo NOT use these words at all: "
        f"'booty', 'shiver me timbers', 'savvy', 'Davy Jones', or any confusing old pirate phrases. "
        f"\n\nPirate rules for talking: "
        f"- Roll your 'R's and use 'Arrr!' "
        f"- Drop the 'G' in words (say 'sailin'' not 'sailing'). "
        f"- Use 'ye' instead of 'you' (say 'Are ye ready?'). "
        f"- Keep it short, fun, and playful. "
        f"\n\nIf someone asks your name or to introduce yourself, always reply: "
        f"'Ahoy! I be {AGENT_NAME}, the jolliest pirate of the seas!' "
        f"Keep the mood light, funny, and easy for everyone to enjoy.\n\n"
    )

    # === Weather Skill ===
    if "weather" in prompt_text.lower() or "whether" in prompt_text.lower():
        try:
            # Extract city from user’s text (basic regex for capitalized words)
            match = re.search(r"(?:in|of)\s+([A-Za-z\s]+)", prompt_text, re.IGNORECASE)
            if match:
                city = match.group(1).strip() 
                # remove common trailing words
                city = re.sub(r"\b(today|now|right now|please|tomorrow)\b", "", city, flags=re.IGNORECASE).strip()
                if city:
                    weather_info = get_weather(city)
                    # Pirate-style weather report
                    pirate_weather = f"Arrr! 🌤 In {city}, it be {weather_info}, matey!"
                    chat_history.append({"role": "assistant", "text": pirate_weather})
                    return pirate_weather
                    
            # If no city found
            pirate_fail = "⚓ Arrr! Ye forgot to tell me the city for the weather, matey!"
            chat_history.append({"role": "assistant", "text": pirate_fail})
            return pirate_fail

        except Exception as e:
            pirate_fail = "⚓ Arrr, me compass be broken! Can't fetch the weather right now."
            chat_history.append({"role": "assistant", "text": pirate_fail})
            return pirate_fail
    # === End Weather Skill ===


    # === 🌙 Moon Skill (IP-based auto location via IPGeolocation) ===
    if "moon" in prompt_text.lower():
        try:
            pirate_moon = get_moon_position()
            chat_history.append({"role": "assistant", "text": pirate_moon})
            return pirate_moon
        except Exception:
            fail_msg = "⚓ Arrr, the moon map be broken!"
            chat_history.append({"role": "assistant", "text": fail_msg})
            return fail_msg
    # === End Moon Skill ===

    # === 🔮 Horoscope Skill (NEW) ===
    if "horoscope" in prompt_text.lower() or "zodiac" in prompt_text.lower():
        try:
            # Extract zodiac sign (basic regex for common signs)
            signs = ["aries","taurus","gemini","cancer","leo","virgo",
                     "libra","scorpio","sagittarius","capricorn","aquarius","pisces"]
            chosen_sign = None

            for s in signs:
                if s in prompt_text.lower():
                    chosen_sign = s
                    break

            if chosen_sign:
                # get_horoscope returns a pirate-styled string (or an error message)
                pirate_horo = get_horoscope(chosen_sign)
                chat_history.append({"role": "assistant", "text": pirate_horo})
                return pirate_horo
            else:
                msg = "⚓ Arrr! Tell me yer zodiac sign, matey (like Aries or Leo)!"
                chat_history.append({"role": "assistant", "text": msg})
                return msg
        except Exception:
            fail_msg = "⚓ Arrr, the stars be cloudy! Can't fetch horoscope now."
            chat_history.append({"role": "assistant", "text": fail_msg})
            return fail_msg
    # === End Horoscope Skill ===


    # Normal Gemini flow if no special skill triggered
    prompt = base_prompt
    for turn in chat_history:
        role = "User" if turn["role"] == "user" else "Assistant"
        prompt += f"{role}: {turn['text']}\n"
    prompt += "Assistant:"

    print("\n🤖 Gemini Response (streaming):")
    full_text = ""
    response = model.generate_content(prompt, stream=True)
    for chunk in response:
        if getattr(chunk, "text", None):
            print(chunk.text, end="", flush=True)
            full_text += chunk.text
    print("\n✅ End of Gemini Response\n", flush=True)

    chat_history.append({"role": "assistant", "text": full_text})
    return full_text



# ---------------------------
# Murf TTS (streamed)
# ---------------------------
async def send_to_murf(text: str, client_send=None):
    """Stream text to Murf TTS and forward audio chunks to client_send."""
    if not text or not text.strip():
        print("⚠ Empty text, skipping Murf TTS", flush=True)
        return

    ctx = "day25-demo"  # === Day 25 CHANGE: updated context name ===
    print(f"\n🚀 send_to_murf CALLED (ctx={ctx}) text len={len(text)}\n", flush=True)

    if not MURF_KEY:
        print("⚠️ MURF_KEY missing — cannot stream TTS", flush=True)
        return

    ws_url = f"{MURF_URL}?api-key={MURF_KEY}&sample_rate=16000&channel_type=MONO&format=mp3"
    sent_end = False
    got_any_audio = False

    try:
        async with websockets.connect(ws_url, max_size=None, ping_interval=None) as ws:
            print("✅ Connected to Murf WS", flush=True)

            # config
            await ws.send(json.dumps({
                "type": "config",
                "context_id": ctx,
                "voice_config": {
                    "voiceId": "en-UK-freddie",
                    "voice_gender": "male",
                    "language": "en-UK"
                },
                "format": "mp3",
                "sample_rate": 16000
            }))
            print("📨 Sent Murf config", flush=True)

            # speak
            await ws.send(json.dumps({
                "type": "speak",
                "context_id": ctx,
                "text": text
            }))
            print("📨 Sent speak text to Murf", flush=True)

            # idle timeout after audio
            IDLE_TIMEOUT = 4
            while True:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=IDLE_TIMEOUT)
                except asyncio.TimeoutError:
                    if got_any_audio:
                        print("⏱ Murf idle timeout after audio — ending turn", flush=True)
                        if client_send:
                            client_send(json.dumps({"type": "murf_audio_end"}))
                        sent_end = True
                        try:
                            await ws.close()
                        except:
                            pass
                        break
                    else:
                        continue
                except websockets.ConnectionClosed:
                    print("ℹ Murf WS closed by server", flush=True)
                    break

                if isinstance(msg, str):
                    try:
                        data = json.loads(msg)
                    except Exception:
                        continue
                else:
                    continue

                # Audio chunk
                if "audio" in data:
                    audio_b64 = data["audio"]
                    got_any_audio = True
                    if client_send:
                        client_send(json.dumps({"type": "murf_audio", "audio": audio_b64}))
                    print(f"🔊 forwarded Murf chunk, size= {len(audio_b64)}", flush=True)
                    continue

                # End of response
                if data.get("type") in ("speak_end", "completed", "response_end", "audio_end", "end"):
                    print("✅ Murf signalled end of response", flush=True)
                    if client_send:
                        client_send(json.dumps({"type": "murf_audio_end"}))
                    sent_end = True
                    break

    except Exception as e:
        print("❌ Murf error:", e, flush=True)
        traceback.print_exc()
    finally:
        if client_send and not sent_end and got_any_audio:
            try:
                print("🛟 Forcing murf_audio_end in finally()", flush=True)
                client_send(json.dumps({"type": "murf_audio_end"}))
            except Exception as e:
                print("❌ failed to send murf_audio_end in finally:", e, flush=True)


# ---------------------------
# AssemblyAI Streaming
# ---------------------------
async def transcribe_realtime(audio_queue, client_send, loop):
    """Connects to AssemblyAI Realtime and forwards audio and transcripts."""
    async with websockets.connect(
        ASSEMBLYAI_URL,
        extra_headers={"Authorization": ASSEMBLYAI_KEY},
        max_size=None
    ) as aai_ws:
        print("✅ Connected to AssemblyAI Realtime API", flush=True)

        async def send_audio():
            while True:
                pcm_chunk = await audio_queue.get()
                if pcm_chunk is None:
                    break
                try:
                    await aai_ws.send(pcm_chunk)
                except Exception as e:
                    print("❌ Failed to send audio to AssemblyAI:", e, flush=True)
                    break

        async def recv_transcripts():
            async for msg in aai_ws:
                try:
                    data = json.loads(msg)
                except Exception:
                    continue

                if client_send:
                    client_send(msg)

                if data.get("type") == "Turn":
                    transcript = data.get("transcript", "")
                    print(f"\n📝 Transcript (Turn): {transcript}", flush=True)

                    if data.get("end_of_turn"):
                        print("✅ End of Turn Reached - processing", flush=True)

                        async def process_turn():
                            try:
                                llm_text = await stream_llm_response(transcript)

                                # Send Gemini text
                                if client_send:
                                    client_send(json.dumps({"type": "gemini_response", "text": llm_text}))

                                # Send Murf audio (new async function)
                                await send_to_murf(llm_text, client_send)

                            except Exception as e:
                                print("❌ process_turn error:", e, flush=True)
                                traceback.print_exc()

                        # ✅ FIXED: actually schedule the processing task
                        asyncio.create_task(process_turn())

        # ✅ FIXED: actually start both coroutines so this function stays alive
        sender_task = asyncio.create_task(send_audio())
        await recv_transcripts()
        try:
            await sender_task
        except Exception:
            pass


def start_transcriber(audio_queue, client_send, loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(transcribe_realtime(audio_queue, client_send, loop))


async def process_user_text(text: str, send_to_client):
    try:
        print(f"💬 process_user_text called with: {text}", flush=True)

        # 1. Gemini
        reply = await stream_llm_response(text)
        print(f"🤖 Gemini reply: {reply}", flush=True)

        # 2. Send Gemini reply as text
        send_to_client(json.dumps({
            "type": "gemini_response",
            "text": reply
        }))


        # 3. Send Murf audio (new async function)
        await send_to_murf(reply, send_to_client)
        print("✅ Murf pipeline finished", flush=True)

    except Exception as e:
        print("❌ process_user_text error:", e, flush=True)
        traceback.print_exc()




# # ---------------------------
# # Gemini Response
# # ---------------------------
# def get_gemini_response(user_text: str) -> str:
#     """
#     Send user text to Gemini and return the reply.
#     Replace this with your actual Gemini API call.
#     """
#     try:
#         url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
#         headers = {"Content-Type": "application/json"}
#         payload = {
#             "contents": [{
#                 "parts": [{"text": user_text}]
#             }]
#         }
#         params = {"key": GEMINI_KEY}
#         resp = requests.post(url, headers=headers, params=params, json=payload, timeout=30)
#         data = resp.json()

#         return data["candidates"][0]["content"]["parts"][0]["text"]
#     except Exception as e:
#         print("⚠ Gemini error:", e, flush=True)
#         return "Sorry, I had trouble thinking of a response."



# ---------------------------
# Flask WebSocket Handler
# ---------------------------
@sock.route('/ws')
def ws_handler(ws):
    print("🎧 WS client connected (browser)", flush=True)

    def send_to_client(message: str):
        try:
            ws.send(message)
        except Exception as e:
            print(f"⚠ send_to_client skipped (client closed?): {e}", flush=True)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    threading.Thread(target=loop.run_forever, daemon=True).start()

    # ffmpeg process for mic input
    ffmpeg_cmd = [
        "ffmpeg", "-loglevel", "quiet", "-i", "pipe:0",
        "-ar", "16000", "-ac", "1", "-f", "s16le", "pipe:1"
    ]
    process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    audio_queue = asyncio.Queue()

    # background reader from ffmpeg → audio_queue
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

            # # === TYPED TEXT FROM USER ===
            # elif obj.get("type") == "user_text":
            #     user_text = obj.get("text", "").strip()
            #     if not user_text:
            #         continue

            #     print(f"📝 Received typed text: {user_text}", flush=True)

            #     # Echo transcript back to frontend
            #     send_to_client(json.dumps({
            #         "type": "user_message",
            #         "text": user_text
            #     }))

            #     # Run AI pipeline async on the same loop thread
            #     asyncio.run_coroutine_threadsafe(
            #         process_user_text(user_text, send_to_client),
            #         loop
            #     )
            #     continue

    finally:
        try:
            if process.stdin:
                process.stdin.close()
        except:
            pass
        try:
            process.wait(timeout=2)
        except Exception:
            process.kill()

        asyncio.run_coroutine_threadsafe(audio_queue.put(None), loop)
        print("✅ Browser connection closed cleanly", flush=True)


# silence favicon 404
@app.route('/favicon.ico')
def favicon():
    return ('', 204)


# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), use_reloader=False)




if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT env var
    app.run(host="0.0.0.0", port=port, debug=False)
