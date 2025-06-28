# 🗺️ Documentación de API - Sistema de Itinerarios Inteligentes

## 🎯 **Descripción General**

Sistema avanzado para generar itinerarios de viaje personalizados usando **DeepSeek** para análisis semántico de preferencias y selección inteligente de lugares. El sistema considera duración, presupuesto, preferencias del usuario y horarios de establecimientos para crear experiencias únicas.

---

## 🚀 **Características Principales**

### ✅ **Funcionalidades Implementadas**
- **Generación Inteligente**: Usa DeepSeek para analizar preferencias y seleccionar lugares
- **Filtrado Avanzado**: Búsqueda en BD usando `tipo_principal` y `tipos_adicionales`
- **Variedad Garantizada**: Diferentes restaurantes cada día para evitar repetición
- **Optimización Temporal**: Distribución inteligente de actividades a lo largo del día
- **Gestión de Presupuesto**: Control de costos por día y actividad
- **Verificación de Horarios**: Considera horarios de operación de establecimientos

### 🎨 **Tipos de Actividades Soportadas**
- **Alojamiento**: Hoteles, resorts, hostales
- **Alimentación**: Restaurantes, cafés, bares (con variedad diaria)
- **Puntos de Interés**: Museos, parques, atracciones turísticas
- **Compras**: Centros comerciales, tiendas, mercados
- **Entretenimiento**: Teatros, cines, actividades nocturnas

---

## 📡 **Endpoints Disponibles**

### **Base URL:** `http://localhost:8000/api/itinerarios/`

---

## 1. 🎯 **Generar Itinerario Inteligente**

### **Endpoint:** `POST /api/itinerarios/generar/`

**Descripción:** Genera un itinerario completo basado en preferencias naturales del usuario.

#### **Request Body:**
```typescript
interface GenerarItinerarioRequest {
  fecha_inicio: string;                    // Requerido - YYYY-MM-DD
  fecha_fin: string;                       // Requerido - YYYY-MM-DD
  preferencias_usuario: string;            // Requerido - Descripción natural
  presupuesto_total?: number;              // Opcional - Presupuesto total
  nivel_precio_preferido?: number;         // Opcional - 1-4 (económico a lujoso)
  titulo?: string;                         // Opcional - Título del itinerario
}
```

#### **Ejemplo de Request:**
```javascript
const response = await fetch('/api/itinerarios/generar/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    fecha_inicio: "2024-02-15",
    fecha_fin: "2024-02-17",
    preferencias_usuario: "Quiero un viaje de aventura con experiencias culturales y buena comida local",
    presupuesto_total: 1500,
    nivel_precio_preferido: 3,
    titulo: "Aventura Cultural en Lima"
  })
});
```

#### **Response:**
```typescript
interface GenerarItinerarioResponse {
  success: boolean;
  itinerario: {
    id: number;
    titulo: string;
    fecha_inicio: string;
    fecha_fin: string;
    num_dias: number;
    num_noches: number;
    presupuesto_total: number | null;
    estado: string;
    estadisticas: {
      costo_total: number;
      costo_promedio_dia: number;
      total_actividades: number;
      actividades_por_dia: number;
    };
    tipos_establecimientos_seleccionados: {
      alojamiento: string[];
      alimentacion: string[];
      puntos_interes: string[];
      compras: string[];
    };
  };
  dias: DiaItinerario[];
}

interface DiaItinerario {
  dia_numero: number;
  fecha: string;
  hotel: {
    id: number;
    nombre: string;
    direccion: string;
    rating: number;
    nivel_precios: number | null;
  } | null;
  actividades: ActividadItinerario[];
  costo_total_dia: number;
}

interface ActividadItinerario {
  id: number;
  tipo_actividad: string;
  lugar: {
    id: number;
    nombre: string;
    direccion: string;
    rating: number;
    nivel_precios: number | null;
  };
  hora_inicio: string;           // HH:MM
  hora_fin: string;              // HH:MM
  duracion_minutos: number;
  costo_estimado: number | null;
  descripcion: string;
  orden: number;
}
```

