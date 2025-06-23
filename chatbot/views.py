from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .deepseek.deepseek import enviar_prompt  
from .images import obtener_fotos_lugar_mejoradas
from .openweather import obtener_clima
import os
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from datetime import datetime

from .place_search import buscar_lugares_foursquare

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
        # Buscar país usando LIKE
        pais_obj = Countries.objects.filter(name__icontains=pais).first()
        if not pais_obj:
            return Response({
                "status": "error",
                "message": f"No se encontró ningún país que coincida con '{pais}'.",
                "data": None
            }, status=404)

        # Buscar ciudad usando LIKE
        ciudad_obj = Cities.objects.filter(
            name__icontains=ciudad,
            country=pais_obj
        ).first()
        
        if not ciudad_obj:
            return Response({
                "status": "error",
                "message": f"No se encontró ninguna ciudad que coincida con '{ciudad}' en el país '{pais_obj.name}'.",
                "data": None
            }, status=404)

        # Buscar en la base de datos primero
        climas_db = Clima.objects.filter(
            ciudad=ciudad_obj,
            pais=pais_obj,
            fecha__gte=datetime.now().date()
        ).order_by('fecha')[:3]  # Solo los primeros 3 días

        if climas_db.exists():
            # Si encontramos datos en la base de datos, los devolvemos
            datos_clima = []
            for clima in climas_db:
                datos_clima.append({
                    "fecha": clima.fecha.strftime('%Y-%m-%d'),
                    "temperatura": {
                        "maxima": clima.temperatura_maxima,
                        "minima": clima.temperatura_minima
                    },
                    "estado": clima.estado_clima,
                    "humedad": clima.humedad,
                    "probabilidad_lluvia": clima.probabilidad_lluvia
                })
            
            return Response({
                "status": "success",
                "message": f"Clima para {ciudad_obj.name}, {pais_obj.name}.",
                "data": datos_clima
            })

        # Si no hay datos en la base de datos, consultamos la API
        clima_api = obtener_clima(ciudad_obj.latitude, ciudad_obj.longitude)

        if clima_api:
            # Guardar solo los primeros 3 días en la base de datos
            for dia_clima in clima_api[:3]:  # Solo los primeros 3 días
                Clima.objects.create(
                    fecha=datetime.strptime(dia_clima['fecha'], '%Y-%m-%d').date(),
                    ciudad=ciudad_obj,
                    pais=pais_obj,
                    temperatura_maxima=dia_clima['temperatura']['maxima'],
                    temperatura_minima=dia_clima['temperatura']['minima'],
                    estado_clima=dia_clima['estado'],
                    humedad=dia_clima['humedad'],
                    probabilidad_lluvia=dia_clima['probabilidad_lluvia']
                )

            return Response({
                "status": "success",
                "message": f"Clima para {ciudad_obj.name}, {pais_obj.name}.",
                "data": clima_api[:3]  # Devolver solo los primeros 3 días
            })
        else:
            return Response({
                "status": "error",
                "message": "No se pudo obtener el clima.",
                "data": None
            }, status=500)
            
    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Error al procesar la solicitud: {str(e)}",
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
    pais_id = request.GET.get("pais_id")
    
    if not pais_id:
        return Response({
            "status": "error",
            "message": "El parámetro 'pais_id' es obligatorio.",
            "data": None
        }, status=400)
    
    try:
        ciudades = Cities.objects.filter(country_id=pais_id).order_by('name')
        data = [{"id": c.id, "name": c.name} for c in ciudades]
        
        return Response({
            "status": "success",
            "message": f"Ciudades encontradas para el país ID {pais_id}.",
            "data": data
        })
    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Error al obtener ciudades: {str(e)}",
            "data": None
        }, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def registrar_viaje(request):
    try:
        data = request.data
        viaje = Viaje.objects.create(
            presupuesto=data.get('presupuesto'),
            dia_salida=data.get('dia_salida'),
            ciudad_salida_id=data.get('ciudad_salida_id'),
            duracion_viaje=data.get('duracion_viaje'),
            estado=data.get('estado', 'pendiente')
        )
        return Response({
            'status': 'success',
            'message': 'Viaje registrado exitosamente',
            'data': {
                'id': viaje.id,
                'presupuesto': viaje.presupuesto,
                'dia_salida': viaje.dia_salida,
                'ciudad_salida': viaje.ciudad_salida.name,
                'duracion_viaje': viaje.duracion_viaje,
                'estado': viaje.estado
            }
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error al registrar el viaje: {str(e)}',
            'data': None
        }, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def registrar_clima(request):
    try:
        data = request.data
        clima = Clima.objects.create(
            fecha=data.get('fecha'),
            temperatura_actual=data.get('temperatura_actual'),
            temperatura_sensacion=data.get('temperatura_sensacion'),
            descripcion=data.get('descripcion'),
            estado_clima=data.get('estado_clima'),
            humedad=data.get('humedad'),
            velocidad_viento=data.get('velocidad_viento'),
            direccion_viento=data.get('direccion_viento'),
            probabilidad_lluvia=data.get('probabilidad_lluvia')
        )
        return Response({
            'status': 'success',
            'message': 'Clima registrado exitosamente',
            'data': {
                'id': clima.id,
                'fecha': clima.fecha,
                'temperatura_actual': clima.temperatura_actual,
                'estado_clima': clima.estado_clima
            }
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error al registrar el clima: {str(e)}',
            'data': None
        }, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def registrar_lugar(request):
    try:
        data = request.data
        lugar = Lugar.objects.create(
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion'),
            ubicacion=data.get('ubicacion'),
            tipo_lugar_id=data.get('tipo_lugar_id'),
            estado=data.get('estado', 'pendiente')
        )
        return Response({
            'status': 'success',
            'message': 'Lugar registrado exitosamente',
            'data': {
                'id': lugar.id,
                'nombre': lugar.nombre,
                'ubicacion': lugar.ubicacion,
                'tipo_lugar': lugar.tipo_lugar.nombre,
                'estado': lugar.estado
            }
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error al registrar el lugar: {str(e)}',
            'data': None
        }, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def registrar_itinerario(request):
    try:
        data = request.data
        itinerario = Itinerario.objects.create(
            lugar=data.get('lugar'),
            ciudad_id=data.get('ciudad_id'),
            pais_id=data.get('pais_id'),
            dia=data.get('dia'),
            costo=data.get('costo'),
            estado=data.get('estado', 'pendiente'),
            viaje_id=data.get('viaje_id'),
            clima_id=data.get('clima_id'),
            transporte_id=data.get('transporte_id')
        )
        return Response({
            'status': 'success',
            'message': 'Itinerario registrado exitosamente',
            'data': {
                'id': itinerario.id,
                'lugar': itinerario.lugar,
                'ciudad': itinerario.ciudad.name,
                'pais': itinerario.pais.name,
                'dia': itinerario.dia,
                'estado': itinerario.estado
            }
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error al registrar el itinerario: {str(e)}',
            'data': None
        }, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def registrar_actividad(request):
    try:
        data = request.data
        actividad = Actividad.objects.create(
            turno=data.get('turno'),
            orden=data.get('orden'),
            estado=data.get('estado', 'pendiente'),
            itinerario_id=data.get('itinerario_id')
        )
        
        # Registrar lugares asociados si se proporcionan
        lugares_ids = data.get('lugares_ids', [])
        if lugares_ids:
            actividad.lugares.set(lugares_ids)
        
        return Response({
            'status': 'success',
            'message': 'Actividad registrada exitosamente',
            'data': {
                'id': actividad.id,
                'turno': actividad.turno,
                'orden': actividad.orden,
                'estado': actividad.estado,
                'itinerario_id': actividad.itinerario_id
            }
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error al registrar la actividad: {str(e)}',
            'data': None
        }, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def registrar_actividad_lugar(request):
    try:
        data = request.data
        actividad_lugar = Actividad_Lugar.objects.create(
            actividad_id=data.get('actividad_id'),
            lugar_id=data.get('lugar_id')
        )
        return Response({
            'status': 'success',
            'message': 'Relación actividad-lugar registrada exitosamente',
            'data': {
                'id': actividad_lugar.id,
                'actividad_id': actividad_lugar.actividad_id,
                'lugar_id': actividad_lugar.lugar_id
            }
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error al registrar la relación actividad-lugar: {str(e)}',
            'data': None
        }, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_ids_ciudad_pais(request):
    ciudad_nombre = request.GET.get('ciudad', '').strip()
    pais_nombre = request.GET.get('pais', '').strip()

    if not ciudad_nombre or not pais_nombre:
        return Response({
            'status': 'error',
            'message': 'Los parámetros "ciudad" y "pais" son obligatorios.',
            'data': None
        }, status=400)

    try:
        # Buscar el país
        pais = Countries.objects.filter(name__icontains=pais_nombre).first()
        if not pais:
            return Response({
                'status': 'error',
                'message': f'No se encontró el país: {pais_nombre}',
                'data': None
            }, status=404)

        # Buscar la ciudad en ese país
        ciudad = Cities.objects.filter(
            name__icontains=ciudad_nombre,
            country=pais
        ).first()

        if not ciudad:
            return Response({
                'status': 'error',
                'message': f'No se encontró la ciudad: {ciudad_nombre} en el país: {pais_nombre}',
                'data': None
            }, status=404)

        return Response({
            'status': 'success',
            'message': 'IDs encontrados exitosamente',
            'data': {
                'ciudad_id': ciudad.id,
                'pais_id': pais.id,
                'ciudad_nombre': ciudad.name,
                'pais_nombre': pais.name
            }
        })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error al buscar los IDs: {str(e)}',
            'data': None
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_itinerario_completo(request):
    try:
        # Obtener todos los itinerarios con sus relaciones
        itinerarios = Itinerario.objects.select_related(
            'ciudad', 'pais', 'viaje', 'clima', 'transporte'
        ).prefetch_related(
            'actividad_set__lugares'
        ).all()

        itinerarios_data = []
        for itinerario in itinerarios:
            actividades = []
            for actividad in itinerario.actividad_set.all():
                lugares_actividad = []
                for lugar in actividad.lugares.all():
                    lugares_actividad.append({
                        'id': lugar.id,
                        'nombre': lugar.nombre,
                        'descripcion': lugar.descripcion,
                        'ubicacion': lugar.ubicacion,
                        'tipo_lugar': lugar.tipo_lugar.nombre
                    })
                
                actividades.append({
                    'id': actividad.id,
                    'turno': actividad.turno,
                    'orden': actividad.orden,
                    'estado': actividad.estado,
                    'lugares': lugares_actividad
                })

            itinerario_data = {
                'id': itinerario.id,
                'lugar': itinerario.lugar,
                'ciudad': {
                    'id': itinerario.ciudad.id,
                    'nombre': itinerario.ciudad.name
                },
                'pais': {
                    'id': itinerario.pais.id,
                    'nombre': itinerario.pais.name
                },
                'dia': itinerario.dia,
                'costo': float(itinerario.costo),
                'estado': itinerario.estado,
                'viaje': {
                    'id': itinerario.viaje.id,
                    'presupuesto': float(itinerario.viaje.presupuesto),
                    'dia_salida': itinerario.viaje.dia_salida,
                    'duracion_viaje': itinerario.viaje.duracion_viaje,
                    'estado': itinerario.viaje.estado
                },
                'clima': {
                    'id': itinerario.clima.id,
                    'fecha': itinerario.clima.fecha,
                    'temperatura_actual': itinerario.clima.temperatura_actual,
                    'temperatura_sensacion': itinerario.clima.temperatura_sensacion,
                    'descripcion': itinerario.clima.descripcion,
                    'estado_clima': itinerario.clima.estado_clima,
                    'humedad': itinerario.clima.humedad,
                    'velocidad_viento': itinerario.clima.velocidad_viento,
                    'direccion_viento': itinerario.clima.direccion_viento,
                    'probabilidad_lluvia': itinerario.clima.probabilidad_lluvia
                },
                'transporte': {
                    'id': itinerario.transporte.id,
                    'nombre': itinerario.transporte.nombre,
                    'tipo_transporte': itinerario.transporte.tipo_transporte.nombre
                },
                'actividades': actividades
            }
            itinerarios_data.append(itinerario_data)

        return Response({
            'status': 'success',
            'message': 'Información de los itinerarios obtenida exitosamente',
            'data': itinerarios_data
        })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error al obtener la información de los itinerarios: {str(e)}',
            'data': None
        }, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def registro_usuario(request):
    try:
        data = request.data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')

        # Validar que los campos requeridos estén presentes
        if not all([username, email, password]):
            return Response({
                'status': 'error',
                'message': 'Todos los campos son obligatorios',
                'data': None
            }, status=400)

        # Validar que el usuario no exista
        if User.objects.filter(username=username).exists():
            return Response({
                'status': 'error',
                'message': 'El nombre de usuario ya existe',
                'data': None
            }, status=400)

        if User.objects.filter(email=email).exists():
            return Response({
                'status': 'error',
                'message': 'El correo electrónico ya está registrado',
                'data': None
            }, status=400)

        # Validar la contraseña
        try:
            validate_password(password)
        except ValidationError as e:
            return Response({
                'status': 'error',
                'message': 'La contraseña no cumple con los requisitos de seguridad',
                'data': list(e.messages)
            }, status=400)

        # Crear el usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Generar token de autenticación
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'status': 'success',
            'message': 'Usuario registrado exitosamente',
            'data': {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'token': token.key
            }
        })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error al registrar el usuario: {str(e)}',
            'data': None
        }, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_usuario(request):
    try:
        data = request.data
        username = data.get('username')
        password = data.get('password')

        if not all([username, password]):
            return Response({
                'status': 'error',
                'message': 'Usuario y contraseña son obligatorios',
                'data': None
            }, status=400)

        # Autenticar usuario
        user = authenticate(username=username, password=password)

        if user is None:
            return Response({
                'status': 'error',
                'message': 'Credenciales inválidas',
                'data': None
            }, status=401)

        # Generar o obtener token
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'status': 'success',
            'message': 'Login exitoso',
            'data': {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'token': token.key
            }
        })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error al iniciar sesión: {str(e)}',
            'data': None
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_usuario(request):
    try:
        # Eliminar el token de autenticación
        request.user.auth_token.delete()
        
        return Response({
            'status': 'success',
            'message': 'Sesión cerrada exitosamente',
            'data': None
        })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error al cerrar sesión: {str(e)}',
            'data': None
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_perfil_usuario(request):
    try:
        user = request.user
        return Response({
            'status': 'success',
            'message': 'Perfil obtenido exitosamente',
            'data': {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error al obtener el perfil: {str(e)}',
            'data': None
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_estado_por_ciudad(request):
    ciudad_nombre = request.GET.get('ciudad', '').strip()
    pais_nombre = request.GET.get('pais', '').strip()

    if not ciudad_nombre or not pais_nombre:
        return Response({
            "status": "error",
            "message": "Los parámetros 'ciudad' y 'pais' son obligatorios.",
            "data": None
        }, status=400)

    try:
        # Buscar el país
        pais = Countries.objects.filter(name__icontains=pais_nombre).first()
        if not pais:
            return Response({
                "status": "error",
                "message": f"No se encontró el país: {pais_nombre}",
                "data": None
            }, status=404)

        # Buscar la ciudad y su estado asociado
        ciudad = Cities.objects.select_related('state').filter(
            name__icontains=ciudad_nombre,
            country=pais
        ).first()

        if not ciudad:
            return Response({
                "status": "error",
                "message": f"No se encontró la ciudad: {ciudad_nombre} en el país: {pais_nombre}",
                "data": None
            }, status=404)

        if not ciudad.state:
            return Response({
                "status": "error",
                "message": f"No se encontró el estado para la ciudad: {ciudad_nombre}",
                "data": None
            }, status=404)

        return Response({
            "status": "success",
            "message": "Estado encontrado exitosamente",
            "data": {
                "id": ciudad.state.id,
                "nombre": ciudad.state.name,
                "pais": {
                    "id": pais.id,
                    "nombre": pais.name
                },
                "ciudad": {
                    "id": ciudad.id,
                    "nombre": ciudad.name
                }
            }
        })

    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Error al buscar el estado: {str(e)}",
            "data": None
        }, status=500)