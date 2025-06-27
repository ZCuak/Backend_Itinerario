# 📱 Documentación de API para Frontend - Sistema LLM

## 🎯 **Descripción General**

Esta API proporciona endpoints para búsqueda semántica inteligente de lugares turísticos usando **DeepSeek** para extracción de filtros y **embeddings vectoriales** para búsqueda semántica. Optimizada para aplicaciones frontend con respuestas rápidas y precisas.

---

## 🚀 **Endpoints Disponibles**

### **Base URL:** `http://localhost:8000/api/llm/`

---

## 1. 🔍 **Búsqueda Completa de Lugares**

### **Endpoint:** `POST /api/llm/buscar-lugares/`

**Descripción:** Procesa un mensaje natural del usuario y devuelve los mejores lugares que coinciden con la consulta.

#### **Request Body:**
```typescript
interface BuscarLugaresRequest {
  mensaje: string;                    // Requerido - Consulta del usuario
  max_candidatos?: number;            // Opcional - Máximo de resultados (default: 5)
  incluir_metadata?: boolean;         // Opcional - Incluir datos adicionales (default: true)
}
```

#### **Ejemplo de Request:**
```javascript
const response = await fetch('/api/llm/buscar-lugares/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    mensaje: "Quiero un hotel lujoso con piscina y spa",
    max_candidatos: 8,
    incluir_metadata: true
  })
});
```

#### **Response:**
```typescript
interface BuscarLugaresResponse {
  success: boolean;
  mensaje_original: string;
  filtros_extraidos: {
    tipo_establecimiento: string;
    consulta_semantica: string;
    caracteristicas: string[];
    nivel_precio: string | null;
    ubicacion: string | null;
    intencion: string;
  };
  candidatos_encontrados: number;
  mejores_candidatos: Lugar[];
  total_seleccionados: number;
  tiempo_procesamiento: number;
}

interface Lugar {
  id: number;
  nombre: string;
  tipo_principal: string;
  tipos_adicionales: string[];
  rating: number;
  score_similitud: number;
  resumen_ia: string;
  palabras_clave_ia: string;
  
  // Datos de ubicación
  direccion: string;
  latitud: number;
  longitud: number;
  total_ratings: number;
  
  // Información de contacto
  website?: string;
  telefono?: string;
  
  // Horarios y estado
  horarios: any[];
  estado_negocio: string;
  
  // Información de nivel de precio
  nivel_precios?: number;
  rango_precio_inferior?: number;
  rango_precio_superior?: number;
  moneda_precio: string;
}
```

#### **Ejemplo de Response:**
```json
{
  "success": true,
  "mensaje_original": "Quiero un hotel lujoso con piscina y spa",
  "filtros_extraidos": {
    "tipo_establecimiento": "hotel",
    "consulta_semantica": "hotel lujoso con instalaciones premium",
    "caracteristicas": ["lujoso", "piscina", "spa", "premium"],
    "nivel_precio": "lujoso",
    "ubicacion": null,
    "intencion": "dormir"
  },
  "candidatos_encontrados": 23,
  "mejores_candidatos": [
    {
      "id": 123,
      "nombre": "Hotel Luxury Resort & Spa",
      "tipo_principal": "hotel",
      "tipos_adicionales": ["lodging", "spa", "wellness"],
      "rating": 4.8,
      "score_similitud": 0.92,
      "resumen_ia": "Hotel de lujo con piscina infinita y spa completo...",
      "palabras_clave_ia": "lujo, piscina, spa, gimnasio, restaurante gourmet",
      "direccion": "Av. Principal 123, Lima",
      "latitud": -12.3456,
      "longitud": -78.9012,
      "total_ratings": 156,
      "website": "https://www.luxuryresort.com",
      "telefono": "+51 1 234-5678",
      "horarios": [
        {
          "day": "monday",
          "open": "06:00",
          "close": "23:00"
        }
      ],
      "estado_negocio": "OPERATIONAL",
      "nivel_precios": 4,
      "rango_precio_inferior": 200.0,
      "rango_precio_superior": 500.0,
      "moneda_precio": "PEN"
    }
  ],
  "total_seleccionados": 8,
  "tiempo_procesamiento": 2.3
}
```

