from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .deepseek import enviar_prompt  

@api_view(['GET'])
@permission_classes([AllowAny])
def connection_test(request):
    return Response({
        'status': 'success',
        'message': 'Conexión exitosa entre Angular y Django',
        'data': None
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def deepseek_response(request):
    prompt = request.data.get("prompt", "")
    
    if not prompt:
        return Response({
            'status': 'error',
            'message': 'El campo "prompt" es obligatorio.',
            'data': None
        }, status=400)

    respuesta = enviar_prompt(prompt)

    if respuesta:
        return Response({
            'status': 'success',
            'message': 'Respuesta generada con éxito.',
            'data': respuesta
        })
    else:
        return Response({
            'status': 'error',
            'message': 'Error al generar respuesta desde DeepSeek.',
            'data': None
        }, status=500)
