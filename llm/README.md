# Sistema de Embeddings y Base de Datos Vectorial

Este sistema implementa búsqueda semántica usando embeddings locales (BAAI/bge-base-en-v1.5) y Pinecone como base de datos vectorial.

## 🏗️ Arquitectura

```
llm/
├── __init__.py              # Paquete Python
├── requirements.txt         # Dependencias
├── pinecone_client.py      # Cliente Pinecone
├── embedder.py             # Modelo de embeddings local
├── vector_db.py            # Sistema integrado
├── ingest.py               # Script de ingesta de datos
├── query.py                # Script de consultas
├── generate_keywords.py    # Script para generar palabras clave
└── README.md               # Esta documentación
```

## 🚀 Configuración

### 1. Variables de Entorno

Asegúrate de tener en tu archivo `.env`:
```bash
PINECONE_API_KEY=tu_api_key_de_pinecone
```

### 2. Instalar Dependencias

```bash
pip install -r llm/requirements.txt
```

## 📊 Especificaciones Técnicas

- **Modelo de Embeddings**: BAAI/bge-base-en-v1.5
- **Dimensiones**: 768
- **Idiomas**: Bilingüe (Español/Inglés)
- **Base de Datos Vectorial**: Pinecone
- **Métrica de Similitud**: Coseno
- **Optimización**: Float16 para GPU, CPU nativo
- **Campo para Embeddings**: `palabras_clave_ia` (preferido) o `resumen_ia`

## 🔧 Uso

### 1. Generar Palabras Clave (Opcional pero Recomendado)

```bash
# Generar palabras clave de resúmenes IA existentes
python -m llm.generate_keywords
```

Este script:
- Extrae palabras clave de resúmenes IA usando DeepSeek
- Optimiza el texto para embeddings (50-100 palabras vs 300+ del resumen)
- Mejora la eficiencia y precisión de búsquedas

### 2. Poblar la Base Vectorial

```bash
# Desde la raíz del proyecto
python -m llm.ingest
```

Este script:
- Obtiene todos los lugares con resúmenes IA de la base de datos
- Usa `palabras_clave_ia` si está disponible, sino `resumen_ia`
- Genera embeddings para cada texto
- Los inserta en Pinecone en lotes de 100

### 3. Hacer Consultas Semánticas

```bash
# Modo interactivo
python -m llm.query
```

Comandos disponibles:
- `buscar <consulta>` - Buscar lugares similares
- `tipo <tipo> <consulta>` - Buscar por tipo específico
- `stats` - Ver estadísticas del índice
- `quit` - Salir

### 4. Uso Programático

```python
from llm.vector_db import get_vector_db

# Obtener sistema de base de datos vectorial
vector_db = get_vector_db()

# Buscar lugares similares
results = vector_db.search_similar("hotel con piscina", top_k=5)

# Buscar por tipo específico
hotels = vector_db.search_by_tipo("hotel con spa", "hotel", top_k=3)
```

## 📈 Rendimiento

### Optimizaciones Implementadas

1. **Palabras Clave Optimizadas**: 50-100 palabras vs 300+ del resumen
2. **Batch Processing**: Procesamiento en lotes de 100 vectores
3. **GPU Optimization**: Float16 para GPU automático
4. **Memory Management**: Normalización de embeddings
5. **Error Handling**: Manejo robusto de errores

### Métricas Esperadas

- **Velocidad de Embedding**: ~100-200 textos/segundo (CPU)
- **Precisión**: Alta similitud semántica con palabras clave
- **Escalabilidad**: Hasta millones de vectores
- **Eficiencia**: 3x más rápido con palabras clave vs resúmenes completos

## 🔍 Ejemplos de Uso

### Consultas Típicas

```python
# Hoteles con amenidades específicas
"hotel con gimnasio y spa"
"hotel para familias con niños"

# Restaurantes por tipo de comida
"restaurante romántico italiano"
"comida rápida vegetariana"

# Actividades de entretenimiento
"parque de diversiones familiar"
"museo de arte moderno"

# Búsquedas por ubicación
"restaurante cerca del centro"
"hotel con vista al mar"
```

### Filtros por Tipo

```python
# Solo hoteles
vector_db.search_by_tipo("con piscina", "hotel")

# Solo restaurantes
vector_db.search_by_tipo("romántico", "restaurant")

# Solo bares
vector_db.search_by_tipo("música en vivo", "bar")
```

## 🛠️ Mantenimiento

### Verificar Estado del Sistema

```python
from llm.vector_db import get_vector_db

vector_db = get_vector_db()
stats = vector_db.get_index_stats()
print(f"Total de vectores: {stats.get('total_vector_count')}")
```

### Recrear Índice

```python
# Eliminar índice existente
vector_db.delete_index()

# Crear nuevo índice
vector_db.create_index()

# Repoblar datos
python -m llm.ingest
```

### Actualizar Palabras Clave

```bash
# Generar palabras clave para nuevos lugares
python -m llm.generate_keywords
```

## 🐛 Troubleshooting

### Problemas Comunes

1. **Error de API Key**: Verificar `PINECONE_API_KEY` en `.env`
2. **Modelo no carga**: Verificar conexión a internet para descargar modelo
3. **Memoria insuficiente**: Reducir batch_size en ingest.py
4. **Dimensiones incorrectas**: Verificar que el modelo sea BAAI/bge-base-en-v1.5
5. **Palabras clave vacías**: Ejecutar `python -m llm.generate_keywords`

### Logs

El sistema genera logs detallados:
- Nivel INFO: Operaciones principales
- Nivel WARNING: Problemas no críticos
- Nivel ERROR: Errores que requieren atención

## 🔄 Integración con ChatBot

Para integrar con el sistema de chatbot existente:

```python
from llm.vector_db import get_vector_db

def buscar_lugares_semantico(query: str, tipo: str = None):
    vector_db = get_vector_db()
    
    if tipo:
        results = vector_db.search_by_tipo(query, tipo, top_k=5)
    else:
        results = vector_db.search_similar(query, top_k=5)
    
    return results
```

## 📚 Referencias

- [BAAI/bge-base-en-v1.5](https://huggingface.co/BAAI/bge-base-en-v1.5)
- [Pinecone Documentation](https://docs.pinecone.io/)
- [Sentence Transformers](https://www.sbert.net/) 