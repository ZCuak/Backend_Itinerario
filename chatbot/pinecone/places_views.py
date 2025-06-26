from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .places_vector_store import PlacesVectorStore
from ..models import LugarGooglePlaces
from ..deepseek.deepseek import enviar_prompt, limpiar_texto

logger = logging.getLogger(__name__)

# Instancia global del gestor de lugares vectoriales
places_vector_store = None

def get_places_vector_store():
    """Obtener instancia del gestor de lugares vectoriales"""
    global places_vector_store
    if places_vector_store is None:
        print("🔄 Inicializando PlacesVectorStore...")
        try:
            places_vector_store = PlacesVectorStore()
            print("✅ PlacesVectorStore inicializado exitosamente")
        except Exception as e:
            print(f"❌ Error al inicializar PlacesVectorStore: {e}")
            import traceback
            print(f"🔍 Traceback completo: {traceback.format_exc()}")
            raise
    else:
        print("✅ PlacesVectorStore ya inicializado, reutilizando instancia")
    return places_vector_store

@api_view(['POST'])
# # @permission_classes([IsAuthenticated])  # Temporalmente deshabilitado  # Temporalmente deshabilitado
def add_place_to_vector_store(request):
    """
    Agregar un lugar a la base de datos vectorial
    
    POST /api/pinecone/places/add-place/
    {
        "place_id": 123
    }
    """
    try:
        data = request.data
        place_id = data.get('place_id')
        
        if not place_id:
            return Response({
                'error': 'place_id es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener el lugar de la base de datos
        try:
            lugar = LugarGooglePlaces.objects.get(id=place_id, is_active=True)
        except LugarGooglePlaces.DoesNotExist:
            return Response({
                'error': f'Lugar con ID {place_id} no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Agregar a la base de datos vectorial
        vector_store = get_places_vector_store()
        vector_id = vector_store.add_place(lugar)
        
        return Response({
            'success': True,
            'vector_id': vector_id,
            'place_id': place_id,
            'place_name': lugar.nombre,
            'message': 'Lugar agregado exitosamente a la base de datos vectorial'
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        logger.error(f"Error al agregar lugar: {e}")
        return Response({
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])  # Temporalmente deshabilitado
def sync_all_places(request):
    """
    Sincronizar todos los lugares de la base de datos a Pinecone
    
    POST /api/pinecone/places/sync-all/
    {
        "batch_size": 100
    }
    """
    try:
        data = request.data
        batch_size = data.get('batch_size', 100)
        
        # Sincronizar lugares
        vector_store = get_places_vector_store()
        processed_count = vector_store.sync_places_from_database(batch_size=batch_size)
        
        return Response({
            'success': True,
            'processed_count': processed_count,
            'message': f'{processed_count} lugares sincronizados exitosamente'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error en sincronización: {e}")
        return Response({
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])  # Temporalmente deshabilitado
def search_places(request):
    """
    Buscar lugares por consulta semántica
    
    GET /api/pinecone/places/search/?query=hotel con gimnasio&top_k=5
    """
    try:
        query = request.GET.get('query', '').strip()
        top_k = int(request.GET.get('top_k', 5))
        
        print(f"🔍 Iniciando búsqueda de lugares")
        print(f"📝 Query recibida: '{query}'")
        print(f"📊 Top_k solicitado: {top_k}")
        
        if not query:
            print("❌ Query vacía recibida")
            return Response({
                'error': 'query es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Realizar búsqueda
        print("🔄 Inicializando vector store...")
        vector_store = get_places_vector_store()
        print("✅ Vector store inicializado")
        
        print("🔍 Ejecutando búsqueda semántica...")
        results = vector_store.search_places(query, top_k=top_k)
        print(f"📊 Resultados obtenidos: {len(results)}")
        
        # Log detallado de resultados
        if results:
            print("📋 Detalles de resultados:")
            for i, result in enumerate(results[:3]):  # Solo primeros 3
                print(f"  {i+1}. Score: {result.get('score', 'N/A')} - ID: {result.get('id', 'N/A')}")
                if 'metadata' in result:
                    metadata = result['metadata']
                    print(f"     Nombre: {metadata.get('nombre', 'N/A')}")
                    print(f"     Tipo: {metadata.get('tipo_principal', 'N/A')}")
                    print(f"     Rating: {metadata.get('rating', 'N/A')}")
        else:
            print("⚠️ No se encontraron resultados")
        
        return Response({
            'success': True,
            'query': query,
            'results': results,
            'total_results': len(results)
        }, status=status.HTTP_200_OK)
    
    except ValueError as e:
        print(f"❌ Error de parámetros: {e}")
        return Response({
            'error': 'Parámetros inválidos'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"❌ Error en búsqueda de lugares: {e}")
        import traceback
        print(f"🔍 Traceback completo: {traceback.format_exc()}")
        return Response({
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])  # Temporalmente deshabilitado
def find_hotels_with_amenities(request):
    """
    Buscar hoteles con amenidades específicas
    
    GET /api/pinecone/places/hotels-with-amenities/?amenities=gimnasio,piscina&top_k=5
    """
    try:
        amenities_str = request.GET.get('amenities', '').strip()
        top_k = int(request.GET.get('top_k', 5))
        
        if not amenities_str:
            return Response({
                'error': 'amenities es requerido (separado por comas)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Parsear amenidades
        amenities = [amenity.strip() for amenity in amenities_str.split(',') if amenity.strip()]
        
        if not amenities:
            return Response({
                'error': 'Debe proporcionar al menos una amenidad'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscar hoteles con amenidades
        vector_store = get_places_vector_store()
        results = vector_store.find_hotels_with_amenities(amenities, top_k=top_k)
        
        return Response({
            'success': True,
            'amenities': amenities,
            'results': results,
            'total_results': len(results)
        }, status=status.HTTP_200_OK)
    
    except ValueError as e:
        return Response({
            'error': 'Parámetros inválidos'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error al buscar hoteles con amenidades: {e}")
        return Response({
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])  # Temporalmente deshabilitado
def find_places_by_features(request):
    """
    Buscar lugares con características específicas
    
    GET /api/pinecone/places/by-features/?features=restaurante,italiano&top_k=5
    """
    try:
        features_str = request.GET.get('features', '').strip()
        top_k = int(request.GET.get('top_k', 5))
        
        if not features_str:
            return Response({
                'error': 'features es requerido (separado por comas)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Parsear características
        features = [feature.strip() for feature in features_str.split(',') if feature.strip()]
        
        if not features:
            return Response({
                'error': 'Debe proporcionar al menos una característica'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscar lugares con características
        vector_store = get_places_vector_store()
        results = vector_store.find_places_by_features(features, top_k=top_k)
        
        return Response({
            'success': True,
            'features': features,
            'results': results,
            'total_results': len(results)
        }, status=status.HTTP_200_OK)
    
    except ValueError as e:
        return Response({
            'error': 'Parámetros inválidos'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error al buscar lugares por características: {e}")
        return Response({
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])  # Temporalmente deshabilitado
def search_places_by_location(request):
    """
    Buscar lugares por ubicación
    
    GET /api/pinecone/places/by-location/?location=Chiclayo&top_k=5
    """
    try:
        location = request.GET.get('location', '').strip()
        top_k = int(request.GET.get('top_k', 5))
        
        if not location:
            return Response({
                'error': 'location es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscar lugares por ubicación
        vector_store = get_places_vector_store()
        results = vector_store.search_places_by_location(location, top_k=top_k)
        
        return Response({
            'success': True,
            'location': location,
            'results': results,
            'total_results': len(results)
        }, status=status.HTTP_200_OK)
    
    except ValueError as e:
        return Response({
            'error': 'Parámetros inválidos'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error al buscar lugares por ubicación: {e}")
        return Response({
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])  # Temporalmente deshabilitado
def search_places_by_type_and_features(request):
    """
    Buscar lugares por tipo y características específicas
    
    POST /api/pinecone/places/search-by-type-and-features/
    {
        "place_type": "restaurante",
        "features": ["italiano", "terraza"],
        "top_k": 5
    }
    """
    try:
        # Validar datos de entrada
        place_type = request.data.get('place_type')
        features = request.data.get('features', [])
        top_k = request.data.get('top_k', 5)
        
        if not place_type:
            return Response({
                'error': 'El tipo de lugar es requerido'
            }, status=400)
        
        if not features or not isinstance(features, list):
            return Response({
                'error': 'Las características son requeridas y deben ser una lista'
            }, status=400)
        
        # Realizar búsqueda
        vector_store = PlacesVectorStore()
        results = vector_store.find_places_by_type_and_features(
            place_type=place_type,
            features=features,
            top_k=int(top_k)
        )
        
        # Formatear resultados
        formatted_results = []
        for result in results:
            metadata = result['metadata']
            formatted_results.append({
                'id': metadata.get('id'),
                'nombre': metadata.get('nombre'),
                'tipo_principal': metadata.get('tipo_principal'),
                'tipos_adicionales': metadata.get('tipos_adicionales'),
                'categoria': metadata.get('categoria'),
                'rating': metadata.get('rating'),
                'nivel_precios': metadata.get('nivel_precios'),
                'direccion': metadata.get('direccion'),
                'resumen_ia': metadata.get('resumen_ia'),
                'descripcion': metadata.get('descripcion'),
                'horarios': metadata.get('horarios'),
                'score': result['score'],
                'vector_id': result['id']
            })
        
        return Response({
            'success': True,
            'query': {
                'place_type': place_type,
                'features': features
            },
            'total_results': len(formatted_results),
            'results': formatted_results
        })
    
    except Exception as e:
        logger.error(f"Error en búsqueda por tipo y características: {e}")
        return Response({
            'error': f'Error en la búsqueda: {str(e)}'
        }, status=500)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])  # Temporalmente deshabilitado
def search_places_with_rating_and_features(request):
    """
    Buscar lugares con rating específico y características
    
    POST /api/pinecone/places/search-with-rating-and-features/
    {
        "place_type": "restaurante",
        "rating": 4.0,
        "features": ["italiano", "terraza"],
        "rating_tolerance": 0.5,
        "top_k": 5
    }
    """
    try:
        # Validar datos de entrada
        place_type = request.data.get('place_type')
        rating = request.data.get('rating')
        features = request.data.get('features', [])
        rating_tolerance = request.data.get('rating_tolerance', 0.5)
        top_k = request.data.get('top_k', 5)
        
        if not place_type:
            return Response({
                'error': 'El tipo de lugar es requerido'
            }, status=400)
        
        if not rating or not isinstance(rating, (int, float)):
            return Response({
                'error': 'El rating es requerido y debe ser un número'
            }, status=400)
        
        if not features or not isinstance(features, list):
            return Response({
                'error': 'Las características son requeridas y deben ser una lista'
            }, status=400)
        
        # Realizar búsqueda
        vector_store = PlacesVectorStore()
        results = vector_store.find_places_with_rating_and_features(
            place_type=place_type,
            rating=float(rating),
            features=features,
            rating_tolerance=float(rating_tolerance),
            top_k=int(top_k)
        )
        
        # Formatear resultados
        formatted_results = []
        for result in results:
            metadata = result['metadata']
            formatted_results.append({
                'id': metadata.get('id'),
                'nombre': metadata.get('nombre'),
                'tipo_principal': metadata.get('tipo_principal'),
                'tipos_adicionales': metadata.get('tipos_adicionales'),
                'categoria': metadata.get('categoria'),
                'rating': metadata.get('rating'),
                'nivel_precios': metadata.get('nivel_precios'),
                'direccion': metadata.get('direccion'),
                'resumen_ia': metadata.get('resumen_ia'),
                'descripcion': metadata.get('descripcion'),
                'horarios': metadata.get('horarios'),
                'score': result['score'],
                'vector_id': result['id']
            })
        
        return Response({
            'success': True,
            'query': {
                'place_type': place_type,
                'rating': rating,
                'features': features,
                'rating_tolerance': rating_tolerance
            },
            'total_results': len(formatted_results),
            'results': formatted_results
        })
    
    except Exception as e:
        logger.error(f"Error en búsqueda con rating y características: {e}")
        return Response({
            'error': f'Error en la búsqueda: {str(e)}'
        }, status=500)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])  # Temporalmente deshabilitado
def search_places_by_opening_hours(request):
    """
    Buscar lugares por criterios de horario de apertura
    
    POST /api/pinecone/places/search-by-opening-hours/
    {
        "place_type": "restaurante",
        "opening_criteria": "abierto_ahora",
        "features": ["italiano"],
        "top_k": 5
    }
    """
    try:
        # Validar datos de entrada
        place_type = request.data.get('place_type')
        opening_criteria = request.data.get('opening_criteria')
        features = request.data.get('features')
        top_k = request.data.get('top_k', 5)
        
        if not place_type:
            return Response({
                'error': 'El tipo de lugar es requerido'
            }, status=400)
        
        if not opening_criteria:
            return Response({
                'error': 'El criterio de horario es requerido'
            }, status=400)
        
        # Validar criterio de horario
        valid_criteria = ['abierto_ahora', '24_horas', 'fines_semana', 'lunes_viernes']
        if opening_criteria not in valid_criteria:
            return Response({
                'error': f'Criterio de horario inválido. Debe ser uno de: {valid_criteria}'
            }, status=400)
        
        # Realizar búsqueda
        vector_store = PlacesVectorStore()
        results = vector_store.find_places_by_opening_hours(
            place_type=place_type,
            opening_criteria=opening_criteria,
            features=features,
            top_k=int(top_k)
        )
        
        # Formatear resultados
        formatted_results = []
        for result in results:
            metadata = result['metadata']
            formatted_results.append({
                'id': metadata.get('id'),
                'nombre': metadata.get('nombre'),
                'tipo_principal': metadata.get('tipo_principal'),
                'tipos_adicionales': metadata.get('tipos_adicionales'),
                'categoria': metadata.get('categoria'),
                'rating': metadata.get('rating'),
                'nivel_precios': metadata.get('nivel_precios'),
                'direccion': metadata.get('direccion'),
                'resumen_ia': metadata.get('resumen_ia'),
                'descripcion': metadata.get('descripcion'),
                'horarios': metadata.get('horarios'),
                'score': result['score'],
                'vector_id': result['id']
            })
        
        return Response({
            'success': True,
            'query': {
                'place_type': place_type,
                'opening_criteria': opening_criteria,
                'features': features
            },
            'total_results': len(formatted_results),
            'results': formatted_results
        })
    
    except Exception as e:
        logger.error(f"Error en búsqueda por horarios: {e}")
        return Response({
            'error': f'Error en la búsqueda: {str(e)}'
        }, status=500)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])  # Temporalmente deshabilitado
def search_places_by_category_and_features(request):
    """
    Buscar lugares por categoría y características
    
    POST /api/pinecone/places/search-by-category-and-features/
    {
        "category": "restaurantes",
        "features": ["italiano", "terraza"],
        "rating_min": 4.0,
        "top_k": 5
    }
    """
    try:
        # Validar datos de entrada
        category = request.data.get('category')
        features = request.data.get('features', [])
        rating_min = request.data.get('rating_min')
        top_k = request.data.get('top_k', 5)
        
        if not category:
            return Response({
                'error': 'La categoría es requerida'
            }, status=400)
        
        if not features or not isinstance(features, list):
            return Response({
                'error': 'Las características son requeridas y deben ser una lista'
            }, status=400)
        
        # Realizar búsqueda
        vector_store = PlacesVectorStore()
        results = vector_store.find_places_by_category_and_features(
            category=category,
            features=features,
            rating_min=float(rating_min) if rating_min else None,
            top_k=int(top_k)
        )
        
        # Formatear resultados
        formatted_results = []
        for result in results:
            metadata = result['metadata']
            formatted_results.append({
                'id': metadata.get('id'),
                'nombre': metadata.get('nombre'),
                'tipo_principal': metadata.get('tipo_principal'),
                'tipos_adicionales': metadata.get('tipos_adicionales'),
                'categoria': metadata.get('categoria'),
                'rating': metadata.get('rating'),
                'nivel_precios': metadata.get('nivel_precios'),
                'direccion': metadata.get('direccion'),
                'resumen_ia': metadata.get('resumen_ia'),
                'descripcion': metadata.get('descripcion'),
                'horarios': metadata.get('horarios'),
                'score': result['score'],
                'vector_id': result['id']
            })
        
        return Response({
            'success': True,
            'query': {
                'category': category,
                'features': features,
                'rating_min': rating_min
            },
            'total_results': len(formatted_results),
            'results': formatted_results
        })
    
    except Exception as e:
        logger.error(f"Error en búsqueda por categoría: {e}")
        return Response({
            'error': f'Error en la búsqueda: {str(e)}'
        }, status=500)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])  # Temporalmente deshabilitado
def smart_place_search(request):
    """
    Búsqueda inteligente que combina múltiples criterios
    
    POST /api/pinecone/places/smart-search/
    {
        "place_type": "restaurante",
        "category": "restaurantes",
        "features": ["italiano", "terraza"],
        "rating_min": 4.0,
        "rating_max": 5.0,
        "opening_hours": "abierto_ahora",
        "location": "Chiclayo centro",
        "price_level": "moderado",
        "top_k": 5
    }
    """
    try:
        # Validar datos de entrada
        search_criteria = request.data.get('search_criteria', {})
        top_k = request.data.get('top_k', 5)
        
        if not search_criteria:
            return Response({
                'error': 'Los criterios de búsqueda son requeridos'
            }, status=400)
        
        # Realizar búsqueda
        vector_store = PlacesVectorStore()
        results = vector_store.smart_place_search(
            search_criteria=search_criteria,
            top_k=int(top_k)
        )
        
        # Formatear resultados
        formatted_results = []
        for result in results:
            metadata = result['metadata']
            formatted_results.append({
                'id': metadata.get('id'),
                'nombre': metadata.get('nombre'),
                'tipo_principal': metadata.get('tipo_principal'),
                'tipos_adicionales': metadata.get('tipos_adicionales'),
                'categoria': metadata.get('categoria'),
                'rating': metadata.get('rating'),
                'nivel_precios': metadata.get('nivel_precios'),
                'direccion': metadata.get('direccion'),
                'resumen_ia': metadata.get('resumen_ia'),
                'descripcion': metadata.get('descripcion'),
                'horarios': metadata.get('horarios'),
                'score': result['score'],
                'vector_id': result['id']
            })
        
        return Response({
            'success': True,
            'query': search_criteria,
            'total_results': len(formatted_results),
            'results': formatted_results
        })
    
    except Exception as e:
        logger.error(f"Error en búsqueda inteligente: {e}")
        return Response({
            'error': f'Error en la búsqueda: {str(e)}'
        }, status=500)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])  # Temporalmente deshabilitado
def get_places_stats(request):
    """
    Obtener estadísticas del índice de lugares
    
    GET /api/pinecone/places/stats/
    """
    try:
        vector_store = get_places_vector_store()
        stats = vector_store.get_index_stats()
        
        return Response({
            'success': True,
            'stats': stats
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        return Response({
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])  # Temporalmente deshabilitado
def clear_places_index(request):
    """
    Limpiar todo el contenido del índice de lugares (solo para administradores)
    
    POST /api/pinecone/places/clear-index/
    """
    try:
        # Verificar si el usuario es administrador
        # if not request.user.is_staff:  # Temporalmente deshabilitado
        #     return Response({
        #         'error': 'Acceso denegado. Se requieren permisos de administrador.'
        #     }, status=status.HTTP_403_FORBIDDEN)
        
        vector_store = get_places_vector_store()
        success = vector_store.clear_index()
        
        if success:
            return Response({
                'success': True,
                'message': 'Índice de lugares limpiado exitosamente'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Error al limpiar el índice'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"Error al limpiar índice de lugares: {e}")
        return Response({
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])  # Temporalmente deshabilitado
def search_hotels_with_rating_and_amenities(request):
    """
    Buscar hoteles con rating específico y amenidades
    
    POST /api/pinecone/places/search_hotels_with_rating_and_amenities/
    {
        "rating": 3.0,
        "amenities": ["restaurante", "gimnasio"],
        "rating_tolerance": 0.5,
        "top_k": 5
    }
    """
    try:
        # Validar datos de entrada
        rating = request.data.get('rating')
        amenities = request.data.get('amenities', [])
        rating_tolerance = request.data.get('rating_tolerance', 0.5)
        top_k = request.data.get('top_k', 5)
        
        if not rating or not isinstance(rating, (int, float)):
            return Response({
                'error': 'El rating es requerido y debe ser un número'
            }, status=400)
        
        if not amenities or not isinstance(amenities, list):
            return Response({
                'error': 'Las amenidades son requeridas y deben ser una lista'
            }, status=400)
        
        # Realizar búsqueda
        vector_store = PlacesVectorStore()
        results = vector_store.find_hotels_with_rating_and_amenities(
            rating=float(rating),
            amenities=amenities,
            rating_tolerance=float(rating_tolerance),
            top_k=int(top_k)
        )
        
        # Formatear resultados
        formatted_results = []
        for result in results:
            metadata = result['metadata']
            formatted_results.append({
                'id': metadata.get('id'),
                'nombre': metadata.get('nombre'),
                'tipo_principal': metadata.get('tipo_principal'),
                'rating': metadata.get('rating'),
                'total_ratings': metadata.get('total_ratings'),
                'nivel_precios': metadata.get('nivel_precios'),
                'direccion': metadata.get('direccion'),
                'resumen_ia': metadata.get('resumen_ia'),
                'descripcion': metadata.get('descripcion'),
                'score': result['score'],
                'vector_id': result['id']
            })
        
        return Response({
            'success': True,
            'query': {
                'rating': rating,
                'amenities': amenities,
                'rating_tolerance': rating_tolerance
            },
            'total_results': len(formatted_results),
            'results': formatted_results
        })
    
    except Exception as e:
        logger.error(f"Error en búsqueda de hoteles con rating y amenidades: {e}")
        return Response({
            'error': f'Error en la búsqueda: {str(e)}'
        }, status=500)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])  # Temporalmente deshabilitado
def search_hotels_by_rating_range(request):
    """
    Buscar hoteles en un rango de rating específico
    
    POST /api/pinecone/places/search_hotels_by_rating_range/
    {
        "min_rating": 3.0,
        "max_rating": 4.0,
        "amenities": ["restaurante"],
        "top_k": 5
    }
    """
    try:
        # Validar datos de entrada
        min_rating = request.data.get('min_rating')
        max_rating = request.data.get('max_rating')
        amenities = request.data.get('amenities')
        top_k = request.data.get('top_k', 5)
        
        if not min_rating or not isinstance(min_rating, (int, float)):
            return Response({
                'error': 'El rating mínimo es requerido y debe ser un número'
            }, status=400)
        
        if not max_rating or not isinstance(max_rating, (int, float)):
            return Response({
                'error': 'El rating máximo es requerido y debe ser un número'
            }, status=400)
        
        if float(min_rating) > float(max_rating):
            return Response({
                'error': 'El rating mínimo no puede ser mayor al rating máximo'
            }, status=400)
        
        # Realizar búsqueda
        vector_store = PlacesVectorStore()
        results = vector_store.find_hotels_by_rating_range(
            min_rating=float(min_rating),
            max_rating=float(max_rating),
            amenities=amenities,
            top_k=int(top_k)
        )
        
        # Formatear resultados
        formatted_results = []
        for result in results:
            metadata = result['metadata']
            formatted_results.append({
                'id': metadata.get('id'),
                'nombre': metadata.get('nombre'),
                'tipo_principal': metadata.get('tipo_principal'),
                'rating': metadata.get('rating'),
                'total_ratings': metadata.get('total_ratings'),
                'nivel_precios': metadata.get('nivel_precios'),
                'direccion': metadata.get('direccion'),
                'resumen_ia': metadata.get('resumen_ia'),
                'descripcion': metadata.get('descripcion'),
                'score': result['score'],
                'vector_id': result['id']
            })
        
        return Response({
            'success': True,
            'query': {
                'min_rating': min_rating,
                'max_rating': max_rating,
                'amenities': amenities
            },
            'total_results': len(formatted_results),
            'results': formatted_results
        })
    
    except Exception as e:
        logger.error(f"Error en búsqueda de hoteles por rango de rating: {e}")
        return Response({
            'error': f'Error en la búsqueda: {str(e)}'
        }, status=500)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])  # Temporalmente deshabilitado
def search_places_by_price_level(request):
    """
    Buscar lugares por nivel de precios
    
    POST /api/pinecone/places/search-by-price-level/
    {
        "price_level": "económico",
        "place_type": "restaurante",
        "features": ["italiano"],
        "top_k": 5
    }
    """
    try:
        # Validar datos de entrada
        price_level = request.data.get('price_level')
        place_type = request.data.get('place_type')
        features = request.data.get('features')
        top_k = request.data.get('top_k', 5)
        
        if not price_level:
            return Response({
                'error': 'El nivel de precio es requerido'
            }, status=400)
        
        # Validar nivel de precio
        valid_price_levels = ['gratis', 'económico', 'barato', 'accesible', 'moderado', 'medio', 'normal', 'caro', 'lujoso', 'exclusivo', 'premium']
        if price_level.lower() not in valid_price_levels and not price_level.isdigit():
            return Response({
                'error': f'Nivel de precio inválido. Debe ser uno de: {valid_price_levels} o un número del 0-4'
            }, status=400)
        
        # Realizar búsqueda
        vector_store = PlacesVectorStore()
        results = vector_store.find_places_by_price_level(
            price_level=price_level,
            place_type=place_type,
            features=features,
            top_k=int(top_k)
        )
        
        # Formatear resultados
        formatted_results = []
        for result in results:
            metadata = result['metadata']
            formatted_results.append({
                'id': metadata.get('id'),
                'nombre': metadata.get('nombre'),
                'tipo_principal': metadata.get('tipo_principal'),
                'tipos_adicionales': metadata.get('tipos_adicionales'),
                'categoria': metadata.get('categoria'),
                'rating': metadata.get('rating'),
                'nivel_precios': metadata.get('nivel_precios'),
                'direccion': metadata.get('direccion'),
                'resumen_ia': metadata.get('resumen_ia'),
                'descripcion': metadata.get('descripcion'),
                'horarios': metadata.get('horarios'),
                'score': result['score'],
                'vector_id': result['id']
            })
        
        return Response({
            'success': True,
            'query': {
                'price_level': price_level,
                'place_type': place_type,
                'features': features
            },
            'total_results': len(formatted_results),
            'results': formatted_results
        })
    
    except Exception as e:
        logger.error(f"Error en búsqueda por nivel de precio: {e}")
        return Response({
            'error': f'Error en la búsqueda: {str(e)}'
        }, status=500)

def extract_search_criteria_from_message(user_message: str) -> dict:
    """
    Extrae criterios de búsqueda del mensaje natural del usuario usando DeepSeek
    
    Args:
        user_message: Mensaje natural del usuario
        
    Returns:
        Diccionario con criterios de búsqueda extraídos
    """
    try:
        # Prompt para DeepSeek que extraiga criterios de búsqueda
        prompt = f"""
        Eres un asistente experto en extraer criterios de búsqueda de lugares turísticos. 
        Analiza el siguiente mensaje del usuario y extrae los criterios de búsqueda relevantes.
        
        Mensaje del usuario: "{user_message}"
        
        Extrae y devuelve SOLO un JSON válido con los siguientes campos (usa null si no se menciona):
        
        {{
            "place_type": "tipo de lugar (debe ser uno de estos valores exactos en inglés: hotel, lodging, event_venue, restaurant, food, point_of_interest, establishment, bakery, coffee_shop, cafe, dessert_shop, confectionery, food_store, store, ice_cream_shop, hamburger_restaurant, american_restaurant, chinese_restaurant, bar, night_club, inn, casino, aquarium, beach, natural_feature, market, tourist_attraction, park, museum, church, place_of_worship, historical_landmark, amusement_park, amusement_center, historical_place, bar_and_grill, cafeteria, brunch_restaurant, home_goods_store, art_gallery, painter, shopping_mall, courier_service, supermarket, grocery_store, wholesaler, discount_store, department_store, clothing_store, sporting_goods_store, furniture_store, home_improvement_store, water_park, movie_theater)",
            "features": ["características mencionadas (ej: italiano, terraza, música en vivo)"],
            "rating_min": número mínimo de estrellas mencionado,
            "rating_max": número máximo de estrellas mencionado,
            "opening_hours": "criterio de horario (ej: abierto_ahora, 24_horas, fines_semana, lunes_viernes)",
            "location": "ubicación mencionada",
            "price_level": "nivel de precios mencionado (ej: económico, moderado, caro, muy caro, barato, lujoso)",
            "intent": "intención principal del usuario (ej: comer, dormir, entretenimiento, compras)"
        }}
        
        Reglas importantes:
        1. Si menciona "comer", "almorzar", "cenar" → intent: "comer"
        2. Si menciona "dormir", "alojarse", "hospedarse" → intent: "dormir"
        3. Si menciona "estrellas" o "rating" → extrae el número
        4. Si menciona "abierto", "ahora", "actual" → opening_hours: "abierto_ahora"
        5. Si menciona "24 horas" → opening_hours: "24_horas"
        6. Si menciona "fines de semana" → opening_hours: "fines_semana"
        7. Si menciona "lunes a viernes" → opening_hours: "lunes_viernes"
        
        Reglas específicas para precios (según rangos específicos):
        8. Si menciona "gratis", "sin costo", "sin pago" → price_level: "gratis" (Nivel 0: 0.00 PEN)
        9. Si menciona "barato", "económico", "accesible", "bajo" → price_level: "económico" (Nivel 1: 0.00-50.00 PEN)
        10. Si menciona "moderado", "medio", "normal", "estándar" → price_level: "moderado" (Nivel 2: 50.00-150.00 PEN)
        11. Si menciona "caro", "elevado", "alto" → price_level: "caro" (Nivel 3: 150.00-400.00 PEN)
        12. Si menciona "muy caro", "lujoso", "exclusivo", "premium", "alta cocina", "estrellas michelin" → price_level: "muy caro" (Nivel 4: 400.00-1000.00 PEN)
        13. Si menciona "nivel 1", "nivel 2", "nivel 3", "nivel 4" → extrae el número como price_level
        14. Si menciona rangos específicos como "S/ 20-50", "50-150", "hasta 100" → incluir en features: ["precio S/ 20-50"]
        15. Si menciona "no muy caro", "no caro", "económico" → price_level: "moderado"
        16. Si menciona "de lujo", "exclusivo", "premium" → price_level: "muy caro"
        
        Ejemplos de mapeo de precios:
        - "restaurante barato" → price_level: "económico"
        - "hotel de lujo" → price_level: "muy caro"
        - "café moderado" → price_level: "moderado"
        - "lugar gratis" → price_level: "gratis"
        - "restaurante de alta cocina" → price_level: "muy caro"
        - "hotel económico" → price_level: "económico"
        
        Responde SOLO con el JSON válido, sin texto adicional.
        """
        
        # Enviar a DeepSeek
        response = enviar_prompt(prompt)
        
        if not response:
            logger.error("No se pudo obtener respuesta de DeepSeek")
            return {}
        
        # Limpiar respuesta
        response_clean = limpiar_texto(response)
        
        # Extraer JSON de la respuesta
        try:
            # Buscar JSON en la respuesta
            json_start = response_clean.find('{')
            json_end = response_clean.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = response_clean[json_start:json_end]
                criteria = json.loads(json_str)
                
                # Validar y limpiar criterios
                validated_criteria = {}
                
                if criteria.get('place_type'):
                    validated_criteria['place_type'] = criteria['place_type'].lower()
                
                if criteria.get('features') and isinstance(criteria['features'], list):
                    validated_criteria['features'] = [f.lower() for f in criteria['features'] if f]
                
                if criteria.get('rating_min') and isinstance(criteria['rating_min'], (int, float)):
                    validated_criteria['rating_min'] = float(criteria['rating_min'])
                
                if criteria.get('rating_max') and isinstance(criteria['rating_max'], (int, float)):
                    validated_criteria['rating_max'] = float(criteria['rating_max'])
                
                if criteria.get('opening_hours'):
                    validated_criteria['opening_hours'] = criteria['opening_hours']
                
                if criteria.get('location'):
                    validated_criteria['location'] = criteria['location']
                
                if criteria.get('price_level'):
                    validated_criteria['price_level'] = criteria['price_level']
                
                if criteria.get('intent'):
                    validated_criteria['intent'] = criteria['intent']
                
                logger.info(f"Criterios extraídos: {validated_criteria}")
                return validated_criteria
                
            else:
                logger.error("No se encontró JSON válido en la respuesta de DeepSeek")
                return {}
                
        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear JSON de DeepSeek: {e}")
            logger.error(f"Respuesta recibida: {response_clean}")
            return {}
            
    except Exception as e:
        logger.error(f"Error al extraer criterios de búsqueda: {e}")
        return {}

@api_view(['POST'])
# @permission_classes([IsAuthenticated])  # Temporalmente deshabilitado
def process_natural_search(request):
    """
    Procesa un mensaje natural del usuario y realiza búsqueda automática
    
    POST /api/pinecone/places/process-natural-search/
    {
        "user_message": "para comer quiero ir a una cafetería de 4 estrellas"
    }
    """
    try:
        # Validar datos de entrada
        user_message = request.data.get('user_message', '').strip()
        
        if not user_message:
            return Response({
                'error': 'El mensaje del usuario es requerido'
            }, status=400)
        
        logger.info(f"Procesando mensaje natural: {user_message}")
        
        # Extraer criterios de búsqueda usando DeepSeek
        search_criteria = extract_search_criteria_from_message(user_message)
        
        if not search_criteria:
            return Response({
                'error': 'No se pudieron extraer criterios de búsqueda del mensaje'
            }, status=400)
        
        # Realizar búsqueda usando los criterios extraídos
        vector_store = PlacesVectorStore()
        
        # Determinar qué tipo de búsqueda realizar basado en los criterios
        results = []
        search_method = "smart_search"
        
        # Si solo tenemos tipo de lugar y características, usar búsqueda específica
        if search_criteria.get('place_type') and search_criteria.get('features') and not search_criteria.get('rating_min'):
            results = vector_store.find_places_by_type_and_features(
                place_type=search_criteria['place_type'],
                features=search_criteria['features'],
                top_k=5
            )
            search_method = "type_and_features"
        
        # Si tenemos rating específico, usar búsqueda con rating
        elif search_criteria.get('place_type') and search_criteria.get('rating_min') and search_criteria.get('features'):
            results = vector_store.find_places_with_rating_and_features(
                place_type=search_criteria['place_type'],
                rating=search_criteria['rating_min'],
                features=search_criteria['features'],
                top_k=5
            )
            search_method = "rating_and_features"
        
        # Si tenemos criterios de horario, usar búsqueda por horarios
        elif search_criteria.get('place_type') and search_criteria.get('opening_hours'):
            results = vector_store.find_places_by_opening_hours(
                place_type=search_criteria['place_type'],
                opening_criteria=search_criteria['opening_hours'],
                features=search_criteria.get('features'),
                top_k=5
            )
            search_method = "opening_hours"
        
        # Si tenemos nivel de precios específico, usar búsqueda por precio
        elif search_criteria.get('price_level'):
            results = vector_store.find_places_by_price_level(
                price_level=search_criteria['price_level'],
                place_type=search_criteria.get('place_type'),
                features=search_criteria.get('features'),
                top_k=5
            )
            search_method = "price_level"
        
        # Si tenemos múltiples criterios, usar búsqueda inteligente
        else:
            results = vector_store.smart_place_search(
                search_criteria=search_criteria,
                top_k=5
            )
            search_method = "smart_search"
        
        # Formatear resultados
        formatted_results = []
        for result in results:
            metadata = result['metadata']
            formatted_results.append({
                'id': metadata.get('id'),
                'nombre': metadata.get('nombre'),
                'tipo_principal': metadata.get('tipo_principal'),
                'tipos_adicionales': metadata.get('tipos_adicionales'),
                'categoria': metadata.get('categoria'),
                'rating': metadata.get('rating'),
                'nivel_precios': metadata.get('nivel_precios'),
                'direccion': metadata.get('direccion'),
                'resumen_ia': metadata.get('resumen_ia'),
                'descripcion': metadata.get('descripcion'),
                'horarios': metadata.get('horarios'),
                'score': result['score'],
                'vector_id': result['id']
            })
        
        return Response({
            'success': True,
            'user_message': user_message,
            'extracted_criteria': search_criteria,
            'search_method_used': search_method,
            'total_results': len(formatted_results),
            'results': formatted_results
        })
    
    except Exception as e:
        logger.error(f"Error en procesamiento de búsqueda natural: {e}")
        return Response({
            'error': f'Error en el procesamiento: {str(e)}'
        }, status=500) 