from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union, Dict, Any
import logging
import hashlib
from functools import lru_cache
import re

logger = logging.getLogger(__name__)

class HuggingFaceEmbeddings:
    """Clase para generar embeddings usando modelos de Hugging Face con chunking y cache"""
    
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2', 
                 max_tokens: int = 350, chunk_overlap: int = 50):
        """
        Inicializar el modelo de embeddings
        
        Args:
            model_name: Nombre del modelo de Hugging Face a usar
            max_tokens: Máximo número de tokens por chunk
            chunk_overlap: Número de tokens de solapamiento entre chunks
        """
        self.model_name = model_name
        self.model = None
        self.max_tokens = max_tokens
        self.chunk_overlap = chunk_overlap
        self.embedding_cache = {}
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
    
    def _count_tokens_approximate(self, text: str) -> int:
        """
        Contar tokens de forma aproximada (1 palabra ≈ 1.2-1.5 tokens)
        
        Args:
            text: Texto a contar
            
        Returns:
            Número aproximado de tokens
        """
        try:
            # Dividir por espacios y contar palabras
            words = text.split()
            # Factor de conversión aproximado
            return int(len(words) * 1.3)
        except Exception as e:
            logger.error(f"Error al contar tokens: {e}")
            return len(text.split())
    
    def _split_text_into_chunks(self, text: str) -> List[str]:
        """
        Dividir texto en chunks respetando límites de tokens
        
        Args:
            text: Texto a dividir
            
        Returns:
            Lista de chunks de texto
        """
        try:
            if not text or not text.strip():
                return [""]
            
            # Si el texto es corto, no necesita chunking
            estimated_tokens = self._count_tokens_approximate(text)
            if estimated_tokens <= self.max_tokens:
                return [text]
            
            # Dividir por oraciones primero
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            chunks = []
            current_chunk = ""
            current_tokens = 0
            
            for sentence in sentences:
                sentence_tokens = self._count_tokens_approximate(sentence)
                
                # Si agregar esta oración excede el límite
                if current_tokens + sentence_tokens > self.max_tokens and current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                    current_tokens = sentence_tokens
                else:
                    if current_chunk:
                        current_chunk += ". " + sentence
                    else:
                        current_chunk = sentence
                    current_tokens += sentence_tokens
            
            # Agregar el último chunk
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            # Si no se pudo dividir por oraciones, dividir por palabras
            if not chunks:
                words = text.split()
                chunk_size = int(self.max_tokens / 1.3)  # Convertir tokens a palabras
                
                for i in range(0, len(words), chunk_size - self.chunk_overlap):
                    chunk_words = words[i:i + chunk_size]
                    chunks.append(" ".join(chunk_words))
            
            logger.info(f"Texto dividido en {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error al dividir texto en chunks: {e}")
            return [text]
    
    def _get_cached_embedding(self, text: str) -> Union[List[float], None]:
        """
        Obtener embedding del cache si existe
        
        Args:
            text: Texto para buscar en cache
            
        Returns:
            Embedding cacheado o None si no existe
        """
        try:
            # Generar hash del texto
            text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
            return self.embedding_cache.get(text_hash)
        except Exception as e:
            logger.error(f"Error al obtener embedding cacheado: {e}")
            return None
    
    def _cache_embedding(self, text: str, embedding: List[float]):
        """
        Guardar embedding en cache
        
        Args:
            text: Texto original
            embedding: Embedding a cachear
        """
        try:
            # Generar hash del texto
            text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
            self.embedding_cache[text_hash] = embedding
            
            # Limpiar cache si es muy grande (más de 1000 entradas)
            if len(self.embedding_cache) > 1000:
                # Mantener solo las últimas 500 entradas
                keys_to_keep = list(self.embedding_cache.keys())[-500:]
                self.embedding_cache = {k: self.embedding_cache[k] for k in keys_to_keep}
                
        except Exception as e:
            logger.error(f"Error al cachear embedding: {e}")
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Generar embedding para un texto (con chunking y cache)
        
        Args:
            text: Texto a convertir en embedding
            
        Returns:
            Lista de floats representando el vector embedding
        """
        try:
            if not text or not text.strip():
                raise ValueError("El texto no puede estar vacío")
            
            # Verificar cache primero
            cached_embedding = self._get_cached_embedding(text)
            if cached_embedding is not None:
                logger.debug("Embedding obtenido del cache")
                return cached_embedding
            
            # Dividir texto en chunks si es necesario
            chunks = self._split_text_into_chunks(text)
            
            if len(chunks) == 1:
                # Texto corto, generar embedding normal
                embedding = self.model.encode(text)
                embedding_list = embedding.tolist()
                
                # Cachear resultado
                self._cache_embedding(text, embedding_list)
                return embedding_list
            else:
                # Texto largo, usar chunking
                logger.info(f"Generando embedding con chunking para texto de {len(chunks)} chunks")
                return self._get_chunked_embedding(chunks)
        
        except Exception as e:
            logger.error(f"Error al generar embedding: {e}")
            raise
    
    def _get_chunked_embedding(self, chunks: List[str]) -> List[float]:
        """
        Generar embedding combinado para múltiples chunks
        
        Args:
            chunks: Lista de chunks de texto
            
        Returns:
            Embedding combinado
        """
        try:
            if not chunks:
                raise ValueError("La lista de chunks no puede estar vacía")
            
            # Generar embeddings para cada chunk
            chunk_embeddings = []
            for i, chunk in enumerate(chunks):
                logger.debug(f"Procesando chunk {i+1}/{len(chunks)}: {len(chunk)} caracteres")
                
                # Verificar cache para este chunk
                cached_chunk_embedding = self._get_cached_embedding(chunk)
                if cached_chunk_embedding is not None:
                    chunk_embeddings.append(cached_chunk_embedding)
                else:
                    # Generar embedding para este chunk
                    chunk_embedding = self.model.encode(chunk)
                    chunk_embedding_list = chunk_embedding.tolist()
                    
                    # Cachear este chunk
                    self._cache_embedding(chunk, chunk_embedding_list)
                    chunk_embeddings.append(chunk_embedding_list)
            
            # Combinar embeddings (promedio ponderado)
            combined_embedding = self._combine_chunk_embeddings(chunk_embeddings)
            
            return combined_embedding
            
        except Exception as e:
            logger.error(f"Error al generar embedding con chunking: {e}")
            raise
    
    def _combine_chunk_embeddings(self, chunk_embeddings: List[List[float]]) -> List[float]:
        """
        Combinar múltiples embeddings de chunks en uno solo
        
        Args:
            chunk_embeddings: Lista de embeddings de chunks
            
        Returns:
            Embedding combinado
        """
        try:
            if not chunk_embeddings:
                raise ValueError("La lista de embeddings no puede estar vacía")
            
            if len(chunk_embeddings) == 1:
                return chunk_embeddings[0]
            
            # Convertir a arrays numpy
            embeddings_array = np.array(chunk_embeddings)
            
            # Ponderación: dar más peso a los primeros chunks (información más importante)
            weights = np.linspace(1.0, 0.5, len(chunk_embeddings))
            weights = weights / np.sum(weights)  # Normalizar pesos
            
            # Calcular promedio ponderado
            weighted_embedding = np.average(embeddings_array, axis=0, weights=weights)
            
            # Normalizar el vector resultante
            norm = np.linalg.norm(weighted_embedding)
            if norm > 0:
                weighted_embedding = weighted_embedding / norm
            
            return weighted_embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error al combinar embeddings: {e}")
            # Fallback: promedio simple
            embeddings_array = np.array(chunk_embeddings)
            return np.mean(embeddings_array, axis=0).tolist()
    
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
            
            # Generar embeddings (cada uno puede usar chunking si es necesario)
            embeddings = []
            for text in valid_texts:
                embedding = self.get_embedding(text)
                embeddings.append(embedding)
            
            return embeddings
        
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
    
    def clear_cache(self):
        """Limpiar cache de embeddings"""
        try:
            self.embedding_cache.clear()
            logger.info("Cache de embeddings limpiado")
        except Exception as e:
            logger.error(f"Error al limpiar cache: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del cache
        
        Returns:
            Diccionario con estadísticas del cache
        """
        try:
            return {
                'cache_size': len(self.embedding_cache),
                'cache_keys': list(self.embedding_cache.keys())[:10],  # Primeros 10
                'model_name': self.model_name,
                'max_tokens': self.max_tokens,
                'chunk_overlap': self.chunk_overlap
            }
        except Exception as e:
            logger.error(f"Error al obtener estadísticas del cache: {e}")
            return {} 