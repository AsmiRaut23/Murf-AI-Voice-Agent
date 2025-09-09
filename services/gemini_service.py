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



# import re
# import google.generativeai as genai

# from config import settings
# from services.weather_service import get_weather
# from services.moon_service import get_moon_position
# from services.horoscope_service import get_horoscope

# # Global chat history kept the same as your original
# chat_history = []


# async def stream_llm_response(prompt_text: str) -> str:
#     """
#     EXACT logic from your original:
#     - Append user to history (duplicate append also happens in STT pipeline — preserved)
#     - Weather / Moon / Horoscope skills
#     - Otherwise stream from Gemini 1.5 Flash
#     - Keep pirate persona & short replies
#     """
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
#             match = re.search(r"(?:in|of)\s+([A-Za-z\s]+)", prompt_text, re.IGNORECASE)
#             if match:
#                 city = match.group(1).strip()
#                 city = re.sub(r"\b(today|now|right now|please|tomorrow)\b", "", city, flags=re.IGNORECASE).strip()
#                 if city:
#                     weather_info = get_weather(city)
#                     pirate_weather = f"Arrr! 🌤 In {city}, it be {weather_info}, matey!"
#                     chat_history.append({"role": "assistant", "text": pirate_weather})
#                     return pirate_weather

#             pirate_fail = "⚓ Arrr! Ye forgot to tell me the city for the weather, matey!"
#             chat_history.append({"role": "assistant", "text": pirate_fail})
#             return pirate_fail

#         except Exception:
#             pirate_fail = "⚓ Arrr, me compass be broken! Can't fetch the weather right now."
#             chat_history.append({"role": "assistant", "text": pirate_fail})
#             return pirate_fail
#     # === End Weather Skill ===

#     # === Moon Skill ===
#     if "moon" in prompt_text.lower():
#         try:
#             pirate_moon = get_moon_position()
#             chat_history.append({"role": "assistant", "text": pirate_moon})
#             return pirate_moon
#         except Exception:
#             fail_msg = "⚓ Arrr, the moon map be broken!"
#             chat_history.append({"role": "assistant", "text": fail_msg})
#             return fail_msg

#     # === Horoscope Skill ===
#     if "horoscope" in prompt_text.lower() or "zodiac" in prompt_text.lower():
#         try:
#             signs = ["aries","taurus","gemini","cancer","leo","virgo",
#                      "libra","scorpio","sagittarius","capricorn","aquarius","pisces"]
#             chosen_sign = None
#             for s in signs:
#                 if s in prompt_text.lower():
#                     chosen_sign = s
#                     break

#             if chosen_sign:
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

#     # === Normal Gemini flow ===
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



# # gemini_servicee.py
# import re
# import google.generativeai as genai

# from config import settings
# from services.weather_service import get_weather
# from services.moon_service import get_moon_position
# from services.horoscope_service import get_horoscope

# # Global chat history
# chat_history = []

# # --------------------------
# # Pirate Persona Wrapper
# # --------------------------
# def pirate_persona(text: str) -> str:
#     """
#     Wrap any text in pirate-style persona.
#     Ensures all Gemini outputs and skill outputs sound like the Captain pirate.
#     """
#     if not text or not text.strip():
#         return "Arrr! Silence be strange, matey!"
    
#     prefix = "Arrr! Ahoy, matey! "
#     suffix = " Yo-ho-ho! Keep sailin'!"
    
#     text = text.strip().replace("\n", " ")
#     return f"{prefix}{text}{suffix}"


# # def pirate_persona(text: str) -> str:
# #     if not text or not text.strip():
# #         return "Arrr! Silence be strange, matey!"
    
# #     text = text.strip().replace("\n", " ")
    
# #     # Simple word replacements for pirate flavor
# #     replacements = {
# #         " you ": " ye ",
# #         " my ": " me ",
# #         " is ": " be ",
# #         " are ": " be ",
# #         "friend": "matey",
# #         "hello": "Ahoy",
# #         "hi": "Ahoy",
# #         "yes": "Aye",
# #         "no": "Nay",
# #         "the": "th'",
# #         "ing": "in'",
# #     }
    
