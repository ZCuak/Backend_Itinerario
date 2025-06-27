"""
Modelo de embeddings local usando BAAI/bge-base-en-v1.5
Configurado para 768 dimensiones y bilingüe (español/inglés)
"""

import torch
from sentence_transformers import SentenceTransformer
from typing import List, Union
import logging
import numpy as np

logger = logging.getLogger(__name__)

class LocalEmbedder:
    """Modelo de embeddings local usando Sentence Transformers"""
    
    def __init__(self, 
                 model_name: str = "BAAI/bge-base-en-v1.5",
                 device: str = None,
                 max_length: int = 512):
        """
        Inicializa el modelo de embeddings
        
        Args:
            model_name: Nombre del modelo de HuggingFace
            device: Dispositivo ('cpu', 'cuda', etc.)
            max_length: Longitud máxima de secuencia
        """
        self.model_name = model_name
        self.max_length = max_length
        
        # Detectar dispositivo automáticamente si no se especifica
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        logger.info(f"Inicializando modelo de embeddings: {model_name}")
        logger.info(f"Dispositivo: {self.device}")
        
        try:
            # Cargar modelo con optimizaciones
            self.model = SentenceTransformer(
                model_name,
                device=self.device
            )
            
            # Configurar dtype para optimización
            if self.device == "cuda":
                self.model = self.model.half()  # float16 para GPU
                logger.info("Modelo configurado en float16 para GPU")
            
            # Verificar dimensión
            self.dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"Dimensión del modelo: {self.dimension}")
            
            if self.dimension != 768:
                logger.warning(f"Modelo tiene {self.dimension} dimensiones, esperadas: 768")
            
        except Exception as e:
            logger.error(f"Error al cargar modelo: {e}")
            raise
    
    def encode_text(self, text: str) -> List[float]:
        """
        Codifica un texto a vector de embeddings
        
        Args:
            text: Texto a codificar
            
        Returns:
            Lista de floats (vector de embeddings)
        """
        try:
            # Preprocesar texto
            if not text or not text.strip():
                logger.warning("Texto vacío proporcionado")
                return [0.0] * self.dimension
            
            # Codificar texto
            embedding = self.model.encode(
                text,
                convert_to_tensor=False,
                normalize_embeddings=True  # Normalizar para similitud coseno
            )
            
            # Convertir a lista de floats
            embedding_list = embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
            
            logger.debug(f"Texto codificado exitosamente: {len(embedding_list)} dimensiones")
            return embedding_list
            
        except Exception as e:
            logger.error(f"Error al codificar texto: {e}")
            raise
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Codifica múltiples textos a vectores de embeddings
        
        Args:
            texts: Lista de textos a codificar
            
        Returns:
            Lista de listas de floats (vectores de embeddings)
        """
        try:
            # Filtrar textos vacíos
            valid_texts = [text.strip() for text in texts if text and text.strip()]
            
            if not valid_texts:
                logger.warning("No hay textos válidos para codificar")
                return []
            
            # Codificar en lote
            embeddings = self.model.encode(
                valid_texts,
                convert_to_tensor=False,
                normalize_embeddings=True,
                batch_size=32  # Tamaño de lote optimizado
            )
            
            # Convertir a lista de listas
            embeddings_list = embeddings.tolist() if hasattr(embeddings, 'tolist') else embeddings
            
            logger.info(f"Lote de {len(valid_texts)} textos codificado exitosamente")
            return embeddings_list
            
        except Exception as e:
            logger.error(f"Error al codificar lote: {e}")
            raise
    
    def get_similarity(self, text1: str, text2: str) -> float:
        """
        Calcula la similitud coseno entre dos textos
        
        Args:
            text1: Primer texto
            text2: Segundo texto
            
        Returns:
            Score de similitud (0-1)
        """
        try:
            # Codificar ambos textos
            embedding1 = self.encode_text(text1)
            embedding2 = self.encode_text(text2)
            
            # Calcular similitud coseno
            similarity = self.model.similarity(embedding1, embedding2)
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error al calcular similitud: {e}")
            raise
    
    def get_dimension(self) -> int:
        """Retorna la dimensión del modelo"""
        return self.dimension
    
    def get_model_info(self) -> dict:
        """Retorna información del modelo"""
        return {
            "model_name": self.model_name,
            "dimension": self.dimension,
            "device": self.device,
            "max_length": self.max_length
        }

# Instancia global del embedder
_embedder_instance = None

def get_embedder() -> LocalEmbedder:
    """
    Obtiene la instancia global del embedder (singleton)
    
    Returns:
        Instancia de LocalEmbedder
    """
    global _embedder_instance
    
    if _embedder_instance is None:
        _embedder_instance = LocalEmbedder()
    
    return _embedder_instance 