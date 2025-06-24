from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import json

from .vector_store import PineconeVectorStore

logger = logging.getLogger(__name__)

class ChatbotMemoryManager:
    """Gestor de memoria para el chatbot usando Pinecone"""
    
    def __init__(self):
        """Inicializar el gestor de memoria"""
        self.vector_store = PineconeVectorStore()
        logger.info("ChatbotMemoryManager inicializado")
    
    def store_conversation(self, user_id: str, user_message: str, bot_response: str, 
                          context: Optional[Dict[str, Any]] = None) -> str:
        """
        Almacenar una conversación en la memoria
        
        Args:
            user_id: ID del usuario
            user_message: Mensaje del usuario
            bot_response: Respuesta del bot
            context: Contexto adicional
            
        Returns:
            ID del vector almacenado
        """
        try:
            # Crear texto combinado para el embedding
            conversation_text = f"Usuario: {user_message}\nBot: {bot_response}"
            
            # Preparar metadatos
            metadata = {
                'user_id': user_id,
                'user_message': user_message,
                'bot_response': bot_response,
                'conversation_type': 'chat',
                'timestamp': datetime.now().isoformat()
            }
            
            if context:
                metadata.update(context)
            
            # Almacenar en Pinecone
            vector_id = self.vector_store.add_text(conversation_text, metadata)
            
            logger.info(f"Conversación almacenada para usuario {user_id}")
            return vector_id
        
        except Exception as e:
            logger.error(f"Error al almacenar conversación: {e}")
            raise
    
    def store_user_preference(self, user_id: str, preference_text: str, 
                             category: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Almacenar preferencias del usuario
        
        Args:
            user_id: ID del usuario
            preference_text: Texto de la preferencia
            category: Categoría de la preferencia
            context: Contexto adicional
            
        Returns:
            ID del vector almacenado
        """
        try:
            # Preparar metadatos
            metadata = {
                'user_id': user_id,
                'preference_text': preference_text,
                'category': category,
                'conversation_type': 'preference',
                'timestamp': datetime.now().isoformat()
            }
            
            if context:
                metadata.update(context)
            
            # Almacenar en Pinecone
            vector_id = self.vector_store.add_text(preference_text, metadata)
            
            logger.info(f"Preferencia almacenada para usuario {user_id}: {category}")
            return vector_id
        
        except Exception as e:
            logger.error(f"Error al almacenar preferencia: {e}")
            raise
    
    def search_user_memory(self, user_id: str, query: str, top_k: int = 5, 
                          conversation_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Buscar en la memoria del usuario
        
        Args:
            user_id: ID del usuario
            query: Consulta de búsqueda
            top_k: Número máximo de resultados
            conversation_type: Tipo de conversación a filtrar
            
        Returns:
            Lista de resultados relevantes
        """
        try:
            # Preparar filtros
            filter_dict = {'user_id': user_id}
            if conversation_type:
                filter_dict['conversation_type'] = conversation_type
            
            # Realizar búsqueda
            results = self.vector_store.search(query, top_k=top_k, filter_dict=filter_dict)
            
            logger.info(f"Búsqueda completada para usuario {user_id}: {len(results)} resultados")
            return results
        
        except Exception as e:
            logger.error(f"Error en búsqueda de memoria: {e}")
            raise
    
    def get_user_context(self, user_id: str, query: str, max_results: int = 3) -> str:
        """
        Obtener contexto del usuario para una consulta específica
        
        Args:
            user_id: ID del usuario
            query: Consulta actual
            max_results: Número máximo de resultados a incluir
            
        Returns:
            Contexto formateado como texto
        """
        try:
            # Buscar conversaciones relevantes
            conversation_results = self.search_user_memory(
                user_id, query, top_k=max_results, conversation_type='chat'
            )
            
            # Buscar preferencias relevantes
            preference_results = self.search_user_memory(
                user_id, query, top_k=max_results, conversation_type='preference'
            )
            
            # Construir contexto
            context_parts = []
            
            if conversation_results:
                context_parts.append("Conversaciones anteriores relevantes:")
                for result in conversation_results:
                    metadata = result['metadata']
                    context_parts.append(f"- Usuario: {metadata.get('user_message', '')}")
                    context_parts.append(f"  Bot: {metadata.get('bot_response', '')}")
            
            if preference_results:
                context_parts.append("\nPreferencias del usuario:")
                for result in preference_results:
                    metadata = result['metadata']
                    context_parts.append(f"- {metadata.get('category', 'General')}: {metadata.get('preference_text', '')}")
            
            return "\n".join(context_parts) if context_parts else "No hay contexto previo relevante."
        
        except Exception as e:
            logger.error(f"Error al obtener contexto: {e}")
            return "Error al obtener contexto del usuario."
    
    def get_recent_conversations(self, user_id: str, hours: int = 24, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Obtener conversaciones recientes del usuario
        
        Args:
            user_id: ID del usuario
            hours: Horas hacia atrás para buscar
            max_results: Número máximo de resultados
            
        Returns:
            Lista de conversaciones recientes
        """
        try:
            # Calcular timestamp límite
            time_limit = datetime.now() - timedelta(hours=hours)
            
            # Buscar conversaciones recientes
            results = self.search_user_memory(
                user_id, "", top_k=max_results, conversation_type='chat'
            )
            
            # Filtrar por tiempo
            recent_conversations = []
            for result in results:
                metadata = result['metadata']
                timestamp_str = metadata.get('timestamp', '')
                
                if timestamp_str:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str)
                        if timestamp >= time_limit:
                            recent_conversations.append(result)
                    except ValueError:
                        # Si no se puede parsear el timestamp, incluir de todas formas
                        recent_conversations.append(result)
            
            logger.info(f"Obtenidas {len(recent_conversations)} conversaciones recientes para usuario {user_id}")
            return recent_conversations
        
        except Exception as e:
            logger.error(f"Error al obtener conversaciones recientes: {e}")
            return []
    
    def delete_user_memory(self, user_id: str) -> bool:
        """
        Eliminar toda la memoria de un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            # Buscar todos los vectores del usuario
            results = self.search_user_memory(user_id, "", top_k=1000)
            
            if results:
                vector_ids = [result['id'] for result in results]
                success = self.vector_store.delete_vectors(vector_ids)
                
                if success:
                    logger.info(f"Memoria eliminada para usuario {user_id}: {len(vector_ids)} vectores")
                
                return success
            
            return True
        
        except Exception as e:
            logger.error(f"Error al eliminar memoria del usuario: {e}")
            return False
    
    def get_memory_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtener estadísticas de la memoria
        
        Args:
            user_id: ID del usuario (opcional, si no se especifica se obtienen estadísticas globales)
            
        Returns:
            Diccionario con estadísticas
        """
        try:
            if user_id:
                # Estadísticas del usuario específico
                conversations = self.search_user_memory(user_id, "", top_k=1000, conversation_type='chat')
                preferences = self.search_user_memory(user_id, "", top_k=1000, conversation_type='preference')
                
                return {
                    'user_id': user_id,
                    'total_conversations': len(conversations),
                    'total_preferences': len(preferences),
                    'total_memories': len(conversations) + len(preferences)
                }
            else:
                # Estadísticas globales
                return self.vector_store.get_index_stats()
        
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            return {} 