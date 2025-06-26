"""
Utilidades para el sistema de chatbot.
Incluye funciones para traducción de tipos de lugares y otras utilidades.
"""

def traducir_tipo_lugar(codigo_tipo):
    """
    Traduce un código de tipo de lugar a su nombre en español.
    
    Args:
        codigo_tipo (str): Código del tipo de lugar (ej: 'hotel', 'restaurant')
    
    Returns:
        str: Nombre traducido en español o el código original si no se encuentra
    """
    traducciones = {
        'hotel': 'Hotel',
        'restaurant': 'Restaurante',
        'coffee_shop': 'Cafetería',
        'chinese_restaurant': 'Restaurante Chino',
        'bar': 'Bar',
        'lodging': 'Alojamiento',
        'aquarium': 'Acuario',
        'beach': 'Playa',
        'market': 'Mercado',
        'park': 'Parque',
        'museum': 'Museo',
        'church': 'Iglesia',
        'historical_landmark': 'Monumento Histórico',
        'tourist_attraction': 'Atracción Turística',
        'night_club': 'Club Nocturno',
        'bar_and_grill': 'Bar y Parrilla',
        'home_goods_store': 'Tienda de Hogar',
        'art_gallery': 'Galería de Arte',
        'shopping_mall': 'Centro Comercial',
        'store': 'Tienda',
        'supermarket': 'Supermercado',
        'food_store': 'Tienda de Comida',
        'discount_store': 'Tienda de Descuentos',
        'department_store': 'Tienda por Departamentos',
        'water_park': 'Parque Acuático',
        'movie_theater': 'Cine',
        'casino': 'Casino',
        'amusement_park': 'Parque de Diversiones',
        'amusement_center': 'Centro de Entretenimiento',
        'event_venue': 'Lugar de Eventos',
        'food': 'Comida',
        'point_of_interest': 'Punto de Interés',
        'establishment': 'Establecimiento',
        'bakery': 'Panadería',
        'cafe': 'Café',
        'dessert_shop': 'Tienda de Postres',
        'confectionery': 'Confitería',
        'ice_cream_shop': 'Heladería',
        'hamburger_restaurant': 'Restaurante de Hamburguesas',
        'american_restaurant': 'Restaurante Americano',
        'inn': 'Posada',
        'natural_feature': 'Característica Natural',
        'place_of_worship': 'Lugar de Culto',
        'historical_place': 'Lugar Histórico',
        'cafeteria': 'Cafetería',
        'brunch_restaurant': 'Restaurante de Brunch',
        'painter': 'Pintor',
        'courier_service': 'Servicio de Mensajería',
        'grocery_store': 'Tienda de Abarrotes',
        'wholesaler': 'Mayorista',
        'clothing_store': 'Tienda de Ropa',
        'sporting_goods_store': 'Tienda Deportiva',
        'furniture_store': 'Tienda de Muebles',
        'home_improvement_store': 'Tienda de Mejoras para el Hogar',
    }
    
    return traducciones.get(codigo_tipo, codigo_tipo)

def traducir_lista_tipos(lista_tipos):
    """
    Traduce una lista de códigos de tipos a sus nombres en español.
    
    Args:
        lista_tipos (list): Lista de códigos de tipos
    
    Returns:
        list: Lista de nombres traducidos en español
    """
    return [traducir_tipo_lugar(tipo) for tipo in lista_tipos]

def obtener_tipo_principal_traducido(lugar):
    """
    Obtiene el tipo principal de un lugar traducido a español.
    
    Args:
        lugar: Instancia de LugarGooglePlaces
    
    Returns:
        str: Nombre del tipo principal en español
    """
    return traducir_tipo_lugar(lugar.tipo_principal)

def obtener_tipos_adicionales_traducidos(lugar):
    """
    Obtiene los tipos adicionales de un lugar traducidos a español.
    
    Args:
        lugar: Instancia de LugarGooglePlaces
    
    Returns:
        list: Lista de nombres de tipos adicionales en español
    """
    return traducir_lista_tipos(lugar.tipos_adicionales)

def formatear_tipos_lugar(lugar):
    """
    Formatea todos los tipos de un lugar para mostrar en español.
    
    Args:
        lugar: Instancia de LugarGooglePlaces
    
    Returns:
        dict: Diccionario con tipos formateados
    """
    return {
        'tipo_principal': obtener_tipo_principal_traducido(lugar),
        'tipos_adicionales': obtener_tipos_adicionales_traducidos(lugar),
        'todos_los_tipos': [obtener_tipo_principal_traducido(lugar)] + obtener_tipos_adicionales_traducidos(lugar)
    } 