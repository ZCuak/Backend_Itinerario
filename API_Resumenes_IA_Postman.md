# API de Resúmenes por IA - Documentación para Postman

Esta documentación describe cómo usar las nuevas APIs para generar resúmenes por IA de los lugares de Google Places usando DeepSeek.

## Configuración Base

**URL Base:** `http://localhost:8000/chatbot/places/`

**Headers requeridos:**
```
Content-Type: application/json
```

## 1. Generar Resumen IA para un Lugar Específico

### Endpoint
```
POST /generar-resumen-ia/
```

### Descripción
Genera un resumen por IA para un lugar específico usando DeepSeek.

### Body (JSON)
```json
{
    "lugar_id": 1
}
```

### Respuesta Exitosa (200)
```json
{
    "status": "success",
    "message": "Resumen generado exitosamente",
    "data": {
        "lugar_id": 1,
        "nombre": "Restaurante El Buen Sabor",
        "resumen_ia": "El Restaurante El Buen Sabor es un establecimiento gastronómico que ofrece una experiencia culinaria única en el corazón de la ciudad. Con una calificación de 4.2/5 basada en más de 150 reseñas, este restaurante se destaca por su ambiente acogedor y su cocina tradicional con toques modernos.\n\nEl lugar ofrece una experiencia gastronómica completa, desde platos principales hasta postres artesanales. Su menú incluye opciones para todos los gustos, con especialidades locales que reflejan la cultura culinaria de la región.\n\nVale la pena visitarlo por su excelente relación calidad-precio, su servicio atento y la autenticidad de sus sabores. El restaurante mantiene un nivel de precios moderado, perfecto para comidas familiares o cenas románticas.\n\nInformación práctica: El restaurante está abierto de lunes a domingo, con horarios que van desde las 12:00 hasta las 23:00. Para reservas o consultas, pueden contactar al teléfono disponible o visitar su sitio web.\n\nRecomendaciones: Se sugiere hacer reserva los fines de semana, especialmente durante las horas pico. También es recomendable probar sus platos de la casa y no perderse sus postres caseros."
    }
}
```

### Respuesta de Error (400/404/500)
```json
{
    "status": "error",
    "message": "Lugar no encontrado",
    "data": null
}
```

---

## 2. Generar Resúmenes IA en Lotes

### Endpoint
```
POST /generar-resumenes-lotes-ia/
```

### Descripción
Genera resúmenes por IA para múltiples lugares en lotes, ideal para procesar muchos lugares a la vez.

### Body (JSON)
```json
{
    "categoria": "restaurantes",
    "max_lugares": 10,
    "max_lotes": 5
}
```

### Parámetros Opcionales
- `categoria`: Filtrar por categoría específica (restaurantes, hoteles, museos, etc.)
- `max_lugares`: Número máximo de lugares a procesar (default: 10)
- `max_lotes`: Número de lugares por lote (default: 5)

### Respuesta Exitosa (200)
```json
{
    "status": "success",
    "message": "Procesamiento completado. 8 resúmenes generados",
    "data": {
        "lugares_procesados": 10,
        "resumenes_generados": 8,
        "resumenes": {
            "1": "Resumen generado para lugar 1...",
            "3": "Resumen generado para lugar 3...",
            "5": "Resumen generado para lugar 5..."
        }
    }
}
```

---

## 3. Listar Lugares con Resúmenes

### Endpoint
```
GET /listar-lugares-resumenes/
```

### Descripción
Lista lugares con sus resúmenes de IA, con paginación y filtros.

### Parámetros de Query
- `page`: Número de página (default: 1)
- `page_size`: Elementos por página (default: 10)
- `categoria`: Filtrar por categoría
- `tiene_resumen`: Filtrar por si tiene resumen de IA ("true"/"false")

### Ejemplos de URLs

**Listar todos los lugares:**
```
GET /listar-lugares-resumenes/
```

**Listar lugares con resúmenes:**
```
GET /listar-lugares-resumenes/?tiene_resumen=true
```

**Listar lugares sin resúmenes:**
```
GET /listar-lugares-resumenes/?tiene_resumen=false
```

**Listar restaurantes con resúmenes:**
```
GET /listar-lugares-resumenes/?categoria=restaurantes&tiene_resumen=true
```

