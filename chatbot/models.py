# mi_app/models.py

from django.db import models
from django.contrib.auth.models import User

# Modelo Viaje
class Viaje(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Relación con la tabla User
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    destino = models.CharField(max_length=255)  # Destino general, por ejemplo "París"
    estado = models.CharField(max_length=50, default='pendiente')  # Estado de la transacción, ejemplo "pendiente", "aceptado"
    
    def __str__(self):
        return f"Viaje de {self.usuario.username} a {self.destino}"

# Modelo Destino
class Destino(models.Model):
    CATEGORIAS = [
        ('restaurante', 'Restaurante'),
        ('hotel', 'Hotel'),
        ('club', 'Club'),
        ('centro_turistico', 'Centro Turístico'),
        # Agrega más categorías si es necesario
    ]

    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE, related_name='destinos')  # Relación con el modelo Viaje
    categoria = models.CharField(max_length=50, choices=CATEGORIAS)  # Categoría del destino
    nombre_destino = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre_destino} - {self.categoria}"

# Modelo Pregunta
class Pregunta(models.Model):
    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE, related_name='preguntas')  # Relación con Viaje
    pregunta = models.CharField(max_length=500)  # La pregunta que se le hace al usuario
    respuesta = models.TextField(null=True, blank=True)  # La respuesta del usuario

    def __str__(self):
        return f"Pregunta para {self.viaje.destino}"
    

class Countries(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        managed = False

class Cities(models.Model):
    country = models.ForeignKey(Countries, on_delete=models.DO_NOTHING, db_column='country_id')
    state_id = models.IntegerField()
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        managed = False

