#!/usr/bin/env python
"""
Script para traducir los tipos de lugares existentes en la base de datos.
Este script actualiza los campos tipo_principal y tipos_adicionales para que usen
los códigos estandarizados definidos en el modelo LugarGooglePlaces.
"""

import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itinerario_backend.settings')
django.setup()

from chatbot.models import LugarGooglePlaces

def mapear_tipos_antiguos_a_nuevos():
    """
    Mapea los tipos antiguos a los nuevos códigos estandarizados.
    """
    mapeo_tipos = {
        # Mapeo de tipos antiguos a nuevos
        'restaurante': 'restaurant',
        'restaurantes': 'restaurant',
        'hotel': 'hotel',
        'hoteles': 'hotel',
        'cafetería': 'coffee_shop',
        'cafeteria': 'coffee_shop',
        'café': 'cafe',
        'cafe': 'cafe',
        'bar': 'bar',
        'bares': 'bar',
        'alojamiento': 'lodging',
        'acuario': 'aquarium',
        'playa': 'beach',
        'mercado': 'market',
        'parque': 'park',
        'museo': 'museum',
        'museos': 'museum',
        'iglesia': 'church',
        'monumento_historico': 'historical_landmark',
        'monumento histórico': 'historical_landmark',
        'atraccion_turistica': 'tourist_attraction',
        'atracción turística': 'tourist_attraction',
        'club_nocturno': 'night_club',
        'discoteca': 'night_club',
        'bar_y_parrilla': 'bar_and_grill',
        'tienda_de_hogar': 'home_goods_store',
        'galeria_de_arte': 'art_gallery',
        'galería de arte': 'art_gallery',
        'centro_comercial': 'shopping_mall',
        'tienda': 'store',
        'supermercado': 'supermarket',
        'tienda_de_comida': 'food_store',
        'tienda_de_descuentos': 'discount_store',
        'tienda_por_departamentos': 'department_store',
        'parque_acuatico': 'water_park',
        'parque acuático': 'water_park',
        'cine': 'movie_theater',
        'casino': 'casino',
        'parque_de_diversiones': 'amusement_park',
        'parque de diversiones': 'amusement_park',
        'centro_de_entretenimiento': 'amusement_center',
        'lugar_de_eventos': 'event_venue',
        'comida': 'food',
        'punto_de_interes': 'point_of_interest',
        'punto de interés': 'point_of_interest',
        'establecimiento': 'establishment',
        'panaderia': 'bakery',
        'panadería': 'bakery',
        'tienda_de_postres': 'dessert_shop',
        'confiteria': 'confectionery',
        'confitería': 'confectionery',
        'heladeria': 'ice_cream_shop',
        'heladería': 'ice_cream_shop',
        'restaurante_de_hamburguesas': 'hamburger_restaurant',
        'restaurante_americano': 'american_restaurant',
        'posada': 'inn',
        'caracteristica_natural': 'natural_feature',
        'característica natural': 'natural_feature',
        'lugar_de_culto': 'place_of_worship',
        'lugar_historico': 'historical_place',
        'lugar histórico': 'historical_place',
        'restaurante_de_brunch': 'brunch_restaurant',
        'pintor': 'painter',
        'servicio_de_mensajeria': 'courier_service',
        'servicio de mensajería': 'courier_service',
        'tienda_de_abarrotes': 'grocery_store',
        'mayorista': 'wholesaler',
        'tienda_de_ropa': 'clothing_store',
        'tienda_deportiva': 'sporting_goods_store',
        'tienda_de_muebles': 'furniture_store',
        'tienda_de_mejoras_para_el_hogar': 'home_improvement_store',
        
        # Tipos adicionales comunes que pueden estar en tipos_adicionales
        'restaurant': 'restaurant',
        'lodging': 'lodging',
        'food': 'food',
        'point_of_interest': 'point_of_interest',
        'establishment': 'establishment',
        'coffee_shop': 'coffee_shop',
        'chinese_restaurant': 'chinese_restaurant',
        'aquarium': 'aquarium',
        'beach': 'beach',
        'market': 'market',
        'park': 'park',
        'museum': 'museum',
        'church': 'church',
        'historical_landmark': 'historical_landmark',
        'tourist_attraction': 'tourist_attraction',
        'night_club': 'night_club',
        'bar_and_grill': 'bar_and_grill',
        'home_goods_store': 'home_goods_store',
        'art_gallery': 'art_gallery',
        'shopping_mall': 'shopping_mall',
        'store': 'store',
        'supermarket': 'supermarket',
        'food_store': 'food_store',
        'discount_store': 'discount_store',
        'department_store': 'department_store',
        'water_park': 'water_park',
        'movie_theater': 'movie_theater',
        'casino': 'casino',
        'amusement_park': 'amusement_park',
        'amusement_center': 'amusement_center',
        'event_venue': 'event_venue',
        'bakery': 'bakery',
        'cafe': 'cafe',
        'dessert_shop': 'dessert_shop',
        'confectionery': 'confectionery',
        'ice_cream_shop': 'ice_cream_shop',
        'hamburger_restaurant': 'hamburger_restaurant',
        'american_restaurant': 'american_restaurant',
        'inn': 'inn',
        'natural_feature': 'natural_feature',
        'place_of_worship': 'place_of_worship',
        'historical_place': 'historical_place',
        'cafeteria': 'cafeteria',
        'brunch_restaurant': 'brunch_restaurant',
        'painter': 'painter',
        'courier_service': 'courier_service',
        'grocery_store': 'grocery_store',
        'wholesaler': 'wholesaler',
        'clothing_store': 'clothing_store',
        'sporting_goods_store': 'sporting_goods_store',
        'furniture_store': 'furniture_store',
        'home_improvement_store': 'home_improvement_store',
    }
    
    return mapeo_tipos

