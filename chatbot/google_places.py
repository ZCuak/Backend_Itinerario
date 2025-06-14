import googlemaps
from django.conf import settings
import json
import requests

def buscar_lugares_cercanos(latitud, longitud, radio=15000, tipos=None):
    """
    Busca lugares cercanos usando la API de Google Places
    
    Args:
        latitud (float): Latitud del punto central
        longitud (float): Longitud del punto central
        radio (int): Radio de búsqueda en metros (por defecto 15000)
        tipos (list): Lista de tipos de lugares a buscar
    
    Returns:
        list: Lista de lugares encontrados
    """
    try:
        # Si no se especifican tipos, usar los predeterminados
        if tipos is None:
            tipos = ['restaurant', 'bar', 'night_club', 'amusement_park', 'aquarium', 
                    'art_gallery', 'bowling_alley', 'casino', 'movie_theater', 
                    'museum', 'park', 'stadium', 'tourist_attraction', 'zoo']

        # Preparar la solicitud a la nueva API
        url = "https://places.googleapis.com/v1/places:searchNearby"
        
        # Definir los campos que queremos obtener
        field_mask = [
            "places.displayName",
            "places.formattedAddress",
            "places.types",
            "places.rating",
            "places.userRatingCount",
            "places.primaryType",
            "places.websiteUri",
            "places.formattedPhoneNumber",
            "places.priceLevel",
            "places.currentOpeningHours",
            "places.photos"
        ]

        # Preparar el cuerpo de la solicitud
        payload = {
            "includedTypes": tipos,
            "maxResultCount": 20,  # Máximo permitido por la API
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": latitud,
                        "longitude": longitud
                    },
                    "radius": float(radio)
                }
            }
        }

        # Realizar la solicitud
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': settings.GOOGLE_MAPS_API_KEY,
            'X-Goog-FieldMask': ','.join(field_mask)
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        lugares_encontrados = []
        
        if 'places' in data:
            for lugar in data['places']:
                # Procesar horarios
                horarios = []
                if 'currentOpeningHours' in lugar:
                    for dia in lugar['currentOpeningHours'].get('weekdayDescriptions', []):
                        horarios.append(dia)
                
                # Procesar nivel de precios
                nivel_precios = lugar.get('priceLevel', 0)
                descripcion_precios = {
                    0: "No especificado",
                    1: "Económico",
                    2: "Moderado",
                    3: "Costoso",
                    4: "Muy costoso"
                }
                
                # Procesar fotos
                fotos = []
                if 'photos' in lugar:
                    for foto in lugar['photos'][:3]:  # Solo las primeras 3 fotos
                        fotos.append(f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={foto['name']}&key={settings.GOOGLE_MAPS_API_KEY}")
                
                lugar_info = {
                    'nombre': lugar['displayName']['text'],
                    'direccion': lugar.get('formattedAddress', ''),
                    'tipo': lugar.get('primaryType', tipos[0]),
                    'tipos_adicionales': lugar.get('types', []),
                    'rating': lugar.get('rating', 0),
                    'total_ratings': lugar.get('userRatingCount', 0),
                    'place_id': lugar['name'].split('/')[-1],  # Extraer el ID del nombre
                    'latitud': latitud,  # La API no devuelve las coordenadas en la respuesta básica
                    'longitud': longitud,  # La API no devuelve las coordenadas en la respuesta básica
                    'abierto_ahora': lugar.get('currentOpeningHours', {}).get('openNow', False),
                    'horarios': horarios,
                    'nivel_precios': {
                        'nivel': nivel_precios,
                        'descripcion': descripcion_precios.get(nivel_precios, "No especificado")
                    },
                    'fotos': fotos,
                    'website': lugar.get('websiteUri', ''),
                    'telefono': lugar.get('formattedPhoneNumber', '')
                }
                
                lugares_encontrados.append(lugar_info)
        
        return lugares_encontrados
    
    except Exception as e:
        print(f"Error al buscar lugares cercanos: {str(e)}")
        return [] 