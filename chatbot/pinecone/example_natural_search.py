#!/usr/bin/env python3
"""
Ejemplo de uso de la búsqueda natural con DeepSeek
Este archivo demuestra cómo procesar mensajes naturales del usuario
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itinerario_backend.settings')
django.setup()

from chatbot.pinecone.places_views import extract_search_criteria_from_message, process_natural_search
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from django.contrib.auth.models import User

def test_natural_search():
    """
    Prueba la funcionalidad de búsqueda natural con diferentes mensajes
    """
    
    # Mensajes de prueba
    test_messages = [
        "para comer quiero ir a una cafetería de 4 estrellas",
        "busco un restaurante italiano que esté abierto ahora",
        "necesito un hotel de 3 estrellas con gimnasio y piscina",
        "quiero ir a un bar con música en vivo abierto 24 horas",
        "busco un centro comercial abierto fines de semana",
        "necesito un parque con áreas para niños",
        "busco un museo con exposiciones de arte moderno",
        "quiero un restaurante peruano barato cerca del centro",
        "necesito un hotel lujoso de 5 estrellas con spa",
        "busco un lugar para tomar café con terraza",
        "quiero un restaurante económico con comida italiana",
        "busco un hotel caro con vista al mar",
        "necesito un bar moderado con música en vivo",
        "quiero un restaurante gratis o muy barato",
        "busco un lugar lujoso para cenar",
        # Nuevos mensajes con referencias específicas a precios
        "quiero un restaurante económico con comida peruana",
        "busco un hotel de lujo con spa y vista al mar",
        "necesito un café barato cerca del centro",
        "quiero un restaurante de alta cocina para una cena especial",
        "busco un lugar moderado para comer con la familia",
        "necesito un hotel exclusivo de 5 estrellas",
        "quiero un restaurante gratis para estudiantes",
        "busco un bar premium con música en vivo",
        "necesito un lugar accesible para comer",
        "quiero un restaurante de estrellas michelin",
        "busco un hotel económico con estacionamiento",
        "necesito un lugar muy caro para una ocasión especial"
    ]
    
    print("🤖 PROBANDO BÚSQUEDA NATURAL CON DEEPSEEK")
    print("=" * 60)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Mensaje {i}: {message}")
        print("-" * 40)
        
        # Extraer criterios usando DeepSeek
        criteria = extract_search_criteria_from_message(message)
        
        if criteria:
            print("✅ Criterios extraídos:")
            for key, value in criteria.items():
                print(f"   {key}: {value}")
        else:
            print("❌ No se pudieron extraer criterios")
            continue
        
        # Simular request para procesar búsqueda
        factory = APIRequestFactory()
        request = factory.post('/api/pinecone/places/process-natural-search/', {
            'user_message': message
        })
        
        # Crear usuario de prueba para autenticación
        user = User.objects.create_user(username='testuser', password='testpass')
        force_authenticate(request, user=user)
        
        try:
            # Procesar búsqueda
            response = process_natural_search(request)
            
            if response.status_code == 200:
                data = response.data
                print(f"🔍 Método de búsqueda usado: {data.get('search_method_used')}")
                print(f"📊 Resultados encontrados: {data.get('total_results')}")
                
                # Mostrar primeros 3 resultados
                results = data.get('results', [])
                for j, result in enumerate(results[:3], 1):
                    print(f"   {j}. {result.get('nombre')} - Rating: {result.get('rating')}")
                
                if len(results) > 3:
                    print(f"   ... y {len(results) - 3} más")
            else:
                print(f"❌ Error en búsqueda: {response.data.get('error')}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        # Limpiar usuario de prueba
        user.delete()
        
        print()

def test_criteria_extraction():
    """
    Prueba solo la extracción de criterios sin hacer búsqueda
    """
    
    print("🧠 PROBANDO EXTRACCIÓN DE CRITERIOS")
    print("=" * 50)
    
    # Mensajes complejos para probar
    complex_messages = [
        "Necesito un restaurante japonés de 4 estrellas con sushi fresco y que esté abierto ahora",
        "Busco un hotel de lujo de 5 estrellas con spa, gimnasio y vista al mar",
        "Quiero ir a un bar con música en vivo, karaoke y que esté abierto hasta tarde",
        "Necesito un centro comercial grande con tiendas de ropa y restaurantes, abierto fines de semana",
        "Busco un parque tranquilo con áreas de picnic, juegos para niños y estacionamiento gratuito"
    ]
    
    for i, message in enumerate(complex_messages, 1):
        print(f"\n📝 Mensaje complejo {i}: {message}")
        print("-" * 50)
        
        criteria = extract_search_criteria_from_message(message)
        
        if criteria:
            print("✅ Criterios extraídos:")
            for key, value in criteria.items():
                if isinstance(value, list):
                    print(f"   {key}: {', '.join(value)}")
                else:
                    print(f"   {key}: {value}")
        else:
            print("❌ No se pudieron extraer criterios")
        
        print()

def main():
    """
    Función principal que ejecuta todas las pruebas
    """
    print("🚀 INICIANDO PRUEBAS DE BÚSQUEDA NATURAL")
    print("=" * 60)
    
    # Verificar configuración
    if not os.getenv('API_KEY_OPENAI'):
        print("❌ Error: API_KEY_OPENAI no está configurada")
        print("   Configura la variable de entorno API_KEY_OPENAI con tu clave de DeepSeek")
        return
    
    if not os.getenv('PINECONE_API_KEY'):
        print("❌ Error: PINECONE_API_KEY no está configurada")
        print("   Configura la variable de entorno PINECONE_API_KEY")
        return
    
    print("✅ Configuración verificada")
    print()
    
    # Ejecutar pruebas
    try:
        test_criteria_extraction()
        print("\n" + "=" * 60)
        test_natural_search()
        
        print("\n🎉 ¡Pruebas completadas!")
        print("\n💡 Consejos:")
        print("   - Asegúrate de tener datos en la base de datos")
        print("   - Sincroniza los lugares con Pinecone antes de probar")
        print("   - Verifica que DeepSeek esté funcionando correctamente")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {str(e)}")
        print("   Verifica la configuración y los datos")

if __name__ == "__main__":
    main() 