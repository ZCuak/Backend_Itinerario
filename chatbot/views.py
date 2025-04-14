from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

# Create your views here.
@api_view(['GET'])
@permission_classes([AllowAny])
def connection_test(request):
    return Response({
        'status': 'success',
        'message': 'Conexión exitosa entre Angular y Django',
        'data': None
    })