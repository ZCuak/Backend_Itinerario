from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .deepseek import (
    enviar_prompt, 
    generar_resumen_lugar, 
    extraer_caracteristicas_lugar,
    generar_resumenes_lotes,
    extraer_caracteristicas_lotes
)
import json
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def test_prompt(request):
    """
    API básica para probar DeepSeek con cualquier prompt
    
    POST /api/deepseek/test-prompt/
    {
        "prompt": "Tu prompt aquí"
    }
    """
    try:
        prompt = request.data.get('prompt', '').strip()
        
        if not prompt:
            return Response({
                'error': 'El campo "prompt" es requerido'
            }, status=400)
        
        respuesta = enviar_prompt(prompt)
        
        if respuesta:
            return Response({
                'success': True,
                'prompt': prompt,
                'respuesta': respuesta
            })
        else:
            return Response({
                'error': 'No se pudo obtener respuesta de DeepSeek'
            }, status=500)
            
    except Exception as e:
        logger.error(f"Error en test_prompt: {e}")
        return Response({
            'error': f'Error interno: {str(e)}'
        }, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def procesar_consulta_nlp(request):
    """
    Procesa consultas naturales del usuario para extraer intención y características
    
    POST /api/deepseek/procesar-consulta/
    {
        "query": "Quiero un hotel donde pueda ejercitarme y relajarme"
    }
    """
    try:
        query = request.data.get('query', '').strip()
        
        if not query:
            return Response({
                'error': 'El campo "query" es requerido'
            }, status=400)
        
        prompt = f"""
        Eres un asistente experto en análisis de consultas de turismo y recomendaciones de lugares.
        
        Analiza la siguiente consulta del usuario y determina el tipo de establecimiento y las características específicas que busca:
        
        CONSULTA: "{query}"
        
        REGLAS IMPORTANTES:
        1. Si el usuario menciona EXPLÍCITAMENTE un tipo de lugar (ej: "hotel", "restaurante", "bar"), ese es el tipo_lugar
        2. Las características de búsqueda deben incluir tanto lo que menciona directamente como lo que implícitamente necesita
        3. Piensa en las AMENIDADES y SERVICIOS que necesita para cumplir su intención
        
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
        
        EJEMPLOS DE ANÁLISIS:
        - "hotel para ejercitarme" → tipo_lugar: "hotel", caracteristicas_busqueda: ["gimnasio", "ejercicio", "fitness", "entrenamiento", "equipos deportivos"]
        - "restaurante romántico" → tipo_lugar: "restaurant", caracteristicas_busqueda: ["ambiente romántico", "cena romántica", "intimidad", "decoración elegante"]
        - "lugar para trabajar" → tipo_lugar: "cafe", caracteristicas_busqueda: ["wifi", "mesas de trabajo", "ambiente tranquilo", "enchufes", "café"]
        - "bar para fiesta" → tipo_lugar: "bar", caracteristicas_busqueda: ["música", "ambiente festivo", "bebidas", "entretenimiento", "baile"]
        - "comprar ropa" → tipo_lugar: "clothing_store", caracteristicas_busqueda: ["ropa", "moda", "vestimenta", "accesorios"]
        - "dulces y postres" → tipo_lugar: "bakery", caracteristicas_busqueda: ["pan", "dulces", "postres", "repostería"]
        - "entretenimiento familiar" → tipo_lugar: "amusement_park", caracteristicas_busqueda: ["diversión", "atracciones", "familia", "entretenimiento"]
        - "actividad cultural" → tipo_lugar: "museum", caracteristicas_busqueda: ["cultura", "arte", "educación", "exposiciones"]
        - "comida rápida" → tipo_lugar: "hamburger_restaurant", caracteristicas_busqueda: ["comida rápida", "hamburguesas", "fast food"]
        - "supermercado" → tipo_lugar: "supermarket", caracteristicas_busqueda: ["comestibles", "productos", "supermercado", "abarrotes"]
        
        Extrae y devuelve SOLO un JSON válido con los siguientes campos:
        
        {{
            "tipo_lugar": "tipo de lugar más apropiado (respetar si el usuario lo menciona explícitamente)",
            "caracteristicas_busqueda": ["lista detallada de características, amenidades y servicios que busca"],
            "intencion": "intención principal del usuario",
            "nivel_precio": "nivel de precio mencionado o null",
            "rating_minimo": "rating mínimo mencionado o null",
            "ubicacion": "ubicación específica mencionada o null",
            "horario": "criterio de horario mencionado o null",
            "publico_objetivo": "público objetivo o null"
        }}
        
        IMPORTANTE: 
        - Si el usuario dice "hotel para X", el tipo_lugar es "hotel" y las características incluyen X y sus necesidades relacionadas
        - Las características deben ser específicas y útiles para la búsqueda
        - Incluye tanto características explícitas como implícitas necesarias
        
        Responde SOLO con el JSON válido, sin texto adicional.
        """
        
        respuesta = enviar_prompt(prompt)
        
        if respuesta:
            # Limpiar y parsear respuesta
            respuesta_clean = respuesta.strip()
            if respuesta_clean.startswith('```json'):
                respuesta_clean = respuesta_clean[7:]
            if respuesta_clean.endswith('```'):
                respuesta_clean = respuesta_clean[:-3]
            
            try:
                resultado = json.loads(respuesta_clean)
                return Response({
                    'success': True,
                    'query': query,
                    'analisis_nlp': resultado
                })
            except json.JSONDecodeError as e:
                return Response({
                    'error': f'Error al parsear JSON: {e}',
                    'respuesta_raw': respuesta_clean
                }, status=500)
        else:
            return Response({
                'error': 'No se pudo procesar la consulta'
            }, status=500)
            
    except Exception as e:
        logger.error(f"Error en procesar_consulta_nlp: {e}")
        return Response({
            'error': f'Error interno: {str(e)}'
        }, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def analizar_intencion_usuario(request):
    """
    Analiza específicamente la intención del usuario en una consulta
    
    POST /api/deepseek/analizar-intencion/
    {
        "query": "Necesito un lugar para una cena romántica"
    }
    """
    try:
        query = request.data.get('query', '').strip()
        
        if not query:
            return Response({
                'error': 'El campo "query" es requerido'
            }, status=400)
        
        prompt = f"""
        Analiza la siguiente consulta del usuario y determina su intención principal:
        
        CONSULTA: "{query}"
        
        Responde con un JSON que contenga:
        
        {{
            "intencion_principal": "intención principal (ej: hospedaje, comida, entretenimiento, relajación, ejercicio, cultura, compras)",
            "intenciones_secundarias": ["otras intenciones menores"],
            "emocion": "emoción o sentimiento expresado (ej: romántico, familiar, profesional, aventurero)",
            "urgencia": "nivel de urgencia (baja, media, alta)",
            "presupuesto": "indicación de presupuesto (económico, moderado, alto, premium)",
            "compania": "tipo de compañía (solo, pareja, familia, amigos, negocios)",
            "momento_dia": "momento del día (mañana, tarde, noche, 24h)",
            "palabras_clave": ["palabras clave importantes en la consulta"]
        }}
        
        Responde SOLO con el JSON válido.
        """
        
        respuesta = enviar_prompt(prompt)
        
        if respuesta:
            try:
                # Limpiar respuesta
                respuesta_clean = respuesta.strip()
                if respuesta_clean.startswith('```json'):
                    respuesta_clean = respuesta_clean[7:]
                if respuesta_clean.endswith('```'):
                    respuesta_clean = respuesta_clean[:-3]
                
                resultado = json.loads(respuesta_clean)
                return Response({
                    'success': True,
                    'query': query,
                    'analisis_intencion': resultado
                })
            except json.JSONDecodeError as e:
                return Response({
                    'error': f'Error al parsear JSON: {e}',
                    'respuesta_raw': respuesta_clean
                }, status=500)
        else:
            return Response({
                'error': 'No se pudo analizar la intención'
            }, status=500)
            
    except Exception as e:
        logger.error(f"Error en analizar_intencion_usuario: {e}")
        return Response({
            'error': f'Error interno: {str(e)}'
        }, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def extraer_caracteristicas_texto(request):
    """
    Extrae características de un texto descriptivo
    
    POST /api/deepseek/extraer-caracteristicas/
    {
        "texto": "Hotel con piscina, gimnasio, spa y restaurante gourmet"
    }
    """
    try:
        texto = request.data.get('texto', '').strip()
        
        if not texto:
            return Response({
                'error': 'El campo "texto" es requerido'
            }, status=400)
        
        prompt = f"""
        Extrae características específicas del siguiente texto:
        
        TEXTO: "{texto}"
        
        Responde con un JSON que contenga:
        
        {{
            "amenidades": ["lista de amenidades físicas"],
            "servicios": ["lista de servicios ofrecidos"],
            "caracteristicas_especiales": ["características únicas"],
            "tipo_experiencia": "tipo de experiencia",
            "nivel_lujo": "nivel de lujo",
            "horario_servicio": "tipo de horario",
            "publico_objetivo": ["tipos de público"],
            "palabras_clave": ["palabras clave para búsquedas"]
        }}
        
        Responde SOLO con el JSON válido.
        """
        
        respuesta = enviar_prompt(prompt)
        
        if respuesta:
            try:
                # Limpiar respuesta
                respuesta_clean = respuesta.strip()
                if respuesta_clean.startswith('```json'):
                    respuesta_clean = respuesta_clean[7:]
                if respuesta_clean.endswith('```'):
                    respuesta_clean = respuesta_clean[:-3]
                
                resultado = json.loads(respuesta_clean)
                return Response({
                    'success': True,
                    'texto': texto,
                    'caracteristicas_extraidas': resultado
                })
            except json.JSONDecodeError as e:
                return Response({
                    'error': f'Error al parsear JSON: {e}',
                    'respuesta_raw': respuesta_clean
                }, status=500)
        else:
            return Response({
                'error': 'No se pudieron extraer características'
            }, status=500)
            
    except Exception as e:
        logger.error(f"Error en extraer_caracteristicas_texto: {e}")
        return Response({
            'error': f'Error interno: {str(e)}'
        }, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def generar_resumen_lugar(request):
    """
    Genera un resumen IA para un lugar
    
    POST /api/deepseek/generar-resumen/
    {
        "nombre": "Hotel Plaza",
        "tipo_principal": "hotel",
        "descripcion": "Hotel de lujo en el centro de la ciudad",
        "rating": 4.5,
        "nivel_precios": "alto"
    }
    """
    try:
        lugar_data = {
            'nombre': request.data.get('nombre', ''),
            'tipo_principal': request.data.get('tipo_principal', ''),
            'descripcion': request.data.get('descripcion', ''),
            'rating': request.data.get('rating', 0),
            'nivel_precios': request.data.get('nivel_precios', ''),
            'direccion': request.data.get('direccion', ''),
            'categoria': request.data.get('categoria', ''),
            'total_ratings': request.data.get('total_ratings', 0),
            'horarios': request.data.get('horarios', []),
            'website': request.data.get('website', ''),
            'telefono': request.data.get('telefono', '')
        }
        
        if not lugar_data['nombre']:
            return Response({
                'error': 'El campo "nombre" es requerido'
            }, status=400)
        
        resumen = generar_resumen_lugar(lugar_data)
        
        if resumen:
            return Response({
                'success': True,
                'lugar': lugar_data,
                'resumen_ia': resumen
            })
        else:
            return Response({
                'error': 'No se pudo generar el resumen'
            }, status=500)
            
    except Exception as e:
        logger.error(f"Error en generar_resumen_lugar: {e}")
        return Response({
            'error': f'Error interno: {str(e)}'
        }, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def extraer_caracteristicas_lugar(request):
    """
    Extrae características específicas de un lugar
    
    POST /api/deepseek/extraer-caracteristicas-lugar/
    {
        "nombre": "Hotel Plaza",
        "tipo_principal": "hotel",
        "descripcion": "Hotel con piscina y spa",
        "resumen_ia": "Hotel de lujo con excelentes amenidades",
        "rating": 4.5,
        "nivel_precios": "alto"
    }
    """
    try:
        lugar_data = {
            'nombre': request.data.get('nombre', ''),
            'tipo_principal': request.data.get('tipo_principal', ''),
            'descripcion': request.data.get('descripcion', ''),
            'resumen_ia': request.data.get('resumen_ia', ''),
            'rating': request.data.get('rating', 0),
            'nivel_precios': request.data.get('nivel_precios', '')
        }
        
        if not lugar_data['nombre']:
            return Response({
                'error': 'El campo "nombre" es requerido'
            }, status=400)
        
        caracteristicas = extraer_caracteristicas_lugar(lugar_data)
        
        if caracteristicas:
            return Response({
                'success': True,
                'lugar': lugar_data,
                'caracteristicas_extraidas': caracteristicas
            })
        else:
            return Response({
                'error': 'No se pudieron extraer características'
            }, status=500)
            
    except Exception as e:
        logger.error(f"Error en extraer_caracteristicas_lugar: {e}")
        return Response({
            'error': f'Error interno: {str(e)}'
        }, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def procesar_lotes_lugares(request):
    """
    Procesa múltiples lugares en lotes
    
    POST /api/deepseek/procesar-lotes/
    {
        "lugares": [
            {
                "id": 1,
                "nombre": "Hotel A",
                "tipo_principal": "hotel",
                "descripcion": "Hotel con piscina"
            },
            {
                "id": 2,
                "nombre": "Restaurante B",
                "tipo_principal": "restaurant",
                "descripcion": "Restaurante gourmet"
            }
        ],
        "tipo_procesamiento": "resumenes" // o "caracteristicas"
    }
    """
    try:
        lugares = request.data.get('lugares', [])
        tipo_procesamiento = request.data.get('tipo_procesamiento', 'resumenes')
        
        if not lugares:
            return Response({
                'error': 'El campo "lugares" es requerido'
            }, status=400)
        
        if tipo_procesamiento not in ['resumenes', 'caracteristicas']:
            return Response({
                'error': 'tipo_procesamiento debe ser "resumenes" o "caracteristicas"'
            }, status=400)
        
        if tipo_procesamiento == 'resumenes':
            resultados = generar_resumenes_lotes(lugares)
        else:
            resultados = extraer_caracteristicas_lotes(lugares)
        
        return Response({
            'success': True,
            'tipo_procesamiento': tipo_procesamiento,
            'lugares_procesados': len(resultados),
            'resultados': resultados
        })
        
    except Exception as e:
        logger.error(f"Error en procesar_lotes_lugares: {e}")
        return Response({
            'error': f'Error interno: {str(e)}'
        }, status=500) 