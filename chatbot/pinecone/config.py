import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class PineconeConfig:
    """Configuración para Pinecone"""
    
    # Configuración de Pinecone
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT', 'gcp-starter')
    PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'chatbot-memory')
    PINECONE_NAMESPACE = os.getenv('PINECONE_NAMESPACE', 'conversations')
    
    # Configuración del servidor (para el plan gratuito)
    PINECONE_CLOUD = 'aws'
    PINECONE_REGION = 'us-east-1'
    
    # Variables de compatibilidad (para mantener código existente)
    INDEX_NAME = PINECONE_INDEX_NAME
    NAMESPACE = PINECONE_NAMESPACE
    API_KEY = PINECONE_API_KEY
    ENVIRONMENT = PINECONE_ENVIRONMENT
    
    # Configuración del índice de lugares
    PLACES_INDEX_NAME = os.getenv('PLACES_INDEX_NAME', 'places-index')
    PLACES_NAMESPACE = os.getenv('PLACES_NAMESPACE', 'places')
    
    # Configuración de embeddings
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-mpnet-base-v2')
    EMBEDDING_DIMENSION = int(os.getenv('EMBEDDING_DIMENSION', '768'))
    
    # Configuración de búsqueda
    SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', '0.65'))
    PLACES_SIMILARITY_THRESHOLD = float(os.getenv('PLACES_SIMILARITY_THRESHOLD', '0.65'))
    
    # Configuración de chunking
    MAX_TOKENS_PER_CHUNK = int(os.getenv('MAX_TOKENS_PER_CHUNK', '350'))
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '50'))
    
    # Configuración de cache
    EMBEDDING_CACHE_SIZE = int(os.getenv('EMBEDDING_CACHE_SIZE', '1000'))
    
    # Configuración de logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Configuración adicional para compatibilidad
    METRIC = os.getenv('PINECONE_METRIC', 'cosine')
    TOP_K = int(os.getenv('PINECONE_TOP_K', '5'))
    DIMENSION = EMBEDDING_DIMENSION
    
    @classmethod
    def validate_config(cls):
        """Validar que la configuración esté completa"""
        if not cls.PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY no está configurada")
        
        return True 