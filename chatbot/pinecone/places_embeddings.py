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
        Generar texto optimizado para embedding usando múltiples campos estructurados
        
        Args:
            lugar: Instancia de LugarGooglePlaces
            
        Returns:
            Texto formateado para generar embedding
        """
        try:
            text_parts = []
            
            # 1. Información básica del lugar
            if lugar.nombre:
                text_parts.append(f"establecimiento {lugar.nombre}")
            
            # 2. Traducir tipo principal de inglés a español
            tipo_principal_es = self._translate_place_type(lugar.tipo_principal)
            if tipo_principal_es:
                text_parts.append(f"tipo {tipo_principal_es}")
            
            # 3. Categoría
            if lugar.categoria:
                text_parts.append(f"categoría {lugar.categoria}")
            
            # 4. Traducir tipos adicionales de inglés a español
            tipos_adicionales_es = self._translate_additional_types(lugar.tipos_adicionales)
            for tipo in tipos_adicionales_es[:3]:  # Máximo 3 tipos adicionales
                text_parts.append(f"característica {tipo}")
            
            # 5. Ubicación (solo dirección, no coordenadas)
            if lugar.direccion:
                text_parts.append(f"ubicación {lugar.direccion}")
            
            # 6. Calificaciones
            if lugar.rating and lugar.rating > 0:
                text_parts.append(f"rating {lugar.rating} estrellas")
                if lugar.total_ratings and lugar.total_ratings > 0:
                    text_parts.append(f"con {lugar.total_ratings} reseñas")
            
            # 7. Información de precios
            if lugar.nivel_precios:
                text_parts.append(f"precio {lugar.nivel_precios.descripcion}")
                if lugar.nivel_precios.rango_inferior and lugar.nivel_precios.rango_superior:
                    text_parts.append(f"rango precio {lugar.nivel_precios.rango_inferior} a {lugar.nivel_precios.rango_superior} {lugar.nivel_precios.moneda}")
            
            # 8. Horarios (procesados y simplificados)
            horarios_info = self._extract_horarios_info(lugar.horarios)
            if horarios_info:
                text_parts.append(f"horarios {horarios_info}")
            
            # 9. Estado del negocio
            if lugar.estado_negocio and lugar.estado_negocio != 'OPERATIONAL':
                estado_es = self._translate_business_status(lugar.estado_negocio)
                text_parts.append(f"estado {estado_es}")
            
            # 10. Descripción original (si existe y es diferente del resumen IA)
            if lugar.descripcion and lugar.descripcion != lugar.resumen_ia and lugar.descripcion != 'No hay descripción disponible':
                desc_short = lugar.descripcion[:150] if len(lugar.descripcion) > 150 else lugar.descripcion
                text_parts.append(f"descripción {desc_short}")
            
            # 11. Resumen de IA (limitado y procesado)
            if lugar.resumen_ia:
                resumen_processed = self._process_resumen_ia(lugar.resumen_ia)
                if resumen_processed:
                    text_parts.append(f"resumen {resumen_processed}")
            
            # Combinar todas las partes
            final_text = " ".join(text_parts)
            
            # Normalizar y limpiar
            normalized_text = self._normalize_text(final_text)
            
            print(f"📝 Texto optimizado para lugar {lugar.id}: {normalized_text[:150]}...")
            return normalized_text
        
        except Exception as e:
            print(f"❌ Error al generar texto para lugar {lugar.id}: {e}")
            # Fallback: usar solo el nombre y tipo principal
            fallback_text = f"establecimiento {lugar.nombre}"
            if lugar.tipo_principal:
                tipo_es = self._translate_place_type(lugar.tipo_principal)
                fallback_text += f" tipo {tipo_es}"
            return fallback_text

    def _translate_place_type(self, tipo_principal: str) -> str:
        """
        Traducir tipo principal de inglés a español
        """
        try:
            if not tipo_principal:
                return ""
            
            # Mapeo de tipos principales
            type_mapping = {
                # Restaurantes
                'restaurant': 'restaurante',
                'cafe': 'cafetería',
                'bar': 'bar',
                'bakery': 'panadería',
                'meal_delivery': 'entrega de comida',
                'meal_takeaway': 'comida para llevar',
                
                # Hoteles
                'hotel': 'hotel',
                'lodging': 'alojamiento',
                'guest_house': 'casa de huéspedes',
                'hostel': 'hostal',
                'bed_and_breakfast': 'bed and breakfast',
                'campground': 'camping',
                'rv_park': 'parque para caravanas',
                
                # Lugares acuáticos
                'beach': 'playa',
                'aquarium': 'acuario',
                
                # Lugares turísticos
                'tourist_attraction': 'atracción turística',
                
                # Entretenimiento
                'night_club': 'discoteca',
                'movie_theater': 'cine',
                'amusement_park': 'parque de diversiones',
                'bowling_alley': 'bolera',
                'casino': 'casino',
                
                # Museos
                'museum': 'museo',
                'art_gallery': 'galería de arte',
                
                # Lugares campestres
                'park': 'parque',
                'natural_feature': 'atractivo natural',
                
                # Centros comerciales
                'shopping_mall': 'centro comercial',
                'department_store': 'tienda por departamentos',
                'store': 'tienda',
                'supermarket': 'supermercado',
                'clothing_store': 'tienda de ropa',
                'jewelry_store': 'joyería',
                'convenience_store': 'tienda de conveniencia',
                'electronics_store': 'tienda de electrónicos',
                
                # Otros
                'point_of_interest': 'punto de interés',
                'establishment': 'establecimiento',
                'food': 'comida',
                'event_venue': 'lugar de eventos'
            }
            
            return type_mapping.get(tipo_principal.lower(), tipo_principal.lower())
            
        except Exception as e:
            print(f"❌ Error al traducir tipo principal: {e}")
            return tipo_principal.lower() if tipo_principal else ""

    def _translate_additional_types(self, tipos_adicionales) -> List[str]:
        """
        Traducir tipos adicionales de inglés a español
        """
        try:
            if not tipos_adicionales:
                return []
            
            # Si es string, intentar parsear como JSON
            if isinstance(tipos_adicionales, str):
                try:
                    import json
                    tipos_adicionales = json.loads(tipos_adicionales)
                except:
                    # Si no es JSON válido, dividir por comas
                    tipos_adicionales = [t.strip().strip('"[]') for t in tipos_adicionales.split(',')]
            
            # Mapeo de tipos adicionales (más específicos)
            additional_type_mapping = {
                # Restaurantes
                'restaurant': 'restaurante',
                'cafe': 'cafetería',
                'bar': 'bar',
                'bakery': 'panadería',
                'meal_delivery': 'entrega de comida',
                'meal_takeaway': 'comida para llevar',
                'food': 'comida',
                
                # Hoteles
                'hotel': 'hotel',
                'lodging': 'alojamiento',
                'guest_house': 'casa de huéspedes',
                'hostel': 'hostal',
                'bed_and_breakfast': 'bed and breakfast',
                'campground': 'camping',
                'rv_park': 'parque para caravanas',
                
                # Amenidades de hoteles
                'gym': 'gimnasio',
                'fitness_center': 'centro de fitness',
                'pool': 'piscina',
                'spa': 'spa',
                'restaurant': 'restaurante',
                'bar': 'bar',
                'wifi': 'wifi',
                'internet': 'internet',
                'parking': 'estacionamiento',
                'concierge': 'conserjería',
                'room_service': 'servicio a la habitación',
                
                # Lugares acuáticos
                'beach': 'playa',
                'aquarium': 'acuario',
                'water_park': 'parque acuático',
                
                # Lugares turísticos
                'tourist_attraction': 'atracción turística',
                'landmark': 'monumento',
                'historic': 'histórico',
                'cultural': 'cultural',
                
                # Entretenimiento
                'night_club': 'discoteca',
                'movie_theater': 'cine',
                'amusement_park': 'parque de diversiones',
                'bowling_alley': 'bolera',
                'casino': 'casino',
                'entertainment': 'entretenimiento',
                
                # Museos
                'museum': 'museo',
                'art_gallery': 'galería de arte',
                'exhibit': 'exhibición',
                
                # Lugares campestres
                'park': 'parque',
                'natural_feature': 'atractivo natural',
                'outdoor': 'aire libre',
                'recreation': 'recreación',
                
                # Centros comerciales
                'shopping_mall': 'centro comercial',
                'department_store': 'tienda por departamentos',
                'store': 'tienda',
                'supermarket': 'supermercado',
                'clothing_store': 'tienda de ropa',
                'jewelry_store': 'joyería',
                'convenience_store': 'tienda de conveniencia',
                'electronics_store': 'tienda de electrónicos',
                'shopping': 'compras',
                'retail': 'minorista',
                
                # Otros
                'point_of_interest': 'punto de interés',
                'establishment': 'establecimiento',
                'business': 'negocio',
                'service': 'servicio'
            }
            
            tipos_traducidos = []
            for tipo in tipos_adicionales:
                if isinstance(tipo, str):
                    tipo_clean = tipo.strip().strip('"[]')
                    tipo_traducido = additional_type_mapping.get(tipo_clean.lower(), tipo_clean.lower())
                    if tipo_traducido and tipo_traducido not in tipos_traducidos:
                        tipos_traducidos.append(tipo_traducido)
            
            return tipos_traducidos
            
        except Exception as e:
            print(f"❌ Error al traducir tipos adicionales: {e}")
            return []

    def _extract_horarios_info(self, horarios) -> str:
        """
        Extraer información útil de los horarios
        """
        try:
            if not horarios:
                return ""
            
            # Si es string, intentar parsear como JSON
            if isinstance(horarios, str):
                try:
                    import json
                    horarios = json.loads(horarios)
                except:
                    return ""
            
            if not isinstance(horarios, list):
                return ""
            
            # Analizar patrones de horarios
            horarios_info = []
            
            # Verificar si está abierto 24 horas
            if self._is_24_hours(horarios):
                return "abierto 24 horas"
            
            # Verificar si está abierto fines de semana
            if self._is_weekend_open(horarios):
                horarios_info.append("abierto fines de semana")
            
            # Verificar si está abierto lunes a viernes
            if self._is_weekday_open(horarios):
                horarios_info.append("abierto lunes a viernes")
            
            # Extraer horario típico
            horario_tipico = self._extract_typical_hours(horarios)
            if horario_tipico:
                horarios_info.append(horario_tipico)
            
            return " ".join(horarios_info) if horarios_info else ""
            
        except Exception as e:
            print(f"❌ Error al extraer horarios: {e}")
            return ""

    def _is_24_hours(self, horarios: List[str]) -> bool:
        """Verificar si está abierto 24 horas"""
        try:
            for horario in horarios:
                if isinstance(horario, str) and "24 horas" in horario.lower():
                    return True
            return False
        except:
            return False

    def _is_weekend_open(self, horarios: List[str]) -> bool:
        """Verificar si está abierto fines de semana"""
        try:
            weekend_days = ['sábado', 'domingo', 'saturday', 'sunday']
            for horario in horarios:
                if isinstance(horario, str):
                    if any(dia in horario.lower() for dia in weekend_days):
                        return True
            return False
        except:
            return False

    def _is_weekday_open(self, horarios: List[str]) -> bool:
        """Verificar si está abierto lunes a viernes"""
        try:
            weekday_days = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday']
            for horario in horarios:
                if isinstance(horario, str):
                    if any(dia in horario.lower() for dia in weekday_days):
                        return True
            return False
        except:
            return False

    def _extract_typical_hours(self, horarios: List[str]) -> str:
        """Extraer horario típico"""
        try:
            for horario in horarios:
                if isinstance(horario, str):
                    # Buscar patrones de horario como "8:00-23:00"
                    import re
                    time_pattern = r'(\d{1,2}:\d{2}).*?(\d{1,2}:\d{2})'
                    match = re.search(time_pattern, horario)
                    if match:
                        return f"horario {match.group(1)} a {match.group(2)}"
            return ""
        except:
            return ""

    def _translate_business_status(self, status: str) -> str:
        """
        Traducir estado del negocio
        """
        try:
            status_mapping = {
                'OPERATIONAL': 'operativo',
                'CLOSED_TEMPORARILY': 'cerrado temporalmente',
                'CLOSED_PERMANENTLY': 'cerrado permanentemente',
                'OPENING_SOON': 'abriendo pronto'
            }
            return status_mapping.get(status, status.lower())
        except:
            return status.lower() if status else ""

    def _process_resumen_ia(self, resumen_ia: str) -> str:
        """
        Procesar y limitar el resumen de IA para evitar textos muy largos
        """
        try:
            if not resumen_ia:
                return ""
            
            # Limitar longitud máxima
            max_length = 300
            if len(resumen_ia) <= max_length:
                return resumen_ia
            
            # Truncar inteligentemente
            truncated = resumen_ia[:max_length]
            
            # Buscar el último punto o coma para cortar en una frase completa
            last_period = truncated.rfind('.')
            last_comma = truncated.rfind(',')
            
            if last_period > max_length * 0.7:  # Si hay un punto en el último 30%
                return truncated[:last_period + 1]
            elif last_comma > max_length * 0.8:  # Si hay una coma en el último 20%
                return truncated[:last_comma + 1]
            else:
                return truncated + "..."
                
        except Exception as e:
            print(f"❌ Error al procesar resumen IA: {e}")
            return resumen_ia[:200] if resumen_ia else ""
    
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