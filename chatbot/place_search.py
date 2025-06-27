#!/usr/bin/env python3
"""
Sistema de búsqueda inteligente de lugares usando DeepSeek + Filtro de palabras clave
"""

import json
import logging
from typing import List, Dict, Any
from django.db import models
from .models import LugarGooglePlaces
from .deepseek.deepseek import enviar_prompt

logger = logging.getLogger(__name__)

class BuscadorInteligenteLugares:
    """Sistema de búsqueda inteligente que combina DeepSeek + filtro de palabras clave"""
    
    def __init__(self):
        self.caracteristicas_mapeadas = {
            # Ejercicio y bienestar
            'ejercitarme': ['gimnasio', 'fitness', 'ejercicio', 'entrenamiento'],
            'ejercitar': ['gimnasio', 'fitness', 'ejercicio', 'entrenamiento'],
            'hacer ejercicio': ['gimnasio', 'fitness', 'ejercicio', 'entrenamiento'],
            'entrenar': ['gimnasio', 'fitness', 'ejercicio', 'entrenamiento'],
            'gimnasio': ['gimnasio', 'fitness', 'ejercicio', 'entrenamiento'],
            
            # Actividades acuáticas
            'refrescarme': ['piscina', 'natación', 'actividad acuática'],
            'nadar': ['piscina', 'natación', 'actividad acuática'],
            'bañarme': ['piscina', 'natación', 'actividad acuática'],
            'piscina': ['piscina', 'natación', 'actividad acuática'],
            
            # Relajación
            'relajarme': ['spa', 'masajes', 'bienestar', 'relajación'],
            'descansar': ['spa', 'masajes', 'bienestar', 'relajación'],
            'spa': ['spa', 'masajes', 'bienestar', 'relajación'],
            
            # Comida y bebida
            'comer': ['restaurante', 'comida', 'gastronomía'],
            'cenar': ['restaurante', 'comida', 'gastronomía'],
            'almorzar': ['restaurante', 'comida', 'gastronomía'],
            'tomar algo': ['bar', 'bebidas', 'cocteles'],
            'beber': ['bar', 'bebidas', 'cocteles'],
            
            # Conectividad
            'trabajar': ['wifi', 'internet', 'conectividad'],
            'internet': ['wifi', 'internet', 'conectividad'],
            'conectarme': ['wifi', 'internet', 'conectividad'],
            
            # Estacionamiento
            'estacionar': ['estacionamiento', 'parking'],
            'parking': ['estacionamiento', 'parking'],
            'aparcar': ['estacionamiento', 'parking'],
            
            # Experiencias
            'romántico': ['romántico', 'parejas', 'intimidad'],
            'familiar': ['familiar', 'niños', 'familia'],
            'negocios': ['negocios', 'empresarial', 'reuniones'],
            
            # Nivel de lujo
            'lujo': ['lujoso', 'exclusivo', 'premium'],
            'económico': ['económico', 'barato', 'accesible'],
            'barato': ['económico', 'barato', 'accesible'],
            
            # Horarios
            '24 horas': ['24 horas', 'disponibilidad continua'],
            'tarde': ['horario nocturno', 'abierto tarde'],
            'noche': ['horario nocturno', 'abierto tarde'],
        }
    
    def procesar_consulta_con_deepseek(self, query_usuario: str) -> Dict[str, Any]:
        """
        Usar DeepSeek para procesar la consulta natural y extraer características
        
        Args:
            query_usuario: Consulta natural del usuario
            
        Returns:
            Diccionario con características extraídas y mapeadas
        """
        try:
            prompt = f"""
            Eres un asistente experto en análisis de consultas de turismo y recomendaciones de lugares.
            
            Analiza la siguiente consulta del usuario y piensa qué tipo de establecimiento sería más apropiado:
            
            CONSULTA: "{query_usuario}"
            
            TIPOS DE ESTABLECIMIENTOS DISPONIBLES:
            - amusement_park: parques de diversiones, atracciones
            - aquarium: acuarios, vida marina
            - art_gallery: galerías de arte, exposiciones
            - bar: bares, bebidas, entretenimiento nocturno
            - beach: playas, actividades acuáticas
            - casino: casinos, juegos de azar
            - hotel: hoteles, hospedaje, alojamiento
            - lodging: alojamiento, hospedaje
            - movie_theater: cines, películas
            - museum: museos, cultura, arte
            - night_club: clubes nocturnos, fiestas
            - restaurant: restaurantes, comida, gastronomía
            - shopping_mall: centros comerciales, compras
            - store: tiendas, comercio
            - tourist_attraction: atracciones turísticas
            - water_park: parques acuáticos
            - event_venue: lugares de eventos
            - food: comida, gastronomía
            - point_of_interest: puntos de interés
            - establishment: establecimientos
            - bakery: panaderías
            - coffee_shop: cafeterías, café
            - cafe: cafés, bebidas
            - dessert_shop: tiendas de postres
            - confectionery: confiterías, dulces
            - food_store: tiendas de comida
            - ice_cream_shop: heladerías
            - hamburger_restaurant: restaurantes de hamburguesas
            - american_restaurant: restaurantes americanos
            - chinese_restaurant: restaurantes chinos
            - inn: posadas, hospedaje
            - natural_feature: características naturales
            - market: mercados
            - park: parques, recreación
            - church: iglesias
            - place_of_worship: lugares de culto
            - historical_landmark: monumentos históricos
            - amusement_center: centros de entretenimiento
            - historical_place: lugares históricos
            - bar_and_grill: bares y parrillas
            - cafeteria: cafeterías
            - brunch_restaurant: restaurantes de brunch
            - home_goods_store: tiendas de hogar
            - painter: pintores, arte
            - courier_service: servicios de mensajería
            - supermarket: supermercados
            - grocery_store: tiendas de abarrotes
            - wholesaler: mayoristas
            - discount_store: tiendas de descuentos
            - department_store: tiendas por departamentos
            - clothing_store: tiendas de ropa
            - sporting_goods_store: tiendas deportivas
            - furniture_store: tiendas de muebles
            - home_improvement_store: tiendas de mejoras para el hogar
            
            Piensa en la INTENCIÓN del usuario y relaciona con el tipo de establecimiento más apropiado.
            
            Ejemplos de relaciones inteligentes:
            - "noche de fiesta con amigos" → bar, night_club
            - "quiero ejercitarme" → sporting_goods_store, hotel (con gimnasio)
            - "relajarme y descansar" → spa, hotel, beach
            - "trabajar con wifi" → coffee_shop, cafe, hotel
            - "comida romántica" → restaurant, american_restaurant, chinese_restaurant
            - "actividad cultural" → museum, art_gallery, historical_landmark
            - "pasar tiempo al aire libre" → park, beach, amusement_park
            - "comprar ropa" → clothing_store, department_store, shopping_mall
            - "comida rápida" → hamburger_restaurant, food_store
            - "dulces y postres" → bakery, dessert_shop, confectionery, ice_cream_shop
            - "evento especial" → event_venue, restaurant, hotel
            - "entretenimiento familiar" → amusement_park, water_park, movie_theater

            
            Extrae y devuelve SOLO un JSON válido con los siguientes campos:
            
            {{
                "tipo_lugar": "tipo de lugar más apropiado (ej: bar, restaurant, hotel, etc.)",
                "caracteristicas_busqueda": ["lista de características relevantes que busca el usuario"],
                "intencion": "intención principal del usuario (ej: fiesta, ejercitarse, relajarse, comer, trabajar, cultura, recreación, compras)",
                "nivel_precio": "nivel de precio mencionado (ej: económico, moderado, caro, lujoso) o null",
                "rating_minimo": "rating mínimo mencionado (número) o null",
                "ubicacion": "ubicación específica mencionada o null",
                "horario": "criterio de horario mencionado (ej: 24 horas, abierto tarde, noche) o null",
                "publico_objetivo": "público objetivo (ej: jóvenes, familias, parejas, negocios) o null"
            }}
            
            IMPORTANTE: Piensa en la INTENCIÓN del usuario, no solo en palabras clave. 
            Relaciona lo que realmente quiere hacer con el tipo de establecimiento más apropiado.
            
            Responde SOLO con el JSON válido, sin texto adicional.
            """
            
            # Enviar a DeepSeek
            respuesta = enviar_prompt(prompt)
            
            if not respuesta:
                logger.error("No se pudo obtener respuesta de DeepSeek")
                return {}
            
            # Limpiar y parsear respuesta
            respuesta_clean = respuesta.strip()
            if respuesta_clean.startswith('```json'):
                respuesta_clean = respuesta_clean[7:]
            if respuesta_clean.endswith('```'):
                respuesta_clean = respuesta_clean[:-3]
            
            # Parsear JSON
            try:
                resultado = json.loads(respuesta_clean)
                logger.info(f"Características extraídas: {resultado}")
                return resultado
            except json.JSONDecodeError as e:
                logger.error(f"Error al parsear JSON de DeepSeek: {e}")
                logger.error(f"Respuesta recibida: {respuesta_clean}")
                return {}
                
        except Exception as e:
            logger.error(f"Error al procesar consulta con DeepSeek: {e}")
            return {}
    
    def filtrar_lugares_por_caracteristicas(self, caracteristicas: List[str], 
                                          tipo_lugar: str = None, 
                                          top_k: int = 5) -> List[LugarGooglePlaces]:
        """
        Filtrar lugares por características específicas usando búsqueda de palabras clave
        
        Args:
            caracteristicas: Lista de características a buscar
            tipo_lugar: Tipo de lugar específico (opcional)
            top_k: Número máximo de resultados
            
        Returns:
            Lista de lugares que coinciden con las características
        """
        try:
            # Obtener todos los lugares activos
            lugares_query = LugarGooglePlaces.objects.filter(is_active=True)
            
            # Filtrar por tipo si se especifica
            if tipo_lugar:
                lugares_query = lugares_query.filter(tipo_principal__icontains=tipo_lugar)
            
            lugares = list(lugares_query)
            
            # Calcular puntuación para cada lugar
            lugares_puntuados = []
            
            for lugar in lugares:
                score = 0
                lugar_texto = f"{lugar.nombre} {lugar.tipo_principal} {lugar.resumen_ia or ''}".lower()
                
                # Puntuación por características
                for caracteristica in caracteristicas:
                    if caracteristica.lower() in lugar_texto:
                        score += 10
                
                # Puntuación por características extraídas (si existen)
                if lugar.caracteristicas_extraidas:
                    caracteristicas_extraidas = lugar.caracteristicas_extraidas
                    
                    # Buscar en amenidades
                    amenidades = caracteristicas_extraidas.get('amenidades', [])
                    for caracteristica in caracteristicas:
                        for amenidad in amenidades:
                            if caracteristica.lower() in amenidad.lower():
                                score += 15  # Más peso para características extraídas
                    
                    # Buscar en palabras clave
                    palabras_clave = caracteristicas_extraidas.get('palabras_clave', [])
                    for caracteristica in caracteristicas:
                        for palabra in palabras_clave:
                            if caracteristica.lower() in palabra.lower():
                                score += 12
                
                if score > 0:
                    lugares_puntuados.append((lugar, score))
            
            # Ordenar por puntuación y retornar top_k
            lugares_puntuados.sort(key=lambda x: x[1], reverse=True)
            lugares_filtrados = [lugar for lugar, _ in lugares_puntuados[:top_k]]
            
            logger.info(f"Encontrados {len(lugares_filtrados)} lugares con características: {caracteristicas}")
            return lugares_filtrados
            
        except Exception as e:
            logger.error(f"Error al filtrar lugares: {e}")
            return []
    
    def seleccionar_mejor_lugar_con_deepseek(self, query_usuario: str, 
                                           candidatos: List[LugarGooglePlaces]) -> str:
        """
        Usar DeepSeek para seleccionar el mejor lugar de los candidatos
        
        Args:
            query_usuario: Consulta original del usuario
            candidatos: Lista de lugares candidatos
            
        Returns:
            Respuesta final con la recomendación
        """
        try:
            # Preparar información de candidatos
            info_candidatos = []
            for i, lugar in enumerate(candidatos, 1):
                caracteristicas = lugar.caracteristicas_extraidas or {}
                amenidades = caracteristicas.get('amenidades', [])
                palabras_clave = caracteristicas.get('palabras_clave', [])
                
                info_candidato = f"""
                {i}. {lugar.nombre} ({lugar.tipo_principal})
                    - Resumen: {lugar.resumen_ia or 'Sin descripción'}
                    - Rating: {lugar.rating}/5 ({lugar.total_ratings} reseñas)
                    - Precio: {lugar.nivel_precios.descripcion if lugar.nivel_precios else 'No especificado'}
                    - Amenidades: {', '.join(amenidades[:5]) if amenidades else 'No especificadas'}
                    - Palabras clave: {', '.join(palabras_clave[:3]) if palabras_clave else 'No especificadas'}
                """
                info_candidatos.append(info_candidato)
            
            prompt = f"""
            Eres un asistente experto en turismo y recomendaciones de lugares.
            
            El usuario busca: "{query_usuario}"
            
            Tienes los siguientes candidatos disponibles:
            {chr(10).join(info_candidatos)}
            
            Analiza cada candidato y selecciona el que mejor se ajuste a la consulta del usuario.
            
            Responde con:
            1. El número del candidato seleccionado
            2. Una explicación detallada de por qué es la mejor opción
            3. Las características específicas que lo hacen ideal para el usuario
            4. Información adicional relevante (ubicación, horarios, etc.)
            
            Sé específico y útil en tu recomendación.
            """
            
            respuesta = enviar_prompt(prompt)
            return respuesta if respuesta else "No se pudo generar una recomendación."
            
        except Exception as e:
            logger.error(f"Error al seleccionar mejor lugar: {e}")
            return "Error al procesar la recomendación."
    
    def buscar_lugares_inteligente(self, query_usuario: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Búsqueda inteligente completa: DeepSeek → Filtro → DeepSeek
        
        Args:
            query_usuario: Consulta natural del usuario
            top_k: Número máximo de candidatos a considerar
            
        Returns:
            Diccionario con resultados de la búsqueda
        """
        try:
            logger.info(f"Iniciando búsqueda inteligente: {query_usuario}")
            
            # Paso 1: Procesar consulta con DeepSeek
            caracteristicas_extraidas = self.procesar_consulta_con_deepseek(query_usuario)
            
            if not caracteristicas_extraidas:
                return {
                    'error': 'No se pudo procesar la consulta',
                    'query': query_usuario
                }
            
            # Paso 2: Filtrar lugares por características
            caracteristicas = caracteristicas_extraidas.get('caracteristicas_busqueda', [])
            tipo_lugar = caracteristicas_extraidas.get('tipo_lugar')
            
            candidatos = self.filtrar_lugares_por_caracteristicas(
                caracteristicas=caracteristicas,
                tipo_lugar=tipo_lugar,
                top_k=top_k
            )
            
            if not candidatos:
                return {
                    'error': 'No se encontraron lugares que coincidan con tu búsqueda',
                    'query': query_usuario,
                    'caracteristicas_busqueda': caracteristicas
                }
            
            # Paso 3: Seleccionar mejor lugar con DeepSeek
            recomendacion = self.seleccionar_mejor_lugar_con_deepseek(query_usuario, candidatos)
            
            return {
                'query': query_usuario,
                'caracteristicas_extraidas': caracteristicas_extraidas,
                'candidatos_encontrados': len(candidatos),
                'recomendacion': recomendacion,
                'lugares_candidatos': [
                    {
                        'id': lugar.id,
                        'nombre': lugar.nombre,
                        'tipo_principal': lugar.tipo_principal,
                        'rating': lugar.rating,
                        'resumen': lugar.resumen_ia
                    } for lugar in candidatos
                ]
            }
            
        except Exception as e:
            logger.error(f"Error en búsqueda inteligente: {e}")
            return {
                'error': f'Error en la búsqueda: {str(e)}',
                'query': query_usuario
            }
