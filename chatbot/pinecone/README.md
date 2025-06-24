# Pinecone con Hugging Face - Implementación para Chatbot

Esta implementación integra Pinecone (base de datos vectorial) con Hugging Face (modelos de embeddings) para proporcionar memoria de largo plazo al chatbot.

## 🏗️ Estructura del Proyecto

```
chatbot/pinecone/
├── __init__.py              # Paquete Python
├── config.py                # Configuración y variables de entorno
├── embeddings.py            # Generación de embeddings con Hugging Face
├── vector_store.py          # Manejo de la base de datos vectorial Pinecone
├── memory_manager.py        # Gestor de memoria para el chatbot
├── views.py                 # Vistas de Django REST API
├── urls.py                  # Rutas de la API
├── example_usage.py         # Ejemplos de uso
└── README.md               # Esta documentación
```

## 🚀 Características Principales

- **Embeddings con Hugging Face**: Utiliza modelos de Sentence Transformers para generar vectores de texto
- **Base de Datos Vectorial Pinecone**: Almacenamiento escalable y búsqueda semántica
- **Gestión de Memoria**: Almacena conversaciones y preferencias de usuarios
- **API REST**: Endpoints para integrar con el frontend
- **Búsqueda Semántica**: Encuentra información relevante basada en similitud de significado

## 📋 Requisitos

### Dependencias
```bash
pip install pinecone-client==3.1.0
pip install transformers==4.40.0
pip install torch==2.3.0
pip install sentence-transformers==3.0.0
pip install numpy==1.26.0
```

### Variables de Entorno
Crear un archivo `.env` en la raíz del proyecto:

```env
# Pinecone Configuration
PINECONE_API_KEY=tu_api_key_de_pinecone
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=chatbot-memory
PINECONE_DIMENSION=768
PINECONE_METRIC=cosine

# Hugging Face Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Search Configuration
PINECONE_TOP_K=5
PINECONE_SIMILARITY_THRESHOLD=0.7
```

## 🔧 Configuración

