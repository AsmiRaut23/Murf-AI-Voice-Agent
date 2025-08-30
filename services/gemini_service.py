# import requests
# from os import getenv

# GEMINI_API_KEY = getenv("GEMINI_API_KEY", "").strip()
# MODEL_NAME = getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()

# def query_gemini(conversation):
#     url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"
#     contents = [{"role": turn["role"], "parts": [{"text": turn["content"]}]} for turn in conversation]
#     resp = requests.post(url, json={"contents": contents})
#     if resp.status_code == 429:
#         return "[Gemini quota exceeded. Please try again later.]"
#     resp.raise_for_status()
#     return resp.json()["candidates"][0]["content"]["parts"][0]["text"]



import re
import google.generativeai as genai

from config import settings
from services.weather_service import get_weather
from services.moon_service import get_moon_position
from services.horoscope_service import get_horoscope

# Global chat history kept the same as your original
chat_history = []


async def stream_llm_response(prompt_text: str) -> str:
    """
    EXACT logic from your original:
    - Append user to history (duplicate append also happens in STT pipeline — preserved)
    - Weather / Moon / Horoscope skills
    - Otherwise stream from Gemini 1.5 Flash
    - Keep pirate persona & short replies
    """
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
            match = re.search(r"(?:in|of)\s+([A-Za-z\s]+)", prompt_text, re.IGNORECASE)
            if match:
                city = match.group(1).strip()
                city = re.sub(r"\b(today|now|right now|please|tomorrow)\b", "", city, flags=re.IGNORECASE).strip()
                if city:
                    weather_info = get_weather(city)
                    pirate_weather = f"Arrr! 🌤 In {city}, it be {weather_info}, matey!"
                    chat_history.append({"role": "assistant", "text": pirate_weather})
                    return pirate_weather

            pirate_fail = "⚓ Arrr! Ye forgot to tell me the city for the weather, matey!"
            chat_history.append({"role": "assistant", "text": pirate_fail})
            return pirate_fail

        except Exception:
            pirate_fail = "⚓ Arrr, me compass be broken! Can't fetch the weather right now."
            chat_history.append({"role": "assistant", "text": pirate_fail})
            return pirate_fail
    # === End Weather Skill ===

    # === Moon Skill ===
    if "moon" in prompt_text.lower():
        try:
            pirate_moon = get_moon_position()
            chat_history.append({"role": "assistant", "text": pirate_moon})
            return pirate_moon
        except Exception:
            fail_msg = "⚓ Arrr, the moon map be broken!"
            chat_history.append({"role": "assistant", "text": fail_msg})
            return fail_msg

    # === Horoscope Skill ===
    if "horoscope" in prompt_text.lower() or "zodiac" in prompt_text.lower():
        try:
            signs = ["aries","taurus","gemini","cancer","leo","virgo",
                     "libra","scorpio","sagittarius","capricorn","aquarius","pisces"]
            chosen_sign = None
            for s in signs:
                if s in prompt_text.lower():
                    chosen_sign = s
                    break

            if chosen_sign:
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

    # === Normal Gemini flow ===
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
