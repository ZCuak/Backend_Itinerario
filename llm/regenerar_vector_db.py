#!/usr/bin/env python3
"""
Script para regenerar la base de datos vectorial con tipos_adicionales
"""

import os
import sys
import django
import logging
from typing import List, Dict, Any

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itinerario_backend.settings')
django.setup()

from chatbot.models import LugarGooglePlaces
from .vector_db import get_vector_db

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def obtener_todos_lugares_activos() -> List[Dict[str, Any]]:
    """
    Obtiene todos los lugares activos con sus tipos_adicionales
    
    Returns:
        Lista de diccionarios con datos completos de lugares
    """
    try:
        # Obtener todos los lugares activos
        lugares = LugarGooglePlaces.objects.filter(is_active=True)
        
        logger.info(f"Encontrados {lugares.count()} lugares activos")
        
        # Convertir a diccionarios
        lugares_data = []
        for lugar in lugares:
            lugar_dict = {
                'id': lugar.id,
                'nombre': lugar.nombre,
                'tipo_principal': lugar.tipo_principal,
                'tipos_adicionales': lugar.tipos_adicionales,
                'rating': float(lugar.rating) if lugar.rating else 0.0,
                'nivel_precios': lugar.nivel_precios.descripcion if lugar.nivel_precios else '',
                'direccion': lugar.direccion,
                'latitud': float(lugar.latitud) if lugar.latitud else 0.0,
                'longitud': float(lugar.longitud) if lugar.longitud else 0.0,
                'palabras_clave_ia': lugar.palabras_clave_ia or '',
                'resumen_ia': lugar.resumen_ia or '',
                'total_ratings': lugar.total_ratings
            }
            lugares_data.append(lugar_dict)
        
        return lugares_data
        
    except Exception as e:
        logger.error(f"Error al obtener lugares activos: {e}")
        raise

def mostrar_estadisticas_tipos(lugares_data: List[Dict[str, Any]]):
    """Muestra estadísticas de tipos principales y adicionales"""
    print("\n📊 Estadísticas de Tipos:")
    print("=" * 60)
    
    # Contar tipos principales
    tipos_principales = {}
    tipos_adicionales_todos = {}
    
    for lugar in lugares_data:
        # Tipo principal
        tipo_principal = lugar.get('tipo_principal', '')
        tipos_principales[tipo_principal] = tipos_principales.get(tipo_principal, 0) + 1
        
        # Tipos adicionales
        tipos_adicionales = lugar.get('tipos_adicionales', [])
        for tipo in tipos_adicionales:
            tipos_adicionales_todos[tipo] = tipos_adicionales_todos.get(tipo, 0) + 1
    
    print(f"Tipos principales únicos: {len(tipos_principales)}")
    print(f"Tipos adicionales únicos: {len(tipos_adicionales_todos)}")
    
    print("\nTop 10 tipos principales:")
    for tipo, count in sorted(tipos_principales.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {tipo}: {count} lugares")
    
    print("\nTop 10 tipos adicionales:")
    for tipo, count in sorted(tipos_adicionales_todos.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {tipo}: {count} lugares")

def main():
    """Función principal del script"""
    try:
        logger.info("🚀 Iniciando regeneración de base de datos vectorial...")
        logger.info("💡 Incluyendo tipos_adicionales en los metadatos")
        
        # Obtener instancia de la base de datos vectorial
        vector_db = get_vector_db()
        
        # Eliminar índice existente
        logger.info("🗑️ Eliminando índice existente...")
        try:
            vector_db.delete_index()
            logger.info("✅ Índice eliminado")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo eliminar índice: {e}")
        
        # Crear nuevo índice
        logger.info("🏗️ Creando nuevo índice...")
        vector_db.create_index()
        
        # Obtener todos los lugares activos
        logger.info("📊 Obteniendo lugares activos...")
        lugares_data = obtener_todos_lugares_activos()
        
        # Mostrar estadísticas
        mostrar_estadisticas_tipos(lugares_data)
        
        # Filtrar lugares con contenido para embeddings
        lugares_con_contenido = []
        lugares_sin_contenido = []
        
        for lugar in lugares_data:
            if lugar.get('palabras_clave_ia') or lugar.get('resumen_ia'):
                lugares_con_contenido.append(lugar)
            else:
                lugares_sin_contenido.append(lugar)
        
        logger.info(f"📈 Lugares con contenido para embeddings: {len(lugares_con_contenido)}")
        logger.info(f"⚠️ Lugares sin contenido: {len(lugares_sin_contenido)}")
        
        if lugares_sin_contenido:
            logger.warning("Algunos lugares no tienen palabras_clave_ia ni resumen_ia")
            logger.warning("Estos lugares no se incluirán en la base vectorial")
        
        # Añadir lugares a la base vectorial
        if lugares_con_contenido:
            logger.info(f"✅ Añadiendo {len(lugares_con_contenido)} lugares a la base vectorial...")
            success = vector_db.add_lugares(lugares_con_contenido)
            
            if success:
                logger.info("✅ Lugares añadidos exitosamente")
            else:
                logger.error("❌ Error al añadir lugares")
                return
        else:
            logger.warning("⚠️ No hay lugares con contenido para añadir")
            return
        
        # Estadísticas finales
        final_stats = vector_db.get_index_stats()
        logger.info("🎉 Regeneración completada!")
        logger.info(f"📊 Estadísticas finales del índice:")
        logger.info(f"   - Total de vectores: {final_stats.get('total_vector_count', 0)}")
        logger.info(f"   - Dimensiones: {final_stats.get('dimension', 0)}")
        logger.info(f"   - Índice: {final_stats.get('index_fullness', 0)}")
        
        # Verificar que los tipos_adicionales se incluyeron
        logger.info("🔍 Verificando inclusión de tipos_adicionales...")
        try:
            # Hacer una búsqueda de prueba
            resultados_prueba = vector_db.search_similar("hotel", top_k=1)
            if resultados_prueba:
                metadata = resultados_prueba[0]['metadata']
                tipos_adicionales = metadata.get('tipos_adicionales', [])
                logger.info(f"✅ Tipos adicionales incluidos en metadata: {tipos_adicionales}")
            else:
                logger.warning("⚠️ No se pudieron obtener resultados de prueba")
        except Exception as e:
            logger.error(f"❌ Error en verificación: {e}")
        
        logger.info("✅ Regeneración completada exitosamente")
        logger.info("💡 Ahora el sistema considera tanto tipo_principal como tipos_adicionales")
        
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 