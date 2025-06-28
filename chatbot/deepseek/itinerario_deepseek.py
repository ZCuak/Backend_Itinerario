"""
Integración de DeepSeek para generación inteligente de itinerarios
"""
import logging
import json
from typing import List, Dict, Any, Optional
from .deepseek import DeepSeekClient

logger = logging.getLogger(__name__)


class ItinerarioDeepSeek:
    """
    Clase para integrar DeepSeek en la generación de itinerarios
    """
    
    def __init__(self):
        self.client = DeepSeekClient()
        self.logger = logging.getLogger(__name__)
    
    def determinar_tipos_establecimientos(
        self,
        preferencias_usuario: str,
        presupuesto: Optional[float] = None,
        nivel_precio: Optional[int] = None
    ) -> Dict[str, List[str]]:
        """
        Determina los tipos de establecimientos apropiados basado en las preferencias del usuario
        
        Args:
            preferencias_usuario: Descripción de las preferencias (ej: "aventura", "relajante")
            presupuesto: Presupuesto total disponible
            nivel_precio: Nivel de precio preferido (1-4)
        
        Returns:
            Dict con tipos de establecimientos por categoría
        """
        
        prompt = f"""
        Como experto en turismo, analiza las siguientes preferencias de viaje y determina los tipos de establecimientos más apropiados.

        PREFERENCIAS DEL USUARIO: {preferencias_usuario}
        PRESUPUESTO: {presupuesto if presupuesto else 'No especificado'}
        NIVEL DE PRECIO: {nivel_precio if nivel_precio else 'No especificado'}

        Basándote en estas preferencias, selecciona los tipos de establecimientos más apropiados para cada categoría:

        CATEGORÍAS A EVALUAR:
        1. ALOJAMIENTO: Tipos de hoteles, hostales, resorts, etc.
        2. ALIMENTACIÓN: Tipos de restaurantes, cafeterías, bares, etc.
        3. PUNTOS DE INTERÉS: Museos, parques, atracciones turísticas, etc.
        4. COMPRAS: Centros comerciales, tiendas, mercados, etc.

        REGLAS IMPORTANTES:
        - Para ALIMENTACIÓN, asegúrate de incluir variedad (restaurantes, cafés, bares)
        - Para PUNTOS DE INTERÉS, considera el tipo de experiencia (cultural, aventura, relajante)
        - Para ALOJAMIENTO, considera el nivel de comodidad y servicios
        - Para COMPRAS, considera el tipo de productos y experiencia

        RESPONDE EN FORMATO JSON:
        {{
            "alojamiento": ["tipo1", "tipo2", ...],
            "alimentacion": ["tipo1", "tipo2", ...],
            "puntos_interes": ["tipo1", "tipo2", ...],
            "compras": ["tipo1", "tipo2", ...]
        }}

        TIPOS DISPONIBLES:
        - ALOJAMIENTO: hotel, resort, hostel, inn, guest_house, vacation_rental
        - ALIMENTACIÓN: restaurant, cafe, bar, bakery, food_court, fast_food
        - PUNTOS DE INTERÉS: museum, park, tourist_attraction, art_gallery, theater, zoo, aquarium
        - COMPRAS: shopping_mall, store, market, boutique, department_store
        """
        
        try:
            response = self.client.generate_response(prompt)
            
            # Parsear respuesta JSON
            tipos_establecimientos = json.loads(response)
            
            self.logger.info(f"Tipos de establecimientos determinados: {tipos_establecimientos}")
            return tipos_establecimientos
            
        except Exception as e:
            self.logger.error(f"Error determinando tipos de establecimientos: {e}")
            
            # Fallback con tipos básicos
            return {
                "alojamiento": ["hotel", "resort"],
                "alimentacion": ["restaurant", "cafe", "bar"],
                "puntos_interes": ["tourist_attraction", "museum", "park"],
                "compras": ["shopping_mall", "store"]
            }
    
    def seleccionar_lugares_itinerario(
        self,
        lugares_candidatos: List[Dict[str, Any]],
        tipo_actividad: str,
        preferencias_usuario: str,
        presupuesto_diario: Optional[float] = None,
        max_lugares: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Selecciona los mejores lugares para una actividad específica del itinerario
        
        Args:
            lugares_candidatos: Lista de lugares candidatos
            tipo_actividad: Tipo de actividad (restaurante, visita_turistica, etc.)
            preferencias_usuario: Preferencias del usuario
            presupuesto_diario: Presupuesto disponible para el día
            max_lugares: Máximo número de lugares a seleccionar
        
        Returns:
            Lista de lugares seleccionados
        """
        
        if not lugares_candidatos:
            return []
        
        # Mapear tipo de actividad a descripción
        mapeo_actividad = {
            'restaurante': 'restaurante para comer',
            'cafe': 'cafetería para tomar algo',
            'bar': 'bar para beber y socializar',
            'visita_turistica': 'lugar turístico para visitar',
            'shopping': 'lugar para compras',
            'entretenimiento': 'lugar de entretenimiento',
            'alojamiento': 'hotel para hospedarse'
        }
        
        descripcion_actividad = mapeo_actividad.get(tipo_actividad, tipo_actividad)
        
        # Preparar información de candidatos
        candidatos_info = []
        for i, lugar in enumerate(lugares_candidatos):
            candidato_info = f"""
            CANDIDATO {i+1}:
            - Nombre: {lugar.get('nombre', 'N/A')}
            - Tipo: {lugar.get('tipo_principal', 'N/A')} + {', '.join(lugar.get('tipos_adicionales', []))}
            - Rating: {lugar.get('rating', 0)}/5
            - Nivel de precio: {lugar.get('nivel_precios', 'N/A')}
            - Dirección: {lugar.get('direccion', 'N/A')}
            - Resumen IA: {lugar.get('resumen_ia', 'N/A')}
            - Palabras clave: {lugar.get('palabras_clave_ia', 'N/A')}
            """
            candidatos_info.append(candidato_info)
        
        prompt = f"""
        Como experto en turismo, selecciona los mejores lugares para esta actividad específica del itinerario.

        ACTIVIDAD: {descripcion_actividad}
        PREFERENCIAS DEL USUARIO: {preferencias_usuario}
        PRESUPUESTO DIARIO: {presupuesto_diario if presupuesto_diario else 'No especificado'}
        MÁXIMO LUGARES A SELECCIONAR: {max_lugares}

        CANDIDATOS DISPONIBLES:
        {chr(10).join(candidatos_info)}

        CRITERIOS DE SELECCIÓN:
        1. RELEVANCIA: El lugar debe ser apropiado para la actividad
        2. CALIDAD: Considerar rating y reseñas
        3. PREFERENCIAS: Alinear con las preferencias del usuario
        4. PRESUPUESTO: Considerar nivel de precio si hay presupuesto
        5. VARIEDAD: Para restaurantes, asegurar diferentes tipos de cocina/ambiente
        6. UBICACIÓN: Considerar proximidad y accesibilidad

        REGLAS ESPECIALES:
        - Para RESTAURANTES: Priorizar variedad de cocinas y ambientes
        - Para VISITAS TURÍSTICAS: Priorizar lugares únicos y representativos
        - Para ALOJAMIENTO: Priorizar comodidad y servicios
        - Para COMPRAS: Priorizar variedad de productos

        RESPONDE EN FORMATO JSON con los IDs de los lugares seleccionados:
        {{
            "lugares_seleccionados": [
                {{
                    "id": ID_DEL_LUGAR,
                    "razon_seleccion": "Explicación de por qué fue seleccionado"
                }}
            ]
        }}

        Selecciona máximo {max_lugares} lugar(es).
        """
        
        try:
            response = self.client.generate_response(prompt)
            
            # Parsear respuesta JSON
            resultado = json.loads(response)
            
            lugares_seleccionados = resultado.get('lugares_seleccionados', [])
            
            # Obtener los lugares completos
            lugares_finales = []
            for seleccion in lugares_seleccionados:
                lugar_id = seleccion.get('id')
                lugar_completo = next(
                    (l for l in lugares_candidatos if l.get('id') == lugar_id),
                    None
                )
                if lugar_completo:
                    lugar_completo['razon_seleccion'] = seleccion.get('razon_seleccion', '')
                    lugares_finales.append(lugar_completo)
            
            self.logger.info(f"Seleccionados {len(lugares_finales)} lugares para {tipo_actividad}")
            return lugares_finales
            
        except Exception as e:
            self.logger.error(f"Error seleccionando lugares: {e}")
            
            # Fallback: seleccionar por rating
            lugares_ordenados = sorted(
                lugares_candidatos,
                key=lambda x: (x.get('rating', 0), x.get('total_ratings', 0)),
                reverse=True
            )
            
            return lugares_ordenados[:max_lugares]
    
    def optimizar_distribucion_dia(
        self,
        actividades_propuestas: List[Dict[str, Any]],
        preferencias_usuario: str,
        presupuesto_diario: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Optimiza la distribución temporal de las actividades del día
        
        Args:
            actividades_propuestas: Lista de actividades propuestas
            preferencias_usuario: Preferencias del usuario
            presupuesto_diario: Presupuesto disponible para el día
        
        Returns:
            Lista de actividades optimizadas con horarios
        """
        
        if not actividades_propuestas:
            return []
        
        # Preparar información de actividades
        actividades_info = []
        for i, actividad in enumerate(actividades_propuestas):
            lugar = actividad.get('lugar', {})
            actividad_info = f"""
            ACTIVIDAD {i+1}:
            - Tipo: {actividad.get('tipo_actividad', 'N/A')}
            - Lugar: {lugar.get('nombre', 'N/A')}
            - Rating: {lugar.get('rating', 0)}/5
            - Nivel de precio: {lugar.get('nivel_precios', 'N/A')}
            - Horarios: {lugar.get('horarios', 'N/A')}
            """
            actividades_info.append(actividad_info)
        
        prompt = f"""
        Como experto en planificación de itinerarios, optimiza la distribución temporal de estas actividades para un día completo.

        PREFERENCIAS DEL USUARIO: {preferencias_usuario}
        PRESUPUESTO DIARIO: {presupuesto_diario if presupuesto_diario else 'No especificado'}

        ACTIVIDADES A DISTRIBUIR:
        {chr(10).join(actividades_info)}

        REGLAS DE DISTRIBUCIÓN:
        1. DESAYUNO: Entre 7:00-9:00 (café/restaurante)
        2. ACTIVIDADES MAÑANA: 9:00-12:00 (visitas turísticas)
        3. ALMUERZO: 12:00-14:00 (restaurante)
        4. ACTIVIDADES TARDE: 14:00-18:00 (visitas, compras)
        5. CENA: 18:00-20:00 (restaurante)
        6. ACTIVIDADES NOCTURNAS: 20:00-23:00 (bar, entretenimiento)

        CONSIDERACIONES:
        - Respetar horarios de operación de los lugares
        - Dejar tiempo para traslados entre lugares
        - No sobrecargar el día
        - Considerar ritmo del usuario según preferencias
        - Para restaurantes, variar horarios de comida

        RESPONDE EN FORMATO JSON:
        {{
            "actividades_optimizadas": [
                {{
                    "id": ID_DE_LA_ACTIVIDAD,
                    "hora_inicio": "HH:MM",
                    "hora_fin": "HH:MM",
                    "duracion_minutos": MINUTOS,
                    "descripcion": "Descripción de la actividad"
                }}
            ]
        }}

        HORARIOS SUGERIDOS:
        - Desayuno: 7:30-8:30 (60 min)
        - Visita mañana: 9:00-11:00 (120 min)
        - Almuerzo: 12:30-13:30 (60 min)
        - Visita tarde: 14:00-16:00 (120 min)
        - Compras: 16:30-17:30 (60 min)
        - Cena: 19:00-20:00 (60 min)
        - Bar: 20:30-22:00 (90 min)
        """
        
        try:
            response = self.client.generate_response(prompt)
            
            # Parsear respuesta JSON
            resultado = json.loads(response)
            
            actividades_optimizadas = resultado.get('actividades_optimizadas', [])
            
            # Validar y ajustar horarios
            for actividad in actividades_optimizadas:
                # Validar formato de hora
                try:
                    hora_inicio = actividad.get('hora_inicio', '09:00')
                    hora_fin = actividad.get('hora_fin', '10:00')
                    
                    # Calcular duración si no está especificada
                    if 'duracion_minutos' not in actividad:
                        from datetime import datetime
                        inicio = datetime.strptime(hora_inicio, '%H:%M')
                        fin = datetime.strptime(hora_fin, '%H:%M')
                        duracion = int((fin - inicio).total_seconds() / 60)
                        actividad['duracion_minutos'] = duracion
                    
                except Exception as e:
                    self.logger.warning(f"Error procesando horarios: {e}")
                    # Fallback
                    actividad['hora_inicio'] = '09:00'
                    actividad['hora_fin'] = '10:00'
                    actividad['duracion_minutos'] = 60
            
            self.logger.info(f"Optimizadas {len(actividades_optimizadas)} actividades")
            return actividades_optimizadas
            
        except Exception as e:
            self.logger.error(f"Error optimizando distribución: {e}")
            
            # Fallback: distribución básica
            horarios_base = [
                ('07:30', '08:30', 60),   # Desayuno
                ('09:00', '11:00', 120),  # Visita mañana
                ('12:30', '13:30', 60),   # Almuerzo
                ('14:00', '16:00', 120),  # Visita tarde
                ('16:30', '17:30', 60),   # Compras
                ('19:00', '20:00', 60),   # Cena
                ('20:30', '22:00', 90),   # Bar
            ]
            
            actividades_optimizadas = []
            for i, actividad in enumerate(actividades_propuestas):
                if i < len(horarios_base):
                    hora_inicio, hora_fin, duracion = horarios_base[i]
                    actividades_optimizadas.append({
                        'id': actividad.get('id'),
                        'hora_inicio': hora_inicio,
                        'hora_fin': hora_fin,
                        'duracion_minutos': duracion,
                        'descripcion': f"Actividad {actividad.get('tipo_actividad', 'general')}"
                    })
            
            return actividades_optimizadas 