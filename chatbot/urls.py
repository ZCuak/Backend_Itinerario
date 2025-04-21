from django.urls import path
from .views import connection_test, deepseek_response, images_response, clima_actual, listar_paises, listar_ciudades_por_pais

urlpatterns = [
    path('test/', connection_test, name='connection_test'),         
    path('deepseek/', deepseek_response, name='deepseek_response'), 
    path('images/', images_response, name='images_response'), 
    path('clima/', clima_actual, name='clima_actual'),  # nueva ruta
    path('paises/', listar_paises, name='listar_paises'),
    path('ciudades/', listar_ciudades_por_pais, name='listar_ciudades_por_pais'),
]
