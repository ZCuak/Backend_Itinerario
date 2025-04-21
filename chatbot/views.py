from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .deepseek import enviar_prompt  
from .images import obtener_fotos_lugar

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

@api_view(['POST'])
@permission_classes([AllowAny])
def images_response(request):
    nombre_lugar = request.data.get("nombre_lugar", "")
    api_key = 'AIzaSyDWFyOlDVNw2A8Q9s07cCPMnAOA139egf0'  # Puedes moverla a settings si quieres mantenerlo más seguro

    if not nombre_lugar:
        return Response({
            'status': 'error',
            'message': 'El campo "nombre_lugar" es obligatorio.',
            'data': None
        }, status=400)

    try:
        imagenes = obtener_fotos_lugar(nombre_lugar, api_key)
        if imagenes:
            return Response({
                'status': 'success',
                'message': f'Se encontraron {len(imagenes)} imágenes.',
                'data': imagenes
            })
        else:
            return Response({
                'status': 'error',
                'message': 'No se encontraron imágenes para ese lugar.',
                'data': []
            })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error al obtener imágenes: {str(e)}',
            'data': None
        }, status=500)
