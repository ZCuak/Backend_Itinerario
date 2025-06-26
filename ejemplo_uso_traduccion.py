#!/usr/bin/env python
"""
Ejemplo de uso de las funciones de traducción de tipos de lugares.
Este archivo muestra cómo integrar las funciones de traducción en tu aplicación.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itinerario_backend.settings')
django.setup()

from chatbot.models import LugarGooglePlaces
from chatbot.utils import (
    traducir_tipo_lugar, 
    traducir_lista_tipos,
    obtener_tipo_principal_traducido,
    obtener_tipos_adicionales_traducidos,
    formatear_tipos_lugar
)

def ejemplo_traduccion_basica():
    """
    Ejemplo básico de traducción de tipos.
    """
    print("=== Ejemplo de Traducción Básica ===")
    
    # Traducir un tipo individual
    tipo_ingles = "hotel"
    tipo_espanol = traducir_tipo_lugar(tipo_ingles)
    print(f"'{tipo_ingles}' → '{tipo_espanol}'")
    
    # Traducir una lista de tipos
    tipos_ingles = ["restaurant", "bar", "cafe"]
    tipos_espanol = traducir_lista_tipos(tipos_ingles)
    print(f"{tipos_ingles} → {tipos_espanol}")
    
    print()

def ejemplo_con_lugar_real():
    """
    Ejemplo usando un lugar real de la base de datos.
    """
    print("=== Ejemplo con Lugar Real ===")
    
    # Obtener un lugar de ejemplo (Casa Andina Select Chiclayo)
    lugar = LugarGooglePlaces.objects.filter(nombre__icontains="Casa Andina").first()
    
    if lugar:
        print(f"Lugar: {lugar.nombre}")
        print(f"Tipo principal (código): {lugar.tipo_principal}")
        print(f"Tipo principal (traducido): {obtener_tipo_principal_traducido(lugar)}")
        print(f"Tipos adicionales (códigos): {lugar.tipos_adicionales}")
        print(f"Tipos adicionales (traducidos): {obtener_tipos_adicionales_traducidos(lugar)}")
        
        # Usar la función de formateo completo
        tipos_formateados = formatear_tipos_lugar(lugar)
        print(f"Todos los tipos: {tipos_formateados['todos_los_tipos']}")
    else:
        print("No se encontró el lugar de ejemplo")
    
    print()

def ejemplo_serializer():
    """
    Ejemplo de cómo usar en un serializer de Django REST Framework.
    """
    print("=== Ejemplo para Serializer ===")
    
    class LugarSerializer:
        """
        Ejemplo de serializer que incluye tipos traducidos.
        """
        def __init__(self, lugar):
            self.lugar = lugar
        
        def to_dict(self):
            """
            Convierte el lugar a un diccionario con tipos traducidos.
            """
            return {
                'id': self.lugar.id,
                'nombre': self.lugar.nombre,
                'direccion': self.lugar.direccion,
                'tipo_principal': obtener_tipo_principal_traducido(self.lugar),
                'tipos_adicionales': obtener_tipos_adicionales_traducidos(self.lugar),
                'rating': self.lugar.rating,
                'total_ratings': self.lugar.total_ratings,
                'nivel_precios': self.lugar.nivel_precios.nivel if self.lugar.nivel_precios else None,
                'website': self.lugar.website,
                'telefono': self.lugar.telefono,
            }
    
    # Ejemplo de uso
    lugar = LugarGooglePlaces.objects.first()
    if lugar:
        serializer = LugarSerializer(lugar)
        datos = serializer.to_dict()
        print("Datos del lugar con tipos traducidos:")
        for key, value in datos.items():
            print(f"  {key}: {value}")
    
    print()

def ejemplo_vista_api():
    """
    Ejemplo de cómo usar en una vista de API.
    """
    print("=== Ejemplo para Vista de API ===")
    
    def buscar_lugares_por_tipo(tipo_buscar):
        """
        Busca lugares por tipo y retorna con nombres traducidos.
        """
        # Buscar lugares que tengan el tipo especificado
        lugares = LugarGooglePlaces.objects.filter(
            tipo_principal=tipo_buscar
        ) | LugarGooglePlaces.objects.filter(
            tipos_adicionales__contains=[tipo_buscar]
        )
        
        resultados = []
        for lugar in lugares[:5]:  # Solo los primeros 5 para el ejemplo
            tipos_formateados = formatear_tipos_lugar(lugar)
            resultados.append({
                'id': lugar.id,
                'nombre': lugar.nombre,
                'tipo_principal': tipos_formateados['tipo_principal'],
                'todos_los_tipos': tipos_formateados['todos_los_tipos'],
                'rating': lugar.rating,
                'direccion': lugar.direccion
            })
        
        return resultados
    
    # Ejemplo de búsqueda
    tipo_buscar = "hotel"
    resultados = buscar_lugares_por_tipo(tipo_buscar)
    
    print(f"Búsqueda de lugares tipo '{traducir_tipo_lugar(tipo_buscar)}':")
    for resultado in resultados:
        print(f"  - {resultado['nombre']} ({', '.join(resultado['todos_los_tipos'])})")
    
    print()

def main():
    """
    Función principal que ejecuta todos los ejemplos.
    """
    print("=== Ejemplos de Uso de Traducción de Tipos ===")
    print()
    
    ejemplo_traduccion_basica()
    ejemplo_con_lugar_real()
    ejemplo_serializer()
    ejemplo_vista_api()
    
    print("=== Fin de Ejemplos ===")
    print("\nPara usar estas funciones en tu código:")
    print("1. Importa las funciones desde chatbot.utils")
    print("2. Usa traducir_tipo_lugar() para tipos individuales")
    print("3. Usa formatear_tipos_lugar() para lugares completos")
    print("4. Los códigos internos se mantienen en inglés")
    print("5. Solo la visualización se traduce a español")

if __name__ == "__main__":
    main() 