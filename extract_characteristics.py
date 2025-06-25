#!/usr/bin/env python3
"""
Script para extraer características de lugares usando DeepSeek
"""

import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itinerario_backend.settings')
django.setup()

from chatbot.models import LugarGooglePlaces
from chatbot.deepseek.deepseek import extraer_caracteristicas_lugar, extraer_caracteristicas_lotes

def extract_characteristics_for_places():
    """Extraer características para todos los lugares que no las tengan"""
    
    print("🔍 Iniciando extracción de características para lugares...")
    
    try:
        # Obtener lugares que no tienen características extraídas válidas
        # Buscar lugares con caracteristicas_extraidas vacías, null, o sin estructura completa
        lugares_sin_caracteristicas = LugarGooglePlaces.objects.filter(
            is_active=True
        ).exclude(
            resumen_ia__isnull=True
        ).exclude(
            resumen_ia__exact=''
        ).filter(
            # Lugares con caracteristicas_extraidas null
            caracteristicas_extraidas__isnull=True
        ) | LugarGooglePlaces.objects.filter(
            is_active=True
        ).exclude(
            resumen_ia__isnull=True
        ).exclude(
            resumen_ia__exact=''
        ).filter(
            # Lugares con caracteristicas_extraidas vacías {}
            caracteristicas_extraidas={}
        ) | LugarGooglePlaces.objects.filter(
            is_active=True
        ).exclude(
            resumen_ia__isnull=True
        ).exclude(
            resumen_ia__exact=''
        ).filter(
            # Lugares con caracteristicas_extraidas que no tienen amenidades
            caracteristicas_extraidas__amenidades__isnull=True
        ) | LugarGooglePlaces.objects.filter(
            is_active=True
        ).exclude(
            resumen_ia__isnull=True
        ).exclude(
            resumen_ia__exact=''
        ).filter(
            # Lugares con caracteristicas_extraidas que tienen amenidades vacías
            caracteristicas_extraidas__amenidades=[]
        )
        
        print(f"📊 Encontrados {lugares_sin_caracteristicas.count()} lugares sin características extraídas válidas")
        
        if lugares_sin_caracteristicas.count() == 0:
            print("✅ Todos los lugares ya tienen características extraídas válidas")
            return
        
        # Convertir a formato de diccionario para DeepSeek
        lugares_data = []
        for lugar in lugares_sin_caracteristicas:
            lugar_dict = {
                'id': lugar.id,
                'nombre': lugar.nombre,
                'tipo_principal': lugar.tipo_principal,
                'descripcion': lugar.descripcion or '',
                'resumen_ia': lugar.resumen_ia or '',
                'rating': lugar.rating or 0,
                'nivel_precios': lugar.nivel_precios.descripcion if lugar.nivel_precios else 'No especificado'
            }
            lugares_data.append(lugar_dict)
        
        print(f"🔄 Procesando {len(lugares_data)} lugares...")
        
        # Extraer características en lotes
        caracteristicas_extraidas = extraer_caracteristicas_lotes(lugares_data, max_lotes=2)
        
        print(f"✅ Extraídas características para {len(caracteristicas_extraidas)} lugares")
        
        # Actualizar la base de datos
        lugares_actualizados = 0
        for lugar_id, caracteristicas in caracteristicas_extraidas.items():
            try:
                lugar = LugarGooglePlaces.objects.get(id=lugar_id)
                lugar.caracteristicas_extraidas = caracteristicas
                lugar.save()
                lugares_actualizados += 1
                print(f"✅ Actualizado lugar {lugar.nombre} con {len(caracteristicas.get('amenidades', []))} amenidades")
            except LugarGooglePlaces.DoesNotExist:
                print(f"❌ Lugar con ID {lugar_id} no encontrado")
        
        print(f"🎉 Proceso completado. {lugares_actualizados} lugares actualizados")
        
    except Exception as e:
        print(f"❌ Error en la extracción de características: {e}")
        import traceback
        traceback.print_exc()

def extract_characteristics_for_specific_places(place_ids):
    """Extraer características para lugares específicos"""
    
    print(f"🔍 Extrayendo características para {len(place_ids)} lugares específicos...")
    
    try:
        lugares = LugarGooglePlaces.objects.filter(
            id__in=place_ids,
            is_active=True
        ).exclude(
            resumen_ia__isnull=True
        ).exclude(
            resumen_ia__exact=''
        )
        
        print(f"📊 Encontrados {lugares.count()} lugares válidos")
        
        # Convertir a formato de diccionario
        lugares_data = []
        for lugar in lugares:
            lugar_dict = {
                'id': lugar.id,
                'nombre': lugar.nombre,
                'tipo_principal': lugar.tipo_principal,
                'descripcion': lugar.descripcion or '',
                'resumen_ia': lugar.resumen_ia or '',
                'rating': lugar.rating or 0,
                'nivel_precios': lugar.nivel_precios.descripcion if lugar.nivel_precios else 'No especificado'
            }
            lugares_data.append(lugar_dict)
        
        # Extraer características
        caracteristicas_extraidas = extraer_caracteristicas_lotes(lugares_data, max_lotes=1)
        
        # Actualizar la base de datos
        for lugar_id, caracteristicas in caracteristicas_extraidas.items():
            try:
                lugar = LugarGooglePlaces.objects.get(id=lugar_id)
                lugar.caracteristicas_extraidas = caracteristicas
                lugar.save()
                print(f"✅ Actualizado {lugar.nombre}: {len(caracteristicas.get('amenidades', []))} amenidades")
            except LugarGooglePlaces.DoesNotExist:
                print(f"❌ Lugar con ID {lugar_id} no encontrado")
        
        print("🎉 Proceso completado")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_characteristics_extraction():
    """Probar la extracción de características con algunos lugares de ejemplo"""
    
    print("🧪 Probando extracción de características...")
    
    # Buscar lugares específicos que sabemos que tienen piscina
    lugares_piscina = LugarGooglePlaces.objects.filter(
        resumen_ia__icontains='piscina',
        is_active=True
    )[:3]
    
    if lugares_piscina.count() == 0:
        print("❌ No se encontraron lugares con piscina para probar")
        return
    
    place_ids = [lugar.id for lugar in lugares_piscina]
    print(f"🔍 Probando con lugares: {[lugar.nombre for lugar in lugares_piscina]}")
    
    extract_characteristics_for_specific_places(place_ids)

