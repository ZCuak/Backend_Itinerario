from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .deepseek import enviar_prompt  
from .images import obtener_fotos_lugar_mejoradas
import os
from .models import Cities, Countries
from .openweather import obtener_clima

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
    api_key = os.getenv('API_KEY_IMAGE_GENERATION')

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

@api_view(['POST'])
@permission_classes([AllowAny])
def images_response(request):
    nombre_lugar = request.data.get("nombre_lugar", "")
    api_key = os.getenv('API_KEY_IMAGE_GENERATION')

    if not nombre_lugar:
        return Response({
            'status': 'error',
            'message': 'El campo "nombre_lugar" es obligatorio.',
            'data': None
        }, status=400)

    try:
        imagenes = obtener_fotos_lugar_mejoradas(nombre_lugar, api_key)
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


@api_view(['GET'])
@permission_classes([AllowAny])
def clima_actual(request):
    ciudad = request.GET.get("ciudad", "").strip()
    pais = request.GET.get("pais", "").strip()

    if not ciudad or not pais:
        return Response({
            "status": "error",
            "message": "Los parámetros 'ciudad' y 'pais' son obligatorios.",
            "data": None
        }, status=400)

    try:
        pais_obj = Countries.objects.get(name__iexact=pais)
        ciudad_obj = Cities.objects.get(name__iexact=ciudad, country=pais_obj)
    except Countries.DoesNotExist:
        return Response({
            "status": "error",
            "message": f"El país '{pais}' no fue encontrado.",
            "data": None
        }, status=404)
    except Cities.DoesNotExist:
        return Response({
            "status": "error",
            "message": f"La ciudad '{ciudad}' no fue encontrada en el país '{pais}'.",
            "data": None
        }, status=404)

    clima = obtener_clima(ciudad_obj.latitude, ciudad_obj.longitude)

    if clima:
        return Response({
            "status": "success",
            "message": f"Clima para {ciudad_obj.name}, {pais_obj.name}.",
            "data": clima
        })
    else:
        return Response({
            "status": "error",
            "message": "No se pudo obtener el clima.",
            "data": None
        }, status=500)
    

@api_view(['GET'])
@permission_classes([AllowAny])
def listar_paises(request):
    paises = Countries.objects.all().order_by('name')
    data = [{"id": p.id, "name": p.name} for p in paises]
    return Response({
        "status": "success",
        "data": data
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def listar_ciudades_por_pais(request):
    pais_nombre = request.GET.get('pais', '').strip()

    if not pais_nombre:
        return Response({
            "status": "error",
            "message": "Debe proporcionar el nombre del país.",
            "data": None
        }, status=400)

    try:
        pais = Countries.objects.get(name__iexact=pais_nombre)
        ciudades = Cities.objects.filter(country=pais).order_by('name')
        data = [{"id": c.id, "name": c.name, "latitude": c.latitude, "longitude": c.longitude} for c in ciudades]

        return Response({
            "status": "success",
            "data": data
        })

    except Countries.DoesNotExist:
        return Response({
            "status": "error",
            "message": f"El país '{pais_nombre}' no existe.",
            "data": None
        }, status=404)