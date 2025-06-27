# 🌍 API de Ciudades - Documentación

## 📋 **Descripción**

Este endpoint permite obtener la lista de ciudades de un país específico. Soporta búsqueda tanto por ID del país como por nombre del país.

---

## 🚀 **Endpoint**

### **URL:** `GET /api/ciudades/`

---

## 📝 **Parámetros**

### **Opciones de búsqueda (una de las dos es requerida):**

#### **Opción 1: Por ID del país**
```typescript
interface CiudadesPorIdRequest {
  pais_id: number;  // ID del país en la base de datos
}
```

#### **Opción 2: Por nombre del país**
```typescript
interface CiudadesPorNombreRequest {
  pais: string;     // Nombre del país (búsqueda parcial)
}
```

---

## 📊 **Ejemplos de Uso**

### **1. Búsqueda por nombre de país**
```bash
GET /api/ciudades/?pais=Peru
```

**Response:**
```json
{
  "status": "success",
  "message": "Ciudades encontradas para Peru.",
  "data": [
    {
      "id": 1,
      "name": "Lima"
    },
    {
      "id": 2,
      "name": "Arequipa"
    },
    {
      "id": 3,
      "name": "Cusco"
    }
  ]
}
```

### **2. Búsqueda por ID de país**
```bash
GET /api/ciudades/?pais_id=1
```

**Response:**
```json
{
  "status": "success",
  "message": "Ciudades encontradas para ID 1.",
  "data": [
    {
      "id": 1,
      "name": "Lima"
    },
    {
      "id": 2,
      "name": "Arequipa"
    }
  ]
}
```

### **3. Sin parámetros (error)**
```bash
GET /api/ciudades/
```

**Response:**
```json
{
  "status": "error",
  "message": "Se requiere el parámetro 'pais_id' o 'pais'.",
  "data": null
}
```

### **4. País inexistente**
```bash
GET /api/ciudades/?pais=PaisInexistente
```

**Response:**
```json
{
  "status": "error",
  "message": "No se encontró ningún país que coincida con 'PaisInexistente'.",
  "data": null
}
```

---

## 🔧 **Implementación en Frontend**

### **JavaScript/TypeScript:**
```javascript
class CiudadesAPI {
  constructor(baseURL = 'http://localhost:8000/api') {
    this.baseURL = baseURL;
  }
  
  // Buscar por nombre de país
  async getCiudadesPorPais(nombrePais) {
    try {
      const response = await fetch(`${this.baseURL}/ciudades/?pais=${encodeURIComponent(nombrePais)}`);
      const data = await response.json();
      
      if (response.ok) {
        return data.data;
      } else {
        throw new Error(data.message);
      }
    } catch (error) {
      console.error('Error al obtener ciudades:', error);
      throw error;
    }
  }
  
  // Buscar por ID de país
  async getCiudadesPorId(paisId) {
    try {
      const response = await fetch(`${this.baseURL}/ciudades/?pais_id=${paisId}`);
      const data = await response.json();
      
      if (response.ok) {
        return data.data;
      } else {
        throw new Error(data.message);
      }
    } catch (error) {
      console.error('Error al obtener ciudades:', error);
      throw error;
    }
  }
}

// Ejemplo de uso
const ciudadesAPI = new CiudadesAPI();

// Buscar ciudades de Perú
ciudadesAPI.getCiudadesPorPais('Peru')
  .then(ciudades => {
    console.log('Ciudades de Perú:', ciudades);
  })
  .catch(error => {
    console.error('Error:', error.message);
  });
```

### **React Hook:**
```javascript
import { useState, useEffect } from 'react';

function useCiudades(pais) {
  const [ciudades, setCiudades] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!pais) return;

    const fetchCiudades = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await fetch(`/api/ciudades/?pais=${encodeURIComponent(pais)}`);
        const data = await response.json();
        
        if (response.ok) {
          setCiudades(data.data);
        } else {
          setError(data.message);
        }
      } catch (err) {
        setError('Error al cargar las ciudades');
      } finally {
        setLoading(false);
      }
    };

    fetchCiudades();
  }, [pais]);

  return { ciudades, loading, error };
}

// Uso en componente
function SelectorCiudades({ paisSeleccionado }) {
  const { ciudades, loading, error } = useCiudades(paisSeleccionado);

  if (loading) return <div>Cargando ciudades...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <select>
      <option value="">Selecciona una ciudad</option>
      {ciudades.map(ciudad => (
        <option key={ciudad.id} value={ciudad.id}>
          {ciudad.name}
        </option>
      ))}
    </select>
  );
}
```

---

## 🚨 **Códigos de Error**

| Código | Descripción |
|--------|-------------|
| `400` | Parámetros faltantes o inválidos |
| `404` | País no encontrado |
| `500` | Error interno del servidor |

---

## 📈 **Optimizaciones**

### **Búsqueda por Nombre:**
- Usa `icontains` para búsqueda parcial (no sensible a mayúsculas)
- Ejemplo: "peru", "Peru", "PERU" todos funcionan

### **Ordenamiento:**
- Las ciudades se devuelven ordenadas alfabéticamente por nombre

### **Rendimiento:**
- Consulta optimizada con filtros de base de datos
- Respuesta JSON ligera con solo ID y nombre

---

## 🔗 **Endpoints Relacionados**

- **`/api/paises/`** - Lista de países disponibles
- **`/api/obtener-ids/`** - Obtener IDs de ciudad y país por nombres
- **`/api/estado-por-ciudad/`** - Obtener estado de una ciudad

---

**📅 Última actualización**: Enero 2024  
**🔄 Versión**: 2.0 (Soporte para búsqueda por nombre)  
**📧 Soporte**: Endpoint de ciudades con búsqueda flexible 