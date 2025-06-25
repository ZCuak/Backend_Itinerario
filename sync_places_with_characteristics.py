#!/usr/bin/env python3
"""
Script para sincronizar lugares con características extraídas al índice de Pinecone
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itinerario_backend.settings')
django.setup()

from chatbot.models import LugarGooglePlaces
from chatbot.pinecone.places_vector_store import PlacesVectorStore

def sync_places_with_characteristics():
    """Sincronizar lugares que tienen características extraídas"""
    
    print("🔄 Iniciando sincronización de lugares con características extraídas...")
    
    try:
        # Obtener lugares con características extraídas válidas
        lugares_con_caracteristicas = LugarGooglePlaces.objects.filter(
            is_active=True,
            caracteristicas_extraidas__isnull=False
        ).exclude(
            caracteristicas_extraidas={}
        ).filter(
            caracteristicas_extraidas__amenidades__isnull=False
        ).exclude(
            caracteristicas_extraidas__amenidades=[]
        )
        
        print(f"📊 Encontrados {lugares_con_caracteristicas.count()} lugares con características extraídas")
        
        if lugares_con_caracteristicas.count() == 0:
            print("❌ No hay lugares con características extraídas para sincronizar")
            return
        
        # Inicializar vector store
        vector_store = PlacesVectorStore()
        
        # Mostrar algunos ejemplos antes de sincronizar
        print(f"\n📋 Ejemplos de lugares a sincronizar:")
        for lugar in lugares_con_caracteristicas[:3]:
            caracteristicas = lugar.caracteristicas_extraidas
            amenidades = caracteristicas.get('amenidades', [])
            palabras_clave = caracteristicas.get('palabras_clave', [])
            print(f"  - {lugar.nombre}")
            print(f"    Amenidades: {amenidades}")
            print(f"    Palabras clave: {palabras_clave[:3]}...")
        
        # Sincronizar lugares en lotes
        batch_size = 10
        total_synced = 0
        
        for i in range(0, lugares_con_caracteristicas.count(), batch_size):
            batch = lugares_con_caracteristicas[i:i + batch_size]
            print(f"\n🔄 Procesando lote {i//batch_size + 1} de {(lugares_con_caracteristicas.count() + batch_size - 1) // batch_size}")
            
            try:
                # Agregar lugares al índice
                vector_ids = vector_store.add_places(batch)
                total_synced += len(vector_ids)
                
                print(f"✅ Sincronizados {len(vector_ids)} lugares del lote")
                
                # Mostrar algunos detalles del lote
                for lugar in batch[:2]:
                    caracteristicas = lugar.caracteristicas_extraidas
                    amenidades = caracteristicas.get('amenidades', [])
                    print(f"    - {lugar.nombre}: {len(amenidades)} amenidades")
                
            except Exception as e:
                print(f"❌ Error al sincronizar lote: {e}")
                continue
        
        print(f"\n🎉 Sincronización completada. {total_synced} lugares sincronizados")
        
        # Verificar estadísticas del índice
        try:
            stats = vector_store.get_index_stats()
            print(f"📊 Estadísticas del índice:")
            print(f"  - Total de vectores: {stats.get('total_vector_count', 'N/A')}")
            print(f"  - Dimensión: {stats.get('dimension', 'N/A')}")
            print(f"  - Métrica: {stats.get('metric', 'N/A')}")
        except Exception as e:
            print(f"❌ Error al obtener estadísticas: {e}")
        
    except Exception as e:
        print(f"❌ Error en la sincronización: {e}")
        import traceback
        traceback.print_exc()

def test_embedding_generation():
    """Probar la generación de embeddings con características extraídas"""
    
    print("🧪 Probando generación de embeddings con características extraídas...")
    
    try:
        # Obtener algunos lugares con características
        lugares_test = LugarGooglePlaces.objects.filter(
            is_active=True,
            caracteristicas_extraidas__isnull=False
        ).exclude(
            caracteristicas_extraidas={}
        ).filter(
            caracteristicas_extraidas__amenidades__isnull=False
        ).exclude(
            caracteristicas_extraidas__amenidades=[]
        )[:3]
        
        if lugares_test.count() == 0:
            print("❌ No hay lugares con características para probar")
            return
        
        # Inicializar vector store
        vector_store = PlacesVectorStore()
        
        print(f"📋 Probando con {lugares_test.count()} lugares:")
        
        for lugar in lugares_test:
            print(f"\n🔍 Lugar: {lugar.nombre}")
            
            # Mostrar características
            caracteristicas = lugar.caracteristicas_extraidas
            amenidades = caracteristicas.get('amenidades', [])
            palabras_clave = caracteristicas.get('palabras_clave', [])
            
            print(f"  Amenidades: {amenidades}")
            print(f"  Palabras clave: {palabras_clave[:3]}...")
            
            # Generar embedding
            try:
                embedding = vector_store.embedding_generator.get_place_embedding(lugar)
                print(f"  ✅ Embedding generado: {len(embedding)} dimensiones")
                
                # Generar texto de embedding para verificar
                texto_embedding = vector_store.embedding_generator.generate_text_for_embedding(lugar)
                print(f"  📝 Texto de embedding: {texto_embedding[:150]}...")
                
            except Exception as e:
                print(f"  ❌ Error al generar embedding: {e}")
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

def clear_and_resync():
    """Limpiar índice y resincronizar todos los lugares"""
    
    print("🗑️ Limpiando índice y resincronizando...")
    
    try:
        vector_store = PlacesVectorStore()
        
        # Limpiar índice
        print("🗑️ Limpiando índice...")
        vector_store.clear_index()
        print("✅ Índice limpiado")
        
        # Resincronizar todos los lugares
        print("🔄 Resincronizando todos los lugares...")
        total_synced = vector_store.sync_places_from_database(batch_size=20)
        
        print(f"🎉 Resincronización completada. {total_synced} lugares sincronizados")
        
    except Exception as e:
        print(f"❌ Error en resincronización: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            test_embedding_generation()
        elif command == "clear":
            clear_and_resync()
        else:
            print("❌ Comando no reconocido. Usa: test, clear, o sin argumentos para sincronizar")
    else:
        sync_places_with_characteristics() 