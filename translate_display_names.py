#!/usr/bin/env python
"""
Script para traducir los nombres de visualización de los tipos de lugares.
Este script mantiene los códigos internos en inglés pero proporciona nombres
en español para la visualización en la interfaz de usuario.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itinerario_backend.settings')
django.setup()

from chatbot.models import LugarGooglePlaces

def obtener_traducciones_tipos():
    """
    Retorna un diccionario con las traducciones de los códigos a nombres en español.
    """
    traducciones = {
        # Tipos principales
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
    
    return traducciones

def mostrar_tipos_con_traducciones():
    """
    Muestra los tipos actuales con sus traducciones en español.
    """
    traducciones = obtener_traducciones_tipos()
    
    print("=== Tipos de Lugares con Traducciones ===")
    print()
    
    # Obtener tipos principales únicos
    tipos_principales = LugarGooglePlaces.objects.values_list('tipo_principal', flat=True).distinct()
    print(f"Tipos principales encontrados ({len(tipos_principales)}):")
    print("-" * 60)
    for tipo in sorted(tipos_principales):
        count = LugarGooglePlaces.objects.filter(tipo_principal=tipo).count()
        traduccion = traducciones.get(tipo, tipo)
        print(f"  {tipo:25} → {traduccion:30} ({count} lugares)")
    
    print()
    
    # Obtener tipos adicionales únicos
    todos_tipos_adicionales = set()
    lugares_con_tipos_adicionales = LugarGooglePlaces.objects.exclude(tipos_adicionales=[])
    
    for lugar in lugares_con_tipos_adicionales:
        todos_tipos_adicionales.update(lugar.tipos_adicionales)
    
    print(f"Tipos adicionales encontrados ({len(todos_tipos_adicionales)}):")
    print("-" * 60)
    for tipo in sorted(todos_tipos_adicionales):
        count = LugarGooglePlaces.objects.filter(tipos_adicionales__contains=[tipo]).count()
        traduccion = traducciones.get(tipo, tipo)
        print(f"  {tipo:25} → {traduccion:30} ({count} lugares)")

def crear_funcion_traduccion():
    """
    Crea una función que puede ser usada en el código para traducir tipos.
    """
    traducciones = obtener_traducciones_tipos()
    
    codigo_funcion = '''
def traducir_tipo_lugar(codigo_tipo):
    """
    Traduce un código de tipo de lugar a su nombre en español.
    
    Args:
        codigo_tipo (str): Código del tipo de lugar (ej: 'hotel', 'restaurant')
    
    Returns:
        str: Nombre traducido en español o el código original si no se encuentra
    """
    traducciones = {
'''
    
    for codigo, traduccion in traducciones.items():
        codigo_funcion += f"        '{codigo}': '{traduccion}',\n"
    
    codigo_funcion += '''    }
    
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
'''
    
    return codigo_funcion

def main():
    """
    Función principal del script.
    """
    print("=== Script de Traducción de Nombres de Tipos ===")
    print()
    
    # Mostrar tipos con traducciones
    mostrar_tipos_con_traducciones()
    
    print("\n" + "="*60)
    print("\nCódigo de función para usar en tu aplicación:")
    print("-" * 60)
    print(crear_funcion_traduccion())
    
    print("\n" + "="*60)
    print("\nRecomendaciones:")
    print("1. Los códigos internos se mantienen en inglés para compatibilidad")
    print("2. Usa la función traducir_tipo_lugar() para mostrar nombres en español")
    print("3. Los códigos originales se preservan en la base de datos")
    print("4. Esto permite búsquedas más precisas y compatibilidad con APIs")

if __name__ == "__main__":
    main() 