#### **Ejemplo de Response:**
```json
{
  "success": true,
  "itinerario": {
    "id": 1,
    "titulo": "Aventura Cultural en Lima",
    "fecha_inicio": "2024-02-15",
    "fecha_fin": "2024-02-17",
    "num_dias": 3,
    "num_noches": 2,
    "presupuesto_total": 1500.0,
    "estado": "generado",
    "estadisticas": {
      "costo_total": 1420.0,
      "costo_promedio_dia": 473.33,
      "total_actividades": 18,
      "actividades_por_dia": 6
    },
    "tipos_establecimientos_seleccionados": {
      "alojamiento": ["hotel", "resort"],
      "alimentacion": ["restaurant", "cafe", "bar"],
      "puntos_interes": ["museum", "tourist_attraction", "park"],
      "compras": ["shopping_mall", "market"]
    }
  },
  "dias": [
    {
      "dia_numero": 1,
      "fecha": "2024-02-15",
      "hotel": {
        "id": 123,
        "nombre": "Hotel Aventura Premium",
        "direccion": "Av. Principal 456, Lima",
        "rating": 4.6,
        "nivel_precios": 3
      },
      "actividades": [
        {
          "id": 1,
          "tipo_actividad": "restaurante",
          "lugar": {
            "id": 456,
            "nombre": "Restaurante Cevichería El Pescador",
            "direccion": "Calle Marina 789, Lima",
            "rating": 4.8,
            "nivel_precios": 3
          },
          "hora_inicio": "07:30",
          "hora_fin": "08:30",
          "duracion_minutos": 60,
          "costo_estimado": 80.0,
          "descripcion": "Desayuno con ceviche fresco y café peruano",
          "orden": 1
        },
        {
          "id": 2,
          "tipo_actividad": "visita_turistica",
          "lugar": {
            "id": 789,
            "nombre": "Museo de Arte Contemporáneo",
            "direccion": "Av. Cultura 321, Lima",
            "rating": 4.5,
            "nivel_precios": 2
          },
          "hora_inicio": "09:00",
          "hora_fin": "11:00",
          "duracion_minutos": 120,
          "costo_estimado": 50.0,
          "descripcion": "Visita guiada al museo con exposiciones de arte moderno",
          "orden": 2
        }
      ],
      "costo_total_dia": 480.0
    }
  ]
}
```

---

## 2. 📋 **Listar Itinerarios**

### **Endpoint:** `GET /api/itinerarios/`

**Descripción:** Obtiene la lista de itinerarios generados.

#### **Query Parameters:**
```typescript
interface ListarItinerariosParams {
  estado?: string;               // Opcional - Filtrar por estado
  fecha_inicio?: string;         // Opcional - Filtrar desde fecha
  fecha_fin?: string;            // Opcional - Filtrar hasta fecha
  limit?: number;                // Opcional - Límite de resultados
  offset?: number;               // Opcional - Offset para paginación
}
```

#### **Ejemplo de Request:**
```javascript
const response = await fetch('/api/itinerarios/?estado=generado&limit=10');
```

#### **Response:**
```typescript
interface ListarItinerariosResponse {
  success: boolean;
  itinerarios: ItinerarioResumen[];
  total: number;
  limit: number;
  offset: number;
}

interface ItinerarioResumen {
  id: number;
  titulo: string;
  fecha_inicio: string;
  fecha_fin: string;
  num_dias: number;
  presupuesto_total: number | null;
  estado: string;
  costo_total: number;
  total_actividades: number;
}
```

---

## 3. 🔍 **Obtener Itinerario Detallado**

### **Endpoint:** `GET /api/itinerarios/{id}/`

**Descripción:** Obtiene los detalles completos de un itinerario específico.

#### **Ejemplo de Request:**
```javascript
const response = await fetch('/api/itinerarios/1/');
```

#### **Response:**
```typescript
interface ObtenerItinerarioResponse {
  success: boolean;
  itinerario: ItinerarioCompleto;
}

interface ItinerarioCompleto {
  // Misma estructura que en generar itinerario
  // Incluye todos los días y actividades detalladas
}
```

---

## 4. ✏️ **Actualizar Itinerario**

### **Endpoint:** `PUT /api/itinerarios/{id}/`

**Descripción:** Actualiza un itinerario existente.

#### **Request Body:**
```typescript
interface ActualizarItinerarioRequest {
  titulo?: string;
  presupuesto_total?: number;
  nivel_precio_preferido?: number;
  estado?: string;
}
```

#### **Ejemplo de Request:**
```javascript
const response = await fetch('/api/itinerarios/1/', {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    titulo: "Mi Viaje Aventurero Actualizado",
    presupuesto_total: 2000
  })
});
```

---

## 5. 🗑️ **Eliminar Itinerario**

### **Endpoint:** `DELETE /api/itinerarios/{id}/`

**Descripción:** Elimina un itinerario y todas sus actividades asociadas.

#### **Ejemplo de Request:**
```javascript
const response = await fetch('/api/itinerarios/1/', {
  method: 'DELETE'
});
```

#### **Response:**
```json
{
  "success": true,
  "mensaje": "Itinerario eliminado exitosamente"
}
```

---

## 🧠 **Inteligencia Artificial - DeepSeek**

### **Análisis de Preferencias**
El sistema usa DeepSeek para:
- **Interpretar preferencias naturales**: "aventura", "relajante", "cultural"
- **Determinar tipos de establecimientos**: Selecciona categorías apropiadas
- **Seleccionar lugares óptimos**: Considera rating, precio, horarios
- **Optimizar distribución**: Organiza actividades temporalmente

### **Filtrado Inteligente en BD**
```python
# Búsqueda en tipo_principal Y tipos_adicionales
query = LugarGooglePlaces.objects.filter(
    Q(tipo_principal__in=tipos_buscar) |
    Q(tipos_adicionales__overlap=tipos_buscar)
)
```

### **Variedad de Restaurantes**
- **Diferentes lugares cada día**: Evita repetición de restaurantes
- **Variedad de cocinas**: Diferentes tipos de comida
- **Distribución temporal**: Desayuno, almuerzo, cena en horarios apropiados