# #     for k, v in replacements.items():
# #         text = text.replace(k, v)
    
# #     # Wrap with pirate phrases
# #     return f"Arrr! {text} Yo-ho-ho! Keep sailin'!"


# # --------------------------
# # LLM Response (streaming)
# # --------------------------
# async def stream_llm_response(prompt_text: str) -> str:
#     """
#     Handles:
#     - Chat history
#     - Weather / Moon / Horoscope skills
#     - Gemini 1.5 Flash streaming
#     - Pirate persona enforced everywhere
#     """
#     global chat_history
#     chat_history.append({"role": "user", "text": prompt_text})

#     model = genai.GenerativeModel("gemini-1.5-flash")

#     AGENT_NAME = "Captain"
#     base_prompt = (
#         f"You are {AGENT_NAME}, a friendly pirate. "
#         f"- Always keep answers very short — never more than 4 sentences. "
#         f"Always speak in pirate slang, using words like: 'Ahoy', 'Arrr', 'Yo-ho-ho'."
#         f"\n\nDo NOT use these words: 'booty', 'shiver me timbers', 'savvy', 'Davy Jones', or confusing old pirate phrases."
#         f"\n\nPirate rules: Roll your 'R's, drop 'G's (say 'sailin'' not 'sailing'), use 'ye' instead of 'you'. "
#         f"- Keep it short, fun, playful.\n"
#         f"- If asked your name: 'Ahoy! I be {AGENT_NAME}, the jolliest pirate of the seas!'"
#     )

#     # --------------------------
#     # Weather Skill
#     # --------------------------
#     if "weather" in prompt_text.lower() or "whether" in prompt_text.lower():
#         try:
#             match = re.search(r"(?:in|of)\s+([A-Za-z\s]+)", prompt_text, re.IGNORECASE)
#             if match:
#                 city = match.group(1).strip()
#                 city = re.sub(r"\b(today|now|right now|please|tomorrow)\b", "", city, flags=re.IGNORECASE).strip()
#                 if city:
#                     weather_info = get_weather(city)
#                     pirate_weather = pirate_persona(f"In {city}, it be {weather_info}, matey!")
#                     chat_history.append({"role": "assistant", "text": pirate_weather})
#                     return pirate_weather

#             pirate_fail = pirate_persona("Ye forgot to tell me the city for the weather, matey!")
#             chat_history.append({"role": "assistant", "text": pirate_fail})
#             return pirate_fail
#         except Exception:
#             pirate_fail = pirate_persona("Me compass be broken! Can't fetch the weather right now.")
#             chat_history.append({"role": "assistant", "text": pirate_fail})
#             return pirate_fail

#     # --------------------------
#     # Moon Skill
#     # --------------------------
#     if "moon" in prompt_text.lower():
#         try:
#             pirate_moon = pirate_persona(get_moon_position())
#             chat_history.append({"role": "assistant", "text": pirate_moon})
#             return pirate_moon
#         except Exception:
#             fail_msg = pirate_persona("The moon map be broken!")
#             chat_history.append({"role": "assistant", "text": fail_msg})
#             return fail_msg

#     # --------------------------
#     # Horoscope Skill
#     # --------------------------
#     if "horoscope" in prompt_text.lower() or "zodiac" in prompt_text.lower():
#         try:
#             signs = [
#                 "aries","taurus","gemini","cancer","leo","virgo",
#                 "libra","scorpio","sagittarius","capricorn","aquarius","pisces"
#             ]
#             chosen_sign = next((s for s in signs if s in prompt_text.lower()), None)

#             if chosen_sign:
#                 pirate_horo = pirate_persona(get_horoscope(chosen_sign))
#                 chat_history.append({"role": "assistant", "text": pirate_horo})
#                 return pirate_horo
#             else:
#                 msg = pirate_persona("Tell me yer zodiac sign, matey (like Aries or Leo)!")
#                 chat_history.append({"role": "assistant", "text": msg})
#                 return msg
#         except Exception:
#             fail_msg = pirate_persona("The stars be cloudy! Can't fetch horoscope now.")
#             chat_history.append({"role": "assistant", "text": fail_msg})
#             return fail_msg

