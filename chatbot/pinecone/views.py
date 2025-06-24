from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import logging
import json

from .memory_manager import ChatbotMemoryManager
from .vector_store import PineconeVectorStore

logger = logging.getLogger(__name__)

# Instancia global del gestor de memoria
memory_manager = None

def get_memory_manager():
    """Obtener instancia del gestor de memoria"""
    global memory_manager
    if memory_manager is None:
        memory_manager = ChatbotMemoryManager()
    return memory_manager

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def store_conversation(request):
    """
    Almacenar una conversación en la memoria del chatbot
    
    POST /api/pinecone/store-conversation/
    {
        "user_message": "Mensaje del usuario",
        "bot_response": "Respuesta del bot",
        "context": {"additional": "data"}
    }
    """
    try:
        user_id = str(request.user.id)
        data = request.data
        
        user_message = data.get('user_message', '').strip()
        bot_response = data.get('bot_response', '').strip()
        context = data.get('context', {})
        
        if not user_message or not bot_response:
            return Response({
                'error': 'user_message y bot_response son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        memory_manager = get_memory_manager()
        vector_id = memory_manager.store_conversation(
            user_id=user_id,
            user_message=user_message,
            bot_response=bot_response,
            context=context
        )
        
        return Response({
            'success': True,
            'vector_id': vector_id,
            'message': 'Conversación almacenada exitosamente'
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        logger.error(f"Error al almacenar conversación: {e}")
        return Response({
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def store_preference(request):
    """
    Almacenar una preferencia del usuario
    
    POST /api/pinecone/store-preference/
    {
        "preference_text": "Texto de la preferencia",
        "category": "categoria_preferencia",
        "context": {"additional": "data"}
    }
    """
    try:
        user_id = str(request.user.id)
        data = request.data
        
        preference_text = data.get('preference_text', '').strip()
        category = data.get('category', 'general').strip()
        context = data.get('context', {})
        
        if not preference_text:
            return Response({
                'error': 'preference_text es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        memory_manager = get_memory_manager()
        vector_id = memory_manager.store_user_preference(
            user_id=user_id,
            preference_text=preference_text,
            category=category,
            context=context
        )
        
        return Response({
            'success': True,
            'vector_id': vector_id,
            'message': 'Preferencia almacenada exitosamente'
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        logger.error(f"Error al almacenar preferencia: {e}")
        return Response({
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_memory(request):
    """
    Buscar en la memoria del usuario
    
    GET /api/pinecone/search-memory/?query=texto&top_k=5&conversation_type=chat
    """
    try:
        user_id = str(request.user.id)
        query = request.GET.get('query', '').strip()
        top_k = int(request.GET.get('top_k', 5))
        conversation_type = request.GET.get('conversation_type')
        
        if not query:
            return Response({
                'error': 'query es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        memory_manager = get_memory_manager()
        results = memory_manager.search_user_memory(
            user_id=user_id,
            query=query,
            top_k=top_k,
            conversation_type=conversation_type
        )
        
        return Response({
            'success': True,
            'results': results,
            'total_results': len(results)
        }, status=status.HTTP_200_OK)
    
    except ValueError as e:
        return Response({
            'error': 'Parámetros inválidos'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error en búsqueda de memoria: {e}")
        return Response({
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_context(request):
    """
    Obtener contexto del usuario para una consulta
    
    GET /api/pinecone/get-context/?query=texto&max_results=3
    """
    try:
        user_id = str(request.user.id)
        query = request.GET.get('query', '').strip()
        max_results = int(request.GET.get('max_results', 3))
        
        if not query:
            return Response({
                'error': 'query es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        memory_manager = get_memory_manager()
        context = memory_manager.get_user_context(
            user_id=user_id,
            query=query,
            max_results=max_results
        )
        
        return Response({
            'success': True,
            'context': context
        }, status=status.HTTP_200_OK)
    
    except ValueError as e:
        return Response({
            'error': 'Parámetros inválidos'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error al obtener contexto: {e}")
        return Response({
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recent_conversations(request):
    """
    Obtener conversaciones recientes del usuario
    
    GET /api/pinecone/recent-conversations/?hours=24&max_results=10
    """
    try:
        user_id = str(request.user.id)
        hours = int(request.GET.get('hours', 24))
        max_results = int(request.GET.get('max_results', 10))
        
        memory_manager = get_memory_manager()
        conversations = memory_manager.get_recent_conversations(
            user_id=user_id,
            hours=hours,
            max_results=max_results
        )
        
        return Response({
            'success': True,
            'conversations': conversations,
            'total_conversations': len(conversations)
        }, status=status.HTTP_200_OK)
    
    except ValueError as e:
        return Response({
            'error': 'Parámetros inválidos'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error al obtener conversaciones recientes: {e}")
        return Response({
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_memory(request):
    """
    Eliminar toda la memoria del usuario
    
    DELETE /api/pinecone/delete-memory/
    """
    try:
        user_id = str(request.user.id)
        
        memory_manager = get_memory_manager()
        success = memory_manager.delete_user_memory(user_id=user_id)
        
        if success:
            return Response({
                'success': True,
                'message': 'Memoria del usuario eliminada exitosamente'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Error al eliminar la memoria'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"Error al eliminar memoria: {e}")
        return Response({
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_memory_stats(request):
    """
    Obtener estadísticas de la memoria
    
    GET /api/pinecone/memory-stats/
    """
    try:
        user_id = str(request.user.id)
        
        memory_manager = get_memory_manager()
        stats = memory_manager.get_memory_stats(user_id=user_id)
        
        return Response({
            'success': True,
            'stats': stats
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        return Response({
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_index_stats(request):
    """
    Obtener estadísticas globales del índice de Pinecone
    
    GET /api/pinecone/index-stats/
    """
    try:
        vector_store = PineconeVectorStore()
        stats = vector_store.get_index_stats()
        
        return Response({
            'success': True,
            'stats': stats
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error al obtener estadísticas del índice: {e}")
        return Response({
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_index(request):
    """
    Limpiar todo el contenido del índice (solo para administradores)
    
    POST /api/pinecone/clear-index/
    """
    try:
        # Verificar si el usuario es administrador (puedes ajustar esta lógica)
        if not request.user.is_staff:
            return Response({
                'error': 'Acceso denegado. Se requieren permisos de administrador.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        vector_store = PineconeVectorStore()
        success = vector_store.clear_index()
        
        if success:
            return Response({
                'success': True,
                'message': 'Índice limpiado exitosamente'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Error al limpiar el índice'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"Error al limpiar índice: {e}")
        return Response({
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 