### 1. Obtener API Key de Pinecone
1. Crear cuenta en [Pinecone Console](https://app.pinecone.io/)
2. Crear un proyecto
3. Copiar la API Key desde la sección "API Keys"

### 2. Configurar Variables de Entorno
```bash
# En tu archivo .env
PINECONE_API_KEY=tu_api_key_aqui
```

### 3. Verificar Configuración
```python
from chatbot.pinecone.config import PineconeConfig

# Validar configuración
PineconeConfig.validate_config()
```

## 📚 Uso Básico

### 1. Generar Embeddings
```python
from chatbot.pinecone.embeddings import HuggingFaceEmbeddings

# Inicializar modelo
embeddings = HuggingFaceEmbeddings()

# Generar embedding para un texto
texto = "Me gusta viajar a lugares con playas hermosas"
embedding = embeddings.get_embedding(texto)
print(f"Dimensión: {len(embedding)}")
```

### 2. Usar Base de Datos Vectorial
```python
from chatbot.pinecone.vector_store import PineconeVectorStore

# Inicializar vector store
vector_store = PineconeVectorStore()

# Agregar texto
vector_id = vector_store.add_text(
    "Me gusta la comida italiana",
    metadata={'categoria': 'gastronomia'}
)

# Buscar textos similares
resultados = vector_store.search("restaurantes italianos", top_k=3)
for resultado in resultados:
    print(f"Score: {resultado['score']}, Texto: {resultado['metadata']['text']}")
```

### 3. Gestión de Memoria
```python
from chatbot.pinecone.memory_manager import ChatbotMemoryManager

# Inicializar gestor de memoria
memory_manager = ChatbotMemoryManager()

# Almacenar conversación
vector_id = memory_manager.store_conversation(
    user_id="usuario_123",
    user_message="¿Qué lugares me recomiendas en París?",
    bot_response="Te recomiendo la Torre Eiffel y el Louvre."
)

# Obtener contexto para nueva consulta
contexto = memory_manager.get_user_context(
    user_id="usuario_123",
    query="¿Y restaurantes en París?"
)
```

## 🌐 API REST

### Endpoints Disponibles

#### Almacenar Conversación
```http
POST /api/pinecone/store-conversation/
Content-Type: application/json
Authorization: Bearer <token>

{
    "user_message": "Mensaje del usuario",
    "bot_response": "Respuesta del bot",
    "context": {"additional": "data"}
}
```

#### Almacenar Preferencia
```http
POST /api/pinecone/store-preference/
Content-Type: application/json
Authorization: Bearer <token>

{
    "preference_text": "Me gusta la comida italiana",
    "category": "gastronomia",
    "context": {"additional": "data"}
}
```

#### Buscar en Memoria
```http
GET /api/pinecone/search-memory/?query=restaurantes&top_k=5&conversation_type=chat
Authorization: Bearer <token>
```

#### Obtener Contexto
```http
GET /api/pinecone/get-context/?query=restaurantes&max_results=3
Authorization: Bearer <token>
```

#### Conversaciones Recientes
```http
GET /api/pinecone/recent-conversations/?hours=24&max_results=10
Authorization: Bearer <token>
```

#### Estadísticas de Memoria
```http
GET /api/pinecone/memory-stats/
Authorization: Bearer <token>
```

#### Eliminar Memoria
```http
DELETE /api/pinecone/delete-memory/
Authorization: Bearer <token>
```

## 🔄 Integración con Chatbot

### Flujo de Conversación con Memoria

```python
def procesar_mensaje_con_memoria(user_id, mensaje_usuario):
    """Procesar mensaje del usuario con memoria de conversaciones previas"""
    
    # 1. Obtener contexto previo
    contexto = memory_manager.get_user_context(user_id, mensaje_usuario)
    
    # 2. Generar respuesta considerando el contexto
    respuesta_bot = generar_respuesta_ia(mensaje_usuario, contexto)
    
    # 3. Almacenar la nueva conversación
    memory_manager.store_conversation(
        user_id=user_id,
        user_message=mensaje_usuario,
        bot_response=respuesta_bot
    )
    
    return respuesta_bot
```

### Almacenar Preferencias del Usuario

```python
def detectar_y_almacenar_preferencias(user_id, mensaje_usuario):
    """Detectar y almacenar preferencias del usuario"""
    
    # Detectar preferencias (ejemplo simplificado)
    if "me gusta" in mensaje_usuario.lower():
        if "italiana" in mensaje_usuario.lower():
            memory_manager.store_user_preference(
                user_id=user_id,
                preference_text="Prefiere comida italiana",
                category="gastronomia"
            )
        elif "playa" in mensaje_usuario.lower():
            memory_manager.store_user_preference(
                user_id=user_id,
                preference_text="Le gustan los destinos de playa",
                category="destinos"
            )
```

## 🧪 Ejemplos de Uso

Ejecutar el archivo de ejemplos:

```bash
cd chatbot/pinecone
python -c "from example_usage import main; main()"
```

## 📊 Monitoreo y Estadísticas

### Estadísticas del Usuario
```python
stats = memory_manager.get_memory_stats(user_id="usuario_123")
print(f"Conversaciones: {stats['total_conversations']}")
print(f"Preferencias: {stats['total_preferences']}")
```

### Estadísticas del Índice
```python
stats = vector_store.get_index_stats()
print(f"Total vectores: {stats['total_vector_count']}")
print(f"Dimensión: {stats['dimension']}")
```

## 🔒 Seguridad y Privacidad

- **Autenticación**: Todos los endpoints requieren autenticación JWT
- **Aislamiento de Usuarios**: Cada usuario solo puede acceder a su propia memoria
- **Eliminación de Datos**: Endpoint para eliminar toda la memoria de un usuario
- **Filtros de Búsqueda**: Búsquedas filtradas por usuario_id

## 🚨 Manejo de Errores

La implementación incluye manejo robusto de errores:

```python
try:
    resultado = memory_manager.store_conversation(user_id, mensaje, respuesta)
except ValueError as e:
    print(f"Error de validación: {e}")
except Exception as e:
    print(f"Error interno: {e}")
```

## 🔧 Configuración Avanzada

### Cambiar Modelo de Embeddings
```python
# En .env
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2

# O programáticamente
embeddings = HuggingFaceEmbeddings("sentence-transformers/all-mpnet-base-v2")
```

### Ajustar Umbral de Similitud
```python
# En .env
PINECONE_SIMILARITY_THRESHOLD=0.8

# Resultados más estrictos
resultados = vector_store.search(query, top_k=10)
# Solo resultados con score >= 0.8
```

## 📈 Optimización

### Rendimiento
- **Caché de Modelo**: El modelo de embeddings se carga una sola vez
- **Búsqueda Eficiente**: Pinecone optimiza las búsquedas vectoriales
- **Lotes**: Soporte para procesar múltiples textos en lote

### Escalabilidad
- **Pinecone Serverless**: Escalado automático según demanda
- **Índices Múltiples**: Soporte para múltiples índices por aplicación
- **Metadatos**: Filtrado eficiente por metadatos

## 🤝 Contribución

Para contribuir a esta implementación:

1. Fork el repositorio
2. Crear una rama para tu feature
3. Implementar cambios
4. Agregar tests
5. Crear Pull Request

## 📄 Licencia

Esta implementación está bajo la misma licencia que el proyecto principal.

## 🆘 Soporte

Para soporte técnico o preguntas:

1. Revisar la documentación
2. Ejecutar los ejemplos
3. Verificar la configuración
4. Revisar los logs de error

---

**Nota**: Esta implementación está diseñada para ser modular y fácilmente extensible. Puedes adaptar las funcionalidades según las necesidades específicas de tu chatbot. 

# Pinecone Places - Sistema de Búsqueda Vectorial Avanzado

Este módulo implementa un sistema de búsqueda vectorial usando Pinecone y Hugging Face para lugares de Google Places, permitiendo búsquedas semánticas avanzadas para cualquier tipo de lugar.

## Características

- **Búsqueda semántica**: Encuentra lugares similares basado en significado, no solo palabras clave
- **Múltiples tipos de lugar**: Hoteles, restaurantes, bares, parques, centros comerciales, etc.
- **Filtros por rating**: Búsqueda específica por calificación de estrellas
- **Búsqueda por horarios**: Encuentra lugares abiertos ahora, 24 horas, fines de semana, etc.
- **Búsqueda por amenidades**: Encuentra lugares con características específicas
- **Búsqueda inteligente**: Combina múltiples criterios en una sola consulta
- **🆕 Búsqueda natural**: Procesa mensajes naturales del usuario usando DeepSeek
- **Sincronización automática**: Sincroniza la base de datos con Pinecone

## Tipos de Lugares Soportados

El sistema puede buscar cualquier tipo de lugar que esté en la base de datos:

- **Hoteles**: `hotel`, `lodging`
- **Restaurantes**: `restaurant`, `food`
- **Bares**: `bar`, `night_club`
- **Parques**: `park`, `natural_feature`
- **Centros Comerciales**: `shopping_mall`, `store`
- **Museos**: `museum`, `art_gallery`
- **Discotecas**: `night_club`, `bar`
- **Lugares Turísticos**: `tourist_attraction`, `point_of_interest`

## Configuración

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

## Uso

### 🆕 1. Búsqueda Natural (Recomendado)

El sistema puede procesar mensajes naturales del usuario y extraer automáticamente los criterios de búsqueda:

```python
from chatbot.pinecone.places_vector_store import PlacesVectorStore

# Procesar mensaje natural del usuario
user_message = "para comer quiero ir a una cafetería de 4 estrellas"

# El sistema automáticamente extrae:
# - place_type: "cafetería"
# - category: "restaurantes"
# - rating_min: 4.0
# - intent: "comer"
# - features: []

# Y realiza la búsqueda apropiada
```

#### Ejemplos de Mensajes Naturales:

```python
# Ejemplo 1: Cafetería con rating específico
user_message = "para comer quiero ir a una cafetería de 4 estrellas"
# Extrae: place_type="cafetería", rating_min=4.0, intent="comer"

# Ejemplo 2: Restaurante italiano abierto ahora
user_message = "busco un restaurante italiano que esté abierto ahora"
# Extrae: place_type="restaurante", features=["italiano"], opening_hours="abierto_ahora"

# Ejemplo 3: Hotel con amenidades específicas
user_message = "necesito un hotel de 3 estrellas con gimnasio y piscina"
# Extrae: place_type="hotel", rating_min=3.0, features=["gimnasio", "piscina"], intent="dormir"

# Ejemplo 4: Bar con música en vivo
user_message = "quiero ir a un bar con música en vivo abierto 24 horas"
# Extrae: place_type="bar", features=["música en vivo"], opening_hours="24_horas"

# Ejemplo 5: Centro comercial para compras
user_message = "busco un centro comercial abierto fines de semana"
# Extrae: place_type="centro comercial", opening_hours="fines_semana", intent="compras"

# Ejemplo 6: Parque para niños
user_message = "necesito un parque con áreas para niños"
# Extrae: place_type="parque", features=["niños"], intent="entretenimiento"

# Ejemplo 7: Restaurante económico
user_message = "quiero un restaurante económico con comida italiana"
# Extrae: place_type="restaurante", features=["italiano"], price_level="económico", intent="comer"

# Ejemplo 8: Hotel lujoso
user_message = "busco un hotel lujoso con vista al mar"
# Extrae: place_type="hotel", features=["vista al mar"], price_level="lujoso", intent="dormir"

# Ejemplo 9: Lugar gratis
user_message = "quiero un restaurante gratis o muy barato"
# Extrae: place_type="restaurante", price_level="gratis", intent="comer"
```

### 2. Sincronización de Datos

```python
from chatbot.pinecone.places_vector_store import PlacesVectorStore

# Sincronizar todos los lugares
vector_store = PlacesVectorStore()
places_synced = vector_store.sync_places_from_database()
print(f"Se sincronizaron {places_synced} lugares")
```

### 3. Búsqueda por Tipo de Lugar y Características

```python
# Buscar restaurantes italianos con terraza
results = vector_store.find_places_by_type_and_features(
    place_type='restaurante',
    features=['italiano', 'terraza'],
    top_k=5
)

for result in results:
    print(f"Restaurante: {result['metadata']['nombre']}")
    print(f"Rating: {result['metadata']['rating']}")
    print(f"Características: {result['metadata']['resumen_ia']}")
    print("---")

# Buscar bares con música en vivo
results = vector_store.find_places_by_type_and_features(
    place_type='bar',
    features=['música en vivo', 'karaoke'],
    top_k=5
)

# Buscar parques con áreas de picnic
results = vector_store.find_places_by_type_and_features(
    place_type='parque',
    features=['picnic', 'área recreativa'],
    top_k=5
)
```

### 4. Búsqueda con Rating Específico

```python
# Buscar restaurantes de 4 estrellas con comida peruana
results = vector_store.find_places_with_rating_and_features(
    place_type='restaurante',
    rating=4.0,
    features=['peruano', 'ceviche'],
    rating_tolerance=0.5,  # Busca restaurantes de 3.5 a 4.5 estrellas
    top_k=5
)

for result in results:
    print(f"Restaurante: {result['metadata']['nombre']}")
    print(f"Rating: {result['metadata']['rating']}")
    print(f"Precios: {result['metadata']['nivel_precios']}")
    print("---")
```

### 5. Búsqueda por Horarios

```python
# Buscar restaurantes abiertos ahora
results = vector_store.find_places_by_opening_hours(
    place_type='restaurante',
    opening_criteria='abierto_ahora',
    features=['italiano'],
    top_k=5
)

# Buscar bares abiertos 24 horas
results = vector_store.find_places_by_opening_hours(
    place_type='bar',
    opening_criteria='24_horas',
    features=['música en vivo'],
    top_k=5
)

# Buscar centros comerciales abiertos fines de semana
results = vector_store.find_places_by_opening_hours(
    place_type='centro comercial',
    opening_criteria='fines_semana',
    top_k=5
)
```

### 6. Búsqueda por Categoría

```python
# Buscar lugares de entretenimiento con actividades para niños
results = vector_store.find_places_by_category_and_features(
    category='lugares_de_entretenimiento',
    features=['niños', 'familia'],
    rating_min=4.0,
    top_k=5
)

# Buscar museos con exposiciones temporales
results = vector_store.find_places_by_category_and_features(
    category='museos',
    features=['exposiciones', 'arte contemporáneo'],
    top_k=5
)
```

### 7. Búsqueda Inteligente (Múltiples Criterios)

```python
# Búsqueda compleja: restaurante italiano con terraza, 4+ estrellas, abierto ahora
search_criteria = {
    'place_type': 'restaurante',
    'category': 'restaurantes',
    'features': ['italiano', 'terraza'],
    'rating_min': 4.0,
    'rating_max': 5.0,
    'opening_hours': 'abierto_ahora',
    'location': 'Chiclayo centro',
    'price_level': 'moderado'
}

results = vector_store.smart_place_search(
    search_criteria=search_criteria,
    top_k=5
)

for result in results:
    print(f"Lugar: {result['metadata']['nombre']}")
    print(f"Tipo: {result['metadata']['tipo_principal']}")
    print(f"Rating: {result['metadata']['rating']}")
    print(f"Dirección: {result['metadata']['direccion']}")
    print(f"Score: {result['score']}")
    print("---")
```

### 8. Búsqueda por Nivel de Precios

```python
# Buscar restaurantes económicos
results = vector_store.find_places_by_price_level(
    price_level='económico',
    place_type='restaurante',
    features=['italiano'],
    top_k=5
)

# Buscar hoteles lujosos
results = vector_store.find_places_by_price_level(
    price_level='muy caro',
    place_type='hotel',
    features=['spa', 'vista al mar'],
    top_k=5
)

# Buscar lugares gratis
results = vector_store.find_places_by_price_level(
    price_level='gratis',
    top_k=5
)
```

## APIs REST

### 🆕 Búsqueda Natural (Recomendado)

```bash
# Procesar mensaje natural del usuario
POST /api/pinecone/places/process-natural-search/
{
    "user_message": "para comer quiero ir a una cafetería de 4 estrellas"
}

# Respuesta:
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
    "results": [...]
}
```

### Búsquedas por Tipo de Lugar

```bash
# Buscar por tipo y características
POST /api/pinecone/places/search-by-type-and-features/
{
    "place_type": "restaurante",
    "features": ["italiano", "terraza"],
    "top_k": 5
}

# Buscar con rating específico
POST /api/pinecone/places/search-with-rating-and-features/
{
    "place_type": "restaurante",
    "rating": 4.0,
    "features": ["peruano", "ceviche"],
    "rating_tolerance": 0.5,
    "top_k": 5
}
```

### Búsquedas por Horarios

```bash
# Buscar lugares abiertos ahora
POST /api/pinecone/places/search-by-opening-hours/
{
    "place_type": "restaurante",
    "opening_criteria": "abierto_ahora",
    "features": ["italiano"],
    "top_k": 5
}

# Buscar lugares abiertos 24 horas
POST /api/pinecone/places/search-by-opening-hours/
{
    "place_type": "bar",
    "opening_criteria": "24_horas",
    "features": ["música en vivo"],
    "top_k": 5
}

# Buscar lugares abiertos fines de semana
POST /api/pinecone/places/search-by-opening-hours/
{
    "place_type": "centro comercial",
    "opening_criteria": "fines_semana",
    "top_k": 5
}
```

### Búsquedas por Categoría

```bash
# Buscar por categoría y características
POST /api/pinecone/places/search-by-category-and-features/
{
    "category": "lugares_de_entretenimiento",
    "features": ["niños", "familia"],
    "rating_min": 4.0,
    "top_k": 5
}
```

### 🆕 Búsquedas por Precio

```bash
# Buscar lugares por nivel de precio
POST /api/pinecone/places/search-by-price-level/
{
    "price_level": "económico",
    "place_type": "restaurante",
    "features": ["italiano"],
    "top_k": 5
}

# Buscar hoteles lujosos
POST /api/pinecone/places/search-by-price-level/
{
    "price_level": "muy caro",
    "place_type": "hotel",
    "features": ["spa"],
    "top_k": 5
}

# Buscar lugares gratis
POST /api/pinecone/places/search-by-price-level/
{
    "price_level": "gratis",
    "top_k": 5
}
```

### Búsqueda Inteligente

```bash
# Búsqueda con múltiples criterios
POST /api/pinecone/places/smart-search/
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

### Hoteles Específicos

```bash
# Buscar hoteles con amenidades
POST /api/pinecone/places/search-hotels/
{
    "amenities": ["gimnasio", "piscina", "spa"],
    "top_k": 5
}

# Buscar hoteles con rating específico
POST /api/pinecone/places/search-hotels-rating/
{
    "rating": 3.0,
    "amenities": ["restaurante", "estacionamiento"],
    "rating_tolerance": 0.5,
    "top_k": 5
}
```

## Criterios de Horarios Disponibles

- **`abierto_ahora`**: Lugares que están abiertos en este momento
- **`24_horas`**: Lugares que están abiertos las 24 horas
- **`fines_semana`**: Lugares que están abiertos los fines de semana
- **`lunes_viernes`**: Lugares que están abiertos de lunes a viernes

## 🆕 Niveles de Precio Disponibles

### Niveles Principales:
- **`gratis`**: Lugares sin costo (Nivel 0) - 0.00 PEN
- **`económico`**: Lugares con precios bajos (Nivel 1) - 0.00 a 50.00 PEN
- **`moderado`**: Lugares con precios estándar (Nivel 2) - 50.00 a 150.00 PEN
- **`caro`**: Lugares con precios elevados (Nivel 3) - 150.00 a 400.00 PEN
- **`muy caro`**: Lugares con precios muy altos (Nivel 4) - 400.00 a 1000.00 PEN

### Sinónimos de Precio:

- **Económico (Nivel 1)**: `barato`, `accesible`, `bajo`
- **Moderado (Nivel 2)**: `medio`, `normal`, `estándar`
- **Caros (Nivel 3)**: `costoso`, `elevado`, `alto`
- **Muy Caros (Nivel 4)**: `lujoso`, `exclusivo`, `premium`, `alta cocina`, `estrellas michelin`

### Búsquedas por Rango de Precios:

También puedes buscar usando rangos específicos:
- **`50-150`**: Busca lugares con precios entre 50 y 150 PEN
- **`hasta 100`**: Busca lugares con precios hasta 100 PEN
- **`desde 200`**: Busca lugares con precios desde 200 PEN

### Ejemplos de Uso:

```python
# Buscar restaurantes económicos
results = vector_store.find_places_by_price_level(
    price_level='económico',
    place_type='restaurante',
    top_k=5
)

# Buscar hoteles de lujo
results = vector_store.find_places_by_price_level(
    price_level='muy caro',
    place_type='hotel',
    features=['spa', 'vista al mar'],
    top_k=5
)

# Buscar lugares con precios entre 100-300 PEN
results = vector_store.find_places_by_price_level(
    price_level='100-300',
    place_type='restaurante',
    top_k=5
)

# Buscar lugares hasta 50 PEN
results = vector_store.find_places_by_price_level(
    price_level='hasta 50',
    top_k=5
)
```

### Ejemplos de Mensajes Naturales con Precios:

```python
# "Quiero un restaurante económico con comida italiana"
# Extrae: place_type="restaurante", price_level="económico", features=["italiano"]

# "Busco un hotel de lujo con spa"
# Extrae: place_type="hotel", price_level="muy caro", features=["spa"]

# "Necesito un lugar para comer que no sea muy caro"
# Extrae: price_level="moderado", intent="comer"

# "Quiero ir a un restaurante de alta cocina"
# Extrae: place_type="restaurante", price_level="muy caro"

# "Busco un café barato cerca del centro"
# Extrae: place_type="café", price_level="económico", location="centro"
```

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

## Estructura de Datos

### Metadatos de Lugar

```python
{
    'id': 123,
    'nombre': 'Restaurante Example',
    'tipo_principal': 'restaurant',
    'tipos_adicionales': ['food', 'establishment'],
    'categoria': 'restaurantes',
    'direccion': 'Av. Principal 123',
    'latitud': -6.7766,
    'longitud': -79.8443,
    'rating': 4.2,
    'total_ratings': 150,
    'nivel_precios': 'Moderado',
    'website': 'https://example.com',
    'telefono': '+51 123 456 789',
    'estado_negocio': 'OPERATIONAL',
    'resumen_ia': 'Restaurante italiano con terraza y vista al mar',
    'descripcion': 'Descripción detallada del restaurante...',
    'horarios': [
        {
            'open': [{'day': 0, 'time': '0800'}, {'day': 1, 'time': '0800'}],
            'weekday_text': ['Lunes: 8:00 AM – 10:00 PM', 'Martes: 8:00 AM – 10:00 PM']
        }
    ],
    'vector_type': 'place',
    'created_at': '2024-01-01T00:00:00',
    'model': 'sentence-transformers/all-MiniLM-L6-v2'
}
```

## Manejo de Horarios

El sistema procesa los horarios de la siguiente manera:

1. **En el embedding**: Se incluye información resumida como "Abierto 7 días a la semana" o "Horarios: Lunes: 8:00 AM – 10:00 PM"
2. **En los metadatos**: Se almacena el JSON completo de horarios para análisis detallado
3. **En las búsquedas**: Se pueden usar criterios específicos de horario

## 🆕 Procesamiento de Lenguaje Natural

El sistema usa DeepSeek para entender mensajes naturales del usuario:

### Criterios que Extrae Automáticamente:

- **Tipo de lugar**: `restaurante`, `hotel`, `bar`, `parque`, etc.
- **Categoría**: `restaurantes`, `hoteles`, `lugares_de_entretenimiento`, etc.
- **Características**: `italiano`, `terraza`, `música en vivo`, etc.
- **Rating**: Número de estrellas mencionado
- **Horarios**: `abierto_ahora`, `24_horas`, `fines_semana`, etc.
- **Ubicación**: Lugar específico mencionado
- **Nivel de precios**: `económico`, `moderado`, `caro`
- **Intención**: `comer`, `dormir`, `entretenimiento`, `compras`

### Reglas de Extracción:

1. **Cafeterías**: `"cafetería"`, `"café"`, `"coffee"` → `place_type: "cafetería"`
2. **Comida**: `"comer"`, `"almorzar"`, `"cenar"` → `intent: "comer"`
3. **Alojamiento**: `"dormir"`, `"alojarse"`, `"hospedarse"` → `intent: "dormir"`
4. **Rating**: `"4 estrellas"`, `"rating 5"` → `rating_min: 4.0`
5. **Horarios**: `"abierto ahora"` → `opening_hours: "abierto_ahora"`
6. **Precios**: `"barato"`, `"económico"` → `price_level: "económico"`

## Ventajas del Sistema

1. **🤖 IA Natural**: Procesa mensajes naturales del usuario
2. **🎯 Flexibilidad total**: Busca cualquier tipo de lugar
3. **🔍 Búsqueda semántica**: Encuentra lugares similares por significado
4. **⚡ Filtros precisos**: Rating, tipo, categoría, horarios, etc.
5. **🕒 Búsqueda por horarios**: Encuentra lugares abiertos según criterios específicos
6. **📊 Escalabilidad**: Pinecone maneja millones de vectores
7. **🚀 Rendimiento**: Búsquedas rápidas en tiempo real

## Consideraciones

- **Umbral de similitud**: Ajusta según la precisión deseada (0.3 por defecto)
- **Tolerancia de rating**: Permite flexibilidad en las búsquedas (0.5 por defecto)
- **Top K**: Limita el número de resultados para mejor rendimiento
- **Horarios**: Los criterios de horario son semánticos, no exactos
- **DeepSeek**: Requiere API key configurada para procesamiento natural
- **Sincronización**: Mantén los datos actualizados regularmente 