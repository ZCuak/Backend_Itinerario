# API Documentation - Sistema de Chatbot Inteligente

## 📋 **Resumen del Sistema**

Este sistema integra **DeepSeek** para extracción de filtros, **embeddings locales** para búsqueda semántica, y **Pinecone** para almacenamiento vectorial. Está optimizado para usar **palabras clave** en lugar de resúmenes completos para ahorrar tokens.

### 🔧 **Optimizaciones Implementadas**

- ✅ **Uso de palabras clave**: Prioriza `palabras_clave_ia` sobre resúmenes completos
- ✅ **Eliminación de duplicados**: Múltiples puntos de verificación para evitar candidatos duplicados
- ✅ **Consulta semántica mejorada**: Combina características extraídas con la consulta original
- ✅ **Filtrado inteligente por tipos**: Considera tanto `tipo_principal` como `tipos_adicionales`
- ✅ **Ahorro de tokens**: Reduce significativamente el uso de tokens en LLM

## 🚀 **Endpoints Disponibles**

### 1. **Búsqueda Completa** - `/api/chatbot/buscar/`

**POST** - Procesa un mensaje completo del usuario y devuelve los mejores candidatos.

#### **Request Body:**
```json
{
    "mensaje": "Quiero un hotel con piscina"
}
```

#### **Response:**
```json
{
    "success": true,
    "filtros": {
        "tipo_establecimiento": "hotel",
        "consulta_semantica": "hotel con instalaciones recreativas y servicios premium",
        "caracteristicas": ["alojamiento premium", "instalaciones recreativas", "servicios de lujo"],
        "nivel_precio": null,
        "ubicacion": null,
        "intencion": "dormir"
    },
    "candidatos_encontrados": 15,
    "mejores_candidatos": [
        {
            "id": 123,
            "nombre": "Hotel Luxury Resort",
            "tipo_principal": "hotel",
            "tipos_adicionales": ["lodging", "spa", "restaurant"],
            "rating": 4.8,
            "score_similitud": 0.92,
            "palabras_clave_ia": "lujo, piscina, spa, gimnasio, restaurante gourmet",
            "resumen_ia": "Hotel de lujo con piscina infinita...",
            "metadata": {
                "direccion": "Av. Principal 123",
                "latitud": -12.3456,
                "longitud": -78.9012
            }
        }
    ]
}
```

### 2. **Extracción de Filtros** - `/api/chatbot/extraer-filtros/`

**POST** - Solo extrae filtros del mensaje del usuario.

#### **Request Body:**
```json
{
    "mensaje": "Busco un restaurante romántico para cenar"
}
```

#### **Response:**
```json
{
    "success": true,
    "filtros": {
        "tipo_establecimiento": "restaurant",
        "consulta_semantica": "restaurante romántico para cena especial",
        "caracteristicas": ["ambiente romántico", "cena especial", "experiencia gastronómica"],
        "nivel_precio": null,
        "ubicacion": null,
        "intencion": "comer"
    }
}
```

### 3. **Búsqueda por Tipo** - `/api/chatbot/buscar-tipo/`

**POST** - Busca lugares de un tipo específico (considera tanto tipo_principal como tipos_adicionales).

#### **Request Body:**
```json
{
    "consulta": "con piscina y spa",
    "tipo_establecimiento": "hotel"
}
```

#### **Response:**
```json
{
    "success": true,
    "candidatos": [
        {
            "id": 456,
            "nombre": "Hotel Wellness Center",
            "tipo_principal": "lodging",
            "tipos_adicionales": ["hotel", "spa", "wellness"],
            "rating": 4.6,
            "score_similitud": 0.88,
            "palabras_clave_ia": "wellness, spa, piscina, masajes, relajación",
            "resumen_ia": "Centro de bienestar con spa completo...",
            "metadata": {
                "direccion": "Calle Wellness 789",
                "latitud": -12.3457,
                "longitud": -78.9013
            }
        }
    ]
}
```

### 4. **Health Check** - `/api/chatbot/health/`

**GET** - Verifica el estado del sistema.

#### **Response:**
```json
{
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "services": {
        "deepseek": "active",
        "pinecone": "active",
        "embeddings": "active"
    }
}
```

## 🔍 **Proceso de Búsqueda Optimizado**

### **1. Extracción de Filtros (DeepSeek)**
- Analiza el mensaje del usuario
- Extrae características **semánticas** (no solo palabras exactas)
- Ejemplo: "hotel con piscina" → `["alojamiento premium", "instalaciones recreativas", "servicios de lujo"]`

