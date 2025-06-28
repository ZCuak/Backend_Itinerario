"""
Servicio para generación inteligente de itinerarios de viaje
"""
import logging
from datetime import datetime, timedelta, time
from typing import List, Dict, Any, Optional, Tuple
from django.db.models import Q, Avg
from django.utils import timezone
from .models import (
    LugarGooglePlaces, NivelPrecio, Itinerario, DiaItinerario, 
    ActividadItinerario
)
from .deepseek.deepseek import generar_resumen_lugar
from .deepseek.itinerario_deepseek import ItinerarioDeepSeek

logger = logging.getLogger(__name__)


class GeneradorItinerarios:
    """
    Clase principal para generar itinerarios inteligentes
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.deepseek = ItinerarioDeepSeek()
        # Almacenar lugares ya seleccionados para evitar duplicados
        self.lugares_seleccionados_global = set()
    
    def generar_itinerario(
        self,
        fecha_inicio: str,
        fecha_fin: str,
        preferencias_usuario: str,
        presupuesto_total: Optional[float] = None,
        nivel_precio_preferido: Optional[int] = None,
        titulo: str = "Mi Viaje"
    ) -> Dict[str, Any]:
        """
        Genera un itinerario completo basado en las preferencias del usuario
        
        Args:
            fecha_inicio: Fecha de inicio del viaje (YYYY-MM-DD)
            fecha_fin: Fecha de fin del viaje (YYYY-MM-DD)
            preferencias_usuario: Descripción de las preferencias (ej: "aventura", "relajante", "cultural")
            presupuesto_total: Presupuesto total disponible
            nivel_precio_preferido: Nivel de precio preferido (1-4)
            titulo: Título del itinerario
        
        Returns:
            Dict con el itinerario generado
        """
        try:
            # Validar fechas
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            
            if fecha_inicio_dt >= fecha_fin_dt:
                raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")
            
            # Calcular duración
            num_dias = (fecha_fin_dt - fecha_inicio_dt).days + 1
            num_noches = num_dias - 1
            
            # Limpiar lugares seleccionados para este itinerario
            self.lugares_seleccionados_global.clear()
            
            # Paso 1: Determinar tipos de establecimientos con DeepSeek
            self.logger.info(f"🔍 Determinando tipos de establecimientos para: {preferencias_usuario}")
            tipos_establecimientos = self.deepseek.determinar_tipos_establecimientos(
                preferencias_usuario=preferencias_usuario,
                presupuesto=presupuesto_total,
                nivel_precio=nivel_precio_preferido
            )
            
            # Crear itinerario en BD
            itinerario = self._crear_itinerario(
                titulo=titulo,
                fecha_inicio=fecha_inicio_dt,
                fecha_fin=fecha_fin_dt,
                num_dias=num_dias,
                num_noches=num_noches,
                presupuesto_total=presupuesto_total,
                nivel_precio_preferido=nivel_precio_preferido,
                preferencias_actividades=[preferencias_usuario],
                preferencias_alimentacion=tipos_establecimientos.get('alimentacion', []),
                preferencias_alojamiento=tipos_establecimientos.get('alojamiento', [])
            )
            
            # Generar días del itinerario
            dias_generados = []
            for dia_num in range(1, num_dias + 1):
                fecha_dia = fecha_inicio_dt + timedelta(days=dia_num - 1)
                
                # Generar día
                dia_itinerario = self._generar_dia_itinerario(
                    itinerario=itinerario,
                    dia_numero=dia_num,
                    fecha=fecha_dia,
                    es_ultimo_dia=(dia_num == num_dias),
                    presupuesto_diario=presupuesto_total / num_dias if presupuesto_total else None,
                    nivel_precio=nivel_precio_preferido,
                    preferencias_usuario=preferencias_usuario,
                    tipos_establecimientos=tipos_establecimientos
                )
                
                dias_generados.append(dia_itinerario)
            
            # Calcular estadísticas finales
            estadisticas = itinerario.obtener_estadisticas()
            
            return {
                'success': True,
                'itinerario': {
                    'id': itinerario.id,
                    'titulo': itinerario.titulo,
                    'fecha_inicio': itinerario.fecha_inicio.isoformat(),
                    'fecha_fin': itinerario.fecha_fin.isoformat(),
                    'num_dias': itinerario.num_dias,
                    'num_noches': itinerario.num_noches,
                    'presupuesto_total': float(itinerario.presupuesto_total) if itinerario.presupuesto_total else None,
                    'estado': itinerario.estado,
                    'estadisticas': estadisticas,
                    'tipos_establecimientos_seleccionados': tipos_establecimientos
                },
                'dias': [
                    self._formatear_dia_itinerario(dia) for dia in dias_generados
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error generando itinerario: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _crear_itinerario(
        self,
        titulo: str,
        fecha_inicio: datetime.date,
        fecha_fin: datetime.date,
        num_dias: int,
        num_noches: int,
        presupuesto_total: Optional[float],
        nivel_precio_preferido: Optional[int],
        preferencias_actividades: List[str],
        preferencias_alimentacion: List[str],
        preferencias_alojamiento: List[str]
    ) -> Itinerario:
        """Crea el itinerario en la base de datos"""
        
        nivel_precio_obj = None
        if nivel_precio_preferido:
            try:
                nivel_precio_obj = NivelPrecio.objects.get(nivel=nivel_precio_preferido)
            except NivelPrecio.DoesNotExist:
                self.logger.warning(f"Nivel de precio {nivel_precio_preferido} no encontrado")
        
        return Itinerario.objects.create(
            titulo=titulo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            num_dias=num_dias,
            num_noches=num_noches,
            presupuesto_total=presupuesto_total,
            nivel_precio_preferido=nivel_precio_obj,
            preferencias_actividades=preferencias_actividades,
            preferencias_alimentacion=preferencias_alimentacion,
            preferencias_alojamiento=preferencias_alojamiento,
            estado='generado'
        )
    
    def _generar_dia_itinerario(
        self,
        itinerario: Itinerario,
        dia_numero: int,
        fecha: datetime.date,
        es_ultimo_dia: bool,
        presupuesto_diario: Optional[float],
        nivel_precio: Optional[int],
        preferencias_usuario: str,
        tipos_establecimientos: Dict[str, List[str]]
    ) -> DiaItinerario:
        """Genera un día específico del itinerario"""
        
        # Crear día
        dia_itinerario = DiaItinerario.objects.create(
            itinerario=itinerario,
            dia_numero=dia_numero,
            fecha=fecha
        )
        
        # Seleccionar hotel para esta noche (excepto último día)
        if not es_ultimo_dia:
            hotel = self._seleccionar_hotel_inteligente(
                tipos_alojamiento=tipos_establecimientos.get('alojamiento', []),
                nivel_precio=nivel_precio,
                preferencias_usuario=preferencias_usuario
            )
            if hotel:
                dia_itinerario.hotel = hotel
                dia_itinerario.save()
        
        # Generar actividades del día
        actividades = self._generar_actividades_dia_inteligente(
            dia_itinerario=dia_itinerario,
            presupuesto_diario=presupuesto_diario,
            nivel_precio=nivel_precio,
            preferencias_usuario=preferencias_usuario,
            tipos_establecimientos=tipos_establecimientos
        )
        
        return dia_itinerario
    
    def _seleccionar_hotel_inteligente(
        self,
        tipos_alojamiento: List[str],
        nivel_precio: Optional[int],
        preferencias_usuario: str
    ) -> Optional[LugarGooglePlaces]:
        """Selecciona un hotel apropiado usando DeepSeek"""
        
        # Construir query base
        query = LugarGooglePlaces.objects.filter(
            is_active=True,
            estado_negocio='OPERATIONAL'
        )
        
        # Filtrar por tipos de alojamiento usando tipo_principal y tipos_adicionales
        if tipos_alojamiento:
            # Buscar en tipo_principal O en tipos_adicionales
            query = query.filter(
                Q(tipo_principal__in=tipos_alojamiento) |
                Q(tipos_adicionales__overlap=tipos_alojamiento)
            )
        else:
            # Fallback a tipos básicos
            query = query.filter(
                Q(tipo_principal__in=['hotel', 'lodging', 'inn']) |
                Q(tipos_adicionales__contains=['hotel', 'lodging', 'inn'])
            )
        
        # Filtrar por nivel de precio
        if nivel_precio is not None:
            query = query.filter(nivel_precios__nivel__lte=nivel_precio)
        
        # Excluir lugares ya seleccionados
        if self.lugares_seleccionados_global:
            query = query.exclude(id__in=self.lugares_seleccionados_global)
        
        # Obtener candidatos
        candidatos = list(query.order_by('-rating', '-total_ratings')[:10])
        
        if not candidatos:
            return None
        
        # Convertir a formato para DeepSeek
        candidatos_data = []
        for candidato in candidatos:
            candidato_data = {
                'id': candidato.id,
                'nombre': candidato.nombre,
                'tipo_principal': candidato.tipo_principal,
                'tipos_adicionales': candidato.tipos_adicionales,
                'rating': candidato.rating,
                'nivel_precios': candidato.nivel_precios.descripcion if candidato.nivel_precios else '',
                'direccion': candidato.direccion,
                'latitud': candidato.latitud,
                'longitud': candidato.longitud,
                'horarios': candidato.horarios,
                'resumen_ia': candidato.resumen_ia or '',
                'palabras_clave_ia': candidato.palabras_clave_ia or ''
            }
            candidatos_data.append(candidato_data)
        
        # Usar DeepSeek para seleccionar el mejor hotel
        hoteles_seleccionados = self.deepseek.seleccionar_lugares_itinerario(
            lugares_candidatos=candidatos_data,
            tipo_actividad='alojamiento',
            preferencias_usuario=preferencias_usuario,
            presupuesto_diario=None,  # Los hoteles se pagan por noche, no por día
            max_lugares=1
        )
        
        if hoteles_seleccionados:
            hotel_id = hoteles_seleccionados[0].get('id')
            # Agregar a lugares seleccionados
            self.lugares_seleccionados_global.add(hotel_id)
            return LugarGooglePlaces.objects.get(id=hotel_id)
        
        return None
    
    def _generar_actividades_dia_inteligente(
        self,
        dia_itinerario: DiaItinerario,
        presupuesto_diario: Optional[float],
        nivel_precio: Optional[int],
        preferencias_usuario: str,
        tipos_establecimientos: Dict[str, List[str]]
    ) -> List[ActividadItinerario]:
        """Genera las actividades para un día específico usando DeepSeek"""
        
        # Distribuir actividades a lo largo del día
        tipos_actividades_dia = self._distribuir_actividades_dia_inteligente(
            tipos_establecimientos=tipos_establecimientos,
            preferencias_usuario=preferencias_usuario
        )
        
        actividades = []
        orden = 1
        
        for tipo_actividad in tipos_actividades_dia:
            # Seleccionar lugares para esta actividad
            lugares_seleccionados = self._seleccionar_lugares_actividad_inteligente(
                tipo_actividad=tipo_actividad,
                tipos_establecimientos=tipos_establecimientos,
                nivel_precio=nivel_precio,
                preferencias_usuario=preferencias_usuario,
                fecha=dia_itinerario.fecha,
                presupuesto_diario=presupuesto_diario
            )
            
            if lugares_seleccionados:
                # Usar DeepSeek para optimizar la distribución
                actividades_propuestas = []
                for lugar in lugares_seleccionados:
                    actividad_propuesta = {
                        'id': lugar.get('id'),
                        'nombre': lugar.get('nombre'),
                        'tipo_actividad': tipo_actividad,
                        'lugar': lugar
                    }
                    actividades_propuestas.append(actividad_propuesta)
                
                # Optimizar distribución con DeepSeek
                actividades_optimizadas = self.deepseek.optimizar_distribucion_dia(
                    actividades_propuestas=actividades_propuestas,
                    preferencias_usuario=preferencias_usuario,
                    presupuesto_diario=presupuesto_diario
                )
                
                # Crear actividades en BD
                for actividad_opt in actividades_optimizadas:
                    lugar_id = actividad_opt.get('id')
                    lugar = next((l for l in lugares_seleccionados if l.get('id') == lugar_id), None)
                    
                    if lugar:
                        # Calcular costo estimado
                        costo_estimado = self._calcular_costo_actividad(
                            lugar=lugar,
                            tipo_actividad=tipo_actividad,
                            presupuesto_diario=presupuesto_diario
                        )
                        
                        # Crear actividad
                        actividad = ActividadItinerario.objects.create(
                            dia=dia_itinerario,
                            tipo_actividad=tipo_actividad,
                            lugar=LugarGooglePlaces.objects.get(id=lugar_id),
                            hora_inicio=datetime.strptime(actividad_opt['hora_inicio'], '%H:%M').time(),
                            hora_fin=datetime.strptime(actividad_opt['hora_fin'], '%H:%M').time(),
                            duracion_minutos=actividad_opt['duracion_minutos'],
                            costo_estimado=costo_estimado,
                            orden=orden,
                            descripcion=actividad_opt['descripcion']
                        )
                        
                        actividades.append(actividad)
                        orden += 1
        
        return actividades
    
    def _distribuir_actividades_dia_inteligente(
        self,
        tipos_establecimientos: Dict[str, List[str]],
        preferencias_usuario: str
    ) -> List[str]:
        """Distribuye las actividades a lo largo del día de forma inteligente"""
        
        actividades = []
        
        # Desayuno
        if tipos_establecimientos.get('alimentacion'):
            actividades.append('restaurante')
        
        # Actividades de la mañana (puntos de interés)
        if tipos_establecimientos.get('puntos_interes'):
            actividades.extend(['visita_turistica', 'visita_turistica'])
        
        # Almuerzo
        if tipos_establecimientos.get('alimentacion'):
            actividades.append('restaurante')
        
        # Actividades de la tarde
        if tipos_establecimientos.get('puntos_interes'):
            actividades.append('visita_turistica')
        
        # Compras
        if tipos_establecimientos.get('compras'):
            actividades.append('shopping')
        
        # Cena
        if tipos_establecimientos.get('alimentacion'):
            actividades.append('restaurante')
        
        # Actividad nocturna
        if tipos_establecimientos.get('alimentacion'):
            actividades.append('bar')
        
        return actividades
    
    def _seleccionar_lugares_actividad_inteligente(
        self,
        tipo_actividad: str,
        tipos_establecimientos: Dict[str, List[str]],
        nivel_precio: Optional[int],
        preferencias_usuario: str,
        fecha: datetime.date,
        presupuesto_diario: Optional[float]
    ) -> List[Dict[str, Any]]:
        """Selecciona lugares apropiados para una actividad usando DeepSeek"""
        
        # Mapear tipo de actividad a categorías de establecimientos
        mapeo_actividad = {
            'visita_turistica': tipos_establecimientos.get('puntos_interes', []),
            'restaurante': tipos_establecimientos.get('alimentacion', []),
            'cafe': tipos_establecimientos.get('alimentacion', []),
            'bar': tipos_establecimientos.get('alimentacion', []),
            'shopping': tipos_establecimientos.get('compras', []),
            'entretenimiento': tipos_establecimientos.get('puntos_interes', [])
        }
        
        tipos_buscar = mapeo_actividad.get(tipo_actividad, ['point_of_interest'])
        
        # Construir query
        query = LugarGooglePlaces.objects.filter(
            is_active=True,
            estado_negocio='OPERATIONAL'
        )
        
        # Filtrar por tipos usando tipo_principal y tipos_adicionales
        if tipos_buscar:
            query = query.filter(
                Q(tipo_principal__in=tipos_buscar) |
                Q(tipos_adicionales__overlap=tipos_buscar)
            )
        else:
            # Fallback para puntos de interés
            query = query.filter(
                Q(tipo_principal='point_of_interest') |
                Q(tipos_adicionales__contains=['point_of_interest'])
            )
        
        # Filtrar por nivel de precio
        if nivel_precio is not None:
            query = query.filter(nivel_precios__nivel__lte=nivel_precio)
        
        # Para restaurantes, asegurar variedad - excluir lugares ya seleccionados
        if tipo_actividad == 'restaurante':
            if self.lugares_seleccionados_global:
                query = query.exclude(id__in=self.lugares_seleccionados_global)
        
        # Obtener candidatos
        candidatos = list(query.order_by('-rating', '-total_ratings')[:15])
        
        if not candidatos:
            return []
        
        # Convertir a formato para DeepSeek
        candidatos_data = []
        for candidato in candidatos:
            candidato_data = {
                'id': candidato.id,
                'nombre': candidato.nombre,
                'tipo_principal': candidato.tipo_principal,
                'tipos_adicionales': candidato.tipos_adicionales,
                'rating': candidato.rating,
                'nivel_precios': candidato.nivel_precios.descripcion if candidato.nivel_precios else '',
                'direccion': candidato.direccion,
                'latitud': candidato.latitud,
                'longitud': candidato.longitud,
                'horarios': candidato.horarios,
                'resumen_ia': candidato.resumen_ia or '',
                'palabras_clave_ia': candidato.palabras_clave_ia or ''
            }
            candidatos_data.append(candidato_data)
        
        # Usar DeepSeek para seleccionar los mejores lugares
        max_lugares = 2 if tipo_actividad == 'restaurante' else 1  # Más opciones para restaurantes
        lugares_seleccionados = self.deepseek.seleccionar_lugares_itinerario(
            lugares_candidatos=candidatos_data,
            tipo_actividad=tipo_actividad,
            preferencias_usuario=preferencias_usuario,
            presupuesto_diario=presupuesto_diario,
            max_lugares=max_lugares
        )
        
        # Agregar lugares seleccionados al conjunto global
        for lugar in lugares_seleccionados:
            self.lugares_seleccionados_global.add(lugar.get('id'))
        
        return lugares_seleccionados
    
    def _calcular_costo_actividad(
        self,
        lugar: Dict[str, Any],
        tipo_actividad: str,
        presupuesto_diario: Optional[float]
    ) -> Optional[float]:
        """Calcula el costo estimado de una actividad"""
        
        # Costos base por tipo de actividad
        costos_base = {
            'visita_turistica': 50,
            'restaurante': 80,
            'cafe': 30,
            'bar': 60,
            'shopping': 100,
            'entretenimiento': 70
        }
        
        costo_base = costos_base.get(tipo_actividad, 50)
        
        # Multiplicar por nivel de precio si está disponible
        nivel_precio_str = lugar.get('nivel_precios', '')
        if 'económico' in nivel_precio_str.lower():
            multiplicador = 1
        elif 'moderado' in nivel_precio_str.lower():
            multiplicador = 2
        elif 'caro' in nivel_precio_str.lower():
            multiplicador = 3
        elif 'muy caro' in nivel_precio_str.lower():
            multiplicador = 4
        else:
            multiplicador = 2  # Default moderado
        
        costo_estimado = costo_base * multiplicador
        
        # Si hay presupuesto diario, ajustar
        if presupuesto_diario:
            costo_estimado = min(costo_estimado, presupuesto_diario * 0.3)
        
        return costo_estimado
    
    def _formatear_dia_itinerario(self, dia: DiaItinerario) -> Dict[str, Any]:
        """Formatea un día de itinerario para la respuesta"""
        
        return {
            'dia_numero': dia.dia_numero,
            'fecha': dia.fecha.isoformat(),
            'hotel': {
                'id': dia.hotel.id,
                'nombre': dia.hotel.nombre,
                'direccion': dia.hotel.direccion,
                'rating': dia.hotel.rating,
                'nivel_precios': dia.hotel.nivel_precios.nivel if dia.hotel.nivel_precios else None
            } if dia.hotel else None,
            'actividades': [
                {
                    'id': actividad.id,
                    'tipo_actividad': actividad.tipo_actividad,
                    'lugar': {
                        'id': actividad.lugar.id,
                        'nombre': actividad.lugar.nombre,
                        'direccion': actividad.lugar.direccion,
                        'rating': actividad.lugar.rating,
                        'nivel_precios': actividad.lugar.nivel_precios.nivel if actividad.lugar.nivel_precios else None
                    },
                    'hora_inicio': actividad.hora_inicio.strftime('%H:%M'),
                    'hora_fin': actividad.hora_fin.strftime('%H:%M'),
                    'duracion_minutos': actividad.duracion_minutos,
                    'costo_estimado': float(actividad.costo_estimado) if actividad.costo_estimado else None,
                    'descripcion': actividad.descripcion,
                    'orden': actividad.orden
                }
                for actividad in dia.actividades.all()
            ],
            'costo_total_dia': dia.calcular_costo_dia()
        } 