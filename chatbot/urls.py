from django.urls import path
from .views import connection_test, deepseek_response, images_response, clima_actual

urlpatterns = [
    path('test/', connection_test, name='connection_test'),         
    path('deepseek/', deepseek_response, name='deepseek_response'), 
    path('images/', images_response, name='images_response'), 
    path('clima/', clima_actual, name='clima_actual'),  # nueva ruta

]
