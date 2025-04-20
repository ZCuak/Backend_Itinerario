from django.urls import path
from .views import connection_test, deepseek_response

urlpatterns = [
    path('test/', connection_test, name='connection_test'),         
    path('deepseek/', deepseek_response, name='deepseek_response'), 
]
