#!/usr/bin/env python3
"""
Script para verificar el estado de las características extraídas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itinerario_backend.settings')
django.setup()

from chatbot.models import LugarGooglePlaces

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
        print(f"✅ Lugares con características extraídas válidas: {lugares_con_caracteristicas}")
        
        # Lugares sin características extraídas
        lugares_sin_caracteristicas = total_lugares - lugares_con_caracteristicas
        print(f"❌ Lugares sin características extraídas: {lugares_sin_caracteristicas}")
        
        # Mostrar algunos ejemplos
        print(f"\n📋 Ejemplos de lugares con características:")
        lugares_ejemplo = LugarGooglePlaces.objects.filter(
            is_active=True,
            caracteristicas_extraidas__isnull=False
        ).exclude(
            caracteristicas_extraidas={}
        )[:3]
        
        for lugar in lugares_ejemplo:
            caracteristicas = lugar.caracteristicas_extraidas
            amenidades = caracteristicas.get('amenidades', [])
            palabras_clave = caracteristicas.get('palabras_clave', [])
            print(f"  - {lugar.nombre}")
            print(f"    Amenidades: {amenidades[:3]}...")
            print(f"    Palabras clave: {palabras_clave[:3]}...")
        
        # Mostrar lugares sin características
        print(f"\n📋 Ejemplos de lugares sin características:")
        lugares_sin = LugarGooglePlaces.objects.filter(
            is_active=True
        ).filter(
            caracteristicas_extraidas__isnull=True
        ) | LugarGooglePlaces.objects.filter(
            is_active=True
        ).filter(
            caracteristicas_extraidas={}
        )[:3]
        
        for lugar in lugares_sin:
            print(f"  - {lugar.nombre} (tiene resumen: {bool(lugar.resumen_ia)})")
        
    except Exception as e:
        print(f"❌ Error al verificar estado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_characteristics_status() 