def traducir_tipos_lugares():
    """
    Traduce los tipos de lugares existentes en la base de datos.
    """
    mapeo = mapear_tipos_antiguos_a_nuevos()
    lugares_actualizados = 0
    lugares_con_errores = 0
    
    print("Iniciando traducción de tipos de lugares...")
    print(f"Total de lugares en la base de datos: {LugarGooglePlaces.objects.count()}")
    
    # Obtener todos los lugares
    lugares = LugarGooglePlaces.objects.all()
    
    for lugar in lugares:
        try:
            cambios_realizados = False
            
            # Traducir tipo_principal
            tipo_principal_original = lugar.tipo_principal
            if tipo_principal_original in mapeo:
                nuevo_tipo_principal = mapeo[tipo_principal_original]
                if nuevo_tipo_principal != tipo_principal_original:
                    lugar.tipo_principal = nuevo_tipo_principal
                    cambios_realizados = True
                    print(f"  - Lugar '{lugar.nombre}': tipo_principal '{tipo_principal_original}' → '{nuevo_tipo_principal}'")
            
            # Traducir tipos_adicionales
            if lugar.tipos_adicionales:
                tipos_adicionales_originales = lugar.tipos_adicionales.copy()
                nuevos_tipos_adicionales = []
                
                for tipo in tipos_adicionales_originales:
                    if tipo in mapeo:
                        nuevo_tipo = mapeo[tipo]
                        nuevos_tipos_adicionales.append(nuevo_tipo)
                        if nuevo_tipo != tipo:
                            print(f"    - Tipo adicional '{tipo}' → '{nuevo_tipo}'")
                    else:
                        # Si no está en el mapeo, mantener el original
                        nuevos_tipos_adicionales.append(tipo)
                
                # Actualizar solo si hay cambios
                if nuevos_tipos_adicionales != tipos_adicionales_originales:
                    lugar.tipos_adicionales = nuevos_tipos_adicionales
                    cambios_realizados = True
            
            # Guardar solo si hubo cambios
            if cambios_realizados:
                lugar.save()
                lugares_actualizados += 1
            
        except Exception as e:
            lugares_con_errores += 1
            print(f"Error al procesar lugar '{lugar.nombre}' (ID: {lugar.id}): {str(e)}")
    
    print(f"\nResumen de la traducción:")
    print(f"  - Lugares actualizados: {lugares_actualizados}")
    print(f"  - Lugares con errores: {lugares_con_errores}")
    print(f"  - Total procesados: {lugares.count()}")
    
    return lugares_actualizados, lugares_con_errores

def verificar_tipos_actuales():
    """
    Verifica los tipos actuales en la base de datos para identificar
    qué tipos necesitan traducción.
    """
    print("Verificando tipos actuales en la base de datos...")
    
    # Obtener tipos principales únicos
    tipos_principales = LugarGooglePlaces.objects.values_list('tipo_principal', flat=True).distinct()
    print(f"\nTipos principales encontrados ({len(tipos_principales)}):")
    for tipo in sorted(tipos_principales):
        count = LugarGooglePlaces.objects.filter(tipo_principal=tipo).count()
        print(f"  - '{tipo}': {count} lugares")
    
    # Obtener tipos adicionales únicos
    todos_tipos_adicionales = set()
    lugares_con_tipos_adicionales = LugarGooglePlaces.objects.exclude(tipos_adicionales=[])
    
    for lugar in lugares_con_tipos_adicionales:
        todos_tipos_adicionales.update(lugar.tipos_adicionales)
    
    print(f"\nTipos adicionales encontrados ({len(todos_tipos_adicionales)}):")
    for tipo in sorted(todos_tipos_adicionales):
        count = LugarGooglePlaces.objects.filter(tipos_adicionales__contains=[tipo]).count()
        print(f"  - '{tipo}': {count} lugares")

def main():
    """
    Función principal del script.
    """
    print("=== Script de Traducción de Tipos de Lugares ===")
    print()
    
    # Primero verificar los tipos actuales
    verificar_tipos_actuales()
    
    print("\n" + "="*50)
    
    # Preguntar al usuario si quiere continuar
    respuesta = input("\n¿Desea proceder con la traducción? (s/n): ").lower().strip()
    
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        print("\nIniciando traducción...")
        lugares_actualizados, lugares_con_errores = traducir_tipos_lugares()
        
        if lugares_actualizados > 0:
            print(f"\n✅ Traducción completada exitosamente!")
            print(f"   {lugares_actualizados} lugares fueron actualizados.")
        else:
            print(f"\nℹ️  No se encontraron lugares que necesiten traducción.")
        
        if lugares_con_errores > 0:
            print(f"⚠️  {lugares_con_errores} lugares tuvieron errores durante el proceso.")
    else:
        print("\n❌ Traducción cancelada por el usuario.")

if __name__ == "__main__":
    main() 