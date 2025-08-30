import os
import json
from dataclasses import dataclass
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()


@dataclass
class Settings:
    # Files
    CONFIG_FILE: str = "config.json"

    # AssemblyAI
    ASSEMBLYAI_KEY: str = os.getenv("ASSEMBLYAI_API_KEY", "").strip()
    ASSEMBLYAI_URL: str = "wss://streaming.assemblyai.com/v3/ws"

    # Gemini
    GEMINI_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()

    # Murf
    MURF_KEY: str = (os.getenv("MURF_API_KEY") or "").strip()
    MURF_URL: str = "wss://api.murf.ai/v1/speech/stream-input"

    # Weather
    OPENWEATHER_KEY: str = os.getenv("OPENWEATHER_API_KEY", "").strip()

    # IP Geolocation (for Moon skill)
    IPGEO_KEY: str = os.getenv("IPGEO_KEY", "").strip()

    # Horoscope (API Ninjas)
    API_NINJAS_KEY: str = os.getenv("API_NINJAS_KEY", "").strip()


settings = Settings()


# ---------------------------
# Config file I/O
# ---------------------------
def load_config_file() -> dict:
    try:
        with open(settings.CONFIG_FILE, "r") as f:
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


def save_config_file(config: dict) -> None:
    with open(settings.CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)


# ---------------------------
# Apply overrides at runtime
# ---------------------------
def apply_runtime_overrides(config: dict) -> None:
    """
    Prefer user-saved keys (config.json) over .env and reconfigure genai.
    Mirrors your original logic exactly.
    """
    try:
        if isinstance(config.get("GEMINI_KEY"), str) and config["GEMINI_KEY"].strip():
            settings.GEMINI_KEY = config["GEMINI_KEY"].strip()
            try:
                genai.configure(api_key=settings.GEMINI_KEY)
                print("🔑 GEMINI_KEY applied", flush=True)
            except Exception as e:
                print("⚠️ genai.configure failed with user key:", e, flush=True)

        if isinstance(config.get("MURF_KEY"), str) and config["MURF_KEY"].strip():
            settings.MURF_KEY = config["MURF_KEY"].strip()

        if isinstance(config.get("ASSEMBLY_KEY"), str) and config["ASSEMBLY_KEY"].strip():
            settings.ASSEMBLYAI_KEY = config["ASSEMBLY_KEY"].strip()

        if isinstance(config.get("WEATHER_KEY"), str) and config["WEATHER_KEY"].strip():
            settings.OPENWEATHER_KEY = config["WEATHER_KEY"].strip()

        if isinstance(config.get("MOON_KEY"), str) and config["MOON_KEY"].strip():
            settings.IPGEO_KEY = config["MOON_KEY"].strip()

        if isinstance(config.get("HOROSCOPE_KEY"), str) and config["HOROSCOPE_KEY"].strip():
            settings.API_NINJAS_KEY = config["HOROSCOPE_KEY"].strip()
    except Exception as e:
        print("⚠️ Error applying config overrides:", e, flush=True)


# Initial configure for Gemini if key is present
if settings.GEMINI_KEY:
    try:
        genai.configure(api_key=settings.GEMINI_KEY)
    except Exception as e:
        print("⚠️ genai.configure failed on startup:", e, flush=True)


# Also apply overrides from config.json on startup
apply_runtime_overrides(load_config_file())
