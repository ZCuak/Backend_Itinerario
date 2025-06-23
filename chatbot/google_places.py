import googlemaps
from django.conf import settings
import json
import requests
from .models import LugarGooglePlaces, NivelPrecio

def inicializar_niveles_precio():
    """
    Inicializa los niveles de precios en la base de datos si no existen.
    """
    niveles_precio = {
        0: "Sin especificar",
        1: "Económico: Lugares con precios bajos, como puestos de comida callejera o tiendas pequeñas",
        2: "Moderado: Lugares con precios estándar, como restaurantes de gama media o tiendas minoristas",
        3: "Caro: Lugares con precios elevados, como restaurantes de alta cocina o tiendas de diseñador",
        4: "Muy caro: Lugares con precios muy altos, como hoteles de lujo o restaurantes de estrellas Michelin"
    }
    
    for nivel, descripcion in niveles_precio.items():
        NivelPrecio.objects.get_or_create(
            nivel=nivel,
            defaults={
                'descripcion': descripcion,
                'is_active': True
            }
        )

def obtener_nivel_precio(nivel):
    """
    Obtiene o crea un nivel de precio.
    
    Args:
        nivel (int): Nivel de precio (0-4)
    
    Returns:
        NivelPrecio: Objeto del nivel de precio
    """
    try:
        return NivelPrecio.objects.get(nivel=nivel)
    except NivelPrecio.DoesNotExist:
        # Si no existe, inicializar todos los niveles
        inicializar_niveles_precio()
        return NivelPrecio.objects.get(nivel=nivel)

def guardar_lugar_en_bd(lugar_info, categoria):
    """
    Guarda un lugar en la base de datos si no existe.
    
    Args:
        lugar_info (dict): Información del lugar de la API
        categoria (str): Categoría del lugar
    
    Returns:
        tuple: (LugarGooglePlaces, bool) - (objeto, si fue creado)
    """
    try:
        # Verificar si el lugar ya existe
        lugar_existente = LugarGooglePlaces.objects.filter(
            nombre=lugar_info['nombre'],
            direccion=lugar_info['direccion'],
            latitud=lugar_info['latitud'],
            longitud=lugar_info['longitud']
        ).first()
        
        if lugar_existente:
            # Actualizar información si es necesario
            lugar_existente.rating = lugar_info['rating']
            lugar_existente.total_ratings = lugar_info['total_ratings']
            lugar_existente.horarios = lugar_info['horarios']
            lugar_existente.nivel_precios = obtener_nivel_precio(lugar_info['nivel_precios']['nivel'])
            lugar_existente.website = lugar_info['website']
            lugar_existente.telefono = lugar_info['telefono']
            lugar_existente.descripcion = lugar_info['descripcion']
            lugar_existente.resumen_ia = lugar_info['resumen_ia']
            lugar_existente.place_id = lugar_info['place_id']
            lugar_existente.estado_negocio = lugar_info['servicios']['estado_negocio']
            lugar_existente.save()
            return lugar_existente, False  # False = no fue creado, solo actualizado
        
        # Crear nuevo lugar
        nuevo_lugar = LugarGooglePlaces.objects.create(
            nombre=lugar_info['nombre'],
            direccion=lugar_info['direccion'],
            tipo_principal=lugar_info['tipo'],
            tipos_adicionales=lugar_info['tipos_adicionales'],
            categoria=categoria,
            place_id=lugar_info['place_id'],
            latitud=lugar_info['latitud'],
            longitud=lugar_info['longitud'],
            rating=lugar_info['rating'],
            total_ratings=lugar_info['total_ratings'],
            website=lugar_info['website'],
            telefono=lugar_info['telefono'],
            nivel_precios=obtener_nivel_precio(lugar_info['nivel_precios']['nivel']),
            horarios=lugar_info['horarios'],
            descripcion=lugar_info['descripcion'],
            resumen_ia=lugar_info['resumen_ia'],
            estado_negocio=lugar_info['servicios']['estado_negocio']
        )
        
        return nuevo_lugar, True  # True = fue creado
        
    except Exception as e:
        print(f"Error al guardar lugar {lugar_info['nombre']}: {str(e)}")
        return None, False