---

## 📊 **Estructura de Datos**

### **Modelo Itinerario**
```python
class Itinerario(models.Model):
    titulo = models.CharField(max_length=200)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    num_dias = models.IntegerField()
    num_noches = models.IntegerField()
    presupuesto_total = models.DecimalField(null=True, blank=True)
    nivel_precio_preferido = models.ForeignKey(NivelPrecio, null=True)
    preferencias_actividades = models.JSONField()
    preferencias_alimentacion = models.JSONField()
    preferencias_alojamiento = models.JSONField()
    estado = models.CharField(max_length=20, default='generado')
```

### **Modelo Día de Itinerario**
```python
class DiaItinerario(models.Model):
    itinerario = models.ForeignKey(Itinerario, on_delete=models.CASCADE)
    dia_numero = models.IntegerField()
    fecha = models.DateField()
    hotel = models.ForeignKey(LugarGooglePlaces, null=True, blank=True)
```

### **Modelo Actividad**
```python
class ActividadItinerario(models.Model):
    dia = models.ForeignKey(DiaItinerario, on_delete=models.CASCADE)
    tipo_actividad = models.CharField(max_length=50)
    lugar = models.ForeignKey(LugarGooglePlaces, on_delete=models.CASCADE)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    duracion_minutos = models.IntegerField()
    costo_estimado = models.DecimalField(null=True, blank=True)
    descripcion = models.TextField()
    orden = models.IntegerField()
```

---

## 🎯 **Casos de Uso Comunes**

### **1. Viaje de Aventura**
```javascript
const itinerarioAventura = await fetch('/api/itinerarios/generar/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    fecha_inicio: "2024-03-01",
    fecha_fin: "2024-03-03",
    preferencias_usuario: "Quiero un viaje lleno de aventura, deportes extremos y experiencias al aire libre",
    presupuesto_total: 2000,
    nivel_precio_preferido: 3
  })
});
```

### **2. Viaje Cultural**
```javascript
const itinerarioCultural = await fetch('/api/itinerarios/generar/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    fecha_inicio: "2024-04-15",
    fecha_fin: "2024-04-17",
    preferencias_usuario: "Busco un viaje cultural con museos, arte, historia y gastronomía local",
    presupuesto_total: 1200,
    nivel_precio_preferido: 2
  })
});
```

### **3. Viaje Relajante**
```javascript
const itinerarioRelajante = await fetch('/api/itinerarios/generar/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    fecha_inicio: "2024-05-10",
    fecha_fin: "2024-05-12",
    preferencias_usuario: "Necesito un viaje relajante con spa, masajes, buena comida y descanso",
    presupuesto_total: 1800,
    nivel_precio_preferido: 4
  })
});
```

---

## ⚡ **Optimizaciones Implementadas**

### **1. Filtrado Eficiente en BD**
- **Búsqueda en múltiples campos**: `tipo_principal` y `tipos_adicionales`
- **Filtros combinados**: Rating, precio, horarios, estado
- **Exclusión de duplicados**: Evita lugares ya seleccionados

### **2. Variedad de Restaurantes**
- **Control global**: Conjunto de lugares ya seleccionados
- **Diferentes tipos**: Restaurantes, cafés, bares
- **Distribución temporal**: Horarios apropiados para cada comida

### **3. Optimización de Rendimiento**
- **Consultas eficientes**: Uso de `select_related` y `prefetch_related`
- **Caché de selecciones**: Evita reprocesamiento
- **Límites inteligentes**: Máximo de candidatos por consulta

---

## 🚨 **Manejo de Errores**

### **Códigos de Error Comunes:**
- `400` - Datos de entrada inválidos
- `404` - Itinerario no encontrado
- `500` - Error interno del servidor

### **Ejemplo de Manejo:**
```javascript
async function generarItinerario(datos) {
  try {
    const response = await fetch('/api/itinerarios/generar/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos)
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || 'Error en la generación');
    }
    
    if (!data.success) {
      throw new Error(data.error || 'Error en el procesamiento');
    }
    
    return data;
  } catch (error) {
    console.error('Error:', error.message);
    throw error;
  }
}
```

---

## 📈 **Métricas de Rendimiento**

### **Tiempos Promedio:**
- **Análisis de preferencias**: 3-5 segundos
- **Selección de lugares**: 2-4 segundos por actividad
- **Optimización temporal**: 1-2 segundos
- **Generación completa**: 10-20 segundos

### **Límites Recomendados:**
- **Duración del viaje**: 1-14 días
- **Presupuesto**: 100-10000 unidades monetarias
- **Actividades por día**: 4-8 actividades

---

## 🔧 **Configuración**

### **Variables de Entorno:**
```bash
# DeepSeek
DEEPSEEK_API_KEY=tu_api_key
DEEPSEEK_MODEL=deepseek-chat

# Base de Datos
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Configuración
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

**📅 Última actualización**: Enero 2024  
**🔄 Versión**: 2.0 (Con filtrado inteligente y variedad de restaurantes)  
**📧 Soporte**: Sistema completo de itinerarios inteligentes 