from django.urls import path
from . import views, places_views

app_name = 'pinecone'

urlpatterns = [
    # Gestión de conversaciones
    path('store-conversation/', views.store_conversation, name='store_conversation'),
    path('store-preference/', views.store_preference, name='store_preference'),
    
    # Búsqueda y consulta
    path('search-memory/', views.search_memory, name='search_memory'),
    path('get-context/', views.get_user_context, name='get_user_context'),
    path('recent-conversations/', views.get_recent_conversations, name='recent_conversations'),
    
    # Gestión de memoria
    path('delete-memory/', views.delete_user_memory, name='delete_user_memory'),
    path('memory-stats/', views.get_memory_stats, name='memory_stats'),
    
    # Estadísticas del índice
    path('index-stats/', views.get_index_stats, name='index_stats'),
    path('clear-index/', views.clear_index, name='clear_index'),
    
    # Rutas específicas para lugares
    path('places/add-place/', places_views.add_place_to_vector_store, name='add_place'),
    path('places/sync-all/', places_views.sync_all_places, name='sync_all_places'),
    path('places/search/', places_views.search_places, name='search_places'),
    path('places/stats/', places_views.get_places_stats, name='places_stats'),
    path('places/clear-index/', places_views.clear_places_index, name='clear_places_index'),
    
    # Búsqueda inteligente
    path('places/smart-search/', places_views.smart_place_search, name='smart_place_search'),
    
    # Búsqueda natural (procesamiento con DeepSeek)
    path('places/process-natural-search/', places_views.process_natural_search, name='process_natural_search'),
    
    # Búsquedas genéricas por amenidades y características
    path('places/places-with-amenities/', places_views.find_places_with_amenities, name='places_with_amenities'),
    path('places/search-with-rating-and-amenities/', places_views.search_places_with_rating_and_amenities, name='search_places_with_rating_and_amenities'),
    path('places/search-by-rating-range/', places_views.search_places_by_rating_range, name='search_places_by_rating_range'),
    
    # Documentación de la API
    path('places/docs/', places_views.api_documentation, name='api_documentation'),
] 