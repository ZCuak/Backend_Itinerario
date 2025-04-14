from django.urls import path
from .views import connection_test

urlpatterns = [
    path('test/', connection_test, name='connection_test'),
]