### **2. Búsqueda Vectorial (Embeddings + Pinecone)**
- Usa **palabras clave** preferentemente para embeddings
- Combina consulta original con características extraídas
- Filtra por tipo de establecimiento
- **Elimina duplicados** automáticamente

### **3. Selección Final (LLM)**
- Analiza candidatos usando **palabras clave** (no resúmenes completos)
- Prioriza relevancia semántica y características
- Evita duplicados en la selección final

## 📊 **Estructura de Datos**

### **Lugar en Base de Datos:**
```python
{
    'id': 123,
    'nombre': 'Hotel Luxury Resort',
    'tipo_principal': 'hotel',
    'tipos_adicionales': ['lodging', 'spa', 'restaurant'],
    'rating': 4.8,
    'nivel_precios': '$$$',
    'direccion': 'Av. Principal 123',
    'latitud': -12.3456,
    'longitud': -78.9012,
    'resumen_ia': 'Hotel de lujo con piscina infinita...',
    'palabras_clave_ia': 'lujo, piscina, spa, gimnasio, restaurante gourmet'  # ← Priorizado
}
```

### **Vector en Pinecone:**
```python
{
    'id': 'lugar_123',
    'values': [0.1, 0.2, 0.3, ...],  # Embedding de palabras_clave_ia
    'metadata': {
        'lugar_id': 123,
        'nombre': 'Hotel Luxury Resort',
        'tipo_principal': 'hotel',
        'tipos_adicionales': ['lodging', 'spa', 'restaurant'],
        'rating': 4.8,
        'palabras_clave_ia': 'lujo, piscina, spa, gimnasio, restaurante gourmet',
        'resumen_ia': 'Hotel de lujo con piscina infinita...'  # Truncado
    }
}
```

## 🛠 **Configuración y Uso**

### **Variables de Entorno Requeridas:**
```bash
# DeepSeek
DEEPSEEK_API_KEY=tu_api_key_deepseek

# Pinecone
PINECONE_API_KEY=tu_api_key_pinecone
PINECONE_ENVIRONMENT=tu_environment
PINECONE_INDEX_NAME=lugares-turisticos

# Django
DJANGO_SECRET_KEY=tu_secret_key
```

### **Instalación:**
```bash
pip install -r requirements.txt
python manage.py migrate
```

### **Ejemplo de Uso en Python:**
```python
import requests

# Búsqueda completa
response = requests.post('http://localhost:8000/api/chatbot/buscar/', {
    'mensaje': 'Quiero un hotel con piscina'
})

resultado = response.json()
print(f"Mejores candidatos: {len(resultado['mejores_candidatos'])}")
```

## 📈 **Métricas de Rendimiento**

### **Optimizaciones de Tokens:**
- **Antes**: ~500-1000 tokens por consulta (resúmenes completos)
- **Después**: ~100-200 tokens por consulta (palabras clave)
- **Ahorro**: 70-80% de tokens

### **Eliminación de Duplicados:**
- Verificación en búsqueda inicial
- Verificación en selección final
- Verificación en respuesta final

### **Tiempos de Respuesta:**
- Extracción de filtros: ~2-3 segundos
- Búsqueda vectorial: ~1-2 segundos
- Selección final: ~1-2 segundos
- **Total**: ~4-7 segundos

## 🔧 **Mantenimiento**

### **Regenerar Palabras Clave:**
```bash
python manage.py shell
from llm.generate_keywords import generar_palabras_clave_todos
generar_palabras_clave_todos()
```

### **Regenerar Base Vectorial (con tipos_adicionales):**
```bash
# Regenerar completamente con tipos_adicionales
python -m llm.regenerar_vector_db
```

### **Reindexar Pinecone (método anterior):**
```bash
python manage.py shell
from llm.ingest import reindexar_pinecone
reindexar_pinecone()
```

### **Verificar Estado:**
```bash
curl http://localhost:8000/api/chatbot/health/
```

## 🚨 **Solución de Problemas**

### **Error: "No se pudo extraer filtros"**
- Verificar conexión a DeepSeek
- Revisar formato del mensaje
- Verificar API key

### **Error: "No se encontraron candidatos"**
- Verificar datos en Pinecone
- Revisar embeddings generados
- Verificar filtros aplicados

### **Candidatos duplicados**
- Verificar función `_eliminar_duplicados`
- Revisar IDs únicos en base de datos
- Verificar proceso de ingestión

---

**Última actualización**: Enero 2024  
**Versión**: 2.0 (Optimizada con palabras clave) 