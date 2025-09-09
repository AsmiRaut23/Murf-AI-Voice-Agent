# import requests, time
# from os import getenv

# ASSEMBLYAI_API_KEY = getenv("ASSEMBLYAI_API_KEY", "").strip()
# UPLOAD_URL = "https://api.assemblyai.com/v2/upload"
# TRANSCRIBE_URL = "https://api.assemblyai.com/v2/transcript"

# def upload_audio(file_bytes: bytes) -> str:
#     headers = {"authorization": ASSEMBLYAI_API_KEY}
#     resp = requests.post(UPLOAD_URL, headers=headers, data=file_bytes)
#     resp.raise_for_status()
#     return resp.json()["upload_url"]

# def transcribe_audio(audio_url: str) -> str:
#     headers = {"authorization": ASSEMBLYAI_API_KEY, "content-type": "application/json"}
#     create = requests.post(TRANSCRIBE_URL, headers=headers, json={"audio_url": audio_url})
#     create.raise_for_status()
#     tid = create.json()["id"]

#     while True:
#         poll = requests.get(f"{TRANSCRIBE_URL}/{tid}", headers=headers)
#         poll.raise_for_status()
#         data = poll.json()
#         if data["status"] == "completed":
#             return data["text"]
#         if data["status"] == "error":
#             raise RuntimeError(data.get("error", "STT error"))
#         time.sleep(1)





# import aiohttp
# import asyncio
# import os

# ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY", "").strip()
# UPLOAD_URL = "https://api.assemblyai.com/v2/upload"
# TRANSCRIBE_URL = "https://api.assemblyai.com/v2/transcript"


# async def upload_audio(file_bytes: bytes) -> str:
#     """
#     Uploads audio bytes to AssemblyAI and returns the audio URL.
#     """
#     headers = {"authorization": ASSEMBLYAI_API_KEY}
#     async with aiohttp.ClientSession() as session:
#         async with session.post(UPLOAD_URL, headers=headers, data=file_bytes) as resp:
#             resp.raise_for_status()
#             data = await resp.json()
#             return data["upload_url"]


# async def transcribe_audio(audio_queue: asyncio.Queue, send_to_client):
#     print("ℹ Starting transcription task...", flush=True)

#     """
#     Consume audio chunks from asyncio.Queue and send transcription.
#     """
#     chunks = []
#     while True:
#         chunk = await audio_queue.get()
#         if chunk is None:
#             break
#         chunks.append(chunk)
#         print(f"🗒 Chunk added: {len(chunk)} bytes", flush=True)

#     # Convert to bytes
#     audio_bytes = b"".join(chunks)
#     print(f"ℹ Total audio bytes: {len(audio_bytes)}", flush=True)

#     # Upload audio
#     audio_url = await upload_audio(audio_bytes)
#     print(f"ℹ Got audio URL: {audio_url}", flush=True)

#     headers = {"authorization": ASSEMBLYAI_API_KEY, "content-type": "application/json"}
#     async with aiohttp.ClientSession() as session:
#         async with session.post(TRANSCRIBE_URL, headers=headers, json={"audio_url": audio_url}) as create_resp:
#             create_resp.raise_for_status()
#             tid = (await create_resp.json())["id"]
#             print(f"ℹ Transcription ID: {tid}", flush=True)

#         # Poll for transcription
#         while True:
#             async with session.get(f"{TRANSCRIBE_URL}/{tid}", headers=headers) as poll_resp:
#                 poll_resp.raise_for_status()
#                 data = await poll_resp.json()
#                 if data["status"] == "completed":
#                     print("✅ Transcription completed:", data["text"], flush=True)
#                     if send_to_client:
#                         await send_to_client(data["text"])
#                     return data["text"]
#                 if data["status"] == "error":
#                     print("❌ Transcription error:", data.get("error"), flush=True)
#                     raise RuntimeError(data.get("error", "STT error"))
#             await asyncio.sleep(1)




# import os
# import asyncio
# import websockets
# import json
# import base64

# ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY", "").strip()
# # ASSEMBLYAI_WS_URL = "wss://streaming.assemblyai.com/v3/ws"
# # ASSEMBLYAI_WS_URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"
# ASSEMBLYAI_WS_URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000&model=universal"




