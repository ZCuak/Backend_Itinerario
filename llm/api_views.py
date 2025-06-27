"""
API Views para el sistema de búsqueda semántica
Integra DeepSeek + Embeddings + LLM para recomendar lugares
"""

import os
import sys
import django
import logging
from typing import List, Dict, Any
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itinerario_backend.settings')
django.setup()

from .integrator import ChatbotIntegrator

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Instancia global del integrador
_integrator_instance = None

def get_integrator():
    """Obtiene la instancia global del integrador"""
    global _integrator_instance
    if _integrator_instance is None:
        _integrator_instance = ChatbotIntegrator()
    return _integrator_instance

@csrf_exempt
@require_http_methods(["POST"])
def buscar_lugares_api(request):
    """
    API endpoint para buscar lugares usando el sistema integrado
    
    POST /api/llm/buscar-lugares/
    
    Body:
    {
        "mensaje": "Necesito un hotel lujoso con piscina",
        "max_candidatos": 5,
        "incluir_metadata": true
    }
    
    Response:
    {
        "success": true,
        "mensaje_original": "...",
        "filtros_extraidos": {...},
        "candidatos_encontrados": 15,
        "mejores_candidatos": [...],
        "total_seleccionados": 5,
        "tiempo_procesamiento": 2.5
    }
    """
    try:
        # Parsear JSON del request
        data = json.loads(request.body.decode('utf-8'))
        mensaje = data.get('mensaje', '').strip()
        max_candidatos = data.get('max_candidatos', 5)
        incluir_metadata = data.get('incluir_metadata', True)
        
        # Validar mensaje
        if not mensaje:
            return JsonResponse({
                'success': False,
                'error': 'El campo "mensaje" es requerido'
            }, status=400)
        
        logger.info(f"🔍 API: Procesando mensaje: {mensaje}")
        
        # Obtener integrador
        integrator = get_integrator()
        
        # Procesar mensaje completo
        import time
        tiempo_inicio = time.time()
        
        resultado = integrator.procesar_mensaje_completo(mensaje)
        
        tiempo_procesamiento = time.time() - tiempo_inicio
        
        # Formatear respuesta
        response_data = {
            'success': True,
            'mensaje_original': resultado['mensaje_original'],
            'filtros_extraidos': resultado['filtros_extraidos'],
            'candidatos_encontrados': resultado['candidatos_encontrados'],
            'total_seleccionados': resultado['total_seleccionados'],
            'tiempo_procesamiento': round(tiempo_procesamiento, 2)
        }
        
        # Formatear candidatos según configuración
        candidatos_formateados = []
        for candidato in resultado['mejores_candidatos']:
            candidato_formateado = {
                'id': candidato['id'],
                'nombre': candidato['nombre'],
                'tipo_principal': candidato['tipo_principal'],
                'rating': candidato['rating'],
                'score_similitud': round(candidato['score_similitud'], 3),
                'resumen_ia': candidato.get('resumen_ia', '')
            }
            
            # Incluir metadata si se solicita
            if incluir_metadata and candidato.get('metadata'):
                metadata = candidato['metadata']
                candidato_formateado.update({
                    'direccion': metadata.get('direccion', ''),
                    'nivel_precios': metadata.get('nivel_precios', ''),
                    'latitud': metadata.get('latitud', 0),
                    'longitud': metadata.get('longitud', 0),
                    'total_ratings': metadata.get('total_ratings', 0)
                })
            
            candidatos_formateados.append(candidato_formateado)
        
        response_data['mejores_candidatos'] = candidatos_formateados
        
        logger.info(f"✅ API: Procesamiento exitoso - {len(candidatos_formateados)} candidatos")
        
        return JsonResponse(response_data, status=200)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido en el body del request'
        }, status=400)
        
    except Exception as e:
        logger.error(f"❌ API: Error en procesamiento: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def extraer_filtros_api(request):
    """
    API endpoint solo para extraer filtros con DeepSeek
    
    POST /api/llm/extraer-filtros/
    
    Body:
    {
        "mensaje": "Necesito un hotel lujoso con piscina"
    }
    
    Response:
    {
        "success": true,
        "filtros_extraidos": {
            "tipo_establecimiento": "hotel",
            "consulta_semantica": "hotel lujoso con piscina",
            "caracteristicas": ["lujoso", "piscina"],
            "nivel_precio": "lujoso",
            "ubicacion": null,
            "intencion": "dormir"
        }
    }
    """
    try:
        # Parsear JSON del request
        data = json.loads(request.body.decode('utf-8'))
        mensaje = data.get('mensaje', '').strip()
        
        # Validar mensaje
        if not mensaje:
            return JsonResponse({
                'success': False,
                'error': 'El campo "mensaje" es requerido'
            }, status=400)
        
        logger.info(f"🔍 API: Extrayendo filtros de: {mensaje}")
        
        # Obtener integrador
        integrator = get_integrator()
        
        # Extraer solo filtros
        filtros = integrator.extraer_filtros_deepseek(mensaje)
        
        response_data = {
            'success': True,
            'mensaje_original': mensaje,
            'filtros_extraidos': filtros
        }
        
        logger.info(f"✅ API: Filtros extraídos exitosamente")
        
        return JsonResponse(response_data, status=200)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido en el body del request'
        }, status=400)
        
    except Exception as e:
        logger.error(f"❌ API: Error al extraer filtros: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def health_check_api(request):
    """
    API endpoint para verificar el estado del sistema
    
    GET /api/llm/health/
    
    Response:
    {
        "success": true,
        "status": "healthy",
        "vector_db_connected": true,
        "deepseek_available": true,
        "total_lugares_indexados": 130
    }
    """
    try:
        # Verificar conexión con vector DB
        integrator = get_integrator()
        vector_db = integrator.query_engine.vector_db
        
        try:
            stats = vector_db.get_index_stats()
            vector_db_connected = True
            total_lugares = stats.get('total_vector_count', 0)
        except Exception:
            vector_db_connected = False
            total_lugares = 0
        
        # Verificar DeepSeek (prueba simple)
        try:
            from chatbot.deepseek.deepseek import enviar_prompt
            test_response = enviar_prompt("Test")
            deepseek_available = test_response is not None
        except Exception:
            deepseek_available = False
        
        response_data = {
            'success': True,
            'status': 'healthy',
            'vector_db_connected': vector_db_connected,
            'deepseek_available': deepseek_available,
            'total_lugares_indexados': total_lugares,
            'timestamp': django.utils.timezone.now().isoformat()
        }
        
        return JsonResponse(response_data, status=200)
        
    except Exception as e:
        logger.error(f"❌ API: Error en health check: {e}")
        return JsonResponse({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def buscar_por_tipo_api(request):
    """
    API endpoint para buscar lugares por tipo específico
    
    POST /api/llm/buscar-por-tipo/
    
    Body:
    {
        "consulta": "lujoso con piscina",
        "tipo_establecimiento": "hotel",
        "max_resultados": 10
    }
    
    Response:
    {
        "success": true,
        "consulta": "...",
        "tipo_establecimiento": "hotel",
        "resultados": [...],
        "total_encontrados": 10
    }
    """
    try:
        # Parsear JSON del request
        data = json.loads(request.body.decode('utf-8'))
        consulta = data.get('consulta', '').strip()
        tipo_establecimiento = data.get('tipo_establecimiento', '').strip()
        max_resultados = data.get('max_resultados', 10)
        
        # Validar parámetros
        if not consulta:
            return JsonResponse({
                'success': False,
                'error': 'El campo "consulta" es requerido'
            }, status=400)
        
        logger.info(f"🔍 API: Buscando por tipo - Consulta: {consulta}, Tipo: {tipo_establecimiento}")
        
        # Obtener integrador
        integrator = get_integrator()
        
        # Buscar candidatos
        candidatos = integrator.query_engine.buscar_por_tipo(
            consulta=consulta,
            tipo_principal=tipo_establecimiento,
            top_k=max_resultados
        )
        
        # Formatear resultados
        resultados_formateados = []
        for candidato in candidatos:
            resultado = {
                'id': candidato['id'],
                'nombre': candidato['nombre'],
                'tipo_principal': candidato['tipo_principal'],
                'rating': candidato['rating'],
                'score_similitud': round(candidato['score_similitud'], 3),
                'resumen_ia': candidato.get('resumen_ia', '')
            }
            resultados_formateados.append(resultado)
        
        response_data = {
            'success': True,
            'consulta': consulta,
            'tipo_establecimiento': tipo_establecimiento,
            'resultados': resultados_formateados,
            'total_encontrados': len(resultados_formateados)
        }
        
        logger.info(f"✅ API: Búsqueda por tipo exitosa - {len(resultados_formateados)} resultados")
        
        return JsonResponse(response_data, status=200)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido en el body del request'
        }, status=400)
        
    except Exception as e:
        logger.error(f"❌ API: Error en búsqueda por tipo: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }, status=500) 