def check_characteristics_status():
    """Verificar el estado actual de las características extraídas"""
    
    print("🔍 Verificando estado de características extraídas...")
    
    try:
        # Total de lugares activos
        total_lugares = LugarGooglePlaces.objects.filter(is_active=True).count()
        print(f"📊 Total de lugares activos: {total_lugares}")
        
        # Lugares con resumen IA
        lugares_con_resumen = LugarGooglePlaces.objects.filter(
            is_active=True,
            resumen_ia__isnull=False
        ).exclude(
            resumen_ia__exact=''
        ).count()
        print(f"📝 Lugares con resumen IA: {lugares_con_resumen}")
        
        # Lugares con características extraídas válidas
        lugares_con_caracteristicas = LugarGooglePlaces.objects.filter(
            is_active=True,
            caracteristicas_extraidas__isnull=False
        ).exclude(
            caracteristicas_extraidas={}
        ).filter(
            caracteristicas_extraidas__amenidades__isnull=False
        ).exclude(
            caracteristicas_extraidas__amenidades=[]
        ).count()
        print(f"✅ Lugares con características válidas: {lugares_con_caracteristicas}")
        
        # Lugares con características vacías
        lugares_vacios = LugarGooglePlaces.objects.filter(
            is_active=True,
            caracteristicas_extraidas={}
        ).count()
        print(f"❌ Lugares con características vacías: {lugares_vacios}")
        
        # Lugares con características null
        lugares_null = LugarGooglePlaces.objects.filter(
            is_active=True,
            caracteristicas_extraidas__isnull=True
        ).count()
        print(f"❌ Lugares con características null: {lugares_null}")
        
        # Lugares que necesitan procesamiento
        lugares_necesitan_procesamiento = LugarGooglePlaces.objects.filter(
            is_active=True
        ).exclude(
            resumen_ia__isnull=True
        ).exclude(
            resumen_ia__exact=''
        ).filter(
            caracteristicas_extraidas__isnull=True
        ).count() + LugarGooglePlaces.objects.filter(
            is_active=True
        ).exclude(
            resumen_ia__isnull=True
        ).exclude(
            resumen_ia__exact=''
        ).filter(
            caracteristicas_extraidas={}
        ).count()
        
        print(f"🔄 Lugares que necesitan procesamiento: {lugares_necesitan_procesamiento}")
        
        # Mostrar algunos ejemplos de lugares con características
        print(f"\n📋 Ejemplos de lugares con características extraídas:")
        lugares_ejemplo = LugarGooglePlaces.objects.filter(
            is_active=True,
            caracteristicas_extraidas__isnull=False
        ).exclude(
            caracteristicas_extraidas={}
        ).filter(
            caracteristicas_extraidas__amenidades__isnull=False
        ).exclude(
            caracteristicas_extraidas__amenidades=[]
        )[:5]
        
        for lugar in lugares_ejemplo:
            caracteristicas = lugar.caracteristicas_extraidas
            amenidades = caracteristicas.get('amenidades', [])
            servicios = caracteristicas.get('servicios', [])
            print(f"  - {lugar.nombre}")
            print(f"    Amenidades: {amenidades}")
            print(f"    Servicios: {servicios}")
        
        # Mostrar algunos ejemplos de lugares sin características
        print(f"\n📋 Ejemplos de lugares sin características:")
        lugares_sin_ejemplo = LugarGooglePlaces.objects.filter(
            is_active=True,
            caracteristicas_extraidas={}
        )[:3]
        
        for lugar in lugares_sin_ejemplo:
            print(f"  - {lugar.nombre} (ID: {lugar.id})")
            if lugar.resumen_ia:
                print(f"    Resumen: {lugar.resumen_ia[:100]}...")
        
    except Exception as e:
        print(f"❌ Error al verificar estado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            test_characteristics_extraction()
        elif command == "specific":
            if len(sys.argv) > 2:
                place_ids = [int(pid) for pid in sys.argv[2:]]
                extract_characteristics_for_specific_places(place_ids)
            else:
                print("❌ Debes especificar IDs de lugares")
        elif command == "status":
            check_characteristics_status()
        else:
            print("❌ Comando no reconocido. Usa: test, specific, status, o sin argumentos para procesar todos")
    else:
        extract_characteristics_for_places() 