# import requests
# from os import getenv

# MURF_API_KEY = getenv("MURF_API_KEY", "").strip()
# MURF_URL = "https://api.murf.ai/v1/speech/generate"
# FALLBACK_MESSAGE = "I'm having trouble connecting right now. Please try again later."

# def generate_audio(text: str, voice_id: str) -> str | None:
#     headers = {'Content-Type': 'application/json', 'api-key': MURF_API_KEY}
#     payload = {"text": text, "voice_id": "en-US-natalie", "format": "mp3", "sampleRate": "44100"}
#     resp = requests.post(MURF_URL, headers=headers, json=payload)
#     if resp.ok:
#         return resp.json().get("audioFile")
#     return None

# def fallback_audio(voice_id: str) -> str | None:
#     return generate_audio(FALLBACK_MESSAGE, voice_id)





# services/tts_service.py
import os
import json
import asyncio
import traceback
import base64
import websockets
from config import settings

# MURF_KEY = os.getenv("MURF_API_KEY", "").strip()
MURF_KEY = settings.MURF_KEY.strip()

# Correct Murf streaming WebSocket endpoint (streaming TTS)
MURF_WS_BASE = "wss://api.murf.ai/v1/speech/stream-input"
FALLBACK_MESSAGE = "I'm having trouble connecting right now. Please try again later."


async def send_to_murf(text: str, client_send=None, voice_id: str = "en-UK-freddie"):
    """
    Stream text to Murf via their streaming WebSocket endpoint and forward audio chunks to the client.
    client_send: sync or async callable that accepts a JSON string.
    We will:
      - send {"type":"murf_text","text": text} to client (so UI shows the assistant text),
      - stream audio chunks via {"type":"murf_audio","audio": "<base64>"}
      - send {"type":"murf_audio_end"} when done.
    """

    if not text or not text.strip():
        print("⚠ Empty text, skipping Murf TTS")
        return

    if not MURF_KEY:
        print("⚠️ MURF_KEY missing — cannot stream TTS")
        return

    # Build WS URL with query param api_key (Murf docs accept header or query param)
    ws_url = f"{MURF_WS_BASE}?api_key={MURF_KEY}&sample_rate=16000&channel_type=MONO&format=MP3"

    async def safe_client_send_obj(obj: dict):
        if not client_send:
            return
        payload_text = json.dumps(obj)
        try:
            if asyncio.iscoroutinefunction(client_send):
                await client_send(payload_text)
            else:
                # sync callable
                client_send(payload_text)
        except Exception as e:
            print("⚠ client_send failed:", e, flush=True)

    sent_end = False
    got_any_audio = False

    try:
        async with websockets.connect(ws_url, max_size=None, ping_interval=None) as ws:
            # Send config message as Murf examples expect
            await ws.send(json.dumps({
                "type": "config",
                "context_id": "day25-demo",
                "voice_config": {
                    "voiceId": voice_id,
                    "voice_gender": "male",
                    "language": "en-UK"
                },
                "format": "mp3",
                "sample_rate": 16000
            }))

            # Instruct Murf to speak the text
            await ws.send(json.dumps({"type": "speak", "context_id": "day25-demo", "text": text}))

            # Notify client UI of the text that'll be spoken
            await safe_client_send_obj({"type": "murf_text", "text": text})

            IDLE_TIMEOUT = 6
            while True:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=IDLE_TIMEOUT)
                except asyncio.TimeoutError:
                    # If we got audio earlier, treat timeout as done
                    if got_any_audio:
                        await safe_client_send_obj({"type": "murf_audio_end"})
                        sent_end = True
                        try:
                            await ws.close()
                        except:
                            pass
                        break
                    else:
                        # keep waiting
                        continue
                except websockets.ConnectionClosed:
                    break

                # Murf returns JSON frames with "audio" base64 or other events
                if isinstance(msg, (bytes, bytearray)):
                    # Murf typically sends JSON text messages; ignore raw binary if any
                    continue

                try:
                    data = json.loads(msg)
                except Exception:
                    continue

                if "audio" in data:
                    audio_b64 = data["audio"]
                    got_any_audio = True
                    await safe_client_send_obj({"type": "murf_audio", "audio": audio_b64})
                    continue

                if data.get("type") in ("speak_end", "completed", "audio_end", "end", "response_end"):
                    await safe_client_send_obj({"type": "murf_audio_end"})
                    sent_end = True
                    break

    except Exception as e:
        print("❌ Murf streaming TTS error:", e)
        traceback.print_exc()
        try:
            if client_send:
                await safe_client_send_obj({"type": "murf_error", "message": "TTS failed."})
        except Exception:
            pass
    finally:
        if client_send and not sent_end and got_any_audio:
            try:
                await safe_client_send_obj({"type": "murf_audio_end"})
            except Exception:
                pass











