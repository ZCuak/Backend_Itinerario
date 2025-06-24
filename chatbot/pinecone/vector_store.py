from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Any, Optional, Tuple
import logging
import uuid
from datetime import datetime

from .config import PineconeConfig
from .embeddings import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

class PineconeVectorStore:
    """Clase para manejar la base de datos vectorial de Pinecone"""
    
    def __init__(self):
        """Inicializar la conexión con Pinecone"""
        self.config = PineconeConfig()
        self.config.validate_config()
        
        # Inicializar cliente de Pinecone
        self.pc = Pinecone(api_key=self.config.PINECONE_API_KEY)
        
        # Inicializar modelo de embeddings
        self.embeddings = HuggingFaceEmbeddings(self.config.EMBEDDING_MODEL)
        
        # Obtener o crear el índice
        self.index = self._get_or_create_index()
        
        logger.info(f"PineconeVectorStore inicializado con índice: {self.config.INDEX_NAME}")
    
    def _get_or_create_index(self):
        """Obtener el índice existente o crear uno nuevo"""
        try:
            index_name = self.config.INDEX_NAME
            
            # Verificar si el índice existe
            if index_name not in self.pc.list_indexes().names():
                logger.info(f"Creando nuevo índice: {index_name}")
                
                # Crear el índice
                self.pc.create_index(
                    name=index_name,
                    dimension=self.embeddings.get_dimension(),
                    metric=self.config.METRIC,
                    spec=ServerlessSpec(
                        cloud='aws',
                        region=self.config.PINECONE_ENVIRONMENT
                    )
                )
                
                logger.info(f"Índice {index_name} creado exitosamente")
            
            # Conectar al índice
            return self.pc.Index(index_name)
        
        except Exception as e:
            logger.error(f"Error al obtener/crear índice: {e}")
            raise
    
    def add_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Agregar un texto a la base de datos vectorial
        
        Args:
            text: Texto a almacenar
            metadata: Metadatos adicionales
            
        Returns:
            ID del vector almacenado
        """
        try:
            # Generar embedding
            embedding = self.embeddings.get_embedding(text)
            
            # Generar ID único
            vector_id = str(uuid.uuid4())
            
            # Preparar metadatos
            if metadata is None:
                metadata = {}
            
            metadata.update({
                'text': text,
                'created_at': datetime.now().isoformat(),
                'model': self.config.EMBEDDING_MODEL
            })
            
            # Insertar en Pinecone
            self.index.upsert(
                vectors=[{
                    'id': vector_id,
                    'values': embedding,
                    'metadata': metadata
                }]
            )
            
            logger.info(f"Texto agregado con ID: {vector_id}")
            return vector_id
        
        except Exception as e:
            logger.error(f"Error al agregar texto: {e}")
            raise
    
    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        Agregar múltiples textos a la base de datos vectorial
        
        Args:
            texts: Lista de textos a almacenar
            metadatas: Lista de metadatos (opcional)
            
        Returns:
            Lista de IDs de los vectores almacenados
        """
        try:
            if not texts:
                return []
            
            # Generar embeddings
            embeddings = self.embeddings.get_embeddings(texts)
            
            # Preparar vectores
            vectors = []
            for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                vector_id = str(uuid.uuid4())
                
                # Preparar metadatos
                metadata = {}
                if metadatas and i < len(metadatas):
                    metadata.update(metadatas[i])
                
                metadata.update({
                    'text': text,
                    'created_at': datetime.now().isoformat(),
                    'model': self.config.EMBEDDING_MODEL
                })
                
                vectors.append({
                    'id': vector_id,
                    'values': embedding,
                    'metadata': metadata
                })
            
            # Insertar en Pinecone
            self.index.upsert(vectors=vectors)
            
            vector_ids = [v['id'] for v in vectors]
            logger.info(f"Agregados {len(vector_ids)} textos a la base de datos")
            
            return vector_ids
        
        except Exception as e:
            logger.error(f"Error al agregar textos: {e}")
            raise
    
    def search(self, query: str, top_k: Optional[int] = None, 
               filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Buscar textos similares en la base de datos
        
        Args:
            query: Texto de consulta
            top_k: Número máximo de resultados
            filter_dict: Filtros para la búsqueda
            
        Returns:
            Lista de resultados con score y metadatos
        """
        try:
            # Generar embedding de la consulta
            query_embedding = self.embeddings.get_embedding(query)
            
            # Configurar parámetros de búsqueda
            top_k = top_k or self.config.TOP_K
            
            # Realizar búsqueda
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                filter=filter_dict,
                include_metadata=True
            )
            
            # Procesar resultados
            processed_results = []
            for match in results.matches:
                if match.score >= self.config.SIMILARITY_THRESHOLD:
                    processed_results.append({
                        'id': match.id,
                        'score': match.score,
                        'metadata': match.metadata
                    })
            
            logger.info(f"Búsqueda completada: {len(processed_results)} resultados")
            return processed_results
        
        except Exception as e:
            logger.error(f"Error en la búsqueda: {e}")
            raise
    
    def delete_vector(self, vector_id: str) -> bool:
        """
        Eliminar un vector de la base de datos
        
        Args:
            vector_id: ID del vector a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            self.index.delete(ids=[vector_id])
            logger.info(f"Vector eliminado: {vector_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error al eliminar vector: {e}")
            return False
    
    def delete_vectors(self, vector_ids: List[str]) -> bool:
        """
        Eliminar múltiples vectores de la base de datos
        
        Args:
            vector_ids: Lista de IDs de vectores a eliminar
            
        Returns:
            True si se eliminaron correctamente
        """
        try:
            if vector_ids:
                self.index.delete(ids=vector_ids)
                logger.info(f"Eliminados {len(vector_ids)} vectores")
            return True
        
        except Exception as e:
            logger.error(f"Error al eliminar vectores: {e}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del índice
        
        Returns:
            Diccionario con estadísticas del índice
        """
        try:
            stats = self.index.describe_index_stats()
            return {
                'total_vector_count': stats.total_vector_count,
                'dimension': stats.dimension,
                'index_fullness': stats.index_fullness,
                'namespaces': stats.namespaces
            }
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            raise
    
    def clear_index(self) -> bool:
        """
        Limpiar todo el contenido del índice
        
        Returns:
            True si se limpió correctamente
        """
        try:
            # Obtener todos los vectores
            stats = self.index.describe_index_stats()
            total_vectors = stats.total_vector_count
            
            if total_vectors > 0:
                # Eliminar todos los vectores
                self.index.delete(delete_all=True)
                logger.info(f"Índice limpiado: {total_vectors} vectores eliminados")
            
            return True
        
        except Exception as e:
            logger.error(f"Error al limpiar índice: {e}")
            return False 