#     # --------------------------
#     # Normal Gemini flow
#     # --------------------------
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

#     # --------------------------
#     # Apply Pirate Persona
#     # --------------------------
#     pirate_text = pirate_persona(full_text)
#     chat_history.append({"role": "assistant", "text": pirate_text})
#     return pirate_text




import re
import google.generativeai as genai

from config import settings
from services.weather_service import get_weather
from services.moon_service import get_moon_position
from services.horoscope_service import get_horoscope

# Global chat history
chat_history = []

# --------------------------
# Pirate Persona Wrapper
# --------------------------
# --- paste into gemini_service.py, replacing the old pirate_persona ---

def pirate_persona(text: str) -> str:
    """
    Robust pirate transformer:
    - Uses regex with word boundaries and case-insensitive matching
    - Handles punctuation and common words
    - Ensures a clear pirate prefix + suffix
    """
    if not text or not str(text).strip():
        return "Arrr! Silence be strange, matey!"

    s = str(text).strip()
    # normalize whitespace
    s = re.sub(r'\s+', ' ', s)

    # operate on lowercase for consistent replacements
    low = s.lower()

    # ordered replacements (longer/phrases first to avoid partial matches)
    patterns = [
        (r"\byour\b", "yer"),
        (r"\byou\b", "ye"),
        (r"\bmy\b", "me"),
        (r"\bfriend\b", "matey"),
        (r"\bhello\b", "ahoy"),
        (r"\bhi\b", "ahoy"),
        (r"\bhey\b", "ahoy"),
        (r"\bthe\b", "th'"),
        (r"\bfor\b", "fer"),
        (r"\band\b", "'n"),
        (r"\bis\b", "be"),
        (r"\bare\b", "be"),
        (r"\byes\b", "aye"),
        (r"\bno\b", "nay"),
        # change trailing -ing -> in'
        (r"(?<=\w)ing\b", "in'"),
    ]

    for patt, repl in patterns:
        low = re.sub(patt, repl, low, flags=re.IGNORECASE)

    # Trim and ensure punctuation
    low = low.strip()
    # Capitalize first char for readability
    if low:
        low = low[0].upper() + low[1:]

    # Ensure pirate framing (no duplicates)
    if not low.lower().startswith("arrr"):
        low = "Arrr! " + low
    if not low.endswith("!"):
        low = low + "!"
    # keep a friendly pirate sign-off
    if "yo-ho-ho" not in low.lower():
        low = low + " Yo-ho-ho!"

    return low


# --------------------------
# LLM Response (streaming)
# --------------------------
# async def stream_llm_response(prompt_text: str) -> str:
#     """
#     Handles:
#     - Chat history
#     - Weather / Moon / Horoscope skills
#     - Gemini 1.5 Flash streaming
#     - Pirate persona enforced everywhere
#     """
#     global chat_history
#     chat_history.append({"role": "user", "text": prompt_text})

#     model = genai.GenerativeModel("gemini-1.5-flash")

#     pirate_chat_history = []
#     for turn in chat_history:
#         text = turn['text']
#         if turn['role'] == 'assistant':
#             text = pirate_persona(text)  # force pirate style
#         pirate_chat_history.append({"role": turn['role'], "text": text})


#     AGENT_NAME = "Captain"
#     base_prompt = (
#         f"You are {AGENT_NAME}, the jolliest pirate of the seven seas. "
#         f"EVERY word ye speak MUST be in pirate slang. "
#         f"Roll yer R's, drop 'g's (say 'sailin'' instead of 'sailing'), "
#         f"use 'ye' instead of 'you', 'me' instead of 'my', "
#         f"and replace normal words with pirate equivalents. "
#         f"Keep answers very short — never more than 4 sentences. "
#         f"Always be fun, playful, and jolly. "
#         f"NEVER speak normal English. "
#         f"If asked yer name: 'Ahoy! I be {AGENT_NAME}, the jolliest pirate of the seas!'"
#     )