---

## 2. 🎯 **Extracción de Filtros**

### **Endpoint:** `POST /api/llm/extraer-filtros/`

**Descripción:** Extrae solo los filtros semánticos de un mensaje sin realizar búsqueda. Útil para formularios de filtros avanzados.

#### **Request Body:**
```typescript
interface ExtraerFiltrosRequest {
  mensaje: string;  // Requerido - Mensaje del usuario
}
```

#### **Ejemplo de Request:**
```javascript
const response = await fetch('/api/llm/extraer-filtros/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    mensaje: "Busco un restaurante romántico para cenar con mi pareja"
  })
});
```

#### **Response:**
```typescript
interface ExtraerFiltrosResponse {
  success: boolean;
  mensaje_original: string;
  filtros_extraidos: {
    tipo_establecimiento: string;
    consulta_semantica: string;
    caracteristicas: string[];
    nivel_precio: string | null;
    ubicacion: string | null;
    intencion: string;
  };
}
```

#### **Ejemplo de Response:**
```json
{
  "success": true,
  "mensaje_original": "Busco un restaurante romántico para cenar con mi pareja",
  "filtros_extraidos": {
    "tipo_establecimiento": "restaurant",
    "consulta_semantica": "restaurante romántico para cena especial",
    "caracteristicas": ["romántico", "cena especial", "ambiente íntimo"],
    "nivel_precio": "romántico",
    "ubicacion": null,
    "intencion": "comer"
  }
}
```

---

## 3. 🏷️ **Búsqueda por Tipo Específico**

### **Endpoint:** `POST /api/llm/buscar-por-tipo/`

**Descripción:** Busca lugares de un tipo específico con características adicionales. Ideal para filtros de categorías.

#### **Request Body:**
```typescript
interface BuscarPorTipoRequest {
  consulta: string;                   // Requerido - Características adicionales
  tipo_establecimiento: string;       // Requerido - Tipo de lugar
  max_resultados?: number;            // Opcional - Máximo resultados (default: 10)
}
```

#### **Ejemplo de Request:**
```javascript
const response = await fetch('/api/llm/buscar-por-tipo/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    consulta: "con piscina y gimnasio",
    tipo_establecimiento: "hotel",
    max_resultados: 15
  })
});
```

#### **Response:**
```typescript
interface BuscarPorTipoResponse {
  success: boolean;
  consulta: string;
  tipo_establecimiento: string;
  resultados: Lugar[];
  total_encontrados: number;
}
```

#### **Ejemplo de Response:**
```json
{
  "success": true,
  "consulta": "con piscina y gimnasio",
  "tipo_establecimiento": "hotel",
  "resultados": [
    {
      "id": 456,
      "nombre": "Hotel Wellness Center",
      "tipo_principal": "hotel",
      "tipos_adicionales": ["lodging", "gym", "spa"],
      "rating": 4.6,
      "score_similitud": 0.88,
      "resumen_ia": "Hotel con piscina climatizada y gimnasio completo...",
      "palabras_clave_ia": "wellness, spa, piscina, masajes, relajación",
      "direccion": "Calle Wellness 789, Lima",
      "latitud": -12.3457,
      "longitud": -78.9013,
      "total_ratings": 89,
      "website": "https://www.wellnesscenter.com",
      "telefono": "+51 1 987-6543",
      "horarios": [
        {
          "day": "monday",
          "open": "05:00",
          "close": "22:00"
        }
      ],
      "estado_negocio": "OPERATIONAL",
      "nivel_precios": 3,
      "rango_precio_inferior": 120.0,
      "rango_precio_superior": 300.0,
      "moneda_precio": "PEN"
    }
  ],
  "total_encontrados": 15
}
```

---

## 4. 💚 **Health Check**

### **Endpoint:** `GET /api/llm/health/`

**Descripción:** Verifica el estado del sistema y servicios.

