from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Any, Optional, Tuple
import logging
import uuid
from datetime import datetime
import json

from .config import PineconeConfig
from .places_embeddings import PlacesEmbeddingGenerator
from ..models import LugarGooglePlaces

logger = logging.getLogger(__name__)

class PlacesVectorStore:
    """Gestor de base de datos vectorial específico para lugares de Google Places"""
    
    def __init__(self, index_name: Optional[str] = None):
        """
        Inicializar el gestor de lugares vectoriales
        
        Args:
            index_name: Nombre del índice (opcional, usa el de configuración por defecto)
        """
        self.config = PineconeConfig()
        self.config.validate_config()
        
        # Usar índice específico para lugares si se proporciona
        if index_name:
            self.index_name = index_name
        else:
            self.index_name = f"{self.config.INDEX_NAME}-places"
        
        # Inicializar cliente de Pinecone
        self.pc = Pinecone(api_key=self.config.PINECONE_API_KEY)
        
        # Inicializar generador de embeddings para lugares
        self.embedding_generator = PlacesEmbeddingGenerator(self.config.EMBEDDING_MODEL)
        
        # Obtener o crear el índice
        self.index = self._get_or_create_index()
        
        logger.info(f"PlacesVectorStore inicializado con índice: {self.index_name}")
    
    def _get_or_create_index(self):
        """Obtener el índice existente o crear uno nuevo para lugares"""
        try:
            # Verificar si el índice existe
            if self.index_name not in self.pc.list_indexes().names():
                logger.info(f"Creando nuevo índice para lugares: {self.index_name}")
                
                # Obtener dimensión del modelo de embeddings
                dimension = self.embedding_generator.embeddings.get_dimension()
                
                # Crear el índice
                self.pc.create_index(
                    name=self.index_name,
                    dimension=dimension,
                    metric=self.config.METRIC,
                    spec=ServerlessSpec(
                        cloud='aws',
                        region=self.config.PINECONE_ENVIRONMENT
                    )
                )
                
                logger.info(f"Índice {self.index_name} creado exitosamente")
            
            # Conectar al índice
            return self.pc.Index(self.index_name)
        
        except Exception as e:
            logger.error(f"Error al obtener/crear índice de lugares: {e}")
            raise
    
    def add_place(self, lugar: LugarGooglePlaces) -> str:
        """
        Agregar un lugar a la base de datos vectorial
        
        Args:
            lugar: Instancia de LugarGooglePlaces
            
        Returns:
            ID del vector almacenado
        """
        try:
            # Generar embedding del lugar
            embedding = self.embedding_generator.get_place_embedding(lugar)
            
            # Generar ID único
            vector_id = f"place_{lugar.id}_{str(uuid.uuid4())[:8]}"
            
            # Obtener metadatos del lugar
            metadata = self.embedding_generator.get_place_metadata(lugar)
            metadata.update({
                'vector_type': 'place',
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
            
            logger.info(f"Lugar agregado con ID: {vector_id} - {lugar.nombre}")
            return vector_id
        
        except Exception as e:
            logger.error(f"Error al agregar lugar: {e}")
            raise
    
    def add_places(self, lugares: List[LugarGooglePlaces]) -> List[str]:
        """
        Agregar múltiples lugares a la base de datos vectorial
        
        Args:
            lugares: Lista de instancias de LugarGooglePlaces
            
        Returns:
            Lista de IDs de los vectores almacenados
        """
        try:
            if not lugares:
                return []
            
            # Generar embeddings de los lugares
            embeddings = self.embedding_generator.get_places_embeddings(lugares)
            
            # Preparar vectores
            vectors = []
            for i, (lugar, embedding) in enumerate(zip(lugares, embeddings)):
                vector_id = f"place_{lugar.id}_{str(uuid.uuid4())[:8]}"
                
                # Obtener metadatos del lugar
                metadata = self.embedding_generator.get_place_metadata(lugar)
                metadata.update({
                    'vector_type': 'place',
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
            logger.info(f"Agregados {len(vector_ids)} lugares a la base de datos")
            
            return vector_ids
        
        except Exception as e:
            logger.error(f"Error al agregar lugares: {e}")
            raise
    
    def search_places(self, query: str, top_k: Optional[int] = None, 
                     filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Buscar lugares similares en la base de datos
        
        Args:
            query: Texto de consulta
            top_k: Número máximo de resultados
            filter_dict: Filtros para la búsqueda
            
        Returns:
            Lista de resultados con score y metadatos
        """
        try:
            print(f"🔍 PlacesVectorStore.search_places iniciado")
            print(f"📝 Query: '{query}'")
            print(f"📊 Top_k: {top_k}")
            print(f"🔧 Filtros: {filter_dict}")
            
            # Mejorar la query para que sea más semánticamente similar a los textos de embedding
            improved_query = self._improve_query_for_search(query)
            
            # Generar embedding de la consulta
            print("🔄 Generando embedding de la consulta...")
            query_embedding = self.embedding_generator.embeddings.get_embedding(improved_query)
            print(f"✅ Embedding generado, dimensión: {len(query_embedding)}")
            
            # Configurar parámetros de búsqueda
            top_k = top_k or self.config.TOP_K
            print(f"📊 Top_k final: {top_k}")
            
            # Determinar umbral de similitud basado en el tipo de búsqueda
            similarity_threshold = self._get_similarity_threshold(query)
            
            print(f"🎯 Umbral de similitud final: {similarity_threshold}")
            
            # Verificar estadísticas del índice
            try:
                stats = self.index.describe_index_stats()
                total_vectors = stats.total_vector_count
                print(f"📈 Total de vectores en el índice: {total_vectors}")
                
                if total_vectors == 0:
                    print("⚠️ El índice está vacío. No hay lugares indexados.")
                    return []
                    
            except Exception as e:
                print(f"❌ Error al obtener estadísticas del índice: {e}")
            
            # Realizar búsqueda
            print("🔍 Ejecutando búsqueda en Pinecone...")
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                filter=filter_dict,
                include_metadata=True
            )
            print(f"📊 Resultados raw de Pinecone: {len(results.matches)}")
            
            # Log de resultados raw
            for i, match in enumerate(results.matches[:3]):  # Solo primeros 3
                print(f"  Raw {i+1}. ID: {match.id}, Score: {match.score}")
                if hasattr(match, 'metadata') and match.metadata:
                    print(f"     Metadata: {list(match.metadata.keys())}")
                    # Mostrar información específica del lugar
                    if 'nombre' in match.metadata:
                        print(f"     Nombre: {match.metadata.get('nombre', 'N/A')}")
                    if 'tipo_principal' in match.metadata:
                        print(f"     Tipo: {match.metadata.get('tipo_principal', 'N/A')}")
                    if 'resumen_ia' in match.metadata:
                        resumen = match.metadata.get('resumen_ia', '')
                        if resumen:
                            print(f"     Resumen IA: {resumen[:100]}...")
            
            # Procesar resultados
            processed_results = []
            print("🔄 Procesando resultados...")
            
            for match in results.matches:
                print(f"  Procesando: ID={match.id}, Score={match.score}, Threshold={similarity_threshold}")
                
                if match.score >= similarity_threshold:
                    processed_results.append({
                        'id': match.id,
                        'score': match.score,
                        'metadata': match.metadata
                    })
                    print(f"    ✅ Aceptado (score >= threshold)")
                else:
                    print(f"    ❌ Rechazado (score < threshold)")
            
            print(f"📊 Resultados finales procesados: {len(processed_results)}")
            
            # Log detallado de resultados finales
            if processed_results:
                print("📋 Resultados finales:")
                for i, result in enumerate(processed_results[:3]):
                    print(f"  {i+1}. Score: {result['score']} - ID: {result['id']}")
                    if 'metadata' in result and result['metadata']:
                        metadata = result['metadata']
                        print(f"     Nombre: {metadata.get('nombre', 'N/A')}")
                        print(f"     Tipo: {metadata.get('tipo_principal', 'N/A')}")
                        print(f"     Rating: {metadata.get('rating', 'N/A')}")
            else:
                print("⚠️ No hay resultados que cumplan el umbral de similitud")
            
            return processed_results
        
        except Exception as e:
            print(f"❌ Error en búsqueda de lugares: {e}")
            import traceback
            print(f"🔍 Traceback completo: {traceback.format_exc()}")
            raise
    
    def find_hotels_with_amenities(self, amenities: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Buscar hoteles con amenidades específicas
        
        Args:
            amenities: Lista de amenidades (ej: ['gimnasio', 'piscina', 'spa'])
            top_k: Número máximo de resultados
            
        Returns:
            Lista de hoteles que tienen las amenidades
        """
        try:
            # Crear consulta para hoteles con amenidades
            query = f"Hotel con {' y '.join(amenities)}"
            
            # Filtrar solo hoteles
            filter_dict = {
                'vector_type': 'place',
                'tipo_principal': {'$in': ['hotel', 'Hotel', 'lodging', 'Lodging']}
            }
            
            # Realizar búsqueda
            results = self.search_places(query, top_k=top_k, filter_dict=filter_dict)
            
            # Filtrar por umbral de similitud
            threshold = 0.4  # Umbral específico para hoteles
            filtered_results = [r for r in results if r['score'] >= threshold]
            
            logger.info(f"Encontrados {len(filtered_results)} hoteles con amenidades: {amenities}")
            return filtered_results
        
        except Exception as e:
            logger.error(f"Error al buscar hoteles con amenidades: {e}")
            raise
    
    def find_hotels_with_rating_and_amenities(self, rating: float, amenities: List[str], 
                                            top_k: int = 5, rating_tolerance: float = 0.5) -> List[Dict[str, Any]]:
        """
        Buscar hoteles con rating específico y amenidades
        
        Args:
            rating: Rating mínimo requerido (ej: 3.0 para 3 estrellas)
            amenities: Lista de amenidades (ej: ['restaurante', 'gimnasio'])
            top_k: Número máximo de resultados
            rating_tolerance: Tolerancia para el rating (ej: 0.5 significa 3.0-3.5)
            
        Returns:
            Lista de hoteles que cumplen con el rating y amenidades
        """
        try:
            # Crear consulta para hoteles con amenidades
            query = f"Hotel de {rating} estrellas con {' y '.join(amenities)}"
            
            # Filtrar por tipo de lugar y rating
            filter_dict = {
                'vector_type': 'place',
                'tipo_principal': {'$in': ['hotel', 'Hotel', 'lodging', 'Lodging']},
                'rating': {
                    '$gte': rating - rating_tolerance,
                    '$lte': rating + rating_tolerance
                }
            }
            
            # Realizar búsqueda
            results = self.search_places(query, top_k=top_k, filter_dict=filter_dict)
            
            # Filtrar por umbral de similitud
            threshold = 0.35  # Umbral más bajo para búsquedas específicas
            filtered_results = [r for r in results if r['score'] >= threshold]
            
            # Ordenar por rating (mayor a menor) y luego por score
            filtered_results.sort(key=lambda x: (
                x['metadata'].get('rating', 0), 
                x['score']
            ), reverse=True)
            
            logger.info(f"Encontrados {len(filtered_results)} hoteles de {rating} estrellas con amenidades: {amenities}")
            return filtered_results
        
        except Exception as e:
            logger.error(f"Error al buscar hoteles con rating y amenidades: {e}")
            raise
    
    def find_hotels_by_rating_range(self, min_rating: float, max_rating: float, 
                                   amenities: Optional[List[str]] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Buscar hoteles en un rango de rating específico
        
        Args:
            min_rating: Rating mínimo (ej: 3.0)
            max_rating: Rating máximo (ej: 4.0)
            amenities: Lista opcional de amenidades
            top_k: Número máximo de resultados
            
        Returns:
            Lista de hoteles en el rango de rating
        """
        try:
            # Crear consulta base
            if amenities:
                query = f"Hotel de {min_rating} a {max_rating} estrellas con {' y '.join(amenities)}"
            else:
                query = f"Hotel de {min_rating} a {max_rating} estrellas"
            
            # Filtrar por tipo de lugar y rango de rating
            filter_dict = {
                'vector_type': 'place',
                'tipo_principal': {'$in': ['hotel', 'Hotel', 'lodging', 'Lodging']},
                'rating': {
                    '$gte': min_rating,
                    '$lte': max_rating
                }
            }
            
            # Realizar búsqueda
            results = self.search_places(query, top_k=top_k, filter_dict=filter_dict)
            
            # Filtrar por umbral de similitud
            threshold = 0.3  # Umbral más bajo para búsquedas por rating
            filtered_results = [r for r in results if r['score'] >= threshold]
            
            # Ordenar por rating (mayor a menor) y luego por score
            filtered_results.sort(key=lambda x: (
                x['metadata'].get('rating', 0), 
                x['score']
            ), reverse=True)
            
            logger.info(f"Encontrados {len(filtered_results)} hoteles entre {min_rating} y {max_rating} estrellas")
            return filtered_results
        
        except Exception as e:
            logger.error(f"Error al buscar hoteles por rango de rating: {e}")
            raise
    
    def find_places_by_features(self, features: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Buscar lugares con características específicas
        
        Args:
            features: Lista de características (ej: ['restaurante', 'italiano'])
            top_k: Número máximo de resultados
            
        Returns:
            Lista de lugares que tienen las características
        """
        try:
            # Crear consulta para lugares con características
            query = f"Lugar con {' y '.join(features)}"
            
            # Realizar búsqueda
            results = self.search_places(query, top_k=top_k)
            
            # Filtrar por umbral
            threshold = 0.3
            filtered_results = [r for r in results if r['score'] >= threshold]
            
            logger.info(f"Encontrados {len(filtered_results)} lugares con características: {features}")
            return filtered_results
        
        except Exception as e:
            logger.error(f"Error al buscar lugares por características: {e}")
            raise
    
    def search_places_by_location(self, location_query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Buscar lugares por ubicación
        
        Args:
            location_query: Consulta de ubicación (ej: "Chiclayo", "Lima centro")
            top_k: Número máximo de resultados
            
        Returns:
            Lista de lugares en la ubicación
        """
        try:
            # Crear consulta de ubicación
            query = f"Lugares en {location_query}"
            
            # Realizar búsqueda
            results = self.search_places(query, top_k=top_k)
            
            logger.info(f"Encontrados {len(results)} lugares en: {location_query}")
            return results
        
        except Exception as e:
            logger.error(f"Error al buscar lugares por ubicación: {e}")
            raise
    
    def find_places_by_type_and_features(self, place_type: str, features: List[str], 
                                         top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Buscar lugares por tipo y características específicas
        
        Args:
            place_type: Tipo de lugar (ej: "hotel", "restaurante", "parque", "bar")
            features: Lista de características
            top_k: Número máximo de resultados
            
        Returns:
            Lista de lugares que coinciden
        """
        try:
            # Crear consulta combinada
            query = f"{place_type} con {' y '.join(features)}"
            
            # Filtrar por tipo (más flexible)
            filter_dict = {
                'vector_type': 'place',
                '$or': [
                    {'tipo_principal': {'$in': [place_type, place_type.title(), place_type.lower()]}},
                    {'tipos_adicionales': {'$in': [place_type, place_type.title(), place_type.lower()]}}
                ]
            }
            
            # Realizar búsqueda
            results = self.search_places(query, top_k=top_k, filter_dict=filter_dict)
            
            logger.info(f"Encontrados {len(results)} {place_type}s con características: {features}")
            return results
        
        except Exception as e:
            logger.error(f"Error al buscar lugares por tipo y características: {e}")
            raise
    
    def find_places_with_rating_and_features(self, place_type: str, rating: float, 
                                           features: List[str], top_k: int = 5, 
                                           rating_tolerance: float = 0.5) -> List[Dict[str, Any]]:
        """
        Buscar lugares de un tipo específico con rating y características
        
        Args:
            place_type: Tipo de lugar (ej: "restaurante", "hotel", "bar")
            rating: Rating mínimo requerido
            features: Lista de características
            top_k: Número máximo de resultados
            rating_tolerance: Tolerancia para el rating
            
        Returns:
            Lista de lugares que cumplen con los criterios
        """
        try:
            # Crear consulta
            query = f"{place_type} de {rating} estrellas con {' y '.join(features)}"
            
            # Filtrar por tipo, rating y características
            filter_dict = {
                'vector_type': 'place',
                'rating': {
                    '$gte': rating - rating_tolerance,
                    '$lte': rating + rating_tolerance
                },
                '$or': [
                    {'tipo_principal': {'$in': [place_type, place_type.title(), place_type.lower()]}},
                    {'tipos_adicionales': {'$in': [place_type, place_type.title(), place_type.lower()]}}
                ]
            }
            
            # Realizar búsqueda
            results = self.search_places(query, top_k=top_k, filter_dict=filter_dict)
            
            # Filtrar por umbral de similitud
            threshold = 0.35
            filtered_results = [r for r in results if r['score'] >= threshold]
            
            # Ordenar por rating y score
            filtered_results.sort(key=lambda x: (
                x['metadata'].get('rating', 0), 
                x['score']
            ), reverse=True)
            
            logger.info(f"Encontrados {len(filtered_results)} {place_type}s de {rating} estrellas con características: {features}")
            return filtered_results
        
        except Exception as e:
            logger.error(f"Error al buscar lugares con rating y características: {e}")
            raise
    
    def find_places_by_opening_hours(self, place_type: str, opening_criteria: str, 
                                   features: Optional[List[str]] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Buscar lugares por criterios de horario de apertura
        
        Args:
            place_type: Tipo de lugar (ej: "restaurante", "bar", "centro comercial")
            opening_criteria: Criterio de horario ("abierto_ahora", "24_horas", "fines_semana", "lunes_viernes")
            features: Lista opcional de características
            top_k: Número máximo de resultados
            
        Returns:
            Lista de lugares que cumplen con los criterios de horario
        """
        try:
            # Crear consulta basada en criterios de horario
            if opening_criteria == "abierto_ahora":
                query = f"{place_type} abierto ahora"
            elif opening_criteria == "24_horas":
                query = f"{place_type} abierto 24 horas"
            elif opening_criteria == "fines_semana":
                query = f"{place_type} abierto fines de semana"
            elif opening_criteria == "lunes_viernes":
                query = f"{place_type} abierto de lunes a viernes"
            else:
                query = f"{place_type} con horarios específicos"
            
            # Agregar características si se proporcionan
            if features:
                query += f" con {' y '.join(features)}"
            
            # Filtrar por tipo
            filter_dict = {
                'vector_type': 'place',
                '$or': [
                    {'tipo_principal': {'$in': [place_type, place_type.title(), place_type.lower()]}},
                    {'tipos_adicionales': {'$in': [place_type, place_type.title(), place_type.lower()]}}
                ]
            }
            
            # Realizar búsqueda
            results = self.search_places(query, top_k=top_k, filter_dict=filter_dict)
            
            # Filtrar por umbral de similitud
            threshold = 0.3
            filtered_results = [r for r in results if r['score'] >= threshold]
            
            logger.info(f"Encontrados {len(filtered_results)} {place_type}s con criterio de horario: {opening_criteria}")
            return filtered_results
        
        except Exception as e:
            logger.error(f"Error al buscar lugares por horarios: {e}")
            raise
    
    def find_places_by_category_and_features(self, category: str, features: List[str], 
                                           rating_min: Optional[float] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Buscar lugares por categoría y características
        
        Args:
            category: Categoría del lugar (ej: "restaurantes", "hoteles", "centros_comerciales")
            features: Lista de características
            rating_min: Rating mínimo opcional
            top_k: Número máximo de resultados
            
        Returns:
            Lista de lugares que cumplen con los criterios
        """
        try:
            # Crear consulta
            query = f"Lugar de categoría {category} con {' y '.join(features)}"
            
            # Filtrar por categoría
            filter_dict = {
                'vector_type': 'place',
                'categoria': category
            }
            
            # Agregar filtro de rating si se especifica
            if rating_min is not None:
                filter_dict['rating'] = {'$gte': rating_min}
            
            # Realizar búsqueda
            results = self.search_places(query, top_k=top_k, filter_dict=filter_dict)
            
            # Filtrar por umbral de similitud
            threshold = 0.35
            filtered_results = [r for r in results if r['score'] >= threshold]
            
            # Ordenar por rating si se especificó
            if rating_min is not None:
                filtered_results.sort(key=lambda x: (
                    x['metadata'].get('rating', 0), 
                    x['score']
                ), reverse=True)
            
            logger.info(f"Encontrados {len(filtered_results)} lugares de categoría {category} con características: {features}")
            return filtered_results
        
        except Exception as e:
            logger.error(f"Error al buscar lugares por categoría: {e}")
            raise
    
    def smart_place_search(self, search_criteria: Dict[str, Any], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Búsqueda inteligente que combina múltiples criterios
        
        Args:
            search_criteria: Diccionario con criterios de búsqueda
                {
                    'place_type': 'restaurante',
                    'category': 'restaurantes',
                    'features': ['italiano', 'terraza'],
                    'rating_min': 4.0,
                    'rating_max': 5.0,
                    'opening_hours': 'abierto_ahora',
                    'location': 'Chiclayo centro',
                    'price_level': 'moderado'
                }
            top_k: Número máximo de resultados
            
        Returns:
            Lista de lugares que cumplen con los criterios
        """
        try:
            # Construir consulta inteligente
            query_parts = []
            
            if search_criteria.get('place_type'):
                query_parts.append(search_criteria['place_type'])
            
            if search_criteria.get('features'):
                query_parts.append(f"con {' y '.join(search_criteria['features'])}")
            
            if search_criteria.get('rating_min'):
                query_parts.append(f"de {search_criteria['rating_min']} estrellas")
            
            if search_criteria.get('opening_hours'):
                if search_criteria['opening_hours'] == 'abierto_ahora':
                    query_parts.append("abierto ahora")
                elif search_criteria['opening_hours'] == '24_horas':
                    query_parts.append("abierto 24 horas")
            
            if search_criteria.get('location'):
                query_parts.append(f"en {search_criteria['location']}")
            
            query = " ".join(query_parts)
            
            # Construir filtros
            filter_dict = {'vector_type': 'place'}
            
            # Filtro por tipo
            if search_criteria.get('place_type'):
                filter_dict['$or'] = [
                    {'tipo_principal': {'$in': [search_criteria['place_type'], 
                                               search_criteria['place_type'].title(), 
                                               search_criteria['place_type'].lower()]}},
                    {'tipos_adicionales': {'$in': [search_criteria['place_type'], 
                                                  search_criteria['place_type'].title(), 
                                                  search_criteria['place_type'].lower()]}}
                ]
            
            # Filtro por categoría
            if search_criteria.get('category'):
                filter_dict['categoria'] = search_criteria['category']
            
            # Filtro por rating
            if search_criteria.get('rating_min') or search_criteria.get('rating_max'):
                rating_filter = {}
                if search_criteria.get('rating_min'):
                    rating_filter['$gte'] = search_criteria['rating_min']
                if search_criteria.get('rating_max'):
                    rating_filter['$lte'] = search_criteria['rating_max']
                filter_dict['rating'] = rating_filter
            
            # Filtro por nivel de precios
            if search_criteria.get('price_level'):
                price_level = search_criteria['price_level'].lower()
                
                # Mapear términos de precio a niveles numéricos según los datos del usuario
                price_mapping = {
                    'gratis': 0,
                    'económico': 1,
                    'barato': 1,
                    'accesible': 1,
                    'bajo': 1,
                    'moderado': 2,
                    'medio': 2,
                    'normal': 2,
                    'estándar': 2,
                    'caro': 3,
                    'elevado': 3,
                    'alto': 3,
                    'muy caro': 4,
                    'lujoso': 4,
                    'exclusivo': 4,
                    'premium': 4,
                    'alta cocina': 4,
                    'estrellas michelin': 4
                }
                
                if price_level in price_mapping:
                    # Filtrar por nivel numérico específico
                    filter_dict['nivel_precios__nivel'] = price_mapping[price_level]
                elif price_level.isdigit():
                    # Si es un número directo (nivel 1, 2, 3, 4)
                    filter_dict['nivel_precios__nivel'] = int(price_level)
                elif '-' in price_level:
                    # Manejar rangos como "50-150"
                    try:
                        min_price, max_price = map(float, price_level.split('-'))
                        filter_dict['$and'] = [
                            {'nivel_precios__rango_inferior__gte': min_price},
                            {'nivel_precios__rango_superior__lte': max_price}
                        ]
                    except:
                        # Si no se puede parsear, buscar en descripción
                        filter_dict['nivel_precios__descripcion__icontains'] = price_level
                elif 'hasta' in price_level:
                    # Manejar "hasta 100"
                    try:
                        max_price = float(price_level.replace('hasta', '').strip())
                        filter_dict['nivel_precios__rango_superior__lte'] = max_price
                    except:
                        filter_dict['nivel_precios__descripcion__icontains'] = price_level
                elif 'desde' in price_level:
                    # Manejar "desde 100"
                    try:
                        min_price = float(price_level.replace('desde', '').strip())
                        filter_dict['nivel_precios__rango_inferior__gte'] = min_price
                    except:
                        filter_dict['nivel_precios__descripcion__icontains'] = price_level
                else:
                    # Filtrar por descripción del nivel de precios
                    filter_dict['nivel_precios__descripcion__icontains'] = price_level
            
            # Realizar búsqueda
            results = self.search_places(query, top_k=top_k, filter_dict=filter_dict)
            
            # Filtrar por umbral de similitud
            threshold = 0.3
            filtered_results = [r for r in results if r['score'] >= threshold]
            
            # Ordenar por relevancia
            filtered_results.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(f"Búsqueda inteligente completada: {len(filtered_results)} resultados")
            return filtered_results
        
        except Exception as e:
            logger.error(f"Error en búsqueda inteligente: {e}")
            raise
    
    def delete_place(self, vector_id: str) -> bool:
        """
        Eliminar un lugar de la base de datos
        
        Args:
            vector_id: ID del vector a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            self.index.delete(ids=[vector_id])
            logger.info(f"Lugar eliminado: {vector_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error al eliminar lugar: {e}")
            return False
    
    def delete_places(self, vector_ids: List[str]) -> bool:
        """
        Eliminar múltiples lugares de la base de datos
        
        Args:
            vector_ids: Lista de IDs de vectores a eliminar
            
        Returns:
            True si se eliminaron correctamente
        """
        try:
            if vector_ids:
                self.index.delete(ids=vector_ids)
                logger.info(f"Eliminados {len(vector_ids)} lugares")
            return True
        
        except Exception as e:
            logger.error(f"Error al eliminar lugares: {e}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del índice de lugares
        
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
                logger.info(f"Índice de lugares limpiado: {total_vectors} vectores eliminados")
            
            return True
        
        except Exception as e:
            logger.error(f"Error al limpiar índice de lugares: {e}")
            return False
    
    def sync_places_from_database(self, batch_size: int = 100) -> int:
        """
        Sincronizar todos los lugares de la base de datos a Pinecone
        
        Args:
            batch_size: Tamaño del lote para procesar
            
        Returns:
            Número de lugares sincronizados
        """
        try:
            print(f"🔄 Iniciando sincronización de lugares desde la base de datos")
            print(f"📊 Batch size: {batch_size}")
            
            # Obtener todos los lugares activos
            print("📋 Consultando lugares activos en la base de datos...")
            lugares = LugarGooglePlaces.objects.filter(is_active=True)
            total_lugares = lugares.count()
            print(f"📈 Total de lugares activos encontrados: {total_lugares}")
            
            if total_lugares == 0:
                print("⚠️ No hay lugares activos en la base de datos")
                return 0
            
            # Verificar algunos lugares de ejemplo
            print("📋 Ejemplos de lugares encontrados:")
            for i, lugar in enumerate(lugares[:3]):
                print(f"  {i+1}. ID: {lugar.id}, Nombre: {lugar.nombre}, Tipo: {lugar.tipo_principal}")
                if lugar.resumen_ia:
                    print(f"     Resumen IA: {lugar.resumen_ia[:100]}...")
            
            # Procesar en lotes
            processed_count = 0
            for i in range(0, total_lugares, batch_size):
                batch = lugares[i:i + batch_size]
                print(f"🔄 Procesando lote {i//batch_size + 1}: lugares {i+1} a {min(i+batch_size, total_lugares)}")
                
                # Agregar lote a Pinecone
                try:
                    vector_ids = self.add_places(list(batch))
                    processed_count += len(vector_ids)
                    print(f"✅ Lote procesado: {len(vector_ids)} lugares agregados")
                except Exception as e:
                    print(f"❌ Error al procesar lote: {e}")
                    import traceback
                    print(f"🔍 Traceback completo: {traceback.format_exc()}")
                    continue
                
                print(f"📊 Progreso: {processed_count}/{total_lugares} lugares procesados")
            
            print(f"🎉 Sincronización completada: {processed_count} lugares procesados")
            
            # Verificar estadísticas finales
            try:
                stats = self.index.describe_index_stats()
                print(f"📈 Estadísticas finales del índice: {stats.total_vector_count} vectores totales")
            except Exception as e:
                print(f"❌ Error al obtener estadísticas finales: {e}")
            
            return processed_count
        
        except Exception as e:
            print(f"❌ Error en sincronización de lugares: {e}")
            import traceback
            print(f"🔍 Traceback completo: {traceback.format_exc()}")
            raise
    
    def find_places_by_price_level(self, price_level: str, place_type: Optional[str] = None, 
                                  features: Optional[List[str]] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Buscar lugares por nivel de precios
        
        Args:
            price_level: Nivel de precios ("gratis", "económico", "moderado", "caro", "muy caro", "lujoso")
                        o rango específico como "50-150" o "hasta 100"
            place_type: Tipo de lugar opcional
            features: Características opcionales
            top_k: Número máximo de resultados
            
        Returns:
            Lista de lugares que cumplen con el criterio de precio
        """
        try:
            # Mapear términos de precio a niveles numéricos según los datos del usuario
            price_mapping = {
                'gratis': 0,
                'económico': 1,
                'barato': 1,
                'accesible': 1,
                'bajo': 1,
                'moderado': 2,
                'medio': 2,
                'normal': 2,
                'estándar': 2,
                'caro': 3,
                'elevado': 3,
                'alto': 3,
                'muy caro': 4,
                'lujoso': 4,
                'exclusivo': 4,
                'premium': 4,
                'alta cocina': 4,
                'estrellas michelin': 4
            }
            
            # Mapear niveles a rangos de precios según los datos del usuario
            price_ranges = {
                0: (0.00, 0.00),      # Gratis
                1: (0.00, 50.00),     # Económico
                2: (50.00, 150.00),   # Moderado
                3: (150.00, 400.00),  # Caro
                4: (400.00, 1000.00)  # Muy caro
            }
            
            # Crear consulta
            query_parts = []
            
            if place_type:
                query_parts.append(place_type)
            
            # Manejar diferentes tipos de entrada de precio
            if price_level.lower() in price_mapping:
                nivel = price_mapping[price_level.lower()]
                query_parts.append(f"nivel de precio {nivel}")
                precio_desc = f"nivel {nivel}"
            elif '-' in price_level or 'hasta' in price_level.lower() or 'desde' in price_level.lower():
                # Manejar rangos específicos
                query_parts.append(f"precio {price_level}")
                precio_desc = f"rango {price_level}"
            else:
                query_parts.append(f"precio {price_level}")
                precio_desc = price_level
            
            if features:
                query_parts.append(f"con {' y '.join(features)}")
            
            query = " ".join(query_parts)
            
            # Construir filtros
            filter_dict = {'vector_type': 'place'}
            
            # Filtro por nivel de precios
            if price_level.lower() in price_mapping:
                nivel = price_mapping[price_level.lower()]
                filter_dict['nivel_precios__nivel'] = nivel
            elif price_level.isdigit():
                filter_dict['nivel_precios__nivel'] = int(price_level)
            elif '-' in price_level:
                # Manejar rangos como "50-150"
                try:
                    min_price, max_price = map(float, price_level.split('-'))
                    filter_dict['$and'] = [
                        {'nivel_precios__rango_inferior__gte': min_price},
                        {'nivel_precios__rango_superior__lte': max_price}
                    ]
                except:
                    # Si no se puede parsear, buscar en descripción
                    filter_dict['nivel_precios__descripcion__icontains'] = price_level
            elif 'hasta' in price_level.lower():
                # Manejar "hasta 100"
                try:
                    max_price = float(price_level.lower().replace('hasta', '').strip())
                    filter_dict['nivel_precios__rango_superior__lte'] = max_price
                except:
                    filter_dict['nivel_precios__descripcion__icontains'] = price_level
            elif 'desde' in price_level.lower():
                # Manejar "desde 100"
                try:
                    min_price = float(price_level.lower().replace('desde', '').strip())
                    filter_dict['nivel_precios__rango_inferior__gte'] = min_price
                except:
                    filter_dict['nivel_precios__descripcion__icontains'] = price_level
            else:
                # Búsqueda por descripción
                filter_dict['nivel_precios__descripcion__icontains'] = price_level
            
            # Filtro por tipo de lugar
            if place_type:
                filter_dict['$or'] = [
                    {'tipo_principal': {'$in': [place_type, place_type.title(), place_type.lower()]}},
                    {'tipos_adicionales': {'$in': [place_type, place_type.title(), place_type.lower()]}}
                ]
            
            # Realizar búsqueda
            results = self.search_places(query, top_k=top_k, filter_dict=filter_dict)
            
            # Filtrar por umbral de similitud
            threshold = 0.3
            filtered_results = [r for r in results if r['score'] >= threshold]
            
            # Ordenar por nivel de precio y score
            filtered_results.sort(key=lambda x: (
                x['metadata'].get('nivel_precios__nivel', 0),
                x['score']
            ))
            
            logger.info(f"Encontrados {len(filtered_results)} lugares con nivel de precio: {precio_desc}")
            return filtered_results
        
        except Exception as e:
            logger.error(f"Error al buscar lugares por nivel de precio: {e}")
            raise
    
    def _improve_query_for_search(self, query: str) -> str:
        """
        Mejorar la query para que sea más semánticamente similar a los textos de embedding
        
        Args:
            query: Query original del usuario
            
        Returns:
            Query mejorada
        """
        try:
            # Convertir a minúsculas
            query = query.lower()
            
            # Mapear términos comunes a términos más específicos
            query_improvements = {
                'quiero': '',
                'busco': '', 
                'necesito': '',
                'hotel con piscina': 'hotel piscina',
                'hotel que tenga piscina': 'hotel piscina',
                'hotel con gimnasio': 'hotel gimnasio',
                'restaurante con terraza': 'restaurante terraza',
                'lugar con wifi': 'wifi internet',
                'hotel 24 horas': 'hotel 24 horas',
                'restaurante abierto tarde': 'restaurante horario nocturno',
                'lugar económico': 'económico barato',
                'hotel de lujo': 'hotel lujo premium'
            }
            
            # Aplicar mejoras
            improved_query = query
            for original, improved in query_improvements.items():
                if original in improved_query:
                    improved_query = improved_query.replace(original, improved)
                    break  # Solo aplicar una mejora
            
            # Limpiar espacios extra
            improved_query = ' '.join(improved_query.split())
            
            print(f"🔧 Query original: '{query}'")
            print(f"🔧 Query mejorada: '{improved_query}'")
            
            return improved_query
        
        except Exception as e:
            print(f"❌ Error al mejorar query: {e}")
            return query
    
    def _get_similarity_threshold(self, query: str) -> float:
        """
        Obtener umbral de similitud basado en el tipo de búsqueda
        
        Args:
            query: Query de búsqueda
            
        Returns:
            Umbral de similitud (0.0 a 1.0)
        """
        query_lower = query.lower()
        
        # Umbrales más permisivos para el enfoque simplificado
        if 'hotel' in query_lower:
            return 0.55  # Hoteles: más permisivo
        elif 'restaurante' in query_lower:
            return 0.52  # Restaurantes: más permisivo
        else:
            return 0.50  # General: más permisivo 