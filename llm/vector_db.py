"""
Sistema de vectorización que integra embeddings locales con Pinecone
"""

import logging
from typing import List, Dict, Any, Optional
from .pinecone_client import PineconeClient
from .embedder import get_embedder, LocalEmbedder

logger = logging.getLogger(__name__)

class VectorDatabase:
    """Sistema de base de datos vectorial integrado"""
    
    def __init__(self):
        self.pinecone_client = PineconeClient()
        self.embedder = get_embedder()
        
        # Verificar que las dimensiones coincidan
        if self.embedder.get_dimension() != self.pinecone_client.dimension:
            raise ValueError(
                f"Dimensiones no coinciden: Embedder={self.embedder.get_dimension()}, "
                f"Pinecone={self.pinecone_client.dimension}"
            )
    
    def create_index(self) -> bool:
        """Crea el índice de Pinecone"""
        return self.pinecone_client.create_index()
    
    def add_lugares(self, lugares_data: List[Dict[str, Any]]) -> bool:
        """
        Añade lugares a la base de datos vectorial
        
        Args:
            lugares_data: Lista de diccionarios con datos de lugares
            
        Returns:
            bool: True si se añadieron exitosamente
        """
        try:
            vectors = []
            
            for lugar in lugares_data:
                # Verificar que tenga palabras clave IA (preferido) o resumen IA
                palabras_clave_ia = lugar.get('palabras_clave_ia')
                resumen_ia = lugar.get('resumen_ia')
                
                if not palabras_clave_ia and not resumen_ia:
                    logger.warning(f"Lugar {lugar.get('id', 'N/A')} no tiene palabras clave ni resumen IA, saltando")
                    continue
                
                # Usar palabras clave si están disponibles, sino usar resumen
                texto_para_embedding = palabras_clave_ia if palabras_clave_ia else resumen_ia
                
                # Generar embedding del texto
                embedding = self.embedder.encode_text(texto_para_embedding)
                
                # Crear vector para Pinecone
                vector = {
                    'id': f"lugar_{lugar['id']}",
                    'values': embedding,
                    'metadata': {
                        'lugar_id': lugar['id'],
                        'nombre': lugar.get('nombre', ''),
                        'tipo_principal': lugar.get('tipo_principal', ''),
                        'tipos_adicionales': lugar.get('tipos_adicionales', []),
                        'rating': lugar.get('rating', 0),
                        'nivel_precios': lugar.get('nivel_precios', ''),
                        'direccion': lugar.get('direccion', ''),
                        'latitud': lugar.get('latitud', 0),
                        'longitud': lugar.get('longitud', 0),
                        'palabras_clave_ia': palabras_clave_ia or '',
                        'resumen_ia': resumen_ia[:500] if resumen_ia else '',  # Truncado para metadata
                        'total_ratings': lugar.get('total_ratings', 0)
                    }
                }
                
                vectors.append(vector)
            
            if not vectors:
                logger.warning("No hay vectores válidos para insertar")
                return False
            
            # Insertar en Pinecone
            success = self.pinecone_client.upsert_vectors(vectors)
            
            if success:
                logger.info(f"Se añadieron {len(vectors)} lugares a la base vectorial")
            
            return success
            
        except Exception as e:
            logger.error(f"Error al añadir lugares: {e}")
            raise
    
    def search_similar(self, 
                      query: str, 
                      top_k: int = 5,
                      filter_dict: Optional[Dict] = None) -> List[Dict]:
        """
        Busca lugares similares basado en una consulta
        
        Args:
            query: Consulta de texto
            top_k: Número máximo de resultados
            filter_dict: Filtros opcionales
            
        Returns:
            Lista de lugares similares con scores
        """
        try:
            # Generar embedding de la consulta
            query_embedding = self.embedder.encode_text(query)
            
            # Buscar en Pinecone
            results = self.pinecone_client.query_vectors(
                query_vector=query_embedding,
                top_k=top_k,
                filter_dict=filter_dict
            )
            
            # Formatear resultados
            formatted_results = []
            for result in results:
                formatted_result = {
                    'id': result.id,
                    'score': result.score,
                    'metadata': result.metadata,
                    'lugar_id': result.metadata.get('lugar_id'),
                    'nombre': result.metadata.get('nombre', ''),
                    'tipo_principal': result.metadata.get('tipo_principal', ''),
                    'tipos_adicionales': result.metadata.get('tipos_adicionales', []),
                    'rating': result.metadata.get('rating', 0),
                    'resumen_ia': result.metadata.get('resumen_ia', ''),
                    'palabras_clave_ia': result.metadata.get('palabras_clave_ia', '')
                }
                formatted_results.append(formatted_result)
            
            logger.info(f"Búsqueda completada: {len(formatted_results)} resultados")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            raise
    
    def search_by_tipo(self, 
                      query: str, 
                      tipo_principal: str,
                      top_k: int = 5) -> List[Dict]:
        """
        Busca lugares de un tipo específico considerando tanto tipo_principal como tipos_adicionales
        
        Args:
            query: Consulta de texto
            tipo_principal: Tipo de establecimiento
            top_k: Número máximo de resultados
            
        Returns:
            Lista de lugares del tipo especificado
        """
        try:
            # Generar embedding de la consulta
            query_embedding = self.embedder.encode_text(query)
            
            # Buscar en Pinecone sin filtros para obtener más candidatos
            # Luego filtrar por tipo en el código
            results = self.pinecone_client.query_vectors(
                query_vector=query_embedding,
                top_k=top_k * 3,  # Buscar más candidatos para filtrar después
                filter_dict=None
            )
            
            # Filtrar resultados por tipo (tipo_principal o tipos_adicionales)
            filtered_results = []
            for result in results:
                metadata = result.metadata
                tipo_principal_lugar = metadata.get('tipo_principal', '')
                tipos_adicionales_lugar = metadata.get('tipos_adicionales', [])
                
                # Verificar si el lugar tiene el tipo buscado
                if (tipo_principal_lugar == tipo_principal or 
                    tipo_principal in tipos_adicionales_lugar):
                    filtered_results.append(result)
                    
                    # Si ya tenemos suficientes resultados, parar
                    if len(filtered_results) >= top_k:
                        break
            
            # Formatear resultados filtrados
            formatted_results = []
            for result in filtered_results:
                formatted_result = {
                    'id': result.id,
                    'score': result.score,
                    'metadata': result.metadata,
                    'lugar_id': result.metadata.get('lugar_id'),
                    'nombre': result.metadata.get('nombre', ''),
                    'tipo_principal': result.metadata.get('tipo_principal', ''),
                    'tipos_adicionales': result.metadata.get('tipos_adicionales', []),
                    'rating': result.metadata.get('rating', 0),
                    'resumen_ia': result.metadata.get('resumen_ia', ''),
                    'palabras_clave_ia': result.metadata.get('palabras_clave_ia', '')
                }
                formatted_results.append(formatted_result)
            
            logger.info(f"Búsqueda por tipo '{tipo_principal}' completada: {len(formatted_results)} resultados")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error en búsqueda por tipo: {e}")
            raise
    
    def get_index_stats(self) -> Dict:
        """Obtiene estadísticas del índice"""
        return self.pinecone_client.get_index_stats()
    
    def delete_index(self) -> bool:
        """Elimina el índice"""
        return self.pinecone_client.delete_index()

# Instancia global
_vector_db_instance = None

def get_vector_db() -> VectorDatabase:
    """
    Obtiene la instancia global de la base de datos vectorial
    
    Returns:
        Instancia de VectorDatabase
    """
    global _vector_db_instance
    
    if _vector_db_instance is None:
        _vector_db_instance = VectorDatabase()
    
    return _vector_db_instance 