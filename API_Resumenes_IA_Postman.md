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