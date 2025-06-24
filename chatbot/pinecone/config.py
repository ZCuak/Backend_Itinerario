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
    DIMENSION = int(os.getenv('PINECONE_DIMENSION', '768'))  # Dimensiones para all-mpnet-base-v2
    METRIC = os.getenv('PINECONE_METRIC', 'cosine')
    
    # Configuración de Hugging Face
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-mpnet-base-v2')
    
    # Modelos alternativos más precisos (descomenta el que prefieras):
    # EMBEDDING_MODEL = 'sentence-transformers/all-mpnet-base-v2'  # 768d - Excelente precisión
    # EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L12-v2'  # 384d - Mejor que L6
    # EMBEDDING_MODEL = 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'  # Multilingüe avanzado
    # EMBEDDING_MODEL = 'sentence-transformers/all-mpnet-base-v2'  # Mejor rendimiento general
    
    # Configuración de búsqueda
    TOP_K = int(os.getenv('PINECONE_TOP_K', '5'))
    SIMILARITY_THRESHOLD = float(os.getenv('PINECONE_SIMILARITY_THRESHOLD', '0.6'))
    
    # Configuración de precisión semántica
    SEMANTIC_PRECISION = os.getenv('SEMANTIC_PRECISION', 'high')  # high, medium, low
    USE_KEYWORDS = os.getenv('USE_KEYWORDS', 'true').lower() == 'true'
    USE_NORMALIZATION = os.getenv('USE_NORMALIZATION', 'true').lower() == 'true'
    
    # Umbrales específicos por tipo de búsqueda
    HOTEL_SIMILARITY_THRESHOLD = float(os.getenv('HOTEL_SIMILARITY_THRESHOLD', '0.65'))
    RESTAURANT_SIMILARITY_THRESHOLD = float(os.getenv('RESTAURANT_SIMILARITY_THRESHOLD', '0.62'))
    GENERAL_SIMILARITY_THRESHOLD = float(os.getenv('GENERAL_SIMILARITY_THRESHOLD', '0.58'))
    
    @classmethod
    def validate_config(cls):
        """Validar que la configuración esté completa"""
        if not cls.PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY no está configurada")
        
        return True 