# async def transcribe_universal_ws(audio_queue: asyncio.Queue, send_to_client=None):
#     """
#     Stream audio chunks from audio_queue to AssemblyAI WebSocket and receive live transcripts.
#     """
#     if not ASSEMBLYAI_API_KEY:
#         raise RuntimeError("ASSEMBLYAI_API_KEY not set")

#     headers = {
#         "Authorization": ASSEMBLYAI_API_KEY,
#         "Content-Type": "application/json"
#     }

#     async with websockets.connect(
#         ASSEMBLYAI_WS_URL,
#         extra_headers=headers,
#         ping_interval=5
#     ) as ws:
#         print("ℹ Connected to AssemblyAI WS for streaming...", flush=True)

#         async def send_audio_chunks():
#             while True:
#                 chunk = await audio_queue.get()
#                 if chunk is None:
#                     await ws.send(json.dumps({"audio_data": ""}))  # tells AAI no more audio
#                     break

#                 # Send chunk as base64
#                 try:
#                     b64_data = base64.b64encode(chunk).decode("utf-8")
#                     payload = {"audio_data": b64_data}
#                     await ws.send(json.dumps(payload))
#                 except Exception as e:
#                     print("⚠ Error sending chunk:", e, flush=True)

#         async def receive_transcripts():
#             """Listen for transcripts from AssemblyAI."""
#             final_text = None
#             try:
#                 async for msg in ws:
#                     print("🔎 Raw WS message:", msg, flush=True)  # <--- add this
#                     data = json.loads(msg)

#                     # Session confirmation
#                     if data.get("type") == "SessionBegins":
#                         print("✅ Session started:", data, flush=True)

#                     # Partial transcript
#                     elif data.get("type") == "PartialTranscript":
#                         if send_to_client:
#                             await send_to_client(data.get("text", ""))

#                     # Final transcript
#                     elif data.get("type") == "FinalTranscript":
#                         final_text = data.get("text", "")
#                         if send_to_client:
#                             await send_to_client(final_text)
#                         return final_text

#                     # Error handling
#                     elif data.get("type") == "error":
#                         print("⚠ AssemblyAI error:", data, flush=True)
#                         break

#             except websockets.ConnectionClosed:
#                 print("❌ AssemblyAI WS closed", flush=True)
#                     # break
#             return final_text
        
#         send_task = asyncio.create_task(send_audio_chunks())
#         recv_task = asyncio.create_task(receive_transcripts())

#         done, pending = await asyncio.wait(
#             [send_task, recv_task],
#             return_when=asyncio.FIRST_COMPLETED
#         )
#         # Cancel any remaining tasks
#         for task in pending:
#             task.cancel()

#         print("✅  Universal Streaming transcription finished", flush=True)
#         # Return last transcript if available
#         for task in done:
#             if task.exception() is None:
#                 return task.result()





# # services/stt_service.py
# import os
# import json
# import asyncio
# import queue
# import threading
# import assemblyai as aai

# from typing import Callable, Optional
# from assemblyai.streaming.v3 import (
#     StreamingClient,
#     StreamingClientOptions,
#     StreamingEvents,
#     StreamingParameters,
#     BeginEvent,
#     TurnEvent,
#     TerminationEvent,
# )

# ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY", "").strip()


# def start_assemblyai_stream(sdk_queue: "queue.Queue[Optional[bytes]]", client_send: Callable[[str], None]):
#     """
#     Blocking function — run in a thread.
#     - sdk_queue: queue.Queue() that yields raw PCM bytes (s16le, 16kHz, mono). Put None to end stream.
#     - client_send: sync callable that accepts a string (already JSON-serialized).
#     """

#     if not ASSEMBLYAI_API_KEY:
#         raise RuntimeError("ASSEMBLYAI_API_KEY not set")

#     # configure SDK (optional - the SDK also reads ASSEMBLYAI_API_KEY env var)
#     aai.settings.api_key = ASSEMBLYAI_API_KEY

#     # Create StreamingClient pointing to streaming host
#     opts = StreamingClientOptions(api_key=ASSEMBLYAI_API_KEY, api_host="streaming.assemblyai.com")
#     client = StreamingClient(opts)

#     # Event handlers
#     def on_begin(self: StreamingClient, ev: BeginEvent):
#         print("✅ AssemblyAI session started:", getattr(ev, "id", None))

