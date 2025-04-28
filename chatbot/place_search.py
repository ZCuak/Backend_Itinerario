# place_search.py
import os
import requests

API_KEY = os.getenv("FOURSQUARE_API_KEY")
BASE_URL = "https://api.foursquare.com/v3/places/search"

HEADERS = {
    "Accept": "application/json",
    "Authorization": API_KEY
}

def buscar_lugares_foursquare(lugar, radius=3000, limit=20):
    params = {
        "near": lugar,
        "categories": "13065,19014",
        "radius": radius,
        "limit": limit,
        "sort": "DISTANCE"
    }

    try:
        response = requests.get(BASE_URL, headers=HEADERS, params=params)
        
        print(f"Status code: {response.status_code}")
        print(f"Response text: {response.text}")

        response.raise_for_status()
        lugares = response.json()

        resultados = []
        for sitio in lugares.get("results", []):
            resultados.append({
                "nombre": sitio.get("name"),
                "direccion": sitio.get("location", {}).get("formatted_address", ""),
                "categorias": [c["name"] for c in sitio.get("categories", [])]
            })

        return resultados

    except requests.exceptions.RequestException as e:
        print(f"Error en Foursquare API: {e}")
        return None
