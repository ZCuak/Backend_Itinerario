"""
Script para ingesta de datos a la base de datos vectorial
Usa palabras_clave_ia como campo principal para embeddings
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

def get_lugares_con_palabras_clave() -> List[Dict[str, Any]]:
    """
    Obtiene lugares que tienen palabras clave IA para embeddings
    
    Returns:
        Lista de diccionarios con datos de lugares
    """
    try:
        # Obtener lugares activos con palabras clave IA
        lugares = LugarGooglePlaces.objects.filter(
            is_active=True,
            palabras_clave_ia__isnull=False
        ).exclude(
            palabras_clave_ia=''
        )
        
        logger.info(f"Encontrados {lugares.count()} lugares con palabras clave IA")
        
        # Convertir a diccionarios
        lugares_data = []
        for lugar in lugares:
            lugar_dict = {
                'id': lugar.id,
                'nombre': lugar.nombre,
                'tipo_principal': lugar.tipo_principal,
                'rating': float(lugar.rating) if lugar.rating else 0.0,
                'nivel_precios': lugar.nivel_precios.descripcion if lugar.nivel_precios else '',
                'direccion': lugar.direccion,
                'latitud': float(lugar.latitud) if lugar.latitud else 0.0,
                'longitud': float(lugar.longitud) if lugar.longitud else 0.0,
                'palabras_clave_ia': lugar.palabras_clave_ia,
                'resumen_ia': lugar.resumen_ia,
                'total_ratings': lugar.total_ratings
            }
            lugares_data.append(lugar_dict)
        
        return lugares_data
        
    except Exception as e:
        logger.error(f"Error al obtener lugares con palabras clave: {e}")
        raise

def get_lugares_con_resumen_fallback() -> List[Dict[str, Any]]:
    """
    Obtiene lugares que solo tienen resumen IA (fallback)
    
    Returns:
        Lista de diccionarios con datos de lugares
    """
    try:
        # Obtener lugares activos con resumen IA pero sin palabras clave
        lugares = LugarGooglePlaces.objects.filter(
            is_active=True,
            resumen_ia__isnull=False
        ).exclude(
            resumen_ia=''
        ).filter(
            palabras_clave_ia__isnull=True
        ) | LugarGooglePlaces.objects.filter(
            is_active=True,
            resumen_ia__isnull=False
        ).exclude(
            resumen_ia=''
        ).filter(
            palabras_clave_ia=''
        )
        
        logger.info(f"Encontrados {lugares.count()} lugares con solo resumen IA (fallback)")
        
        # Convertir a diccionarios
        lugares_data = []
        for lugar in lugares:
            lugar_dict = {
                'id': lugar.id,
                'nombre': lugar.nombre,
                'tipo_principal': lugar.tipo_principal,
                'rating': float(lugar.rating) if lugar.rating else 0.0,
                'nivel_precios': lugar.nivel_precios.descripcion if lugar.nivel_precios else '',
                'direccion': lugar.direccion,
                'latitud': float(lugar.latitud) if lugar.latitud else 0.0,
                'longitud': float(lugar.longitud) if lugar.longitud else 0.0,
                'palabras_clave_ia': '',  # Vacío para usar resumen como fallback
                'resumen_ia': lugar.resumen_ia,
                'total_ratings': lugar.total_ratings
            }
            lugares_data.append(lugar_dict)
        
        return lugares_data
        
    except Exception as e:
        logger.error(f"Error al obtener lugares con resumen fallback: {e}")
        raise

def main():
    """Función principal del script"""
    try:
        logger.info("🚀 Iniciando ingesta a base de datos vectorial...")
        
        # Obtener instancia de la base de datos vectorial
        vector_db = get_vector_db()
        
        # Crear índice si no existe
        logger.info("Verificando/creando índice de Pinecone...")
        vector_db.create_index()
        
        # Verificar que el índice existe
        stats = vector_db.get_index_stats()
        logger.info(f"Índice actual: {stats}")
        
        # 1. Procesar lugares con palabras clave IA (prioridad)
        logger.info("📊 Procesando lugares con palabras clave IA...")
        lugares_palabras_clave = get_lugares_con_palabras_clave()
        
        if lugares_palabras_clave:
            logger.info(f"✅ Añadiendo {len(lugares_palabras_clave)} lugares con palabras clave")
            success = vector_db.add_lugares(lugares_palabras_clave)
            
            if success:
                logger.info("✅ Lugares con palabras clave añadidos exitosamente")
            else:
                logger.error("❌ Error al añadir lugares con palabras clave")
        else:
            logger.info("ℹ️ No hay lugares con palabras clave para procesar")
        
        # 2. Procesar lugares con solo resumen IA (fallback)
        logger.info("📊 Procesando lugares con solo resumen IA (fallback)...")
        lugares_resumen = get_lugares_con_resumen_fallback()
        
        if lugares_resumen:
            logger.info(f"✅ Añadiendo {len(lugares_resumen)} lugares con resumen IA (fallback)")
            success = vector_db.add_lugares(lugares_resumen)
            
            if success:
                logger.info("✅ Lugares con resumen IA añadidos exitosamente")
            else:
                logger.error("❌ Error al añadir lugares con resumen IA")
        else:
            logger.info("ℹ️ No hay lugares con solo resumen IA para procesar")
        
        # Estadísticas finales
        final_stats = vector_db.get_index_stats()
        logger.info("🎉 Ingesta completada!")
        logger.info(f"📊 Estadísticas finales del índice:")
        logger.info(f"   - Total de vectores: {final_stats.get('total_vector_count', 0)}")
        logger.info(f"   - Dimensiones: {final_stats.get('dimension', 0)}")
        logger.info(f"   - Índice: {final_stats.get('index_fullness', 0)}")
        
        # Resumen de procesamiento
        total_procesados = len(lugares_palabras_clave) + len(lugares_resumen)
        logger.info(f"📈 Resumen de procesamiento:")
        logger.info(f"   - Lugares con palabras clave: {len(lugares_palabras_clave)}")
        logger.info(f"   - Lugares con resumen IA (fallback): {len(lugares_resumen)}")
        logger.info(f"   - Total procesados: {total_procesados}")
        
        if total_procesados > 0:
            logger.info("✅ Ingesta completada exitosamente")
        else:
            logger.warning("⚠️ No se procesó ningún lugar")
            
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 