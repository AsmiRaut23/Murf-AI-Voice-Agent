import requests
from config import settings


def get_weather(city: str) -> str:
    """
    Fetch weather for a given city using OpenWeather API.
    Same behavior & text as your original function.
    """
    try:
        url = (
            f"http://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={settings.OPENWEATHER_KEY}&units=metric"
        )
        resp = requests.get(url, timeout=8)
        data = resp.json()
        if data.get("cod") != 200:
            return f"Arrr! I couldn't find weather for {city}. ⚠"
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        return f"{temp}°C with {desc}"
    except Exception as e:
        return f"⚠ Weather API error: {str(e)}"
