from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import logging

logger = logging.getLogger(__name__)

class HuggingFaceEmbeddings:
    """Clase para generar embeddings usando modelos de Hugging Face"""
    
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'):
        """
        Inicializar el modelo de embeddings
        
        Args:
            model_name: Nombre del modelo de Hugging Face a usar
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Cargar el modelo de embeddings"""
        try:
            logger.info(f"Cargando modelo de embeddings: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Modelo cargado exitosamente")
        except Exception as e:
            logger.error(f"Error al cargar el modelo: {e}")
            raise
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Generar embedding para un texto
        
        Args:
            text: Texto a convertir en embedding
            
        Returns:
            Lista de floats representando el vector embedding
        """
        try:
            if not text or not text.strip():
                raise ValueError("El texto no puede estar vacío")
            
            # Generar embedding
            embedding = self.model.encode(text)
            
            # Convertir a lista de floats
            return embedding.tolist()
        
        except Exception as e:
            logger.error(f"Error al generar embedding: {e}")
            raise
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generar embeddings para múltiples textos
        
        Args:
            texts: Lista de textos a convertir en embeddings
            
        Returns:
            Lista de listas de floats representando los vectores embeddings
        """
        try:
            if not texts:
                raise ValueError("La lista de textos no puede estar vacía")
            
            # Filtrar textos vacíos
            valid_texts = [text.strip() for text in texts if text and text.strip()]
            
            if not valid_texts:
                raise ValueError("No hay textos válidos para procesar")
            
            # Generar embeddings
            embeddings = self.model.encode(valid_texts)
            
            # Convertir a lista de listas de floats
            return embeddings.tolist()
        
        except Exception as e:
            logger.error(f"Error al generar embeddings: {e}")
            raise
    
    def get_dimension(self) -> int:
        """
        Obtener la dimensión del modelo de embeddings
        
        Returns:
            Dimensión del vector de embeddings
        """
        if self.model is None:
            raise ValueError("El modelo no está cargado")
        
        return self.model.get_sentence_embedding_dimension()
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calcular similitud coseno entre dos embeddings
        
        Args:
            embedding1: Primer vector de embedding
            embedding2: Segundo vector de embedding
            
        Returns:
            Valor de similitud entre 0 y 1
        """
        try:
            # Convertir a arrays numpy
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calcular similitud coseno
            cosine_sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            
            return float(cosine_sim)
        
        except Exception as e:
            logger.error(f"Error al calcular similitud: {e}")
            raise 