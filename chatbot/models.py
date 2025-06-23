# mi_app/models.py

from django.db import models
from django.contrib.auth.models import User

class Countries(models.Model):
    name = models.CharField(max_length=100)
    iso2 = models.CharField(max_length=2)
    iso3 = models.CharField(max_length=3)
    numeric_code = models.CharField(max_length=3)
    phonecode = models.CharField(max_length=10)
    capital = models.CharField(max_length=100)
    currency = models.CharField(max_length=10)
    currency_name = models.CharField(max_length=100)
    currency_symbol = models.CharField(max_length=10)
    tld = models.CharField(max_length=10)
    native = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    subregion = models.CharField(max_length=100)
    timezones = models.JSONField()
    translations = models.JSONField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    emoji = models.CharField(max_length=10)
    emojiU = models.CharField(max_length=20)
    flag = models.BooleanField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'countries'

    def __str__(self):
        return self.name

class States(models.Model):
    country = models.ForeignKey(Countries, on_delete=models.CASCADE, db_column='country_id')
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'states'

    def __str__(self):
        return self.name

class Cities(models.Model):
    country = models.ForeignKey(Countries, on_delete=models.CASCADE, db_column='country_id')
    state = models.ForeignKey(States, on_delete=models.CASCADE, db_column='state_id')
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'cities'

    def __str__(self):
        return self.name

class Tipo_Transporte(models.Model):
    nombre = models.CharField(max_length=100)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'tipo_transporte'

    def __str__(self):
        return self.nombre

class Transporte(models.Model):
    tipo_transporte = models.ForeignKey(Tipo_Transporte, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    estado = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'transporte'

    def __str__(self):
        return f"{self.nombre} - {self.tipo_transporte.nombre}"

class Tipo_Lugar(models.Model):
    nombre = models.CharField(max_length=100)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'tipo_lugar'

    def __str__(self):
        return self.nombre

class Lugar(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado')
    ]
    
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    ubicacion = models.CharField(max_length=255)
    tipo_lugar = models.ForeignKey(Tipo_Lugar, on_delete=models.CASCADE)

    class Meta:
        db_table = 'lugar'

    def __str__(self):
        return self.nombre

class Clima(models.Model):
    fecha = models.DateField()
    ciudad = models.ForeignKey(Cities, on_delete=models.CASCADE, null=True, blank=True)
    pais = models.ForeignKey(Countries, on_delete=models.CASCADE, null=True, blank=True)
    temperatura_maxima = models.FloatField(null=True, blank=True)
    temperatura_minima = models.FloatField(null=True, blank=True)
    estado_clima = models.CharField(max_length=50)
    humedad = models.IntegerField()
    probabilidad_lluvia = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        db_table = 'clima'
        unique_together = ('fecha', 'ciudad', 'pais')

    def __str__(self):
        return f"Clima {self.fecha} - {self.ciudad.name if self.ciudad else 'Sin ciudad'}, {self.pais.name if self.pais else 'Sin país'}"

class Viaje(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado')
    ]
    
    presupuesto = models.DecimalField(max_digits=10, decimal_places=2)
    dia_salida = models.DateField()
    ciudad_salida = models.ForeignKey(Cities, on_delete=models.DO_NOTHING)
    duracion_viaje = models.IntegerField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    class Meta:
        db_table = 'viaje'

    def __str__(self):
        return f"Viaje {self.id} - {self.ciudad_salida.name if self.ciudad_salida else 'Sin ciudad de salida'}"

class Itinerario(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado')
    ]
    
    lugar = models.CharField(max_length=255)
    ciudad = models.ForeignKey(Cities, on_delete=models.DO_NOTHING)
    pais = models.ForeignKey(Countries, on_delete=models.DO_NOTHING)
    dia = models.IntegerField()
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE)
    clima = models.ForeignKey(Clima, on_delete=models.CASCADE)
    transporte = models.ForeignKey(Transporte, on_delete=models.CASCADE)

    class Meta:
        db_table = 'itinerario'

    def __str__(self):
        return f"Itinerario {self.id} - {self.lugar}"

class Actividad(models.Model):
    
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada')
    ]
    
    turno = models.CharField(max_length=10)
    orden = models.IntegerField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    itinerario = models.ForeignKey(Itinerario, on_delete=models.CASCADE)
    lugares = models.ManyToManyField(Lugar, through='Actividad_Lugar')

    class Meta:
        db_table = 'actividad'

    def __str__(self):
        return f"Actividad {self.id} - {self.get_turno_display()}"

class Actividad_Lugar(models.Model):
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE)
    lugar = models.ForeignKey(Lugar, on_delete=models.CASCADE)

    class Meta:
        db_table = 'actividad_lugar'
        unique_together = ('actividad', 'lugar')

class NivelPrecio(models.Model):
    nivel = models.IntegerField(unique=True)  # 0-4
    descripcion = models.CharField(max_length=200)
    rango_inferior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rango_superior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    moneda = models.CharField(max_length=3, default='PEN')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'nivel_precio'
        ordering = ['nivel']

    def __str__(self):
        return f"Nivel {self.nivel}: {self.descripcion}"

class LugarGooglePlaces(models.Model):
    CATEGORIAS = [
        ('restaurantes', 'Restaurantes'),
        ('hoteles', 'Hoteles'),
        ('lugares_acuaticos', 'Lugares Acuáticos'),
        ('lugares_turisticos', 'Lugares Turísticos'),
        ('discotecas', 'Discotecas'),
        ('museos', 'Museos'),
        ('lugares_campestres', 'Lugares Campestres'),
        ('centros_comerciales', 'Centros Comerciales'),
        ('lugares_de_entretenimiento', 'Lugares de Entretenimiento'),
    ]
    
    # Campos básicos
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=500)
    tipo_principal = models.CharField(max_length=100)
    tipos_adicionales = models.JSONField(default=list)
    categoria = models.CharField(max_length=50, choices=CATEGORIAS)
    place_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Ubicación
    latitud = models.FloatField()
    longitud = models.FloatField()
    
    # Calificaciones
    rating = models.FloatField(default=0)
    total_ratings = models.IntegerField(default=0)
    
    # Información de contacto
    website = models.URLField(max_length=500, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    
    # Precios y horarios
    nivel_precios = models.ForeignKey(NivelPrecio, on_delete=models.SET_NULL, null=True, blank=True)
    horarios = models.JSONField(default=list)
    
    # Descripción
    descripcion = models.TextField(blank=True, null=True)
    
    # Resumen generado por IA
    resumen_ia = models.TextField(blank=True, null=True)
    
    # Estado del negocio
    estado_negocio = models.CharField(max_length=50, default='OPERATIONAL')
    
    # Campos de control
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lugar_google_places'
        unique_together = ('nombre', 'direccion', 'latitud', 'longitud')
        indexes = [
            models.Index(fields=['categoria']),
            models.Index(fields=['latitud', 'longitud']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return f"{self.nombre} - {self.categoria}"

