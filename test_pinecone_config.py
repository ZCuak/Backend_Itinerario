#!/usr/bin/env python3
"""
Script de prueba para verificar la configuración de Pinecone
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itinerario_backend.settings')
django.setup()

def test_pinecone_config():
    """Probar la configuración de Pinecone"""
    
    print("🧪 Probando configuración de Pinecone...")
    
    try:
        from chatbot.pinecone.config import PineconeConfig
        
        print("✅ Configuración cargada correctamente")
        print(f"📋 Variables de configuración:")
        print(f"  - INDEX_NAME: {PineconeConfig.INDEX_NAME}")
        print(f"  - PINECONE_INDEX_NAME: {PineconeConfig.PINECONE_INDEX_NAME}")
        print(f"  - API_KEY: {'SÍ' if PineconeConfig.API_KEY else 'NO'}")
        print(f"  - ENVIRONMENT: {PineconeConfig.ENVIRONMENT}")
        print(f"  - METRIC: {PineconeConfig.METRIC}")
        print(f"  - TOP_K: {PineconeConfig.TOP_K}")
        print(f"  - DIMENSION: {PineconeConfig.DIMENSION}")
        
        # Validar configuración
        PineconeConfig.validate_config()
        print("✅ Configuración validada correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vector_store_initialization():
    """Probar la inicialización del vector store"""
    
    print("\n🧪 Probando inicialización del vector store...")
    
    try:
        from chatbot.pinecone.places_vector_store import PlacesVectorStore
        
        vector_store = PlacesVectorStore()
        print("✅ Vector store inicializado correctamente")
        print(f"📋 Índice: {vector_store.index_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al inicializar vector store: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_embedding_generator():
    """Probar el generador de embeddings"""
    
    print("\n🧪 Probando generador de embeddings...")
    
    try:
        from chatbot.pinecone.places_embeddings import PlacesEmbeddingGenerator
        from chatbot.pinecone.config import PineconeConfig
        
        embedding_generator = PlacesEmbeddingGenerator(PineconeConfig.EMBEDDING_MODEL)
        print("✅ Generador de embeddings inicializado correctamente")
        
        # Probar generación de embedding simple
        test_text = "restaurante italiano con terraza"
        embedding = embedding_generator.embeddings.get_embedding(test_text)
        print(f"✅ Embedding generado correctamente: {len(embedding)} dimensiones")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en generador de embeddings: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de configuración de Pinecone...")
    
    # Ejecutar pruebas
    config_ok = test_pinecone_config()
    vector_store_ok = test_vector_store_initialization() if config_ok else False
    embedding_ok = test_embedding_generator() if config_ok else False
    
    print(f"\n📊 Resultados de las pruebas:")
    print(f"  - Configuración: {'✅ OK' if config_ok else '❌ ERROR'}")
    print(f"  - Vector Store: {'✅ OK' if vector_store_ok else '❌ ERROR'}")
    print(f"  - Embeddings: {'✅ OK' if embedding_ok else '❌ ERROR'}")
    
    if config_ok and vector_store_ok and embedding_ok:
        print("\n🎉 Todas las pruebas pasaron. El sistema está listo para usar.")
    else:
        print("\n❌ Algunas pruebas fallaron. Revisa la configuración.")
        sys.exit(1) 