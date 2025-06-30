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
            print("🔍 VALIDANDO FECHAS...")
            # Validar fechas
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            
            if fecha_inicio_dt >= fecha_fin_dt:
                raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")
            
            # Calcular duración
            num_dias = (fecha_fin_dt - fecha_inicio_dt).days + 1
            num_noches = num_dias - 1
            
            print(f"✅ Fechas válidas - Duración: {num_dias} días, {num_noches} noches")
            
            # Limpiar lugares seleccionados para este itinerario
            self.lugares_seleccionados_global.clear()
            print("🧹 Limpiando lugares seleccionados anteriores...")
            
            # Paso 1: Determinar tipos de establecimientos con DeepSeek
            print("\n🤖 CONSULTANDO DEEPSEEK PARA TIPOS DE ESTABLECIMIENTOS...")
            self.logger.info(f"🔍 Determinando tipos de establecimientos para: {preferencias_usuario}")
            tipos_establecimientos = self.deepseek.determinar_tipos_establecimientos(
                preferencias_usuario=preferencias_usuario,
                presupuesto=presupuesto_total,
                nivel_precio=nivel_precio_preferido
            )
            
            print("✅ Tipos de establecimientos determinados:")
            for categoria, tipos in tipos_establecimientos.items():
                print(f"   - {categoria}: {', '.join(tipos)}")
            
            # Crear itinerario en BD
            print(f"\n💾 CREANDO ITINERARIO EN BASE DE DATOS...")
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
            print(f"✅ Itinerario creado con ID: {itinerario.id}")
            
            # Generar días del itinerario
            print(f"\n📅 GENERANDO {num_dias} DÍAS DEL ITINERARIO...")
            dias_generados = []
            for dia_num in range(1, num_dias + 1):
                fecha_dia = fecha_inicio_dt + timedelta(days=dia_num - 1)
                
                print(f"\n🌅 GENERANDO DÍA {dia_num} - {fecha_dia}")
                
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
                print(f"✅ Día {dia_num} generado exitosamente")
            
            # Calcular estadísticas finales
            print(f"\n📊 CALCULANDO ESTADÍSTICAS FINALES...")
            estadisticas = itinerario.obtener_estadisticas()
            print(f"✅ Estadísticas calculadas")
            
            print(f"\n🎉 ¡ITINERARIO COMPLETADO!")
            print(f"📋 Título: {itinerario.titulo}")
            print(f"🆔 ID: {itinerario.id}")
            print(f"📅 Período: {fecha_inicio} a {fecha_fin}")
            print(f"💰 Presupuesto: S/. {presupuesto_total}")
            print("=" * 60)
            
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
            print(f"❌ ERROR EN GENERACIÓN: {e}")
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
        
        print(f"   📝 Creando día {dia_numero} en base de datos...")
        # Crear día
        dia_itinerario = DiaItinerario.objects.create(
            itinerario=itinerario,
            dia_numero=dia_numero,
            fecha=fecha
        )
        print(f"   ✅ Día {dia_numero} creado")
        
        # Seleccionar hotel para esta noche (excepto último día)
        if not es_ultimo_dia:
            print(f"   🏨 Buscando hotel para la noche {dia_numero}...")
            hotel = self._seleccionar_hotel_inteligente(
                tipos_alojamiento=tipos_establecimientos.get('alojamiento', []),
                nivel_precio=nivel_precio,
                preferencias_usuario=preferencias_usuario
            )
            if hotel:
                dia_itinerario.hotel = hotel
                dia_itinerario.save()
                print(f"   ✅ Hotel seleccionado: {hotel.nombre}")
            else:
                print(f"   ⚠️  No se encontró hotel para la noche {dia_numero}")
        else:
            print(f"   🏨 Día {dia_numero} es el último - no se asigna hotel")
        
        # Generar actividades del día
        print(f"   🎯 Generando actividades para el día {dia_numero}...")
        actividades = self._generar_actividades_dia_inteligente(
            dia_itinerario=dia_itinerario,
            presupuesto_diario=presupuesto_diario,
            nivel_precio=nivel_precio,
            preferencias_usuario=preferencias_usuario,
            tipos_establecimientos=tipos_establecimientos,
            es_primer_dia=(dia_numero == 1),
            hotel=hotel
        )
        
        print(f"   ✅ {len(actividades)} actividades generadas para el día {dia_numero}")
        
        return dia_itinerario
    
    def _seleccionar_hotel_inteligente(
        self,
        tipos_alojamiento: List[str],
        nivel_precio: Optional[int],
        preferencias_usuario: str
    ) -> Optional[LugarGooglePlaces]:
        """Selecciona un hotel apropiado usando DeepSeek"""
        
        print(f"      🔍 Buscando hoteles con tipos: {tipos_alojamiento}")
        
        # Construir query base
        query = LugarGooglePlaces.objects.filter(
            is_active=True,
            estado_negocio='OPERATIONAL'
        )
        
        # Filtrar por tipos de alojamiento usando tipo_principal y tipos_adicionales
        if tipos_alojamiento:
            # Crear una consulta OR para buscar en tipo_principal O en tipos_adicionales
            query_or = Q()
            
            for tipo in tipos_alojamiento:
                # Buscar en tipo_principal
                query_or |= Q(tipo_principal=tipo)
                # Buscar en tipos_adicionales (si es una lista)
                query_or |= Q(tipos_adicionales__contains=[tipo])
            
            query = query.filter(query_or)
            print(f"      🔍 Filtro aplicado: buscando lugares con al menos uno de {tipos_alojamiento}")
        else:
            # Fallback a tipos básicos
            print(f"      ⚠️  No hay tipos específicos, usando fallback")
            query = query.filter(
                Q(tipo_principal__in=['hotel', 'lodging', 'inn']) |
                Q(tipos_adicionales__contains=['hotel', 'lodging', 'inn'])
            )
        
        # Filtrar por nivel de precio
        if nivel_precio is not None:
            print(f"      💰 Filtrando por nivel de precio: {nivel_precio}")
            query = query.filter(nivel_precios__nivel__lte=nivel_precio)
        
        # Excluir lugares ya seleccionados
        if self.lugares_seleccionados_global:
            print(f"      🚫 Excluyendo {len(self.lugares_seleccionados_global)} lugares ya seleccionados")
            query = query.exclude(id__in=self.lugares_seleccionados_global)
        
        # Obtener candidatos
        candidatos = list(query.order_by('-rating', '-total_ratings')[:10])
        print(f"      📋 Encontrados {len(candidatos)} candidatos")
        
        if not candidatos:
            print(f"      ❌ No se encontraron candidatos de hotel")
            return None
        
        # Convertir a formato para DeepSeek
        print(f"      🤖 Preparando datos para DeepSeek...")
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
        print(f"      🧠 Consultando DeepSeek para selección inteligente...")
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
            hotel_seleccionado = LugarGooglePlaces.objects.get(id=hotel_id)
            print(f"      ✅ Hotel seleccionado por DeepSeek: {hotel_seleccionado.nombre}")
            return hotel_seleccionado
        
        print(f"      ❌ DeepSeek no pudo seleccionar un hotel")
        return None
    
    def _generar_actividades_dia_inteligente(
        self,
        dia_itinerario: DiaItinerario,
        presupuesto_diario: Optional[float],
        nivel_precio: Optional[int],
        preferencias_usuario: str,
        tipos_establecimientos: Dict[str, List[str]],
        es_primer_dia: bool = False,
        hotel: Optional[LugarGooglePlaces] = None
    ) -> List[ActividadItinerario]:
        """Genera las actividades para un día específico usando DeepSeek"""
        
        print(f"      📋 Distribuyendo actividades para el día...")
        # Distribuir actividades a lo largo del día
        tipos_actividades_dia = self._distribuir_actividades_dia_inteligente(
            tipos_establecimientos=tipos_establecimientos,
            preferencias_usuario=preferencias_usuario,
            es_primer_dia=es_primer_dia,
            hotel=hotel
        )
        
        print(f"      🎯 Tipos de actividades planificadas: {tipos_actividades_dia}")
        
        actividades = []
        orden = 1
        
        for tipo_actividad in tipos_actividades_dia:
            print(f"      🔍 Procesando actividad: {tipo_actividad}")
            
            # Manejar casos especiales
            if tipo_actividad == 'checkin_hotel':
                print(f"      🏨 Creando actividad de check-in al hotel")
                # Crear actividad de check-in
                actividad = ActividadItinerario.objects.create(
                    dia=dia_itinerario,
                    tipo_actividad='visita_turistica',  # Usar tipo genérico
                    lugar=dia_itinerario.hotel,
                    hora_inicio=time(7, 0),  # 7:00 AM
                    hora_fin=time(8, 0),     # 8:00 AM
                    duracion_minutos=60,
                    costo_estimado=0,  # Check-in es gratis
                    orden=orden,
                    descripcion=f"Check-in al hotel {dia_itinerario.hotel.nombre}"
                )
                actividades.append(actividad)
                print(f"      ✅ Check-in creado: 07:00-08:00 {dia_itinerario.hotel.nombre}")
                orden += 1
                continue
            
            elif tipo_actividad == 'desayuno_hotel':
                print(f"      🍳 Creando actividad de desayuno en el hotel")
                # Crear actividad de desayuno en hotel
                actividad = ActividadItinerario.objects.create(
                    dia=dia_itinerario,
                    tipo_actividad='restaurante',
                    lugar=dia_itinerario.hotel,
                    hora_inicio=time(8, 0),  # 8:00 AM
                    hora_fin=time(9, 0),     # 9:00 AM
                    duracion_minutos=60,
                    costo_estimado=30,  # Desayuno típico en hotel
                    orden=orden,
                    descripcion=f"Desayuno en el hotel {dia_itinerario.hotel.nombre}"
                )
                actividades.append(actividad)
                print(f"      ✅ Desayuno en hotel creado: 08:00-09:00 {dia_itinerario.hotel.nombre}")
                orden += 1
                continue
            
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
                print(f"      ✅ Encontrados {len(lugares_seleccionados)} lugares para {tipo_actividad}")
                
                # Usar DeepSeek para optimizar la distribución
                print(f"      🧠 Optimizando distribución con DeepSeek...")
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
                
                # Validar que no haya superposiciones
                if not self._validar_horarios_sin_superposicion(actividades_optimizadas):
                    print(f"      ⚠️  Usando distribución de fallback debido a superposiciones")
                    # Usar distribución de fallback
                    actividades_optimizadas = self._distribucion_fallback(actividades_propuestas, orden)
                
                print(f"      💾 Creando actividades en base de datos...")
                # Crear actividades en BD
                for actividad_opt in actividades_optimizadas:
                    lugar_id = actividad_opt.get('id')
                    print(f"      🔍 Buscando lugar con ID: {lugar_id} en {len(lugares_seleccionados)} lugares seleccionados")
                    
                    lugar = next((l for l in lugares_seleccionados if l.get('id') == lugar_id), None)
                    
                    if lugar:
                        print(f"      ✅ Encontrado lugar: {lugar.get('nombre')}")
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
                        print(f"      ✅ Actividad {orden} creada: {actividad_opt['hora_inicio']}-{actividad_opt['hora_fin']} {lugar.get('nombre')}")
                        orden += 1
                    else:
                        print(f"      ❌ No se encontró lugar con ID: {lugar_id}")
                        print(f"      📋 IDs disponibles: {[l.get('id') for l in lugares_seleccionados]}")
                        print(f"      📋 IDs en actividades optimizadas: {[a.get('id') for a in actividades_optimizadas]}")
            else:
                print(f"      ⚠️  No se encontraron lugares para {tipo_actividad}")
        
        print(f"      🎉 Total de actividades creadas: {len(actividades)}")
        return actividades
    
    def _distribuir_actividades_dia_inteligente(
        self,
        tipos_establecimientos: Dict[str, List[str]],
        preferencias_usuario: str,
        es_primer_dia: bool = False,
        hotel: Optional[LugarGooglePlaces] = None
    ) -> List[str]:
        """Distribuye las actividades a lo largo del día de forma inteligente"""
        
        actividades = []
        
        # Primer día: Check-in al hotel
        if es_primer_dia:
            actividades.append('checkin_hotel')
            print(f"      🏨 Agregando check-in al hotel para el primer día")
        
        # Desayuno (solo una vez)
        if tipos_establecimientos.get('alimentacion'):
            # Si es primer día y el hotel tiene restaurante, desayunar ahí
            if es_primer_dia and hotel and self._hotel_tiene_restaurante(hotel):
                actividades.append('desayuno_hotel')
                print(f"      🍳 Desayuno en el hotel: {hotel.nombre}")
            else:
                actividades.append('restaurante')
                print(f"      🍳 Desayuno en restaurante externo")
        
        # Actividades de la mañana (puntos de interés) - máximo 2
        if tipos_establecimientos.get('puntos_interes'):
            actividades.append('visita_turistica')
            # Solo agregar una segunda visita si hay suficientes lugares diferentes
            if len(tipos_establecimientos.get('puntos_interes', [])) > 1:
                actividades.append('visita_turistica')
        
        # Almuerzo (solo una vez) - siempre en restaurante externo
        if tipos_establecimientos.get('alimentacion'):
            actividades.append('restaurante')
        
        # Actividades de la tarde (máximo 1)
        if tipos_establecimientos.get('puntos_interes'):
            actividades.append('visita_turistica')
        
        # Compras (solo una vez)
        if tipos_establecimientos.get('compras'):
            actividades.append('shopping')
        
        # Cena (solo una vez)
        if tipos_establecimientos.get('alimentacion'):
            actividades.append('restaurante')
        
        # Actividad nocturna (solo una vez)
        if tipos_establecimientos.get('alimentacion'):
            actividades.append('bar')
        
        print(f"      📅 Actividades distribuidas: {actividades}")
        return actividades
    
    def _hotel_tiene_restaurante(self, hotel: LugarGooglePlaces) -> bool:
        """Verifica si el hotel tiene restaurante"""
        # Verificar en tipos_adicionales si tiene restaurante
        tipos_restaurante = ['restaurant', 'food', 'dining']
        return any(tipo in hotel.tipos_adicionales for tipo in tipos_restaurante)
    
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
        
        print(f"        🔍 Buscando lugares para: {tipo_actividad}")
        
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
        print(f"        🎯 Tipos a buscar: {tipos_buscar}")
        
        # Construir query
        query = LugarGooglePlaces.objects.filter(
            is_active=True,
            estado_negocio='OPERATIONAL'
        )
        
        # Filtrar por tipos usando tipo_principal y tipos_adicionales
        if tipos_buscar:
            # Crear una consulta OR para buscar en tipo_principal O en tipos_adicionales
            query_or = Q()
            
            for tipo in tipos_buscar:
                # Buscar en tipo_principal
                query_or |= Q(tipo_principal=tipo)
                # Buscar en tipos_adicionales (si es una lista)
                query_or |= Q(tipos_adicionales__contains=[tipo])
            
            query = query.filter(query_or)
            print(f"        🔍 Filtro aplicado: buscando lugares con al menos uno de {tipos_buscar}")
        else:
            # Fallback para puntos de interés
            print(f"        ⚠️  Usando fallback para puntos de interés")
            query = query.filter(
                Q(tipo_principal='point_of_interest') |
                Q(tipos_adicionales__contains=['point_of_interest'])
            )
        
        # Filtrar por nivel de precio
        if nivel_precio is not None:
            print(f"        💰 Filtrando por nivel de precio: {nivel_precio}")
            query = query.filter(nivel_precios__nivel__lte=nivel_precio)
        
        # Para restaurantes, asegurar variedad - excluir lugares ya seleccionados
        if tipo_actividad == 'restaurante':
            if self.lugares_seleccionados_global:
                print(f"        🚫 Excluyendo restaurantes ya seleccionados para variedad")
                query = query.exclude(id__in=self.lugares_seleccionados_global)
        
        # Para visitas turísticas, también evitar duplicados
        if tipo_actividad == 'visita_turistica':
            if self.lugares_seleccionados_global:
                print(f"        🚫 Excluyendo lugares turísticos ya seleccionados para variedad")
                query = query.exclude(id__in=self.lugares_seleccionados_global)
        
        # Obtener candidatos
        candidatos = list(query.order_by('-rating', '-total_ratings')[:15])
        print(f"        📋 Encontrados {len(candidatos)} candidatos")
        
        if not candidatos:
            print(f"        ❌ No se encontraron candidatos para {tipo_actividad}")
            return []
        
        # Convertir a formato para DeepSeek
        print(f"        🤖 Preparando datos para DeepSeek...")
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
        print(f"        🧠 Consultando DeepSeek para seleccionar hasta {max_lugares} lugares...")
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
        
        print(f"        ✅ DeepSeek seleccionó {len(lugares_seleccionados)} lugares para {tipo_actividad}")
        for lugar in lugares_seleccionados:
            print(f"          - {lugar.get('nombre')}")
        
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
    
    def _validar_horarios_sin_superposicion(self, actividades_optimizadas: List[Dict[str, Any]]) -> bool:
        """Valida que no haya superposiciones de horarios entre actividades"""
        from datetime import datetime
        
        horarios = []
        for actividad in actividades_optimizadas:
            try:
                hora_inicio = datetime.strptime(actividad.get('hora_inicio', '09:00'), '%H:%M')
                hora_fin = datetime.strptime(actividad.get('hora_fin', '10:00'), '%H:%M')
                horarios.append((hora_inicio, hora_fin, actividad.get('id')))
            except:
                continue
        
        # Verificar superposiciones
        for i, (inicio1, fin1, id1) in enumerate(horarios):
            for j, (inicio2, fin2, id2) in enumerate(horarios):
                if i != j:
                    # Si hay superposición
                    if (inicio1 < fin2 and fin1 > inicio2):
                        print(f"      ⚠️  SUPERPOSICIÓN DETECTADA:")
                        print(f"         Actividad {id1}: {inicio1.strftime('%H:%M')}-{fin1.strftime('%H:%M')}")
                        print(f"         Actividad {id2}: {inicio2.strftime('%H:%M')}-{fin2.strftime('%H:%M')}")
                        return False
        
        print(f"      ✅ No se detectaron superposiciones de horarios")
        return True
    
    def _distribucion_fallback(self, actividades_propuestas: List[Dict[str, Any]], orden_inicial: int) -> List[Dict[str, Any]]:
        """Distribución de fallback sin superposiciones"""
        
        horarios_base = [
            ('07:00', '08:00', 60),   # Check-in hotel (si es primer día)
            ('08:00', '09:00', 60),   # Desayuno
            ('09:00', '11:00', 120),  # Visita mañana
            ('12:30', '13:30', 60),   # Almuerzo
            ('14:00', '16:00', 120),  # Visita tarde
            ('16:30', '17:30', 60),   # Compras
            ('19:00', '20:00', 60),   # Cena
            ('20:30', '22:00', 90),   # Bar
        ]
        
        actividades_optimizadas = []
        orden = orden_inicial
        
        for i, actividad in enumerate(actividades_propuestas):
            if i < len(horarios_base):
                hora_inicio, hora_fin, duracion = horarios_base[i]
                actividades_optimizadas.append({
                    'id': actividad.get('id'),
                    'hora_inicio': hora_inicio,
                    'hora_fin': hora_fin,
                    'duracion_minutos': duracion,
                    'descripcion': f"Actividad {actividad.get('tipo_actividad', 'general')} - Distribución automática"
                })
                orden += 1
        
        return actividades_optimizadas 