#     def on_turn(self: StreamingClient, ev: TurnEvent):
#         # Print live transcript in terminal (partial or final)
#         if getattr(ev, "end_of_turn", False):
#             print("\n✅ Final transcript (terminal):", ev.transcript, flush=True)
#             final_text = ev.transcript or ""
#             # send final transcript to browser (UI expects only final transcripts)
#             try:
#                 payload = json.dumps({"type": "transcript", "partial": False, "text": final_text})
#                 client_send(payload)
#             except Exception as e:
#                 print("⚠ failed to forward final transcript to client:", e, flush=True)

#             # Generate Murf TTS and forward audio -> run async TTS in its own event loop
#             try:
#                 # import here to avoid circular imports / heavy imports at module load
#                 from services.tts_service import send_to_murf
#                 # run in fresh event loop (safe from this sync thread)
#                 asyncio.run(send_to_murf(final_text, client_send=client_send))
#             except Exception as e:
#                 print("❌ Murf TTS (send_to_murf) failed:", e, flush=True)
#         else:
#             # Partial turn — print inline for debugging, but do NOT send to UI (user wanted only final)
#             print(f"\r(partial) {ev.transcript}", end="", flush=True)

#     def on_termination(self: StreamingClient, ev: TerminationEvent):
#         print("ℹ AssemblyAI session terminated:", getattr(ev, "audio_duration_seconds", None))

#     def on_error(self: StreamingClient, ev):
#         print("⚠ AssemblyAI stream error:", ev)

#     client.on(StreamingEvents.Begin, on_begin)
#     client.on(StreamingEvents.Turn, on_turn)
#     client.on(StreamingEvents.Termination, on_termination)
#     client.on(StreamingEvents.Error, on_error)

#     # Connect with params appropriate for voice agents / low latency
#     params = StreamingParameters(
#         sample_rate=16000,
#         format_turns=False,  # lower latency; turns are still emitted as Turn events
#         end_of_turn_confidence_threshold=0.7,
#     )
#     client.connect(params)

#     # Turn our queue into a synchronous iterable for client.stream()
#     def audio_iter():
#         while True:
#             chunk = sdk_queue.get()
#             if chunk is None:
#                 break
#             # AssemblyAI expects raw PCM bytes (s16le 16kHz mono)
#             yield chunk

#     try:
#         # This blocks until stream ends (when audio_iter finishes)
#         client.stream(audio_iter())
#     finally:
#         try:
#             client.disconnect(terminate=True)
#         except Exception:
#             pass
#         print("✅ AssemblyAI streaming worker exiting")








# services/stt_service.py
import os
import json
import asyncio
import queue
import threading
import traceback
from typing import Callable, Optional
# --- CONFIG KEYS (live from config.json) ---
from config import settings

import assemblyai as aai
from assemblyai.streaming.v3 import (
    StreamingClient,
    StreamingClientOptions,
    StreamingEvents,
    StreamingParameters,
    BeginEvent,
    TurnEvent,
    TerminationEvent,
)

# --- ENV KEYS ---
# ASSEMBLY_KEY = os.getenv("ASSEMBLY_KEY", "").strip()
# GEMINI_KEY = os.getenv("GEMINI_KEY", "").strip()

# cfg = get_config()
ASSEMBLY_KEY = settings.ASSEMBLYAI_KEY.strip()
GEMINI_KEY = settings.GEMINI_KEY.strip()


def _log_err(prefix: str, err: Exception) -> None:
    print(f"❌ {prefix}: {err}", flush=True)
    traceback.print_exc()


def get_ai_response(user_text: str) -> str:
    """Get an AI reply to the user's final transcript using Gemini."""
    if not user_text or not user_text.strip():
        return "I didn't catch that. Could you say it again?"

    GEMINI_KEY = settings.GEMINI_KEY.strip()
    if not GEMINI_KEY:
        return "Hello! I’m here and listening. How can I help you?"

    try:
        import google.generativeai as genai  # type: ignore

        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = (
            "You are 'Captain', a concise, friendly voice assistant. "
            "Reply in one or two short sentences, conversationally.\n\n"
            f"User: {user_text}\nAssistant:"
        )

        resp = model.generate_content(prompt)
        text = getattr(resp, "text", "") or ""
        return text.strip() or "I’m here. How can I help?"
    except Exception as e:
        _log_err("Gemini call failed", e)
        return "I’m having a little trouble thinking right now, but I’m here."


