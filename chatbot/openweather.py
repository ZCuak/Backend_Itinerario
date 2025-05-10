# openweather.py
import os
import requests
from datetime import datetime

API_KEY = os.getenv("OPENWEATHER_API_KEY")  # Esto lo pones en tu .env
BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"

# Diccionario de iconos con sus descripciones
ICONOS_CLIMA = {
    "01d": "Soleado",
    "01n": "Noche despejada",
    "02d": "Parcialmente nublado",
    "02n": "Noche parcialmente nublada",
    "03d": "Nublado",
    "03n": "Nublado",
    "04d": "Muy nublado",
    "04n": "Muy nublado",
    "09d": "Lluvia ligera",
    "09n": "Lluvia ligera",
    "10d": "Lluvia",
    "10n": "Lluvia",
    "11d": "Tormenta eléctrica",
    "11n": "Tormenta eléctrica",
    "13d": "Nieve",
    "13n": "Nieve",
    "50d": "Niebla",
    "50n": "Niebla"
}

def kelvin_a_celsius(kelvin):
    return round(kelvin - 273.15, 1)

def formatear_clima_para_ia(datos_clima):
    if not datos_clima:
        return None
    
    # Procesar datos actuales
    current = datos_clima.get('current', {})
    weather_current = current.get('weather', [{}])[0]
    icono_codigo = weather_current.get('icon', '')
    
    clima_actual = {
        "temperatura": {
            "actual": kelvin_a_celsius(current.get('temp', 0)),
            "sensacion": kelvin_a_celsius(current.get('feels_like', 0))
        },
        "condiciones": {
            "descripcion": weather_current.get('description', ''),
            "icono": icono_codigo,
            "estado": ICONOS_CLIMA.get(icono_codigo, "Desconocido")
        },
        "humedad": current.get('humidity', 0),
        "viento": {
            "velocidad": current.get('wind_speed', 0),
            "direccion": current.get('wind_deg', 0)
        }
    }
    
    # Procesar pronóstico diario
    pronostico = []
    for dia in datos_clima.get('daily', [])[:5]:  # Solo los próximos 5 días
        weather_dia = dia.get('weather', [{}])[0]
        icono_codigo = weather_dia.get('icon', '')
        pronostico.append({
            "fecha": datetime.fromtimestamp(dia.get('dt', 0)).strftime('%Y-%m-%d'),
            "temperatura": {
                "maxima": kelvin_a_celsius(dia.get('temp', {}).get('max', 0)),
                "minima": kelvin_a_celsius(dia.get('temp', {}).get('min', 0))
            },
            "condiciones": {
                "descripcion": weather_dia.get('description', ''),
                "icono": icono_codigo,
                "estado": ICONOS_CLIMA.get(icono_codigo, "Desconocido")
            },
            "probabilidad_lluvia": round(dia.get('pop', 0) * 100, 1)
        })
    
    return {
        "clima_actual": clima_actual,
        "pronostico": pronostico
    }

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
        datos_originales = response.json()
        return formatear_clima_para_ia(datos_originales)
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None
