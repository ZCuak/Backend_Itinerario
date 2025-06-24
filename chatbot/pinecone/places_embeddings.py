from typing import List, Dict, Any, Optional
import logging
import json
from django.db import models
from .embeddings import HuggingFaceEmbeddings
from ..models import LugarGooglePlaces
import re
import unicodedata

logger = logging.getLogger(__name__)

class PlacesEmbeddingGenerator:
    """Generador de embeddings específico para lugares de Google Places"""
    
    def __init__(self, model_name: str = 'sentence-transformers/all-mpnet-base-v2'):
        """
        Inicializar el generador de embeddings para lugares
        
        Args:
            model_name: Nombre del modelo de Hugging Face a usar
        """
        self.embeddings = HuggingFaceEmbeddings(model_name)
        logger.info("PlacesEmbeddingGenerator inicializado")
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalizar texto para embedding
        
        Args:
            text: Texto a normalizar
            
        Returns:
            Texto normalizado
        """
        try:
            if not text:
                return ""
            
            # Decodificar caracteres Unicode si es necesario
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='ignore')
            
            # Normalizar espacios y caracteres especiales
            text = unicodedata.normalize('NFD', text)
            
            # Convertir a minúsculas
            text = text.lower()
            
            # Limpiar espacios extra
            text = ' '.join(text.split())
            
            return text
            
        except Exception as e:
            print(f"❌ Error al normalizar texto: {e}")
            return text if text else ""
    
    def generate_place_text_for_embedding(self, lugar: LugarGooglePlaces) -> str:
        """
        Generar texto optimizado para embedding usando solo el resumen de IA
        
        Args:
            lugar: Instancia de LugarGooglePlaces
            
        Returns:
            Texto formateado para generar embedding
        """
        try:
            # Usar solo el resumen de IA que ya contiene toda la información relevante
            if lugar.resumen_ia:
                # Normalizar el texto final
                normalized_text = self._normalize_text(lugar.resumen_ia)
                print(f"📝 Texto para embedding (ID {lugar.id}): {normalized_text[:100]}...")
                return normalized_text
            else:
                # Fallback: usar nombre y tipo si no hay resumen
                fallback_text = f"establecimiento {lugar.nombre} tipo {lugar.tipo_principal}"
                print(f"⚠️ Sin resumen IA para lugar {lugar.id}, usando fallback: {fallback_text}")
                return fallback_text
        
        except Exception as e:
            print(f"❌ Error al generar texto para lugar {lugar.id}: {e}")
            # Fallback: usar solo el nombre
            return f"establecimiento {lugar.nombre}" if lugar.nombre else "establecimiento sin nombre"
    
    def get_place_embedding(self, lugar: LugarGooglePlaces) -> List[float]:
        """
        Generar embedding para un lugar específico
        
        Args:
            lugar: Instancia de LugarGooglePlaces
            
        Returns:
            Lista de floats representando el vector embedding
        """
        try:
            # Generar texto optimizado para el lugar
            place_text = self.generate_place_text_for_embedding(lugar)
            
            # Generar embedding
            embedding = self.embeddings.get_embedding(place_text)
            
            logger.debug(f"Embedding generado para lugar {lugar.id}: {lugar.nombre}")
            return embedding
        
        except Exception as e:
            logger.error(f"Error al generar embedding para lugar {lugar.id}: {e}")
            raise
    
    def get_places_embeddings(self, lugares: List[LugarGooglePlaces]) -> List[List[float]]:
        """
        Generar embeddings para múltiples lugares
        
        Args:
            lugares: Lista de instancias de LugarGooglePlaces
            
        Returns:
            Lista de listas de floats representando los vectores embeddings
        """
        try:
            if not lugares:
                return []
            
            # Generar textos para todos los lugares
            place_texts = []
            for lugar in lugares:
                text = self.generate_place_text_for_embedding(lugar)
                place_texts.append(text)
            
            # Generar embeddings en lote
            embeddings = self.embeddings.get_embeddings(place_texts)
            
            logger.info(f"Embeddings generados para {len(lugares)} lugares")
            return embeddings
        
        except Exception as e:
            logger.error(f"Error al generar embeddings para lugares: {e}")
            raise
    
    def search_similar_places(self, query: str, lugares: List[LugarGooglePlaces], 
                            top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Buscar lugares similares basado en una consulta
        
        Args:
            query: Consulta de búsqueda
            lugares: Lista de lugares a buscar
            top_k: Número máximo de resultados
            
        Returns:
            Lista de resultados con lugar y score de similitud
        """
        try:
            if not lugares:
                return []
            
            # Generar embedding de la consulta
            query_embedding = self.embeddings.get_embedding(query)
            
            # Generar embeddings de los lugares
            place_embeddings = self.get_places_embeddings(lugares)
            
            # Calcular similitudes
            similarities = []
            for i, place_embedding in enumerate(place_embeddings):
                similarity = self.embeddings.similarity(query_embedding, place_embedding)
                similarities.append({
                    'lugar': lugares[i],
                    'score': similarity,
                    'text': self.generate_place_text_for_embedding(lugares[i])
                })
            
            # Ordenar por similitud (mayor a menor)
            similarities.sort(key=lambda x: x['score'], reverse=True)
            
            # Retornar top_k resultados
            return similarities[:top_k]
        
        except Exception as e:
            logger.error(f"Error en búsqueda de lugares similares: {e}")
            raise
    
    def find_places_by_features(self, features: List[str], lugares: List[LugarGooglePlaces], 
                               top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Buscar lugares que tengan características específicas
        
        Args:
            features: Lista de características a buscar (ej: ['gimnasio', 'piscina'])
            lugares: Lista de lugares a buscar
            top_k: Número máximo de resultados
            
        Returns:
            Lista de lugares que coinciden con las características
        """
        try:
            if not features or not lugares:
                return []
            
            # Crear consulta combinando características
            query = f"Lugar con {' y '.join(features)}"
            
            # Buscar lugares similares
            results = self.search_similar_places(query, lugares, top_k)
            
            # Filtrar por umbral de similitud
            threshold = 0.3  # Umbral más bajo para características específicas
            filtered_results = [r for r in results if r['score'] >= threshold]
            
            logger.info(f"Encontrados {len(filtered_results)} lugares con características: {features}")
            return filtered_results
        
        except Exception as e:
            logger.error(f"Error al buscar lugares por características: {e}")
            raise
    
    def find_hotels_with_amenities(self, amenities: List[str], lugares: List[LugarGooglePlaces], 
                                  top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Buscar hoteles con amenidades específicas
        
        Args:
            amenities: Lista de amenidades (ej: ['gimnasio', 'piscina', 'spa'])
            lugares: Lista de lugares a buscar
            top_k: Número máximo de resultados
            
        Returns:
            Lista de hoteles que tienen las amenidades
        """
        try:
            # Filtrar solo hoteles
            hoteles = [lugar for lugar in lugares if 'hotel' in lugar.tipo_principal.lower() 
                      or 'lodging' in lugar.tipo_principal.lower()]
            
            if not hoteles:
                logger.warning("No se encontraron hoteles en la lista de lugares")
                return []
            
            # Buscar hoteles con las amenidades
            query = f"Hotel con {' y '.join(amenities)}"
            results = self.search_similar_places(query, hoteles, top_k)
            
            # Filtrar por umbral de similitud
            threshold = 0.4  # Umbral específico para hoteles
            filtered_results = [r for r in results if r['score'] >= threshold]
            
            logger.info(f"Encontrados {len(filtered_results)} hoteles con amenidades: {amenities}")
            return filtered_results
        
        except Exception as e:
            logger.error(f"Error al buscar hoteles con amenidades: {e}")
            raise
    
    def get_place_metadata(self, lugar: LugarGooglePlaces) -> Dict[str, Any]:
        """
        Obtener metadatos estructurados de un lugar
        
        Args:
            lugar: Instancia de LugarGooglePlaces
            
        Returns:
            Diccionario con metadatos del lugar
        """
        try:
            metadata = {
                'id': lugar.id,
                'nombre': lugar.nombre or "",
                'tipo_principal': lugar.tipo_principal or "",
                'tipos_adicionales': lugar.tipos_adicionales or [],
                'direccion': lugar.direccion or "",
                'latitud': float(lugar.latitud) if lugar.latitud else 0.0,
                'longitud': float(lugar.longitud) if lugar.longitud else 0.0,
                'rating': float(lugar.rating) if lugar.rating else 0.0,
                'total_ratings': int(lugar.total_ratings) if lugar.total_ratings else 0,
                'website': lugar.website or "",
                'telefono': lugar.telefono or "",
                'estado_negocio': lugar.estado_negocio or "",
                'resumen_ia': lugar.resumen_ia or "",
                'descripcion': lugar.descripcion or "",
                'created_at': lugar.created_at.isoformat() if lugar.created_at else "",
                'updated_at': lugar.updated_at.isoformat() if lugar.updated_at else ""
            }
            
            # Agregar información detallada del nivel de precios
            if lugar.nivel_precios:
                metadata.update({
                    'nivel_precios__descripcion': lugar.nivel_precios.descripcion or "",
                    'nivel_precios__nivel': lugar.nivel_precios.nivel or 0,
                    'nivel_precios__rango_inferior': float(lugar.nivel_precios.rango_inferior) if lugar.nivel_precios.rango_inferior else 0.0,
                    'nivel_precios__rango_superior': float(lugar.nivel_precios.rango_superior) if lugar.nivel_precios.rango_superior else 0.0,
                    'nivel_precios__moneda': lugar.nivel_precios.moneda or "",
                    'nivel_precios__is_active': bool(lugar.nivel_precios.is_active) if lugar.nivel_precios.is_active is not None else False
                })
            else:
                metadata.update({
                    'nivel_precios__descripcion': "",
                    'nivel_precios__nivel': 0,
                    'nivel_precios__rango_inferior': 0.0,
                    'nivel_precios__rango_superior': 0.0,
                    'nivel_precios__moneda': "",
                    'nivel_precios__is_active': False
                })
            
            return metadata
        
        except Exception as e:
            logger.error(f"Error al obtener metadatos del lugar {lugar.id}: {e}")
            return {} 