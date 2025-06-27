#!/usr/bin/env python3
"""
Script de prueba para verificar la optimización de datos adicionales
"""

import os
import sys
import django
import json
from typing import Dict, Any

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itinerario_backend.settings')
django.setup()

from .integrator import ChatbotIntegrator

def test_optimizacion_datos():
    """Prueba la optimización de obtención de datos adicionales"""
    
    print("🚀 Probando optimización de datos adicionales...")
    print("=" * 80)
    
    # Crear integrador
    integrator = ChatbotIntegrator()
    
    # Mensajes de prueba
    mensajes_prueba = [
        "Necesito un hotel lujoso con piscina",
        "Busco un restaurante romántico para cenar",
        "Quiero un café acogedor para trabajar"
    ]
    
    for i, mensaje in enumerate(mensajes_prueba, 1):
        print(f"\n📝 Prueba {i}: {mensaje}")
        print("-" * 60)
        
        try:
            # Procesar mensaje completo
            resultado = integrator.procesar_mensaje_completo(mensaje)
            
            print(f"✅ Filtros extraídos: {resultado['filtros_extraidos']['tipo_establecimiento']}")
            print(f"🔍 Candidatos encontrados: {resultado['candidatos_encontrados']}")
            print(f"📊 Candidatos seleccionados: {resultado['total_seleccionados']}")
            
            # Verificar datos adicionales en el primer candidato
            if resultado['mejores_candidatos']:
                candidato = resultado['mejores_candidatos'][0]
                print(f"\n🏆 Primer candidato: {candidato['nombre']}")
                print(f"   📍 Dirección: {candidato.get('direccion', 'N/A')}")
                print(f"   🌐 Website: {candidato.get('website', 'N/A')}")
                print(f"   📞 Teléfono: {candidato.get('telefono', 'N/A')}")
                print(f"   💰 Nivel precio: {candidato.get('nivel_precios', 'N/A')}")
                print(f"   📊 Rango precio: {candidato.get('rango_precio_inferior', 'N/A')} - {candidato.get('rango_precio_superior', 'N/A')} {candidato.get('moneda_precio', 'PEN')}")
                print(f"   🕒 Horarios: {len(candidato.get('horarios', []))} días configurados")
                print(f"   🏢 Estado: {candidato.get('estado_negocio', 'N/A')}")
                
                # Verificar que los datos están completos
                datos_completos = all([
                    candidato.get('direccion'),
                    candidato.get('latitud') is not None,
                    candidato.get('longitud') is not None,
                    candidato.get('total_ratings') is not None
                ])
                
                if datos_completos:
                    print("   ✅ Datos adicionales completos")
                else:
                    print("   ⚠️ Algunos datos adicionales faltan")
            else:
                print("   ❌ No se encontraron candidatos")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("✅ Pruebas de optimización completadas")

def test_funcion_obtener_datos():
    """Prueba específicamente la función de obtener datos adicionales"""
    
    print("\n🔧 Probando función obtener_datos_adicionales_bd...")
    print("=" * 80)
    
    integrator = ChatbotIntegrator()
    
    # Simular candidatos con solo IDs
    candidatos_simples = [
        {
            'id': 1,
            'nombre': 'Test Place 1',
            'tipo_principal': 'hotel',
            'rating': 4.5,
            'score_similitud': 0.85
        },
        {
            'id': 2,
            'nombre': 'Test Place 2',
            'tipo_principal': 'restaurant',
            'rating': 4.2,
            'score_similitud': 0.78
        }
    ]
    
    try:
        # Obtener datos adicionales
        candidatos_enriquecidos = integrator.obtener_datos_adicionales_bd(candidatos_simples)
        
        print(f"📊 Candidatos originales: {len(candidatos_simples)}")
        print(f"📊 Candidatos enriquecidos: {len(candidatos_enriquecidos)}")
        
        for i, candidato in enumerate(candidatos_enriquecidos):
            print(f"\n🏢 Candidato {i+1}:")
            print(f"   ID: {candidato.get('id')}")
            print(f"   Nombre: {candidato.get('nombre')}")
            print(f"   Dirección: {candidato.get('direccion', 'N/A')}")
            print(f"   Website: {candidato.get('website', 'N/A')}")
            print(f"   Teléfono: {candidato.get('telefono', 'N/A')}")
            print(f"   Nivel precio: {candidato.get('nivel_precios', 'N/A')}")
            print(f"   Horarios: {len(candidato.get('horarios', []))} días")
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")

def main():
    """Función principal"""
    try:
        test_optimizacion_datos()
        test_funcion_obtener_datos()
        
        print("\n🎉 Todas las pruebas completadas exitosamente!")
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 