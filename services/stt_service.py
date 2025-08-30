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


import json
import asyncio
import websockets
import traceback

from config import settings
from services.gemini_service import chat_history, stream_llm_response
from services.tts_service import send_to_murf


async def transcribe_realtime(audio_queue, client_send, loop):
    """
    Connects to AssemblyAI Realtime and forwards audio and transcripts.
    Preserves your exact flow:
      - forward raw messages to client
      - on Turn with end_of_turn: append transcript, call Gemini, send gemini_response, then stream Murf
      - schedule process_turn with asyncio.create_task
    """
    async with websockets.connect(
        settings.ASSEMBLYAI_URL,
        extra_headers={"Authorization": settings.ASSEMBLYAI_KEY},
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
                    # keep same resilience as original
                    if client_send:
                        client_send(msg)
                    continue

                # forward to client
                if client_send:
                    client_send(msg)

                if data.get("type") == "Turn":
                    transcript = data.get("transcript", "")
                    print(f"\n📝 Transcript (Turn): {transcript}", flush=True)

                    if data.get("end_of_turn"):
                        print("✅ End of Turn Reached - processing", flush=True)

                        async def process_turn():
                            try:
                                # Save user transcript (kept, even though stream_llm_response also appends)
                                chat_history.append({"role": "user", "text": transcript})

                                # Gemini
                                llm_text = await stream_llm_response(transcript)

                                # Save AI reply
                                chat_history.append({"role": "assistant", "text": llm_text})

                                # Send Gemini text to client
                                if client_send:
                                    client_send(json.dumps({
                                        "type": "gemini_response",
                                        "text": llm_text
                                    }))

                                # Stream Murf audio
                                await send_to_murf(llm_text, client_send)

                            except Exception as e:
                                print("❌ process_turn error:", e, flush=True)
                                traceback.print_exc()

                        # schedule async processing
                        asyncio.create_task(process_turn())

        sender_task = asyncio.create_task(send_audio())
        await recv_transcripts()
        try:
            await sender_task
        except Exception:
            pass
