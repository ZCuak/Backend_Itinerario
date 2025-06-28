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

class Cities(models.Model):
    country = models.ForeignKey(Countries, on_delete=models.CASCADE, db_column='country_id')
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

class Transporte(models.Model):
    nombre = models.CharField(max_length=100)
    estado = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'transporte'

    def __str__(self):
        return self.nombre

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

class Itinerario(models.Model):
    """
    Modelo principal para almacenar itinerarios de viaje
    """
    # Campos básicos del itinerario
    lugar = models.CharField(max_length=255, default='')
    num_dias = models.IntegerField(default=1)
    estado = models.CharField(max_length=20, default='borrador')
    
    # Relaciones con otras tablas (ahora opcionales)
    pais = models.ForeignKey(Countries, on_delete=models.CASCADE, db_column='pais_id', null=True, blank=True)
    transporte = models.ForeignKey(Transporte, on_delete=models.CASCADE, db_column='transporte_id', null=True, blank=True)
    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE, db_column='viaje_id', null=True, blank=True)
    
    # Información del itinerario
    titulo = models.CharField(max_length=200, default='')
    descripcion = models.TextField(blank=True, null=True)
    
    # Fechas del viaje
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    num_noches = models.IntegerField(default=0)
    
    # Presupuesto
    presupuesto_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    moneda_presupuesto = models.CharField(max_length=3, default='PEN')
    nivel_precio_preferido = models.ForeignKey(
        'NivelPrecio', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        db_column='nivel_precio_preferido_id'
    )
    
    # Preferencias del usuario (JSON)
    preferencias_actividades = models.JSONField(default=list)
    preferencias_alimentacion = models.JSONField(default=list)
    preferencias_alojamiento = models.JSONField(default=list)
    
    # Campos de control
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'itinerario'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.titulo} - {self.lugar}"

    def calcular_costo_total(self):
        """Calcula el costo total del itinerario"""
        if self.presupuesto_total:
            return self.presupuesto_total
        return 0

    def obtener_estadisticas(self):
        """Obtiene estadísticas del itinerario"""
        return {
            'num_dias': self.num_dias,
            'num_noches': self.num_noches,
            'presupuesto': self.presupuesto_total,
            'estado': self.estado
        }

class DiaItinerario(models.Model):
    """
    Representa un día específico del itinerario
    """
    itinerario = models.ForeignKey(
        Itinerario, 
        on_delete=models.CASCADE, 
        related_name='dias'
    )
    dia_numero = models.IntegerField(help_text="Número del día (1, 2, 3, etc.)")
    fecha = models.DateField()
    
    # Alojamiento para esta noche
    hotel = models.ForeignKey(
        'LugarGooglePlaces',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dias_hotel',
        limit_choices_to={'tipo_principal__in': ['hotel', 'lodging', 'inn']}
    )
    
    # Campos de control
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dia_itinerario'
        unique_together = ['itinerario', 'dia_numero']
        ordering = ['dia_numero']
    
    def __str__(self):
        return f"Día {self.dia_numero} - {self.fecha}"
    
    def calcular_costo_dia(self):
        """Calcula el costo total del día"""
        total = 0
        
        # Costo del hotel
        if self.hotel and self.hotel.nivel_precios:
            if self.hotel.nivel_precios.rango_inferior:
                total += float(self.hotel.nivel_precios.rango_inferior)
        
        # Costo de actividades
        for actividad in self.actividades.all():
            if actividad.costo_estimado:
                total += float(actividad.costo_estimado)
        
        return total

class ActividadItinerario(models.Model):
    """
    Representa una actividad específica en un día del itinerario
    """
    TIPOS_ACTIVIDAD = [
        ('visita_turistica', 'Visita Turística'),
        ('restaurante', 'Restaurante'),
        ('cafe', 'Café'),
        ('bar', 'Bar'),
        ('shopping', 'Compras'),
        ('entretenimiento', 'Entretenimiento'),
        ('transporte', 'Transporte'),
        ('descanso', 'Descanso'),
        ('otro', 'Otro')
    ]
    
    dia = models.ForeignKey(
        DiaItinerario,
        on_delete=models.CASCADE,
        related_name='actividades'
    )
    
    # Información de la actividad
    tipo_actividad = models.CharField(max_length=30, choices=TIPOS_ACTIVIDAD)
    lugar = models.ForeignKey(
        'LugarGooglePlaces',
        on_delete=models.CASCADE,
        related_name='actividades_itinerario'
    )
    
    # Horarios
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    duracion_minutos = models.IntegerField(
        help_text="Duración estimada en minutos"
    )
    
    # Costos
    costo_estimado = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Costo estimado de la actividad"
    )
    
    # Notas y descripción
    descripcion = models.TextField(blank=True, null=True)
    notas_adicionales = models.TextField(blank=True, null=True)
    
    # Orden en el día
    orden = models.IntegerField(default=0)
    
    # Campos de control
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'actividad_itinerario'
        ordering = ['dia', 'orden', 'hora_inicio']
        unique_together = ['dia', 'orden']
    
    def __str__(self):
        return f"{self.get_tipo_actividad_display()} - {self.lugar.nombre}"
    
    def es_compatible_horario(self):
        """Verifica si la actividad es compatible con los horarios del lugar"""
        if not self.lugar.horarios:
            return True  # Si no hay horarios, asumir que está abierto
        
        # Obtener el día de la semana
        from datetime import datetime
        dia_semana = self.dia.fecha.strftime('%A').lower()
        
        # Buscar horarios para ese día
        for horario in self.lugar.horarios:
            if isinstance(horario, dict):
                # Formato: {"day": "monday", "open": "09:00", "close": "18:00"}
                if horario.get('day', '').lower() == dia_semana:
                    hora_apertura = horario.get('open', '00:00')
                    hora_cierre = horario.get('close', '23:59')
                    
                    # Verificar si la actividad está dentro del horario
                    return hora_apertura <= self.hora_inicio.strftime('%H:%M') <= hora_cierre
            elif isinstance(horario, str):
                # Formato: "Monday: 9:00 AM – 6:00 PM"
                if dia_semana in horario.lower():
                    # Extraer horarios del string (implementación básica)
                    return True  # Por ahora asumir que es compatible
        
        return False  # Si no se encuentra el día, asumir que está cerrado