**Paginación:**
```
GET /listar-lugares-resumenes/?page=2&page_size=5
```

### Respuesta Exitosa (200)
```json
{
    "status": "success",
    "message": "Lugares encontrados: 25",
    "data": {
        "lugares": [
            {
                "id": 1,
                "nombre": "Restaurante El Buen Sabor",
                "direccion": "Av. Principal 123, Lima",
                "categoria": "restaurantes",
                "tipo_principal": "restaurant",
                "rating": 4.2,
                "total_ratings": 150,
                "nivel_precios": "Moderado: Lugares con precios estándar...",
                "descripcion": "Descripción original del lugar...",
                "resumen_ia": "Resumen generado por IA...",
                "website": "https://example.com",
                "telefono": "+51 123 456 789",
                "horarios": ["Lunes: 12:00-23:00", "Martes: 12:00-23:00"],
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T15:45:00Z"
            }
        ],
        "paginacion": {
            "pagina_actual": 1,
            "total_paginas": 3,
            "total_lugares": 25,
            "lugares_por_pagina": 10,
            "tiene_siguiente": true,
            "tiene_anterior": false
        }
    }
}
```

---

## Categorías Disponibles

Las siguientes categorías están disponibles para filtrar:

- `restaurantes`
- `hoteles`
- `lugares_acuaticos`
- `lugares_turisticos`
- `discotecas`
- `museos`
- `lugares_campestres`
- `centros_comerciales`
- `lugares_de_entretenimiento`

---

## Flujo de Trabajo Recomendado

1. **Buscar lugares cercanos** usando `/lugares-cercanos/`
2. **Generar resúmenes en lotes** usando `/generar-resumenes-lotes-ia/`
3. **Listar y revisar** los resúmenes usando `/listar-lugares-resumenes/`
4. **Generar resúmenes individuales** si es necesario usando `/generar-resumen-ia/`

---

## Notas Importantes

- Los resúmenes se generan usando DeepSeek AI
- El proceso puede tomar tiempo dependiendo del número de lugares
- Se recomienda procesar en lotes pequeños para evitar límites de rate
- Los resúmenes se guardan automáticamente en la base de datos
- Solo se procesan lugares que no tienen resumen de IA o tienen resúmenes vacíos

---

## Ejemplos de Colección Postman

### 1. Generar Resumen Individual
```json
{
    "name": "Generar Resumen IA Individual",
    "request": {
        "method": "POST",
        "header": [
            {
                "key": "Content-Type",
                "value": "application/json"
            }
        ],
        "body": {
            "mode": "raw",
            "raw": "{\n    \"lugar_id\": 1\n}"
        },
        "url": {
            "raw": "{{base_url}}/generar-resumen-ia/",
            "host": ["{{base_url}}"],
            "path": ["generar-resumen-ia", ""]
        }
    }
}
```

### 2. Generar Resúmenes en Lotes
```json
{
    "name": "Generar Resúmenes IA en Lotes",
    "request": {
        "method": "POST",
        "header": [
            {
                "key": "Content-Type",
                "value": "application/json"
            }
        ],
        "body": {
            "mode": "raw",
            "raw": "{\n    \"categoria\": \"restaurantes\",\n    \"max_lugares\": 5,\n    \"max_lotes\": 3\n}"
        },
        "url": {
            "raw": "{{base_url}}/generar-resumenes-lotes-ia/",
            "host": ["{{base_url}}"],
            "path": ["generar-resumenes-lotes-ia", ""]
        }
    }
}
```

### 3. Listar Lugares con Resúmenes
```json
{
    "name": "Listar Lugares con Resúmenes",
    "request": {
        "method": "GET",
        "header": [],
        "url": {
            "raw": "{{base_url}}/listar-lugares-resumenes/?tiene_resumen=true&page=1&page_size=10",
            "host": ["{{base_url}}"],
            "path": ["listar-lugares-resumenes", ""],
            "query": [
                {
                    "key": "tiene_resumen",
                    "value": "true"
                },
                {
                    "key": "page",
                    "value": "1"
                },
                {
                    "key": "page_size",
                    "value": "10"
                }
            ]
        }
    }
}
```

# API de Búsqueda Natural con Pinecone y DeepSeek

