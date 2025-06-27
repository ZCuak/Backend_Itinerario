"""
Cliente Pinecone para el sistema de embeddings
Configurado para 768 dimensiones (BAAI/bge-base-en-v1.5)
"""

import os
from typing import List, Dict, Any, Optional
from pinecone import Pinecone
from dotenv import load_dotenv
import logging

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)

class PineconeClient:
    """Cliente para manejar operaciones con Pinecone"""
    
    def __init__(self):
        self.api_key = os.getenv('PINECONE_API_KEY')
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY no encontrada en variables de entorno")
        
        self.pc = Pinecone(api_key=self.api_key)
        self.index_name = "chatbot-lugares-index"
        self.dimension = 768  # Para BAAI/bge-base-en-v1.5
        
    def create_index(self) -> bool:
        """
        Crea el índice de Pinecone si no existe
        
        Returns:
            bool: True si se creó exitosamente, False si ya existe
        """
        try:
            # Verificar si el índice ya existe
            if self.pc.has_index(self.index_name):
                logger.info(f"Índice '{self.index_name}' ya existe")
                return False
            
            # Crear nuevo índice usando la API tradicional
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric="cosine",
                spec={
                    "serverless": {
                        "cloud": "aws",
                        "region": "us-east-1"
                    }
                }
            )
            
            logger.info(f"Índice '{self.index_name}' creado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error al crear índice: {e}")
            raise
    
    def get_index(self):
        """Obtiene el índice de Pinecone"""
        try:
            return self.pc.Index(self.index_name)
        except Exception as e:
            logger.error(f"Error al obtener índice: {e}")
            raise
    
    def upsert_vectors(self, vectors: List[Dict[str, Any]]) -> bool:
        """
        Inserta o actualiza vectores en Pinecone
        
        Args:
            vectors: Lista de diccionarios con 'id', 'values', 'metadata'
            
        Returns:
            bool: True si se insertaron exitosamente
        """
        try:
            index = self.get_index()
            
            # Verificar que los vectores tengan la dimensión correcta
            for vector in vectors:
                if len(vector['values']) != self.dimension:
                    raise ValueError(f"Vector {vector['id']} tiene dimensión {len(vector['values'])}, esperada: {self.dimension}")
            
            # Formatear para Pinecone: (id, values, metadata)
            pinecone_vectors = [
                (v['id'], v['values'], v['metadata']) for v in vectors
            ]
            
            # Insertar vectores en lotes
            batch_size = 100
            for i in range(0, len(pinecone_vectors), batch_size):
                batch = pinecone_vectors[i:i + batch_size]
                index.upsert(vectors=batch)
                logger.info(f"Insertados {len(batch)} vectores (lote {i//batch_size + 1})")
            
            logger.info(f"Total de {len(vectors)} vectores insertados exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error al insertar vectores: {e}")
            raise
    
    def query_vectors(self, 
                     query_vector: List[float], 
                     top_k: int = 5,
                     filter_dict: Optional[Dict] = None) -> List[Dict]:
        """
        Consulta vectores similares
        
        Args:
            query_vector: Vector de consulta
            top_k: Número máximo de resultados
            filter_dict: Filtros opcionales (ej: {"tipo_principal": "hotel"})
            
        Returns:
            Lista de resultados con 'id', 'score', 'metadata'
        """
        try:
            index = self.get_index()
            
            # Verificar dimensión del vector de consulta
            if len(query_vector) != self.dimension:
                raise ValueError(f"Vector de consulta tiene dimensión {len(query_vector)}, esperada: {self.dimension}")
            
            # Realizar consulta
            results = index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            return results.matches
            
        except Exception as e:
            logger.error(f"Error al consultar vectores: {e}")
            raise
    
    def delete_index(self) -> bool:
        """
        Elimina el índice de Pinecone
        
        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            self.pc.delete_index(self.index_name)
            logger.info(f"Índice '{self.index_name}' eliminado exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error al eliminar índice: {e}")
            raise
    
    def get_index_stats(self) -> Dict:
        """
        Obtiene estadísticas del índice
        
        Returns:
            Diccionario con estadísticas del índice
        """
        try:
            index = self.get_index()
            return index.describe_index_stats()
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            raise 