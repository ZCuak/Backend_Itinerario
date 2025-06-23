from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .google_places import buscar_lugares_cercanos
from .models import LugarGooglePlaces
from .deepseek.deepseek import generar_resumen_lugar, generar_resumenes_lotes
from django.core.paginator import Paginator
import json
from django.db import models
from django.db import connection

@api_view(['POST'])
@permission_classes([AllowAny])
def lugares_cercanos(request):
    try:
        data = request.data
        latitud = data.get('latitud')
        longitud = data.get('longitud')
        radio = data.get('radio', 15000)
        tipos = data.get('tipos')
        
        if not latitud or not longitud:
            return Response({
                'status': 'error',
                'message': 'Se requieren las coordenadas (latitud y longitud)',
                'data': None
            }, status=400)
        
        latitud = float(latitud)
        longitud = float(longitud)
        radio = int(radio)
        
        if tipos:
            tipos = tipos.split(',')
        
        lugares = buscar_lugares_cercanos(latitud, longitud, radio, tipos)
        
        return Response({
            'status': 'success',
            'message': f'Se encontraron {lugares["total_lugares"]} lugares cercanos',
            'data': lugares
        })
        
    except ValueError:
        return Response({
            'status': 'error',
            'message': 'Las coordenadas y el radio deben ser números válidos',
            'data': None
        }, status=400)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error al buscar lugares cercanos: {str(e)}',
            'data': None
        }, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def generar_resumen_ia(request):
    """
    Genera un resumen por IA para un lugar específico.
    """
    try:
        data = request.data
        lugar_id = data.get('lugar_id')
        
        if not lugar_id:
            return Response({
                'status': 'error',
                'message': 'Se requiere el ID del lugar',
                'data': None
            }, status=400)
        
        # Obtener el lugar de la base de datos
        try:
            lugar = LugarGooglePlaces.objects.get(id=lugar_id)
        except LugarGooglePlaces.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Lugar no encontrado',
                'data': None
            }, status=404)
        
        # Preparar datos del lugar para DeepSeek
        lugar_data = {
            'id': lugar.id,
            'nombre': lugar.nombre,
            'direccion': lugar.direccion,
            'categoria': lugar.categoria,
            'tipo_principal': lugar.tipo_principal,
            'rating': lugar.rating,
            'total_ratings': lugar.total_ratings,
            'nivel_precios': lugar.nivel_precios.descripcion if lugar.nivel_precios else 'Sin especificar',
            'descripcion': lugar.descripcion,
            'horarios': lugar.horarios,
            'website': lugar.website,
            'telefono': lugar.telefono
        }
        
        # Generar resumen por IA
        resumen = generar_resumen_lugar(lugar_data)
        
        if resumen:
            # Actualizar el lugar en la base de datos
            lugar.resumen_ia = resumen
            lugar.save()
            
            return Response({
                'status': 'success',
                'message': 'Resumen generado exitosamente',
                'data': {
                    'lugar_id': lugar.id,
                    'nombre': lugar.nombre,
                    'resumen_ia': resumen
                }
            })
        else:
            return Response({
                'status': 'error',
                'message': 'No se pudo generar el resumen por IA',
                'data': None
            }, status=500)
            
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error al generar resumen: {str(e)}',
            'data': None
        }, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def generar_resumenes_lotes_ia(request):
    """
    Genera resúmenes por IA para múltiples lugares en lotes.
    Guarda cada resumen inmediatamente en la BD para evitar pérdida de conexión.
    """
    try:
        data = request.data
        categoria = data.get('categoria')
        max_lugares = data.get('max_lugares', 10)
        max_lotes = data.get('max_lotes', 5)
        
        # Construir query para obtener lugares
        lugares_query = LugarGooglePlaces.objects.filter(is_active=True)
        
        # Filtrar por categoría si se especifica
        if categoria:
            lugares_query = lugares_query.filter(categoria=categoria)
        
        # Obtener lugares sin resumen de IA o con resumen vacío
        lugares_query = lugares_query.filter(
            models.Q(resumen_ia__isnull=True) | 
            models.Q(resumen_ia='') |
            models.Q(resumen_ia__startswith='No hay descripción')
        )
        
        # Limitar el número de lugares
        lugares = list(lugares_query[:max_lugares])
        
        if not lugares:
            return Response({
                'status': 'success',
                'message': 'No hay lugares que requieran resúmenes de IA',
                'data': {
                    'lugares_procesados': 0,
                    'resumenes_generados': 0
                }
            })
        
        resumenes_generados = 0
        lugares_procesados = 0
        resumenes_detalle = {}
        
        # Procesar lugares en lotes
        for i in range(0, len(lugares), max_lotes):
            lote = lugares[i:i + max_lotes]
            print(f"Procesando lote {i//max_lotes + 1} de {(len(lugares) + max_lotes - 1) // max_lotes}")
            
            for lugar in lote:
                try:
                    # Verificar conexión a BD
                    connection.ensure_connection()
                    
                    # Preparar datos del lugar para DeepSeek
                    lugar_data = {
                        'id': lugar.id,
                        'nombre': lugar.nombre,
                        'direccion': lugar.direccion,
                        'categoria': lugar.categoria,
                        'tipo_principal': lugar.tipo_principal,
                        'rating': lugar.rating,
                        'total_ratings': lugar.total_ratings,
                        'nivel_precios': lugar.nivel_precios.descripcion if lugar.nivel_precios else 'Sin especificar',
                        'descripcion': lugar.descripcion,
                        'horarios': lugar.horarios,
                        'website': lugar.website,
                        'telefono': lugar.telefono
                    }
                    
                    # Generar resumen por IA
                    resumen = generar_resumen_lugar(lugar_data)
                    
                    if resumen:
                        # Guardar inmediatamente en la BD
                        lugar.resumen_ia = resumen
                        lugar.save()
                        
                        resumenes_generados += 1
                        resumenes_detalle[lugar.id] = {
                            'nombre': lugar.nombre,
                            'resumen': resumen[:100] + "..." if len(resumen) > 100 else resumen
                        }
                        
                        print(f"✓ Resumen generado y guardado para: {lugar.nombre}")
                    else:
                        print(f"✗ Error al generar resumen para: {lugar.nombre}")
                    
                    lugares_procesados += 1
                    
                except Exception as e:
                    print(f"✗ Error procesando lugar {lugar.nombre}: {str(e)}")
                    lugares_procesados += 1
                    continue
            
            # Pausa entre lotes para evitar límites de rate
            if i + max_lotes < len(lugares):
                import time
                time.sleep(2)
        
        return Response({
            'status': 'success',
            'message': f'Procesamiento completado. {resumenes_generados} resúmenes generados',
            'data': {
                'lugares_procesados': lugares_procesados,
                'resumenes_generados': resumenes_generados,
                'resumenes_detalle': resumenes_detalle
            }
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error al generar resúmenes en lotes: {str(e)}',
            'data': None
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def listar_lugares_con_resumenes(request):
    """
    Lista lugares con sus resúmenes de IA, con paginación.
    """
    try:
        # Parámetros de paginación
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 10)
        categoria = request.GET.get('categoria')
        tiene_resumen = request.GET.get('tiene_resumen')
        
        # Construir query
        lugares_query = LugarGooglePlaces.objects.filter(is_active=True)
        
        # Filtrar por categoría
        if categoria:
            lugares_query = lugares_query.filter(categoria=categoria)
        
        # Filtrar por si tiene resumen de IA
        if tiene_resumen == 'true':
            lugares_query = lugares_query.exclude(
                models.Q(resumen_ia__isnull=True) | 
                models.Q(resumen_ia='') |
                models.Q(resumen_ia__startswith='No hay descripción')
            )
        elif tiene_resumen == 'false':
            lugares_query = lugares_query.filter(
                models.Q(resumen_ia__isnull=True) | 
                models.Q(resumen_ia='') |
                models.Q(resumen_ia__startswith='No hay descripción')
            )
        
        # Ordenar por fecha de creación (más recientes primero)
        lugares_query = lugares_query.order_by('-created_at')
        
        # Paginar resultados
        paginator = Paginator(lugares_query, page_size)
        lugares_page = paginator.get_page(page)
        
        # Preparar datos para respuesta
        lugares_data = []
        for lugar in lugares_page:
            lugar_data = {
                'id': lugar.id,
                'nombre': lugar.nombre,
                'direccion': lugar.direccion,
                'categoria': lugar.categoria,
                'tipo_principal': lugar.tipo_principal,
                'rating': lugar.rating,
                'total_ratings': lugar.total_ratings,
                'nivel_precios': lugar.nivel_precios.descripcion if lugar.nivel_precios else 'Sin especificar',
                'descripcion': lugar.descripcion,
                'resumen_ia': lugar.resumen_ia,
                'website': lugar.website,
                'telefono': lugar.telefono,
                'horarios': lugar.horarios,
                'created_at': lugar.created_at.isoformat() if lugar.created_at else None,
                'updated_at': lugar.updated_at.isoformat() if lugar.updated_at else None
            }
            lugares_data.append(lugar_data)
        
        return Response({
            'status': 'success',
            'message': f'Lugares encontrados: {paginator.count}',
            'data': {
                'lugares': lugares_data,
                'paginacion': {
                    'pagina_actual': lugares_page.number,
                    'total_paginas': paginator.num_pages,
                    'total_lugares': paginator.count,
                    'lugares_por_pagina': page_size,
                    'tiene_siguiente': lugares_page.has_next(),
                    'tiene_anterior': lugares_page.has_previous()
                }
            }
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error al listar lugares: {str(e)}',
            'data': None
        }, status=500) 