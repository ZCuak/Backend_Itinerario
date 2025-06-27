"""
URLs para la API del sistema de búsqueda semántica
"""

from django.urls import path
from . import api_views

app_name = 'llm_api'

urlpatterns = [
    # Endpoint principal para búsqueda completa
    path('buscar-lugares/', api_views.buscar_lugares_api, name='buscar_lugares'),
    
    # Endpoint para extraer solo filtros
    path('extraer-filtros/', api_views.extraer_filtros_api, name='extraer_filtros'),
    
    # Endpoint para búsqueda por tipo específico
    path('buscar-por-tipo/', api_views.buscar_por_tipo_api, name='buscar_por_tipo'),
    
    # Endpoint de health check
    path('health/', api_views.health_check_api, name='health_check'),
] 