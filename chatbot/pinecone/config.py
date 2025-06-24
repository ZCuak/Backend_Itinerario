import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class PineconeConfig:
    """Configuración para Pinecone"""
    
    # Configuración de Pinecone
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY', 'pcsk_43wN95_49uhMuj9uQEynDooZqWxLw9AM3w83LLj5yDPWHUFbPweqJJtktetuy8go4KUJhq')
    PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT', 'us-east-1')
    
    # Configuración del índice
    INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'chatbot-memory')
    DIMENSION = int(os.getenv('PINECONE_DIMENSION', '768'))  # Dimensiones para embeddings
    METRIC = os.getenv('PINECONE_METRIC', 'cosine')
    
    # Configuración de Hugging Face
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
    
    # Configuración de búsqueda
    TOP_K = int(os.getenv('PINECONE_TOP_K', '5'))
    SIMILARITY_THRESHOLD = float(os.getenv('PINECONE_SIMILARITY_THRESHOLD', '0.7'))
    
    @classmethod
    def validate_config(cls):
        """Validar que la configuración esté completa"""
        if not cls.PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY no está configurada")
        
        return True 