## 🆕 Nueva Funcionalidad: Búsqueda Natural

El sistema ahora puede procesar mensajes naturales del usuario usando DeepSeek para extraer automáticamente los criterios de búsqueda.

### Endpoint Principal

```bash
POST /api/pinecone/places/process-natural-search/
```

### Ejemplo de Uso

**Request:**
```json
{
    "user_message": "para comer quiero ir a una cafetería de 4 estrellas"
}
```

**Response:**
```json
{
    "success": true,
    "user_message": "para comer quiero ir a una cafetería de 4 estrellas",
    "extracted_criteria": {
        "place_type": "cafetería",
        "category": "restaurantes",
        "rating_min": 4.0,
        "intent": "comer",
        "features": []
    },
    "search_method_used": "rating_and_features",
    "total_results": 3,
    "results": [
        {
            "id": 123,
            "nombre": "Café Central",
            "tipo_principal": "cafe",
            "rating": 4.2,
            "nivel_precios": "Moderado",
            "direccion": "Av. Principal 123",
            "resumen_ia": "Cafetería elegante con ambiente acogedor...",
            "score": 0.85
        }
    ]
}
```

### Ejemplos de Mensajes Naturales

| Mensaje del Usuario | Criterios Extraídos |
|---------------------|-------------------|
| "para comer quiero ir a una cafetería de 4 estrellas" | `place_type: "cafetería", rating_min: 4.0, intent: "comer"` |
| "busco un restaurante italiano que esté abierto ahora" | `place_type: "restaurante", features: ["italiano"], opening_hours: "abierto_ahora"` |
| "necesito un hotel de 3 estrellas con gimnasio y piscina" | `place_type: "hotel", rating_min: 3.0, features: ["gimnasio", "piscina"], intent: "dormir"` |
| "quiero ir a un bar con música en vivo abierto 24 horas" | `place_type: "bar", features: ["música en vivo"], opening_hours: "24_horas"` |
| "busco un centro comercial abierto fines de semana" | `place_type: "centro comercial", opening_hours: "fines_semana", intent: "compras"` |

## APIs de Búsqueda Específica

### 1. Búsqueda por Tipo y Características

```bash
POST /api/pinecone/places/search-by-type-and-features/
```

```json
{
    "place_type": "restaurante",
    "features": ["italiano", "terraza"],
    "top_k": 5
}
```

### 2. Búsqueda con Rating Específico

```bash
POST /api/pinecone/places/search-with-rating-and-features/
```

```json
{
    "place_type": "restaurante",
    "rating": 4.0,
    "features": ["peruano", "ceviche"],
    "rating_tolerance": 0.5,
    "top_k": 5
}
```

### 3. Búsqueda por Horarios

```bash
POST /api/pinecone/places/search-by-opening-hours/
```

```json
{
    "place_type": "restaurante",
    "opening_criteria": "abierto_ahora",
    "features": ["italiano"],
    "top_k": 5
}
```

**Criterios de horario disponibles:**
- `abierto_ahora`: Lugares abiertos en este momento
- `24_horas`: Lugares abiertos las 24 horas
- `fines_semana`: Lugares abiertos los fines de semana
- `lunes_viernes`: Lugares abiertos de lunes a viernes

### 4. Búsqueda por Categoría

```bash
POST /api/pinecone/places/search-by-category-and-features/
```

```json
{
    "category": "lugares_de_entretenimiento",
    "features": ["niños", "familia"],
    "rating_min": 4.0,
    "top_k": 5
}
```

### 5. Búsqueda Inteligente

```bash
POST /api/pinecone/places/smart-search/
```

```json
{
    "place_type": "restaurante",
    "category": "restaurantes",
    "features": ["italiano", "terraza"],
    "rating_min": 4.0,
    "rating_max": 5.0,
    "opening_hours": "abierto_ahora",
    "location": "Chiclayo centro",
    "price_level": "moderado",
    "top_k": 5
}
```

## APIs para Hoteles Específicos

### 1. Búsqueda de Hoteles con Amenidades

```bash
POST /api/pinecone/places/search-hotels/
```

```json
{
    "amenities": ["gimnasio", "piscina", "spa"],
    "top_k": 5
}
```

### 2. Búsqueda de Hoteles con Rating

