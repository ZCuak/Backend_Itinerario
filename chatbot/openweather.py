# openweather.py
import os
import requests

API_KEY = os.getenv("OPENWEATHER_API_KEY")  # Esto lo pones en tu .env
BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"

def obtener_clima(lat, lon):
    params = {
        "lat": lat,
        "lon": lon,
        "lang": "sp",
        "exclude": "hourly,minutely,alerts",
        "appid": API_KEY
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None
