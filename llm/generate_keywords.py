"""
Script para generar palabras clave de resúmenes IA existentes
Genera y registra inmediatamente, sin esperar a procesar todos
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
from chatbot.deepseek.deepseek import extraer_palabras_clave_resumen

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_lugares_sin_palabras_clave() -> List[Dict[str, Any]]:
    """
    Obtiene lugares que tienen resumen IA pero no palabras clave
    
    Returns:
        Lista de diccionarios con datos de lugares
    """
    try:
        # Obtener lugares con resumen IA pero sin palabras clave
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
        
        logger.info(f"Encontrados {lugares.count()} lugares sin palabras clave")
        
        # Convertir a diccionarios
        lugares_data = []
        for lugar in lugares:
            lugar_dict = {
                'id': lugar.id,
                'nombre': lugar.nombre,
                'resumen_ia': lugar.resumen_ia
            }
            lugares_data.append(lugar_dict)
        
        return lugares_data
        
    except Exception as e:
        logger.error(f"Error al obtener lugares sin palabras clave: {e}")
        raise

def procesar_lugar_individual(lugar_data: Dict[str, Any]) -> bool:
    """
    Procesa un lugar individual: genera palabras clave y las registra inmediatamente
    
    Args:
        lugar_data: Datos del lugar
        
    Returns:
        bool: True si se procesó exitosamente
    """
    try:
        lugar_id = lugar_data['id']
        nombre = lugar_data['nombre']
        resumen_ia = lugar_data['resumen_ia']
        
        logger.info(f"🔍 Procesando lugar {lugar_id}: {nombre}")
        
        # Generar palabras clave
        palabras_clave = extraer_palabras_clave_resumen(resumen_ia)
        
        if palabras_clave:
            # Actualizar inmediatamente en la base de datos
            lugar = LugarGooglePlaces.objects.get(id=lugar_id)
            lugar.palabras_clave_ia = palabras_clave
            lugar.save()
            
            num_palabras = len(palabras_clave.split(','))
            logger.info(f"✅ Lugar {lugar_id} actualizado: {num_palabras} palabras clave")
            logger.info(f"   Palabras clave: {palabras_clave[:100]}...")
            return True
        else:
            logger.warning(f"⚠️ No se pudieron generar palabras clave para lugar {lugar_id}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error procesando lugar {lugar_data.get('id', 'N/A')}: {e}")
        return False

def main():
    """Función principal del script"""
    try:
        logger.info("🚀 Iniciando generación de palabras clave...")
        
        # Obtener lugares sin palabras clave
        lugares_data = get_lugares_sin_palabras_clave()
        
        if not lugares_data:
            logger.info("✅ Todos los lugares ya tienen palabras clave")
            return
        
        # Procesar cada lugar individualmente
        total_lugares = len(lugares_data)
        exitosos = 0
        fallidos = 0
        
        logger.info(f"📊 Procesando {total_lugares} lugares...")
        print("=" * 80)
        
        for i, lugar_data in enumerate(lugares_data, 1):
            print(f"\n[{i}/{total_lugares}] Procesando: {lugar_data['nombre']}")
            
            # Procesar lugar individual
            success = procesar_lugar_individual(lugar_data)
            
            if success:
                exitosos += 1
                print(f"✅ Éxito")
            else:
                fallidos += 1
                print(f"❌ Falló")
            
            # Mostrar progreso
            progreso = (i / total_lugares) * 100
            print(f"📈 Progreso: {progreso:.1f}% ({exitosos} exitosos, {fallidos} fallidos)")
            
            # Pausa breve entre lugares para evitar rate limits
            if i < total_lugares:
                import time
                time.sleep(1)
        
        # Resumen final
        print("\n" + "=" * 80)
        logger.info(f"🎉 Procesamiento completado!")
        logger.info(f"📊 Resumen:")
        logger.info(f"   - Total procesados: {total_lugares}")
        logger.info(f"   - Exitosos: {exitosos}")
        logger.info(f"   - Fallidos: {fallidos}")
        logger.info(f"   - Tasa de éxito: {(exitosos/total_lugares)*100:.1f}%")
        
        if exitosos > 0:
            logger.info("✅ Generación de palabras clave completada exitosamente")
        else:
            logger.error("❌ No se pudo generar ninguna palabra clave")
            
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 