```bash
POST /api/pinecone/places/search-hotels-rating/
```

```json
{
    "rating": 3.0,
    "amenities": ["restaurante", "estacionamiento"],
    "rating_tolerance": 0.5,
    "top_k": 5
}
```

### 3. Búsqueda de Hoteles por Rango de Rating

```bash
POST /api/pinecone/places/search-hotels-rating-range/
```

```json
{
    "min_rating": 3.0,
    "max_rating": 4.0,
    "amenities": ["restaurante"],
    "top_k": 5
}
```

## APIs de Gestión

### 1. Sincronización

```bash
POST /api/pinecone/places/sync/
```

Sincroniza todos los lugares de la base de datos con Pinecone.

### 2. Estadísticas

```bash
GET /api/pinecone/places/stats/
```

Obtiene estadísticas del índice de Pinecone.

### 3. Limpiar Índice

```bash
POST /api/pinecone/places/clear-index/
```

Elimina todos los vectores del índice.

## Categorías Disponibles

- `restaurantes`
- `hoteles`
- `lugares_acuaticos`
- `lugares_turisticos`
- `discotecas`
- `museos`
- `lugares_campestres`
- `centros_comerciales`
- `lugares_de_entretenimiento`

## Tipos de Lugares Soportados

- **Hoteles**: `hotel`, `lodging`
- **Restaurantes**: `restaurant`, `food`, `cafetería`
- **Bares**: `bar`, `night_club`
- **Parques**: `park`, `natural_feature`
- **Centros Comerciales**: `shopping_mall`, `store`
- **Museos**: `museum`, `art_gallery`
- **Discotecas**: `night_club`, `bar`
- **Lugares Turísticos**: `tourist_attraction`, `point_of_interest`

## Configuración Requerida

### Variables de Entorno

```bash
PINECONE_API_KEY=tu_api_key_de_pinecone
PINECONE_ENVIRONMENT=tu_environment
API_KEY_OPENAI=tu_api_key_de_deepseek
```

### Configuración por Defecto

- **Modelo de embeddings**: `sentence-transformers/all-MiniLM-L6-v2`
- **Métrica de similitud**: `cosine`
- **Umbral de similitud**: `0.3`
- **Top K**: `5`

## Ventajas del Sistema

1. **🤖 IA Natural**: Procesa mensajes naturales del usuario
2. **🎯 Flexibilidad total**: Busca cualquier tipo de lugar
3. **🔍 Búsqueda semántica**: Encuentra lugares similares por significado
4. **⚡ Filtros precisos**: Rating, tipo, categoría, horarios, etc.
5. **🕒 Búsqueda por horarios**: Encuentra lugares abiertos según criterios específicos
6. **📊 Escalabilidad**: Pinecone maneja millones de vectores
7. **🚀 Rendimiento**: Búsquedas rápidas en tiempo real

## Ejemplo de Uso Completo

### 1. Configurar Variables de Entorno

```bash
export PINECONE_API_KEY="tu_api_key"
export PINECONE_ENVIRONMENT="tu_environment"
export API_KEY_OPENAI="tu_api_key_deepseek"
```

### 2. Sincronizar Datos

```bash
curl -X POST http://localhost:8000/api/pinecone/places/sync/ \
  -H "Authorization: Bearer tu_token" \
  -H "Content-Type: application/json"
```

### 3. Realizar Búsqueda Natural

```bash
curl -X POST http://localhost:8000/api/pinecone/places/process-natural-search/ \
  -H "Authorization: Bearer tu_token" \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "para comer quiero ir a una cafetería de 4 estrellas"
  }'
```

### 4. Verificar Estadísticas

```bash
curl -X GET http://localhost:8000/api/pinecone/places/stats/ \
  -H "Authorization: Bearer tu_token"
```

## Consideraciones

- **Umbral de similitud**: Ajusta según la precisión deseada (0.3 por defecto)
- **Tolerancia de rating**: Permite flexibilidad en las búsquedas (0.5 por defecto)
- **Top K**: Limita el número de resultados para mejor rendimiento
- **Horarios**: Los criterios de horario son semánticos, no exactos
- **DeepSeek**: Requiere API key configurada para procesamiento natural
- **Sincronización**: Mantén los datos actualizados regularmente 