#### **Request:**
```javascript
const response = await fetch('/api/llm/health/', {
  method: 'GET'
});
```

#### **Response:**
```typescript
interface HealthCheckResponse {
  success: boolean;
  status: 'healthy' | 'unhealthy';
  vector_db_connected: boolean;
  deepseek_available: boolean;
  total_lugares_indexados: number;
  timestamp: string;
}
```

#### **Ejemplo de Response:**
```json
{
  "success": true,
  "status": "healthy",
  "vector_db_connected": true,
  "deepseek_available": true,
  "total_lugares_indexados": 130,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 📱 **Casos de Uso Comunes para Frontend**

### **1. Chatbot Inteligente**
```javascript
// Ejemplo de implementación de chatbot
class ChatbotAPI {
  async procesarMensaje(mensaje) {
    try {
      const response = await fetch('/api/llm/buscar-lugares/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mensaje, max_candidatos: 5 })
      });
      
      const data = await response.json();
      
      if (data.success) {
        return {
          filtros: data.filtros_extraidos,
          lugares: data.mejores_candidatos,
          tiempo: data.tiempo_procesamiento
        };
      } else {
        throw new Error(data.error);
      }
    } catch (error) {
      console.error('Error en chatbot:', error);
      throw error;
    }
  }
}
```

### **2. Filtros Avanzados**
```javascript
// Ejemplo de filtros con extracción automática
class FiltrosAvanzados {
  async extraerFiltros(mensaje) {
    const response = await fetch('/api/llm/extraer-filtros/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mensaje })
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Actualizar UI con filtros extraídos
      this.actualizarFiltrosUI(data.filtros_extraidos);
      
      // Realizar búsqueda con filtros
      return this.buscarConFiltros(data.filtros_extraidos);
    }
  }
  
  async buscarConFiltros(filtros) {
    const response = await fetch('/api/llm/buscar-por-tipo/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        consulta: filtros.consulta_semantica,
        tipo_establecimiento: filtros.tipo_establecimiento,
        max_resultados: 20
      })
    });
    
    return await response.json();
  }
}
```

### **3. Búsqueda en Tiempo Real**
```javascript
// Ejemplo de búsqueda con debounce
class BusquedaTiempoReal {
  constructor() {
    this.timeoutId = null;
    this.ultimaBusqueda = '';
  }
  
  async buscarConDebounce(mensaje, delay = 500) {
    // Cancelar búsqueda anterior
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
    }
    
    // Evitar búsquedas duplicadas
    if (mensaje === this.ultimaBusqueda) {
      return;
    }
    
    this.ultimaBusqueda = mensaje;
    
    // Programar nueva búsqueda
    this.timeoutId = setTimeout(async () => {
      try {
        const response = await fetch('/api/llm/buscar-lugares/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            mensaje, 
            max_candidatos: 10,
            incluir_metadata: false // Más rápido sin metadata
          })
        });
        
        const data = await response.json();
        this.mostrarResultados(data);
      } catch (error) {
        console.error('Error en búsqueda:', error);
      }
    }, delay);
  }
}
```

---

## 🎨 **Tipos de Establecimientos Soportados**

### **Categorías Principales:**
- `hotel` - Hoteles y alojamientos
- `restaurant` - Restaurantes y gastronomía
- `bar` - Bares y pubs
- `cafe` - Cafeterías
- `museum` - Museos y cultura
- `park` - Parques y recreación
- `shopping_mall` - Centros comerciales
- `spa` - Spas y bienestar
- `gym` - Gimnasios
- `tourist_attraction` - Atracciones turísticas

### **Tipos Adicionales:**
Cada lugar puede tener múltiples tipos adicionales que se incluyen en `tipos_adicionales`.

---

## ⚡ **Optimizaciones de Rendimiento**

### **1. Búsquedas Rápidas**
```javascript
// Para búsquedas rápidas, omitir metadata
{
  mensaje: "hotel",
  max_candidatos: 5,
  incluir_metadata: false  // Respuesta más rápida
}
```

### **2. Caché de Filtros**
```javascript
// Cachear filtros extraídos para reutilización
const filtrosCache = new Map();

