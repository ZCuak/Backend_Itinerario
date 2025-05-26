from django.urls import path
from .views import (
    connection_test, deepseek_response, images_response, clima_actual,
    listar_paises, listar_ciudades_por_pais, lugares_cercanos,
    registrar_viaje, registrar_clima, registrar_lugar, registrar_itinerario,
    registrar_actividad, registrar_actividad_lugar, obtener_ids_ciudad_pais,
    obtener_itinerario_completo, registro_usuario, login_usuario,
    logout_usuario, obtener_perfil_usuario, obtener_estado_por_ciudad
)

urlpatterns = [
    path('test/', connection_test, name='connection_test'),         
    path('deepseek/', deepseek_response, name='deepseek_response'), 
    path('images/', images_response, name='images_response'), 
    path('clima/', clima_actual, name='clima_actual'),  # nueva ruta
    path('paises/', listar_paises, name='listar_paises'),
    path('ciudades/', listar_ciudades_por_pais, name='listar_ciudades_por_pais'),
    path('lugares-cercanos/', lugares_cercanos, name='lugares_cercanos'),
    path('estado-por-ciudad/', obtener_estado_por_ciudad, name='obtener_estado_por_ciudad'),
    
    # Nuevas rutas para registro
    path('registrar/viaje/', registrar_viaje, name='registrar_viaje'),
    path('registrar/clima/', registrar_clima, name='registrar_clima'),
    path('registrar/lugar/', registrar_lugar, name='registrar_lugar'),
    path('registrar/itinerario/', registrar_itinerario, name='registrar_itinerario'),
    path('registrar/actividad/', registrar_actividad, name='registrar_actividad'),
    path('registrar/actividad-lugar/', registrar_actividad_lugar, name='registrar_actividad_lugar'),
    
    # Nueva ruta para obtener IDs
    path('obtener-ids/', obtener_ids_ciudad_pais, name='obtener_ids_ciudad_pais'),
    
    # Nueva ruta para obtener itinerario completo
    path('itinerario/', obtener_itinerario_completo, name='obtener_itinerario_completo'),
    
    # Rutas de autenticación
    path('auth/registro/', registro_usuario, name='registro_usuario'),
    path('auth/login/', login_usuario, name='login_usuario'),
    path('auth/logout/', logout_usuario, name='logout_usuario'),
    path('auth/perfil/', obtener_perfil_usuario, name='obtener_perfil_usuario'),
]
