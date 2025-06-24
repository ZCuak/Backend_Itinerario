from typing import List, Dict, Any, Optional
import logging
import json
from django.db import models
from .embeddings import HuggingFaceEmbeddings
from ..models import LugarGooglePlaces

logger = logging.getLogger(__name__)

class PlacesEmbeddingGenerator:
    """Generador de embeddings específico para lugares de Google Places"""
    
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'):
        """
        Inicializar el generador de embeddings para lugares
        
        Args:
            model_name: Nombre del modelo de Hugging Face a usar
        """
        self.embeddings = HuggingFaceEmbeddings(model_name)
        logger.info("PlacesEmbeddingGenerator inicializado")
    
    def generate_place_text_for_embedding(self, lugar: LugarGooglePlaces) -> str:
        """
        Generar texto optimizado para embedding que incluya toda la información relevante del lugar
        
        Args:
            lugar: Instancia de LugarGooglePlaces
            
        Returns:
            Texto formateado para generar embedding
        """
        try:
            text_parts = []
            
            # 1. Nombre del lugar
            if lugar.nombre:
                text_parts.append(f"Lugar: {lugar.nombre}")
            
            # 2. Tipo principal y adicionales
            if lugar.tipo_principal:
                text_parts.append(f"Tipo principal: {lugar.tipo_principal}")
            
            if lugar.tipos_adicionales:
                tipos_text = ", ".join(lugar.tipos_adicionales[:5])  # Limitar a 5 tipos
                text_parts.append(f"Tipos adicionales: {tipos_text}")
            
            # 3. Categoría
            if lugar.categoria:
                text_parts.append(f"Categoría: {lugar.categoria}")
            
            # 4. Resumen de IA (contiene características importantes)
            if lugar.resumen_ia:
                text_parts.append(f"Descripción detallada: {lugar.resumen_ia}")
            
            # 5. Descripción general
            if lugar.descripcion:
                text_parts.append(f"Información: {lugar.descripcion}")
            
                # 6. Nivel de precios (información mejorada)
            if lugar.nivel_precios:
                precio_info = self._format_precio_info(lugar.nivel_precios)
                if precio_info:
                    text_parts.append(f"Precios: {precio_info}")
            
            # 7. Calificación
            if lugar.rating > 0:
                text_parts.append(f"Calificación: {lugar.rating}/5 estrellas")
            
            # 8. Horarios (información importante para búsquedas)
            if lugar.horarios:
                horarios_text = self._format_horarios(lugar.horarios)
                if horarios_text:
                    text_parts.append(f"Horarios: {horarios_text}")
            
            # 9. Estado del negocio
            if lugar.estado_negocio:
                text_parts.append(f"Estado: {lugar.estado_negocio}")
            
            # 10. Dirección (para contexto geográfico)
            if lugar.direccion:
                text_parts.append(f"Ubicación: {lugar.direccion}")
            
            # Unir todas las partes
            combined_text = ". ".join(text_parts)
            
            return combined_text
        
        except Exception as e:
            logger.error(f"Error al generar texto para lugar {lugar.id}: {e}")
            # Fallback: usar solo el nombre
            return f"Lugar: {lugar.nombre}" if lugar.nombre else "Lugar sin nombre"
    
    def _format_horarios(self, horarios: list) -> str:
        """
        Formatear horarios para incluir en el texto de embedding
        
        Args:
            horarios: Lista de horarios en formato JSON
            
        Returns:
            Texto formateado de horarios
        """
        try:
            if not horarios:
                return ""
            
            # Extraer información relevante de horarios
            horarios_info = []
            
            for horario in horarios:
                if isinstance(horario, dict):
                    # Información de días abiertos
                    if 'open' in horario:
                        open_info = horario['open']
                        if isinstance(open_info, list) and len(open_info) > 0:
                            # Contar días abiertos
                            dias_abiertos = len(open_info)
                            horarios_info.append(f"Abierto {dias_abiertos} días a la semana")
                    
                    # Información de horario específico
                    if 'weekday_text' in horario:
                        weekday_text = horario['weekday_text']
                        if isinstance(weekday_text, list) and len(weekday_text) > 0:
                            # Tomar algunos ejemplos de horarios
                            ejemplos = weekday_text[:3]  # Primeros 3 días
                            horarios_info.append(f"Horarios: {', '.join(ejemplos)}")
                    
                    # Información de siempre abierto
                    if horario.get('always_open', False):
                        horarios_info.append("Siempre abierto")
            
            return " | ".join(horarios_info) if horarios_info else ""
        
        except Exception as e:
            logger.error(f"Error al formatear horarios: {e}")
            return ""
    
    def _format_precio_info(self, nivel_precio) -> str:
        """
        Formatear información de precios para incluir en el texto de embedding
        
        Args:
            nivel_precio: Instancia de NivelPrecio
            
        Returns:
            Texto formateado de información de precios
        """
        try:
            if not nivel_precio:
                return ""
            
            precio_info = []
            
            # Agregar descripción del nivel
            if nivel_precio.descripcion:
                precio_info.append(nivel_precio.descripcion)
            
            # Agregar información del rango de precios si está disponible
            if nivel_precio.rango_inferior and nivel_precio.rango_superior:
                rango_text = f"Rango: {nivel_precio.rango_inferior} - {nivel_precio.rango_superior} {nivel_precio.moneda}"
                precio_info.append(rango_text)
            elif nivel_precio.rango_inferior:
                rango_text = f"Desde: {nivel_precio.rango_inferior} {nivel_precio.moneda}"
                precio_info.append(rango_text)
            elif nivel_precio.rango_superior:
                rango_text = f"Hasta: {nivel_precio.rango_superior} {nivel_precio.moneda}"
                precio_info.append(rango_text)
            
            # Agregar información del nivel numérico
            nivel_text = f"Nivel {nivel_precio.nivel}/4"
            precio_info.append(nivel_text)
            
            # Agregar categorización de precio
            if nivel_precio.nivel == 0:
                precio_info.append("Gratis")
            elif nivel_precio.nivel == 1:
                precio_info.append("Muy económico")
            elif nivel_precio.nivel == 2:
                precio_info.append("Económico")
            elif nivel_precio.nivel == 3:
                precio_info.append("Moderado")
            elif nivel_precio.nivel == 4:
                precio_info.append("Caros")
            
            return " | ".join(precio_info)
        
        except Exception as e:
            logger.error(f"Error al formatear información de precios: {e}")
            return nivel_precio.descripcion if nivel_precio.descripcion else ""
    
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
                'categoria': lugar.categoria or "",
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