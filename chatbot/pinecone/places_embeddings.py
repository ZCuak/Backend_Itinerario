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
    
    def generate_text_for_embedding(self, lugar: 'LugarGooglePlaces') -> str:
        """
        Generar texto optimizado para embeddings
        Genérico para TODOS los tipos de establecimientos
        
        Args:
            lugar: Instancia del modelo LugarGooglePlaces
            
        Returns:
            Texto optimizado para generar embeddings
        """
        try:
            # Obtener características extraídas
            caracteristicas = lugar.caracteristicas_extraidas or {}
            
            # Construir texto optimizado
            text_parts = []
            
            # 1. Nombre del lugar (máximo peso)
            if lugar.nombre:
                text_parts.append(f"nombre: {lugar.nombre}")
            
            # 2. Tipo de establecimiento (solo tipo_principal)
            tipo = getattr(lugar, 'tipo_principal', None)
            if tipo:
                text_parts.append(f"tipo: {tipo}")
            
            # 3. Características extraídas (máximo peso)
            if caracteristicas:
                # Amenidades
                if 'amenidades' in caracteristicas and caracteristicas['amenidades']:
                    amenidades_text = ' '.join(caracteristicas['amenidades'])
                    text_parts.append(f"amenidad {amenidades_text}")
                
                # Servicios
                if 'servicios' in caracteristicas and caracteristicas['servicios']:
                    servicios_text = ' '.join(caracteristicas['servicios'])
                    text_parts.append(f"servicio {servicios_text}")
                
                # Tipo de experiencia
                if 'tipo_experiencia' in caracteristicas and caracteristicas['tipo_experiencia']:
                    experiencia_text = ' '.join(caracteristicas['tipo_experiencia'])
                    text_parts.append(f"experiencia {experiencia_text}")
                
                # Nivel de lujo
                if 'nivel_lujo' in caracteristicas and caracteristicas['nivel_lujo']:
                    lujo_text = ' '.join(caracteristicas['nivel_lujo'])
                    text_parts.append(f"nivel {lujo_text}")
                
                # Público objetivo
                if 'publico_objetivo' in caracteristicas and caracteristicas['publico_objetivo']:
                    publico_text = ' '.join(caracteristicas['publico_objetivo'])
                    text_parts.append(f"publico {publico_text}")
                
                # Palabras clave (máximo peso)
                if 'palabras_clave' in caracteristicas and caracteristicas['palabras_clave']:
                    palabras_text = ' '.join(caracteristicas['palabras_clave'])
                    text_parts.append(f"palabra clave {palabras_text}")
            
            # 4. Resumen IA (peso medio)
            if lugar.resumen_ia:
                # Limitar el resumen para evitar que domine el embedding
                resumen_short = lugar.resumen_ia[:200] if len(lugar.resumen_ia) > 200 else lugar.resumen_ia
                text_parts.append(f"descripcion: {resumen_short}")
            
            # 5. Dirección (peso bajo)
            if lugar.direccion:
                text_parts.append(f"ubicacion: {lugar.direccion}")
            
            # 6. Nivel de precios (peso bajo)
            if hasattr(lugar, 'nivel_precios') and lugar.nivel_precios:
                text_parts.append(f"precio: {lugar.nivel_precios}")
            
            # Combinar todas las partes
            final_text = " ".join(text_parts)
            
            # Limpiar espacios extra y normalizar
            final_text = " ".join(final_text.split())
            
            return final_text
            
        except Exception as e:
            logger.error(f"Error al generar texto para embedding: {e}")
            # Fallback: usar solo nombre y resumen
            fallback_parts = []
            if lugar.nombre:
                fallback_parts.append(lugar.nombre)
            if lugar.resumen_ia:
                fallback_parts.append(lugar.resumen_ia[:300])
            return " ".join(fallback_parts) if fallback_parts else "lugar"

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
            place_text = self.generate_text_for_embedding(lugar)
            
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
                text = self.generate_text_for_embedding(lugar)
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
                    'text': self.generate_text_for_embedding(lugares[i])
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