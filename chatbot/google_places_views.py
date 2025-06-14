from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .google_places import buscar_lugares_cercanos

@api_view(['GET'])
@permission_classes([AllowAny])
def lugares_cercanos(request):
    latitud = request.GET.get('latitud')
    longitud = request.GET.get('longitud')
    radio = request.GET.get('radio', 15000)
    tipos = request.GET.get('tipos')
    
    if not latitud or not longitud:
        return Response({
            'status': 'error',
            'message': 'Se requieren las coordenadas (latitud y longitud)',
            'data': None
        }, status=400)
    
    try:
        latitud = float(latitud)
        longitud = float(longitud)
        radio = int(radio)
        
        if tipos:
            tipos = tipos.split(',')
        
        lugares = buscar_lugares_cercanos(latitud, longitud, radio, tipos)
        
        return Response({
            'status': 'success',
            'message': f'Se encontraron {len(lugares)} lugares cercanos',
            'data': lugares
        })
        
    except ValueError:
        return Response({
            'status': 'error',
            'message': 'Las coordenadas y el radio deben ser números válidos',
            'data': None
        }, status=400)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error al buscar lugares cercanos: {str(e)}',
            'data': None
        }, status=500) 