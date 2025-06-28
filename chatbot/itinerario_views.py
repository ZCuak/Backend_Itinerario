"""
Vistas de API para el sistema de itinerarios
"""
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .itinerario_service import GeneradorItinerarios
from .models import Itinerario, DiaItinerario, ActividadItinerario, NivelPrecio
import json

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def generar_itinerario_api(request):
    """
    Genera un itinerario completo basado en las preferencias del usuario
    """
    try:
        data = json.loads(request.body)
        
        # Validar campos requeridos
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        preferencias_usuario = data.get('preferencias_usuario')
        
        if not fecha_inicio or not fecha_fin:
            return JsonResponse({
                'success': False,
                'error': 'Se requieren fecha_inicio y fecha_fin'
            }, status=400)
        
        if not preferencias_usuario:
            return JsonResponse({
                'success': False,
                'error': 'Se requieren las preferencias del usuario'
            }, status=400)
        
        # Extraer parámetros opcionales
        presupuesto_total = data.get('presupuesto_total')
        nivel_precio_preferido = data.get('nivel_precio_preferido')
        titulo = data.get('titulo', 'Mi Viaje')
        
        # Validar nivel de precio
        if nivel_precio_preferido is not None:
            if not isinstance(nivel_precio_preferido, int) or nivel_precio_preferido < 1 or nivel_precio_preferido > 4:
                return JsonResponse({
                    'success': False,
                    'error': 'nivel_precio_preferido debe ser un número entre 1 y 4'
                }, status=400)
        
        # Generar itinerario
        generador = GeneradorItinerarios()
        resultado = generador.generar_itinerario(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            preferencias_usuario=preferencias_usuario,
            presupuesto_total=presupuesto_total,
            nivel_precio_preferido=nivel_precio_preferido,
            titulo=titulo
        )
        
        if resultado['success']:
            logger.info(f"✅ Itinerario generado exitosamente - ID: {resultado['itinerario']['id']}")
            return JsonResponse(resultado, status=200)
        else:
            logger.error(f"❌ Error generando itinerario: {resultado['error']}")
            return JsonResponse(resultado, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido en el body del request'
        }, status=400)
        
    except Exception as e:
        logger.error(f"❌ Error inesperado en generar_itinerario_api: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_itinerario_api(request, itinerario_id):
    """
    Obtiene un itinerario específico por ID
    """
    try:
        itinerario = Itinerario.objects.get(id=itinerario_id, is_active=True)
        
        # Obtener días del itinerario
        dias = DiaItinerario.objects.filter(itinerario=itinerario).order_by('dia_numero')
        
        # Formatear respuesta
        dias_formateados = []
        for dia in dias:
            dia_data = {
                'dia_numero': dia.dia_numero,
                'fecha': dia.fecha.isoformat(),
                'hotel': None,
                'actividades': [],
                'costo_total_dia': dia.calcular_costo_dia()
            }
            
            # Agregar información del hotel
            if dia.hotel:
                dia_data['hotel'] = {
                    'id': dia.hotel.id,
                    'nombre': dia.hotel.nombre,
                    'direccion': dia.hotel.direccion,
                    'rating': dia.hotel.rating,
                    'nivel_precios': dia.hotel.nivel_precios.nivel if dia.hotel.nivel_precios else None,
                    'website': dia.hotel.website,
                    'telefono': dia.hotel.telefono
                }
            
            # Agregar actividades
            actividades = ActividadItinerario.objects.filter(dia=dia).order_by('orden')
            for actividad in actividades:
                actividad_data = {
                    'id': actividad.id,
                    'tipo_actividad': actividad.tipo_actividad,
                    'lugar': {
                        'id': actividad.lugar.id,
                        'nombre': actividad.lugar.nombre,
                        'direccion': actividad.lugar.direccion,
                        'rating': actividad.lugar.rating,
                        'nivel_precios': actividad.lugar.nivel_precios.nivel if actividad.lugar.nivel_precios else None,
                        'website': actividad.lugar.website,
                        'telefono': actividad.lugar.telefono,
                        'horarios': actividad.lugar.horarios
                    },
                    'hora_inicio': actividad.hora_inicio.strftime('%H:%M'),
                    'hora_fin': actividad.hora_fin.strftime('%H:%M'),
                    'duracion_minutos': actividad.duracion_minutos,
                    'costo_estimado': float(actividad.costo_estimado) if actividad.costo_estimado else None,
                    'descripcion': actividad.descripcion,
                    'notas_adicionales': actividad.notas_adicionales,
                    'orden': actividad.orden
                }
                dia_data['actividades'].append(actividad_data)
            
            dias_formateados.append(dia_data)
        
        # Calcular estadísticas
        estadisticas = itinerario.obtener_estadisticas()
        
        response_data = {
            'success': True,
            'itinerario': {
                'id': itinerario.id,
                'titulo': itinerario.titulo,
                'descripcion': itinerario.descripcion,
                'fecha_inicio': itinerario.fecha_inicio.isoformat(),
                'fecha_fin': itinerario.fecha_fin.isoformat(),
                'num_dias': itinerario.num_dias,
                'num_noches': itinerario.num_noches,
                'presupuesto_total': float(itinerario.presupuesto_total) if itinerario.presupuesto_total else None,
                'moneda_presupuesto': itinerario.moneda_presupuesto,
                'nivel_precio_preferido': itinerario.nivel_precio_preferido.nivel if itinerario.nivel_precio_preferido else None,
                'preferencias_actividades': itinerario.preferencias_actividades,
                'preferencias_alimentacion': itinerario.preferencias_alimentacion,
                'preferencias_alojamiento': itinerario.preferencias_alojamiento,
                'estado': itinerario.estado,
                'estadisticas': estadisticas,
                'created_at': itinerario.created_at.isoformat(),
                'updated_at': itinerario.updated_at.isoformat()
            },
            'dias': dias_formateados
        }
        
        return JsonResponse(response_data, status=200)
        
    except Itinerario.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Itinerario no encontrado'
        }, status=404)
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo itinerario {itinerario_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def listar_itinerarios_api(request):
    """
    Lista todos los itinerarios disponibles
    """
    try:
        # Parámetros de paginación
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        
        # Filtros
        estado = request.GET.get('estado')
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        
        # Construir query
        itinerarios = Itinerario.objects.filter(is_active=True)
        
        if estado:
            itinerarios = itinerarios.filter(estado=estado)
        
        if fecha_inicio:
            itinerarios = itinerarios.filter(fecha_inicio__gte=fecha_inicio)
        
        if fecha_fin:
            itinerarios = itinerarios.filter(fecha_fin__lte=fecha_fin)
        
        # Ordenar y paginar
        itinerarios = itinerarios.order_by('-created_at')
        
        # Paginación manual
        start = (page - 1) * page_size
        end = start + page_size
        itinerarios_page = itinerarios[start:end]
        
        # Formatear respuesta
        itinerarios_data = []
        for itinerario in itinerarios_page:
            estadisticas = itinerario.obtener_estadisticas()
            
            itinerario_data = {
                'id': itinerario.id,
                'titulo': itinerario.titulo,
                'fecha_inicio': itinerario.fecha_inicio.isoformat(),
                'fecha_fin': itinerario.fecha_fin.isoformat(),
                'num_dias': itinerario.num_dias,
                'num_noches': itinerario.num_noches,
                'presupuesto_total': float(itinerario.presupuesto_total) if itinerario.presupuesto_total else None,
                'estado': itinerario.estado,
                'estadisticas': estadisticas,
                'created_at': itinerario.created_at.isoformat()
            }
            itinerarios_data.append(itinerario_data)
        
        response_data = {
            'success': True,
            'itinerarios': itinerarios_data,
            'paginacion': {
                'pagina_actual': page,
                'total_paginas': (itinerarios.count() + page_size - 1) // page_size,
                'total_itinerarios': itinerarios.count(),
                'itinerarios_por_pagina': page_size,
                'tiene_siguiente': end < itinerarios.count(),
                'tiene_anterior': page > 1
            }
        }
        
        return JsonResponse(response_data, status=200)
        
    except Exception as e:
        logger.error(f"❌ Error listando itinerarios: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }, status=500)


@api_view(['PUT'])
@permission_classes([AllowAny])
@csrf_exempt
def actualizar_itinerario_api(request, itinerario_id):
    """
    Actualiza un itinerario existente
    """
    try:
        data = json.loads(request.body)
        
        itinerario = Itinerario.objects.get(id=itinerario_id, is_active=True)
        
        # Campos que se pueden actualizar
        campos_actualizables = [
            'titulo', 'descripcion', 'presupuesto_total', 
            'preferencias_actividades', 'preferencias_alimentacion', 
            'preferencias_alojamiento', 'estado'
        ]
        
        for campo in campos_actualizables:
            if campo in data:
                setattr(itinerario, campo, data[campo])
        
        # Actualizar nivel de precio si se proporciona
        if 'nivel_precio_preferido' in data:
            nivel_precio = data['nivel_precio_preferido']
            if nivel_precio is not None:
                try:
                    nivel_precio_obj = NivelPrecio.objects.get(nivel=nivel_precio)
                    itinerario.nivel_precio_preferido = nivel_precio_obj
                except NivelPrecio.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': f'Nivel de precio {nivel_precio} no encontrado'
                    }, status=400)
            else:
                itinerario.nivel_precio_preferido = None
        
        itinerario.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Itinerario actualizado exitosamente',
            'itinerario_id': itinerario.id
        }, status=200)
        
    except Itinerario.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Itinerario no encontrado'
        }, status=404)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido en el body del request'
        }, status=400)
        
    except Exception as e:
        logger.error(f"❌ Error actualizando itinerario {itinerario_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }, status=500)


@api_view(['DELETE'])
@permission_classes([AllowAny])
@csrf_exempt
def eliminar_itinerario_api(request, itinerario_id):
    """
    Elimina (desactiva) un itinerario
    """
    try:
        itinerario = Itinerario.objects.get(id=itinerario_id, is_active=True)
        itinerario.is_active = False
        itinerario.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Itinerario eliminado exitosamente'
        }, status=200)
        
    except Itinerario.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Itinerario no encontrado'
        }, status=404)
        
    except Exception as e:
        logger.error(f"❌ Error eliminando itinerario {itinerario_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_niveles_precio_api(request):
    """
    Obtiene todos los niveles de precio disponibles
    """
    try:
        niveles = NivelPrecio.objects.filter(is_active=True).order_by('nivel')
        
        niveles_data = []
        for nivel in niveles:
            nivel_data = {
                'nivel': nivel.nivel,
                'descripcion': nivel.descripcion,
                'rango_inferior': float(nivel.rango_inferior) if nivel.rango_inferior else None,
                'rango_superior': float(nivel.rango_superior) if nivel.rango_superior else None,
                'moneda': nivel.moneda
            }
            niveles_data.append(nivel_data)
        
        return JsonResponse({
            'success': True,
            'niveles_precio': niveles_data
        }, status=200)
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo niveles de precio: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }, status=500) 