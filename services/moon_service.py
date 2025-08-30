import requests
from config import settings
from utils.helpers import azimuth_to_direction


def get_user_location():
    """
    Uses IPGeolocation IP API to detect user's city + lat/lon automatically.
    """
    try:
        if not settings.IPGEO_KEY:
            return None, None, "Unknown city", "Unknown country"
        url = f"https://api.ipgeolocation.io/ipgeo?apiKey={settings.IPGEO_KEY}"
        res = requests.get(url, timeout=6).json()
        lat = res.get("latitude")
        lon = res.get("longitude")
        city = res.get("city", "Unknown city")
        country = res.get("country_name", "Unknown country")

        lat = float(lat) if lat is not None else None
        lon = float(lon) if lon is not None else None
        return lat, lon, city, country
    except Exception as e:
        print("⚠️ IP location error:", e, flush=True)
        return None, None, "Unknown city", "Unknown country"


def get_moon_position():
    """
    Fetch moon data from IPGeolocation Astronomy API for the user's current IP-based location.
    Returns pirate-styled, short, friendly string including altitude, azimuth, direction,
    rise/set times, phase, and distance. (Same text/logic as your original.)
    """
    try:
        # Step 1: Detect user’s location
        lat, lon, city, country = get_user_location()

        if not settings.IPGEO_KEY:
            return "⚓ Arrr! Me spyglass be empty — set IPGEO_KEY in yer .env, matey!"
        if lat is None or lon is None:
            return "⚓ Arrr! I can't spy yer location. Try again later, matey!"

        # Step 2: Fetch Moon position
        url = f"https://api.ipgeolocation.io/astronomy?apiKey={settings.IPGEO_KEY}&lat={lat}&long={lon}"
        res = requests.get(url, timeout=6).json()

        altitude = res.get("moon_altitude")
        azimuth = res.get("moon_azimuth")
        distance = res.get("moon_distance")
        phase = res.get("moon_phase")
        rise = res.get("moonrise")
        set_time = res.get("moonset")

        direction = azimuth_to_direction(azimuth)

        return (
            f"Arrr! 🌙 From your location, the moon be {altitude}° high, "
            f"azimuth {azimuth}° toward {direction}. "
            f"It rises at {rise} and sets at {set_time}. "
            f"Phase be {phase}, 'n distance {distance} km."
        )
    except Exception as e:
        print("⚠️ Moon API error:", e, flush=True)
        return "⚓ Arrr, me star charts be tangled! Can't fetch the moon right now."