def start_assemblyai_stream(
    sdk_queue: "queue.Queue[Optional[bytes]]",
    client_send: Callable[[str], None],
):
    
    ASSEMBLY_KEY = settings.ASSEMBLYAI_KEY.strip()
    """Blocking function — run in a background thread."""
    if not ASSEMBLY_KEY:
        raise RuntimeError("ASSEMBLYAI_API_KEY not set")

    aai.settings.api_key = ASSEMBLY_KEY
    opts = StreamingClientOptions(api_key=ASSEMBLY_KEY, api_host="streaming.assemblyai.com")
    client = StreamingClient(opts)

    # -----------------------
    # Event Handlers
    # -----------------------
    def on_begin(self: StreamingClient, ev: BeginEvent):
        print("✅ AssemblyAI session started:", getattr(ev, "id", None), flush=True)

    def on_turn(self: StreamingClient, ev: TurnEvent):
        """Handle only FINAL transcripts (no partials)."""
        try:
            if getattr(ev, "end_of_turn", False):
                final_text = (ev.transcript or "").strip()
                if not final_text:
                    print("ℹ Empty transcript received at end_of_turn — ignoring", flush=True)
                    return
                print("\n✅ Final transcript (terminal):", final_text, flush=True)

                # UI: final transcript
                try:
                    payload = json.dumps({"type": "final_transcript", "text": final_text})
                    client_send(payload)
                except Exception as send_err:
                    _log_err("Failed to send final_transcript to client", send_err)

                # # AI reply
                # ai_text = ""
                # try:
                #     ai_text = get_ai_response(final_text)
                # except Exception as ai_err:
                #     _log_err("AI response generation failed", ai_err)
                #     ai_text = "I’m here, but ran into a small error."

                # # UI: assistant text
                # try:
                #     payload = json.dumps({"type": "gemini_response", "text": ai_text})
                #     client_send(payload)
                # except Exception as send_err:
                #     _log_err("Failed to send gemini_response to client", send_err)

                # # Murf TTS
                # try:
                #     from services.tts_service import send_to_murf
                #     asyncio.run(send_to_murf(ai_text, client_send=client_send))
                # except Exception as tts_err:
                #     _log_err("Murf TTS failed", tts_err)


                # AI reply
                ai_text = ""
                try:
                    ai_text = get_ai_response(final_text)
                except Exception as ai_err:
                    _log_err("AI response generation failed", ai_err)
                    ai_text = "I’m here, but ran into a small error."

                # Apply pirate persona
                from services.gemini_service import pirate_persona  # make sure your pirate_persona is here
                pirate_text = pirate_persona(ai_text)

                # UI: assistant text
                try:
                    payload = json.dumps({"type": "gemini_response", "text": pirate_text})
                    client_send(payload)
                except Exception as send_err:
                    _log_err("Failed to send gemini_response to client", send_err)

                # Murf TTS
                try:
                    from services.tts_service import send_to_murf
                    print("➡ Sending to Murf TTS (pirate):", pirate_text, flush=True)
                    asyncio.run(send_to_murf(pirate_text, client_send=client_send))
                except Exception as tts_err:
                    _log_err("Murf TTS failed", tts_err)

        except Exception as e:
            _log_err("on_turn handler error", e)

    def on_termination(self: StreamingClient, ev: TerminationEvent):
        print("ℹ AssemblyAI session terminated:", getattr(ev, "audio_duration_seconds", None), flush=True)

    def on_error(self: StreamingClient, ev):
        print("⚠ AssemblyAI stream error:", ev, flush=True)

    client.on(StreamingEvents.Begin, on_begin)
    client.on(StreamingEvents.Turn, on_turn)
    client.on(StreamingEvents.Termination, on_termination)
    client.on(StreamingEvents.Error, on_error)

    params = StreamingParameters(
        sample_rate=16000,
        format_turns=False,
        end_of_turn_confidence_threshold=0.7,
    )

    client.connect(params)

    def audio_iter():
        while True:
            chunk = sdk_queue.get()
            if chunk is None:
                break
            yield chunk

    try:
        client.stream(audio_iter())
    except Exception as e:
        _log_err("AssemblyAI client.stream error", e)
    finally:
        try:
            client.disconnect(terminate=True)
        except Exception:
            pass
        print("✅ AssemblyAI streaming worker exiting", flush=True)











# import os
# import asyncio
# import websockets
# import json
# import base64

# ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY", "").strip()

