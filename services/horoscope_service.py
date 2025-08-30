import traceback
import requests
from config import settings


def get_horoscope(sign: str) -> str:
    """
    Fetch daily horoscope for a given zodiac sign using API Ninjas.
    Mirrors your original behavior (debug prints + pirate phrasing).
    """
    if not settings.API_NINJAS_KEY:
        print("⚠️ API_NINJAS_KEY not set in .env", flush=True)
        return "⚠ Arrr! The astrology key be missin' in yer .env."

    if not sign:
        return "⚓ Arrr! Tell me yer zodiac sign, matey (like Aries or Leo)!"

    try:
        url = f"https://api.api-ninjas.com/v1/horoscope?zodiac={sign.lower()}"
        headers = {"X-Api-Key": settings.API_NINJAS_KEY}

        resp = requests.get(url, headers=headers, timeout=10)
        print(f"🛰 Horoscope API status: {resp.status_code}", flush=True)
        print(f"🛰 Horoscope API body: {resp.text}", flush=True)

        if resp.status_code == 200:
            try:
                data = resp.json()
            except Exception:
                data = None

            horoscope_text = None
            if isinstance(data, dict):
                horoscope_text = data.get("horoscope") or data.get("text") or None

            if not horoscope_text:
                horoscope_text = resp.text.strip()

            return f"Arrr! 🔮 Fer {sign.capitalize()}, today, it be sayin': {horoscope_text}"
        else:
            return f"⚠ Arrr! I couldn't fetch yer horoscope (API {resp.status_code})."
    except Exception as e:
        print("❌ Horoscope error:", e, flush=True)
        traceback.print_exc()
        return f"⚠ Arrr! Somethin' went wrong fetchin' the stars: {str(e)}"
