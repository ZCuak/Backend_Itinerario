#!/usr/bin/env python3
"""
Prueba específica para búsquedas por nivel de precios
Este archivo prueba el sistema de búsqueda por precios con los datos específicos del usuario
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itinerario_backend.settings')
django.setup()

from chatbot.pinecone.places_vector_store import PlacesVectorStore
from chatbot.pinecone.places_views import extract_search_criteria_from_message

def test_price_level_search():
    """
    Prueba la funcionalidad de búsqueda por nivel de precios
    """
    
    print("💰 PROBANDO BÚSQUEDAS POR NIVEL DE PRECIOS")
    print("=" * 60)
    
    # Mensajes específicos para probar niveles de precio
    price_test_messages = [
        # Nivel 0 - Gratis
        "quiero un lugar gratis para visitar",
        "busco un restaurante sin costo",
        "necesito un lugar sin pago",
        
        # Nivel 1 - Económico (0.00-50.00 PEN)
        "quiero un restaurante económico",
        "busco un hotel barato",
        "necesito un café accesible",
        "quiero un lugar bajo precio",
        
        # Nivel 2 - Moderado (50.00-150.00 PEN)
        "busco un restaurante moderado",
        "quiero un hotel de precio medio",
        "necesito un lugar normal",
        "busco un restaurante estándar",
        
        # Nivel 3 - Caro (150.00-400.00 PEN)
        "quiero un restaurante caro",
        "busco un hotel elevado",
        "necesito un lugar alto precio",
        
        # Nivel 4 - Muy Caro (400.00-1000.00 PEN)
        "quiero un restaurante muy caro",
        "busco un hotel de lujo",
        "necesito un lugar exclusivo",
        "quiero un restaurante premium",
        "busco un lugar de alta cocina",
        "quiero un restaurante de estrellas michelin",
        
        # Combinaciones con otros criterios
        "quiero un restaurante económico con comida italiana",
        "busco un hotel de lujo con spa y vista al mar",
        "necesito un café barato cerca del centro",
        "quiero un restaurante moderado para la familia",
        "busco un lugar gratis para estudiantes",
        "necesito un hotel exclusivo de 5 estrellas"
    ]
    
    # Inicializar vector store
    vector_store = PlacesVectorStore()
    
    for i, message in enumerate(price_test_messages, 1):
        print(f"\n📝 Mensaje {i}: {message}")
        print("-" * 50)
        
        # Extraer criterios usando DeepSeek
        criteria = extract_search_criteria_from_message(message)
        
        if criteria and criteria.get('price_level'):
            print(f"✅ Nivel de precio detectado: {criteria['price_level']}")
            
            # Realizar búsqueda por nivel de precio
            try:
                results = vector_store.find_places_by_price_level(
                    price_level=criteria['price_level'],
                    place_type=criteria.get('place_type'),
                    features=criteria.get('features'),
                    top_k=3
                )
                
                print(f"🔍 Resultados encontrados: {len(results)}")
                
                for j, result in enumerate(results[:3], 1):
                    metadata = result['metadata']
                    print(f"   {j}. {metadata.get('nombre')}")
                    print(f"      Tipo: {metadata.get('tipo_principal')}")
                    print(f"      Rating: {metadata.get('rating')}")
                    print(f"      Nivel Precios: {metadata.get('nivel_precios__descripcion')}")
                    print(f"      Score: {result['score']:.3f}")
                
            except Exception as e:
                print(f"❌ Error en búsqueda: {str(e)}")
        else:
            print("❌ No se detectó nivel de precio")
        
        print()

def test_price_ranges():
    """
    Prueba búsquedas por rangos específicos de precios
    """
    
    print("\n🎯 PROBANDO BÚSQUEDAS POR RANGOS DE PRECIOS")
    print("=" * 60)
    
    # Rangos específicos según los datos del usuario
    price_ranges = [
        "50-150",      # Moderado
        "100-300",     # Rango personalizado
        "hasta 50",    # Económico
        "desde 200",   # Caro o más
        "150-400",     # Caro
        "400-1000"     # Muy caro
    ]
    
    vector_store = PlacesVectorStore()
    
    for price_range in price_ranges:
        print(f"\n💰 Rango: {price_range}")
        print("-" * 30)
        
        try:
            results = vector_store.find_places_by_price_level(
                price_level=price_range,
                top_k=3
            )
            
            print(f"🔍 Resultados encontrados: {len(results)}")
            
            for i, result in enumerate(results[:3], 1):
                metadata = result['metadata']
                print(f"   {i}. {metadata.get('nombre')}")
                print(f"      Nivel: {metadata.get('nivel_precios__nivel')}")
                print(f"      Rango: {metadata.get('nivel_precios__rango_inferior')} - {metadata.get('nivel_precios__rango_superior')} {metadata.get('nivel_precios__moneda')}")
                print(f"      Score: {result['score']:.3f}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print()

def test_smart_search_with_prices():
    """
    Prueba búsquedas inteligentes que incluyen criterios de precio
    """
    
    print("\n🧠 PROBANDO BÚSQUEDAS INTELIGENTES CON PRECIOS")
    print("=" * 60)
    
    # Criterios complejos que incluyen precios
    complex_criteria = [
        {
            'place_type': 'restaurante',
            'features': ['italiano', 'terraza'],
            'price_level': 'económico',
            'rating_min': 4.0
        },
        {
            'place_type': 'hotel',
            'features': ['spa', 'vista al mar'],
            'price_level': 'muy caro',
            'rating_min': 5.0
        },
        {
            'place_type': 'café',
            'features': ['terraza'],
            'price_level': 'moderado',
            'opening_hours': 'abierto_ahora'
        }
    ]
    
    vector_store = PlacesVectorStore()
    
    for i, criteria in enumerate(complex_criteria, 1):
        print(f"\n🔍 Criterios complejos {i}:")
        for key, value in criteria.items():
            print(f"   {key}: {value}")
        print("-" * 40)
        
        try:
            results = vector_store.smart_place_search(
                search_criteria=criteria,
                top_k=3
            )
            
            print(f"✅ Resultados encontrados: {len(results)}")
            
            for j, result in enumerate(results[:3], 1):
                metadata = result['metadata']
                print(f"   {j}. {metadata.get('nombre')}")
                print(f"      Tipo: {metadata.get('tipo_principal')}")
                print(f"      Rating: {metadata.get('rating')}")
                print(f"      Precio: {metadata.get('nivel_precios__descripcion')}")
                print(f"      Score: {result['score']:.3f}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print()

def main():
    """
    Función principal que ejecuta todas las pruebas de precios
    """
    print("🚀 INICIANDO PRUEBAS DE NIVELES DE PRECIO")
    print("=" * 60)
    
    # Verificar configuración
    if not os.getenv('PINECONE_API_KEY'):
        print("❌ Error: PINECONE_API_KEY no está configurada")
        return
    
    if not os.getenv('API_KEY_OPENAI'):
        print("❌ Error: API_KEY_OPENAI no está configurada")
        return
    
    print("✅ Configuración verificada")
    print()
    
    try:
        # Ejecutar pruebas
        test_price_level_search()
        test_price_ranges()
        test_smart_search_with_prices()
        
        print("\n🎉 ¡Pruebas de precios completadas!")
        print("\n💡 Información de niveles de precio:")
        print("   - Nivel 0 (Gratis): 0.00 PEN")
        print("   - Nivel 1 (Económico): 0.00-50.00 PEN")
        print("   - Nivel 2 (Moderado): 50.00-150.00 PEN")
        print("   - Nivel 3 (Caro): 150.00-400.00 PEN")
        print("   - Nivel 4 (Muy Caro): 400.00-1000.00 PEN")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {str(e)}")

if __name__ == "__main__":
    main() 