# import os
# import json
# import asyncio
# import traceback
# import websockets

# MURF_KEY = os.getenv("MURF_API_KEY", "").strip()
# MURF_URL = "wss://api.murf.ai/v1/speech/generate"
# FALLBACK_MESSAGE = "I'm having trouble connecting right now. Please try again later."


# def generate_audio(text: str, voice_id: str) -> str | None:
#     """Synchronous Murf TTS (blocking, returns audio URL)."""
#     import requests
#     if not MURF_KEY:
#         print("⚠️ MURF_KEY missing — cannot generate audio")
#         return None

#     headers = {"Content-Type": "application/json", "api-key": MURF_KEY}
#     payload = {"text": text, "voice_id": voice_id, "format": "mp3", "sampleRate": "16000"}
#     try:
#         resp = requests.post("https://api.murf.ai/v1/speech/generate", headers=headers, json=payload)
#         if resp.ok:
#             return resp.json().get("audioFile")
#     except Exception as e:
#         print("❌ Murf blocking TTS error:", e)
#     return None


# def fallback_audio(voice_id: str) -> str | None:
#     """Fallback Murf TTS message."""
#     return generate_audio(FALLBACK_MESSAGE, voice_id)


# async def send_to_murf(text: str, client_send=None):
#     """
#     Stream text to Murf TTS via WebSocket.
#     client_send: callable to send JSON messages to the client (WebSocket send).
#                  This function may be async or sync; we handle both.
#     """
#     if not text or not text.strip():
#         print("⚠ Empty text, skipping Murf TTS")
#         return

#     if not MURF_KEY:
#         print("⚠️ MURF_KEY missing — cannot stream TTS")
#         return

#     ctx = "day25-demo"
#     ws_url = f"{MURF_URL}?api-key={MURF_KEY}&sample_rate=16000&channel_type=MONO&format=mp3"
#     sent_end = False
#     got_any_audio = False

#     async def safe_client_send(payload_obj):
#         """Send payload_obj (dict) to client; handle sync/async client_send."""
#         if not client_send:
#             return
#         try:
#             payload_text = json.dumps(payload_obj)
#             if asyncio.iscoroutinefunction(client_send):
#                 await client_send(payload_text)
#             else:
#                 # sync callable
#                 try:
#                     client_send(payload_text)
#                 except Exception as e:
#                     # fall back to calling in thread-loop if needed
#                     print("⚠ client_send sync call failed:", e, flush=True)
#         except Exception as e:
#             print("⚠ client_send failed:", e, flush=True)

#     try:
#         async with websockets.connect(ws_url, max_size=None, ping_interval=None) as ws:
#             # Config (keep your original code structure)
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

#             # Send speak text
#             await ws.send(json.dumps({"type": "speak", "context_id": ctx, "text": text}))

#             # Receive audio chunks
#             IDLE_TIMEOUT = 4
#             while True:
#                 try:
#                     msg = await asyncio.wait_for(ws.recv(), timeout=IDLE_TIMEOUT)
#                 except asyncio.TimeoutError:
#                     if got_any_audio:
#                         if client_send:
#                             await safe_client_send({"type": "murf_audio_end"})
#                         sent_end = True
#                         try:
#                             await ws.close()
#                         except:
#                             pass
#                         break
#                     else:
#                         continue
#                 except websockets.ConnectionClosed:
#                     break

#                 if isinstance(msg, str):
#                     try:
#                         data = json.loads(msg)
#                     except Exception:
#                         continue
#                 else:
#                     continue

#                 # Forward audio chunk
#                 if "audio" in data:
#                     audio_b64 = data["audio"]
#                     got_any_audio = True
#                     if client_send:
#                         await safe_client_send({"type": "murf_audio", "audio": audio_b64})
#                     continue

#                 # End signal variants
#                 if data.get("type") in ("speak_end", "completed", "response_end", "audio_end", "end"):
#                     if client_send:
#                         await safe_client_send({"type": "murf_audio_end"})
#                     sent_end = True
#                     break

#     except Exception as e:
#         print("❌ Murf streaming TTS error:", e)
#         traceback.print_exc()
#     finally:
#         # Ensure client gets end-of-audio if we got audio but didn't send the end marker
#         if client_send and not sent_end and got_any_audio:
#             try:
#                 if asyncio.iscoroutinefunction(client_send):
#                     await client_send(json.dumps({"type": "murf_audio_end"}))
#                 else:
#                     client_send(json.dumps({"type": "murf_audio_end"}))
#             except Exception as e:
#                 print("❌ failed to send murf_audio_end in finally:", e)
