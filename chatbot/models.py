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
    # Tipos de establecimiento disponibles
    TIPOS_ESTABLECIMIENTO = [
        ('hotel', 'Hotel'),
        ('restaurant', 'Restaurante'),
        ('coffee_shop', 'Cafetería'),
        ('chinese_restaurant', 'Restaurante Chino'),
        ('bar', 'Bar'),
        ('lodging', 'Alojamiento'),
        ('aquarium', 'Acuario'),
        ('beach', 'Playa'),
        ('market', 'Mercado'),
        ('park', 'Parque'),
        ('museum', 'Museo'),
        ('church', 'Iglesia'),
        ('historical_landmark', 'Monumento Histórico'),
        ('tourist_attraction', 'Atracción Turística'),
        ('night_club', 'Club Nocturno'),
        ('bar_and_grill', 'Bar y Parrilla'),
        ('home_goods_store', 'Tienda de Hogar'),
        ('art_gallery', 'Galería de Arte'),
        ('shopping_mall', 'Centro Comercial'),
        ('store', 'Tienda'),
        ('supermarket', 'Supermercado'),
        ('food_store', 'Tienda de Comida'),
        ('discount_store', 'Tienda de Descuentos'),
        ('department_store', 'Tienda por Departamentos'),
        ('water_park', 'Parque Acuático'),
        ('movie_theater', 'Cine'),
        ('casino', 'Casino'),
        ('amusement_park', 'Parque de Diversiones'),
        ('amusement_center', 'Centro de Entretenimiento'),
        ('event_venue', 'Lugar de Eventos'),
        ('food', 'Comida'),
        ('point_of_interest', 'Punto de Interés'),
        ('establishment', 'Establecimiento'),
        ('bakery', 'Panadería'),
        ('cafe', 'Café'),
        ('dessert_shop', 'Tienda de Postres'),
        ('confectionery', 'Confitería'),
        ('ice_cream_shop', 'Heladería'),
        ('hamburger_restaurant', 'Restaurante de Hamburguesas'),
        ('american_restaurant', 'Restaurante Americano'),
        ('inn', 'Posada'),
        ('natural_feature', 'Característica Natural'),
        ('place_of_worship', 'Lugar de Culto'),
        ('historical_place', 'Lugar Histórico'),
        ('cafeteria', 'Cafetería'),
        ('brunch_restaurant', 'Restaurante de Brunch'),
        ('painter', 'Pintor'),
        ('courier_service', 'Servicio de Mensajería'),
        ('grocery_store', 'Tienda de Abarrotes'),
        ('wholesaler', 'Mayorista'),
        ('clothing_store', 'Tienda de Ropa'),
        ('sporting_goods_store', 'Tienda Deportiva'),
        ('furniture_store', 'Tienda de Muebles'),
        ('home_improvement_store', 'Tienda de Mejoras para el Hogar'),
    ]
    
    # Campos básicos
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=500)
    tipo_principal = models.CharField(max_length=50, choices=TIPOS_ESTABLECIMIENTO)
    tipos_adicionales = models.JSONField(default=list, help_text="Lista de tipos adicionales del establecimiento")
    place_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    
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
    horarios = models.JSONField(default=list, help_text="Horarios de operación por día")
    
    # Descripción
    descripcion = models.TextField(blank=True, null=True)
    
    # Resumen generado por IA
    resumen_ia = models.TextField(blank=True, null=True)
    
    # Palabras clave extraídas por IA para embeddings
    palabras_clave_ia = models.TextField(blank=True, null=True, help_text="Palabras clave extraídas del resumen para embeddings eficientes")
    
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
            models.Index(fields=['tipo_principal']),
            models.Index(fields=['latitud', 'longitud']),
            models.Index(fields=['rating']),
            models.Index(fields=['place_id']),
        ]

    def __str__(self):
        return f"{self.nombre} - {self.get_tipo_principal_display()}"
    
    def get_tipos_adicionales_display(self):
        """Retorna los tipos adicionales formateados"""
        if not self.tipos_adicionales:
            return []
        
        tipos_formateados = []
        for tipo in self.tipos_adicionales:
            # Buscar el display name en las opciones
            for codigo, nombre in self.TIPOS_ESTABLECIMIENTO:
                if codigo == tipo:
                    tipos_formateados.append(nombre)
                    break
            else:
                # Si no se encuentra, usar el código original
                tipos_formateados.append(tipo)
        
        return tipos_formateados
    
    def tiene_tipo(self, tipo_buscar):
        """Verifica si el lugar tiene un tipo específico"""
        if self.tipo_principal == tipo_buscar:
            return True
        return tipo_buscar in self.tipos_adicionales
    
    def es_hotel(self):
        """Verifica si es un hotel"""
        return self.tiene_tipo('hotel') or self.tiene_tipo('lodging') or self.tiene_tipo('inn')
    
    def es_restaurante(self):
        """Verifica si es un restaurante"""
        tipos_restaurante = [
            'restaurant', 'chinese_restaurant', 'bar_and_grill', 
            'hamburger_restaurant', 'american_restaurant', 'brunch_restaurant'
        ]
        return any(self.tiene_tipo(tipo) for tipo in tipos_restaurante)
    
    def es_bar(self):
        """Verifica si es un bar"""
        return self.tiene_tipo('bar') or self.tiene_tipo('night_club')
    
    def es_cafe(self):
        """Verifica si es un café"""
        return self.tiene_tipo('cafe') or self.tiene_tipo('coffee_shop') or self.tiene_tipo('cafeteria')