#     # --------------------------
#     # Weather Skill
#     # --------------------------
#     if "weather" in prompt_text.lower() or "whether" in prompt_text.lower():
#         try:
#             match = re.search(r"(?:in|of)\s+([A-Za-z\s]+)", prompt_text, re.IGNORECASE)
#             if match:
#                 city = match.group(1).strip()
#                 city = re.sub(r"\b(today|now|right now|please|tomorrow)\b", "", city, flags=re.IGNORECASE).strip()
#                 if city:
#                     weather_info = get_weather(city)
#                     pirate_weather = pirate_persona(f"Ahoy! In {city}, it be {weather_info}, matey!")
#                     chat_history.append({"role": "assistant", "text": pirate_weather})
#                     # return pirate_persona(pirate_weather)
#                     return pirate_weather

#             pirate_fail = pirate_persona("Ye forgot to tell me the city for the weather, matey!")
#             chat_history.append({"role": "assistant", "text": pirate_fail})
#             return pirate_fail
#         except Exception:
#             pirate_fail = pirate_persona("Me compass be broken! Can't fetch the weather right now.")
#             chat_history.append({"role": "assistant", "text": pirate_fail})
#             return pirate_fail

#     # --------------------------
#     # Moon Skill
#     # --------------------------
#     if "moon" in prompt_text.lower():
#         try:
#             # pirate_moon = pirate_persona(get_moon_position())
#             # chat_history.append({"role": "assistant", "text": pirate_moon})
#             # return pirate_moon
#             moon_info = get_moon_position()
#             result_text = f"The moon be showin' itself as: {moon_info}, matey!"
#             pirate_moon = pirate_persona(result_text)
#             chat_history.append({"role": "assistant", "text": pirate_moon})
#             return pirate_moon

#         except Exception:
#             fail_msg = pirate_persona("The moon map be broken!")
#             chat_history.append({"role": "assistant", "text": fail_msg})
#             return fail_msg

#     # --------------------------
#     # Horoscope Skill
#     # --------------------------
#     if "horoscope" in prompt_text.lower() or "zodiac" in prompt_text.lower():
#         try:
#             signs = [
#                 "aries","taurus","gemini","cancer","leo","virgo",
#                 "libra","scorpio","sagittarius","capricorn","aquarius","pisces"
#             ]
#             chosen_sign = next((s for s in signs if s in prompt_text.lower()), None)

#             if chosen_sign:
#                 # pirate_horo = pirate_persona(get_horoscope(chosen_sign))
#                 # chat_history.append({"role": "assistant", "text": pirate_horo})
#                 # return pirate_horo
#                 horo_info = get_horoscope(chosen_sign)
#                 result_text = f"Fer yer sign {chosen_sign}, the stars be whisperin': {horo_info}"
#                 pirate_horo = pirate_persona(result_text)
#                 chat_history.append({"role": "assistant", "text": pirate_horo})
#                 return pirate_horo

#             else:
#                 msg = pirate_persona("Tell me yer zodiac sign, matey (like Aries or Leo)!")
#                 chat_history.append({"role": "assistant", "text": msg})
#                 return msg
#         except Exception:
#             fail_msg = pirate_persona("The stars be cloudy! Can't fetch horoscope now.")
#             chat_history.append({"role": "assistant", "text": fail_msg})
#             return fail_msg

#     # --------------------------
#     # Normal Gemini flow
#     # --------------------------
#     prompt = base_prompt
#     for turn in pirate_chat_history:
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

#     # Final pirate enforcement
#     pirate_text = pirate_persona(full_text)
#     chat_history.append({"role": "assistant", "text": pirate_text})
#     return pirate_text









