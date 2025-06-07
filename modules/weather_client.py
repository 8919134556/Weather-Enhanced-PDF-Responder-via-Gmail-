import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

OWM_API_KEY = os.getenv("OWM_API_KEY")
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "New Delhi")
OWM_ENDPOINT = "http://api.openweathermap.org/data/2.5/weather"

def fetch_current_weather(city_name=None):
    """
    Calls OpenWeatherMap API for city_name (or DEFAULT_CITY if None).
    Returns a dict with keys: city, description, temperature (°C), humidity (%), wind_speed (m/s), timestamp (ISO).
    """
    if city_name is None:
        city_name = DEFAULT_CITY

    params = {
        "q": city_name,
        "appid": OWM_API_KEY,
        "units": "metric"
    }
    resp = requests.get(OWM_ENDPOINT, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    weather_info = {
        "city": data.get("name", city_name),
        "description": data["weather"][0]["description"].capitalize(),
        "temperature_celsius": data["main"]["temp"],
        "humidity_percent": data["main"]["humidity"],
        "wind_speed_m_s": data["wind"]["speed"],
        "timestamp": datetime.utcfromtimestamp(data["dt"]).isoformat() + "Z"
    }
    return weather_info