def buscar_lugares_cercanos(latitud, longitud, radio=1000, tipos=None):
    """
    Busca lugares cercanos usando la API de Google Places.
    
    Args:
        latitud (float): Latitud del punto de referencia
        longitud (float): Longitud del punto de referencia
        radio (int): Radio de búsqueda en metros (por defecto 1000m)
        tipos (list): Lista de tipos de lugares a buscar (opcional)
    
    Returns:
        dict: Diccionario con los lugares encontrados organizados por categoría
    """
    # Definir las categorías de lugares
    categorias = {
        'restaurantes': [
            "restaurant",
            "cafe",
            "bar",
            "bakery",
            "meal_delivery",
            "meal_takeaway"
        ],
        'hoteles': [
            "hotel",
            "lodging",
            "guest_house",
            "hostel",
            "bed_and_breakfast",
            "campground",
            "rv_park"
        ]
        ,
        'lugares_acuaticos': [
            "beach",
            "aquarium",
        ],
        
        'lugares_turisticos': [
            "tourist_attraction"
        ],
        'discotecas': [
            "night_club",
            "bar"
        ],
        'museos': [
            "museum",
            "art_gallery"
        ],
        'lugares_campestres': [
            "park",
            "campground",
            "natural_feature"
        ],
        'centros_comerciales': [
            "shopping_mall",
            "department_store",
            "store",
            "supermarket",
            "clothing_store",
            "jewelry_store",
            "convenience_store",
            "electronics_store",
        ],
        'lugares_de_entretenimiento': [
            "movie_theater",
            "amusement_park",
            "bowling_alley",
            "casino",
        ]
    }

    # Si se proporcionan tipos específicos, usar solo esos
    if tipos:
        categorias = {'personalizados': tipos}

    # Definir los campos que queremos obtener (solo los disponibles en Nearby Search)
    field_mask = [
        # Campos básicos disponibles
        "places.id",
        "places.displayName",
        "places.formattedAddress", 
        "places.types",
        "places.rating",
        "places.userRatingCount",
        "places.primaryType",
        "places.websiteUri",
        "places.nationalPhoneNumber",
        "places.priceLevel",
        "places.currentOpeningHours",
        "places.location",
        "places.editorialSummary",
        "places.businessStatus"
        
        # Campo de resumen generado por IA (requiere plan Enterprise + Atmosphere)
        # "places.generativeSummary"
    ]

    # URL de la API
    url = "https://places.googleapis.com/v1/places:searchNearby"
    
    # Diccionario para almacenar todos los resultados
    resultados_totales = {}
    
    # Realizar una búsqueda por cada categoría
    for categoria, tipos_categoria in categorias.items():
        try:
            # Preparar el cuerpo de la solicitud
            payload = {
                "includedTypes": tipos_categoria,
                "maxResultCount": 20,
                "locationRestriction": {
                    "circle": {
                        "center": {
                            "latitude": latitud,
                            "longitude": longitud
                        },
                        "radius": float(radio)
                    }
                },
                "languageCode": "es"
            }

            # Realizar la solicitud
            headers = {
                'Content-Type': 'application/json',
                'X-Goog-Api-Key': settings.GOOGLE_MAPS_API_KEY,
                'X-Goog-FieldMask': ','.join(field_mask)
            }

            print(f"\nBuscando lugares de categoría: {categoria}")
            print("Request URL:", url)
            print("Request Headers:", headers)
            print("Request Payload:", json.dumps(payload, indent=2))

            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code != 200:
                print(f"Error en categoría {categoria}:")
                print("Error Response Status:", response.status_code)
                print("Error Response Headers:", response.headers)
                print("Error Response Body:", response.text)
                resultados_totales[categoria] = []
                continue
                
            data = response.json()
            print(f"Success Response para {categoria}:", json.dumps(data, indent=2))

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
                    # Unificar el formato del nivel de precios
                    if isinstance(nivel_precios, str):
                        # Si es string, convertir a número
                        if 'MODERATE' in nivel_precios:
                            nivel_precios = 2
                        elif 'EXPENSIVE' in nivel_precios:
                            nivel_precios = 3
                        elif 'VERY_EXPENSIVE' in nivel_precios:
                            nivel_precios = 4
                        elif 'INEXPENSIVE' in nivel_precios:
                            nivel_precios = 1
                        else:
                            nivel_precios = 0
                    
                    # Descripciones de los niveles de precios
                    descripcion_precios = {
                        0: "Sin especificar",
                        1: "Económico: Lugares con precios bajos, como puestos de comida callejera o tiendas pequeñas",
                        2: "Moderado: Lugares con precios estándar, como restaurantes de gama media o tiendas minoristas",
                        3: "Caro: Lugares con precios elevados, como restaurantes de alta cocina o tiendas de diseñador",
                        4: "Muy caro: Lugares con precios muy altos, como hoteles de lujo o restaurantes de estrellas Michelin"
                    }
                    
                    # Procesar resumen generado por IA
                    resumen_ia = ""
                    # if 'generativeSummary' in lugar:
                    #     generative_summary = lugar['generativeSummary']
                    #     overview = generative_summary.get('overview', {}).get('text', '')
                    #     disclosure = generative_summary.get('disclosureText', {}).get('text', '')
                    #     resumen_ia = f"{overview} {disclosure}".strip()
                    
                    lugar_info = {
                        'nombre': lugar['displayName']['text'],
                        'direccion': lugar.get('formattedAddress', ''),
                        'tipo': lugar.get('primaryType', tipos_categoria[0]),
                        'tipos_adicionales': lugar.get('types', []),
                        'rating': lugar.get('rating', 0),
                        'total_ratings': lugar.get('userRatingCount', 0),
                        'place_id': lugar.get('id', ''),
                        'latitud': lugar.get('location', {}).get('latitude', latitud),
                        'longitud': lugar.get('location', {}).get('longitude', longitud),
                        'horarios': horarios,
                        'nivel_precios': {
                            'nivel': nivel_precios,
                            'descripcion': descripcion_precios.get(nivel_precios, "Sin especificar")
                        },
                        'website': lugar.get('websiteUri', ''),
                        'telefono': lugar.get('nationalPhoneNumber', ''),
                        'descripcion': lugar.get('editorialSummary', {}).get('text', 'No hay descripción disponible'),
                        'resumen_ia': resumen_ia,
                        
                        # Campo de servicios básicos
                        'servicios': {
                            'estado_negocio': lugar.get('businessStatus', 'OPERATIONAL')
                        }
                    }
                    
                    lugares_encontrados.append(lugar_info)
            
            # Guardar lugares en la base de datos
            lugares_guardados = 0
            lugares_actualizados = 0
            
            for lugar_info in lugares_encontrados:
                lugar_bd, fue_creado = guardar_lugar_en_bd(lugar_info, categoria)
                if lugar_bd:
                    if fue_creado:
                        lugares_guardados += 1
                    else:
                        lugares_actualizados += 1
            
            resultados_totales[categoria] = lugares_encontrados
            print(f"Encontrados {len(lugares_encontrados)} lugares en la categoría {categoria}")
            print(f"  - Nuevos lugares guardados: {lugares_guardados}")
            print(f"  - Lugares actualizados: {lugares_actualizados}")
        
        except Exception as e:
            print(f"Error al buscar lugares de categoría {categoria}: {str(e)}")
            resultados_totales[categoria] = []
            continue

    return {
        'total_categorias': len(resultados_totales),
        'total_lugares': sum(len(lugares) for lugares in resultados_totales.values()),
        'lugares_por_categoria': resultados_totales
    }