# --- replace the existing stream_llm_response with this ---
async def stream_llm_response(prompt_text: str) -> str:
    """
    Centralized LLM flow:
    - Handles skills (weather, moon, horoscope) by producing a plain `result_text`
    - Runs normal Gemini streaming when needed
    - ALWAYS runs pirate_persona(result_text) before returning
    """
    global chat_history
    chat_history.append({"role": "user", "text": prompt_text})

    model = genai.GenerativeModel("gemini-1.5-flash")

    # build a pirate-aware chat history (assistants already pirate-encoded)
    pirate_chat_history = []
    for turn in chat_history:
        text = turn['text']
        if turn['role'] == 'assistant':
            text = pirate_persona(text)  # make sure history stays pirate
        pirate_chat_history.append({"role": turn['role'], "text": text})

    AGENT_NAME = "Captain"
    base_prompt = (
        f"You are {AGENT_NAME}, the jolliest pirate of the seven seas. "
        f"EVERY word ye speak MUST be in pirate slang. "
        f"Roll yer R's, drop 'g's (say 'sailin'' instead of 'sailing'), "
        f"use 'ye' instead of 'you', 'me' instead of 'my', "
        f"and replace normal words with pirate equivalents. "
        f"Keep answers very short — never more than 4 sentences. "
        f"Always be fun, playful, and jolly. "
        f"NEVER speak normal English. "
        f"If asked yer name: 'Ahoy! I be {AGENT_NAME}, the jolliest pirate of the seas!'"
    )

    result_text = None
    lower_prompt = prompt_text.lower()

    # WEATHER
    if "weather" in lower_prompt or "whether" in lower_prompt:
        try:
            match = re.search(r"(?:in|of)\s+([A-Za-z\s]+)", prompt_text, re.IGNORECASE)
            if match:
                city = match.group(1).strip()
                city = re.sub(r"\b(today|now|right now|please|tomorrow)\b", "", city, flags=re.IGNORECASE).strip()
                if city:
                    weather_info = get_weather(city)
                    result_text = f"Ahoy! In {city}, it be {weather_info}, matey!"
            if not result_text:
                result_text = "Ye forgot to tell me the city for the weather, matey!"
        except Exception:
            result_text = "Me compass be broken! Can't fetch the weather right now."

    # MOON
    elif "moon" in lower_prompt:
        try:
            moon_info = get_moon_position()
            result_text = f"The moon be showin' itself as: {moon_info}, matey!"
        except Exception:
            result_text = "The moon map be broken!"

    # HOROSCOPE
    elif "horoscope" in lower_prompt or "zodiac" in lower_prompt:
        try:
            signs = [
                "aries","taurus","gemini","cancer","leo","virgo",
                "libra","scorpio","sagittarius","capricorn","aquarius","pisces"
            ]
            chosen_sign = next((s for s in signs if s in lower_prompt), None)
            if chosen_sign:
                horo_info = get_horoscope(chosen_sign)
                result_text = f"Fer yer sign {chosen_sign}, the stars be whisperin': {horo_info}"
            else:
                result_text = "Tell me yer zodiac sign, matey (like Aries or Leo)!"
        except Exception:
            result_text = "The stars be cloudy! Can't fetch horoscope now."

    # NORMAL GEMINI STREAMING
    else:
        prompt = base_prompt
        for turn in pirate_chat_history:
            role = "User" if turn["role"] == "user" else "Assistant"
            prompt += f"{role}: {turn['text']}\n"
        prompt += "Assistant:"

        print("\n🤖 Gemini Response (streaming):", flush=True)
        full_text = ""
        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            if getattr(chunk, "text", None):
                print(chunk.text, end="", flush=True)
                full_text += chunk.text
        print("\n✅ End of Gemini Response\n", flush=True)

        result_text = full_text or "Arrr! I be speechless, matey!"

    # FINAL: enforce pirate persona once, append to history and return
    pirate_text = pirate_persona(result_text)
    chat_history.append({"role": "assistant", "text": pirate_text})

    # Helpful debug logs (remove or lower verbosity in production)
    print("🧭 [raw_result]:", repr(result_text), flush=True)
    print("🏴‍☠️ [pirate_text]:", repr(pirate_text), flush=True)

    return pirate_text
