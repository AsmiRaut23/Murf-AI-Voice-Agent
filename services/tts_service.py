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





import json
import asyncio
import traceback
import websockets

from config import settings


async def send_to_murf(text: str, client_send=None):
    """
    Stream text to Murf TTS and forward audio chunks to client_send.
    Preserves your idle timeout and 'murf_audio_end' guarantees.
    """
    if not text or not text.strip():
        print("⚠ Empty text, skipping Murf TTS", flush=True)
        return

    ctx = "day25-demo"  # kept from your original
    print(f"\n🚀 send_to_murf CALLED (ctx={ctx}) text len={len(text)}\n", flush=True)

    if not settings.MURF_KEY:
        print("⚠️ MURF_KEY missing — cannot stream TTS", flush=True)
        return

    ws_url = (
        f"{settings.MURF_URL}?api-key={settings.MURF_KEY}"
        f"&sample_rate=16000&channel_type=MONO&format=mp3"
    )
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
                        except Exception:
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