async function obtenerFiltros(mensaje) {
  if (filtrosCache.has(mensaje)) {
    return filtrosCache.get(mensaje);
  }
  
  const response = await fetch('/api/llm/extraer-filtros/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mensaje })
  });
  
  const data = await response.json();
  filtrosCache.set(mensaje, data.filtros_extraidos);
  
  return data.filtros_extraidos;
}
```

---

## 🚨 **Manejo de Errores**

### **Códigos de Error Comunes:**
- `400` - Request inválido (JSON malformado, campos faltantes)
- `500` - Error interno del servidor

### **Ejemplo de Manejo:**
```javascript
async function manejarBusqueda(mensaje) {
  try {
    const response = await fetch('/api/llm/buscar-lugares/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mensaje })
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || 'Error en la búsqueda');
    }
    
    if (!data.success) {
      throw new Error(data.error || 'Error en el procesamiento');
    }
    
    return data;
  } catch (error) {
    console.error('Error:', error.message);
    // Mostrar mensaje de error al usuario
    mostrarError(error.message);
    throw error;
  }
}
```

---

## 📊 **Métricas de Rendimiento**

### **Tiempos Promedio:**
- **Extracción de filtros**: 2-3 segundos
- **Búsqueda completa**: 4-7 segundos
- **Búsqueda por tipo**: 1-3 segundos
- **Health check**: < 1 segundo

### **Límites Recomendados:**
- `max_candidatos`: 5-20 (óptimo: 10)
- `max_resultados`: 10-50 (óptimo: 20)
- Longitud de mensaje: 10-500 caracteres

---

## 🔧 **Configuración para Desarrollo**

### **Variables de Entorno:**
```bash
# Backend
DEEPSEEK_API_KEY=tu_api_key
PINECONE_API_KEY=tu_api_key
PINECONE_ENVIRONMENT=tu_environment
PINECONE_INDEX_NAME=lugares-turisticos
```

### **CORS (si es necesario):**
```python
# En settings.py del backend
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React
    "http://localhost:8080",  # Vue
    "http://localhost:4200",  # Angular
]
```

---

## ⚡ **Optimización de Datos Adicionales**

### **Flujo Optimizado:**
1. **Extracción de Filtros** - DeepSeek analiza el mensaje del usuario
2. **Búsqueda Semántica** - Embeddings encuentran candidatos relevantes
3. **Selección LLM** - DeepSeek selecciona los mejores candidatos
4. **Enriquecimiento BD** - Se obtienen datos adicionales directamente de la base de datos

### **Ventajas de la Optimización:**
- ✅ **Ahorro de Tokens**: No se usa LLM para obtener datos básicos
- ✅ **Datos Completos**: Información actualizada de la base de datos
- ✅ **Rendimiento**: Consultas directas a BD son más rápidas
- ✅ **Precisión**: Datos exactos de nivel de precio, horarios, contacto

### **Datos Obtenidos de la BD:**
- **Información de Contacto**: Website, teléfono
- **Ubicación**: Dirección exacta, coordenadas
- **Horarios**: Horarios de operación por día
- **Nivel de Precio**: Rango inferior/superior y moneda
- **Estado del Negocio**: Si está operativo
- **Ratings**: Total de calificaciones

### **Ejemplo de Implementación:**
```python
# En el integrador
def obtener_datos_adicionales_bd(self, candidatos):
    # Extraer IDs únicos
    ids_lugares = [candidato['id'] for candidato in candidatos]
    
    # Consulta eficiente a la BD
    lugares_bd = LugarGooglePlaces.objects.filter(
        id__in=ids_lugares
    ).select_related('nivel_precios')
    
    # Enriquecer candidatos con datos completos
    return self._enriquecer_candidatos(candidatos, lugares_bd)
```

---

**📅 Última actualización**: Enero 2024  
**🔄 Versión**: 2.0 (Optimizada para Frontend)  
**📧 Soporte**: Documentación técnica para integración frontend 