# # v3 Universal-Streaming endpoint (raw websocket)
# # sample_rate and encoding must match the PCM coming from ffmpeg
# ASSEMBLYAI_WS_URL = "wss://streaming.assemblyai.com/v3/ws?sample_rate=16000&encoding=pcm_s16le"


# async def transcribe_universal_ws(audio_queue: asyncio.Queue, send_to_client=None):
#     """
#     Stream raw PCM audio chunks (bytes) from audio_queue to AssemblyAI v3,
#     and forward incoming transcripts to send_to_client (callable / coroutine).
#     """
#     if not ASSEMBLYAI_API_KEY:
#         raise RuntimeError("ASSEMBLYAI_API_KEY not set")

#     headers = {
#         "Authorization": ASSEMBLYAI_API_KEY,
#     }

#     # Use a reasonable max_size for large messages; disable limit with None if needed
#     async with websockets.connect(
#         ASSEMBLYAI_WS_URL,
#         extra_headers=headers,
#         max_size=None,
#         ping_interval=5,
#     ) as ws:
#         print("ℹ Connected to AssemblyAI WS for streaming...", flush=True)

#         async def send_audio_chunks():
#             """Get bytes from audio_queue and send as binary frames to AssemblyAI.
#             When receives None from queue -> send Terminate JSON and stop."""
#             while True:
#                 chunk = await audio_queue.get()
#                 if chunk is None:
#                     # Gracefully terminate the streaming session (v3 expects {"type": "Terminate"})
#                     try:
#                         await ws.send(json.dumps({"type": "Terminate"}))
#                         print("ℹ Sent Terminate to AssemblyAI", flush=True)
#                     except Exception as e:
#                         print("⚠ Error sending Terminate:", e, flush=True)
#                     break

#                 try:
#                     # chunk must be raw PCM bytes (s16le). If it's a base64 str, decode it.
#                     if isinstance(chunk, str):
#                         try:
#                             chunk = base64.b64decode(chunk)
#                         except Exception:
#                             chunk = chunk.encode("utf-8")

#                     # Send binary frame
#                     await ws.send(chunk)
#                 except Exception as e:
#                     print("⚠ Error sending chunk:", e, flush=True)

#         async def receive_transcripts():
#             """Listen for v3 messages and forward transcripts back to the client."""
#             final_text = None
#             try:
#                 async for msg in ws:
#                     # Server messages are JSON text (Begin, Turn, Termination, Error)
#                     print("🔎 Raw WS message:", msg, flush=True)

#                     # ignore binary messages from server if any
#                     if isinstance(msg, (bytes, bytearray)):
#                         continue

#                     try:
#                         data = json.loads(msg)
#                     except Exception as e:
#                         print("⚠ Failed to parse AssemblyAI message as JSON:", e, flush=True)
#                         continue

#                     msg_type = data.get("type")

#                     if msg_type == "Begin":
#                         print("✅ Session started:", data, flush=True)

#                     elif msg_type == "Turn":
#                         # v3 Turn object contains 'transcript' and 'end_of_turn'
#                         text = data.get("transcript", "")
#                         if text:
#                             if send_to_client:
#                                 try:
#                                     # send_to_client may be coroutine or sync callable; handle both
#                                     if asyncio.iscoroutinefunction(send_to_client):
#                                         await send_to_client(text)
#                                     else:
#                                         send_to_client(text)
#                                 except Exception as e:
#                                     print("⚠ send_to_client failed:", e, flush=True)

#                         if data.get("end_of_turn", False):
#                             final_text = text
#                             return final_text

#                     elif msg_type == "Termination":
#                         print("ℹ Received Termination from AssemblyAI:", data, flush=True)
#                         break

#                     elif msg_type == "Error":
#                         print("⚠ AssemblyAI error:", data, flush=True)
#                         break

#             except websockets.ConnectionClosed:
#                 print("❌ AssemblyAI WS closed", flush=True)

#             return final_text

#         send_task = asyncio.create_task(send_audio_chunks())
#         recv_task = asyncio.create_task(receive_transcripts())

#         done, pending = await asyncio.wait(
#             [send_task, recv_task],
#             return_when=asyncio.FIRST_COMPLETED,
#         )

#         # Cancel any remaining tasks
#         for task in pending:
#             task.cancel()

#         print("✅ Universal Streaming transcription finished", flush=True)

#         # Return result from whichever task completed successfully
#         for task in done:
#             if task.exception() is None:
#                 return task.result()
