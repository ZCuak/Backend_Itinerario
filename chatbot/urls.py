from django.urls import path, include
from .views import (
    connection_test, deepseek_response, images_response, clima_actual,
    listar_paises, listar_ciudades_por_pais, registrar_viaje, registrar_clima,
    registrar_lugar, registrar_itinerario, registrar_actividad,
    registrar_actividad_lugar, obtener_ids_ciudad_pais, obtener_itinerario_completo,
    registro_usuario, login_usuario, logout_usuario, obtener_perfil_usuario,
    obtener_estado_por_ciudad
)
from .google_places_views import (
    lugares_cercanos, generar_resumen_ia, generar_resumenes_lotes_ia, 
    listar_lugares_con_resumenes
)

# Rutas de autenticación
auth_urlpatterns = [
    path('registro/', registro_usuario, name='registro_usuario'),
    path('login/', login_usuario, name='login_usuario'),
    path('logout/', logout_usuario, name='logout_usuario'),
    path('perfil/', obtener_perfil_usuario, name='obtener_perfil_usuario'),
]

# Rutas de Google Places
google_places_urlpatterns = [
    path('lugares-cercanos/', lugares_cercanos, name='lugares_cercanos'),
    path('generar-resumen-ia/', generar_resumen_ia, name='generar_resumen_ia'),
    path('generar-resumenes-lotes-ia/', generar_resumenes_lotes_ia, name='generar_resumenes_lotes_ia'),
    path('listar-lugares-resumenes/', listar_lugares_con_resumenes, name='listar_lugares_con_resumenes'),
]

# Rutas de registro
registro_urlpatterns = [
    path('viaje/', registrar_viaje, name='registrar_viaje'),
    path('clima/', registrar_clima, name='registrar_clima'),
    path('lugar/', registrar_lugar, name='registrar_lugar'),
    path('itinerario/', registrar_itinerario, name='registrar_itinerario'),
    path('actividad/', registrar_actividad, name='registrar_actividad'),
    path('actividad-lugar/', registrar_actividad_lugar, name='registrar_actividad_lugar'),
]

urlpatterns = [
    # Rutas básicas
    path('test/', connection_test, name='connection_test'),         
    path('deepseek/', deepseek_response, name='deepseek_response'), 
    path('images/', images_response, name='images_response'), 
    path('clima/', clima_actual, name='clima_actual'),
    path('paises/', listar_paises, name='listar_paises'),
    path('ciudades/', listar_ciudades_por_pais, name='listar_ciudades_por_pais'),
    path('estado-por-ciudad/', obtener_estado_por_ciudad, name='obtener_estado_por_ciudad'),
    path('obtener-ids/', obtener_ids_ciudad_pais, name='obtener_ids_ciudad_pais'),
    path('itinerario/', obtener_itinerario_completo, name='obtener_itinerario_completo'),
    
    # Rutas agrupadas
    path('auth/', include(auth_urlpatterns)),
    path('places/', include(google_places_urlpatterns)),
    path('registrar/', include(registro_urlpatterns)),
]
