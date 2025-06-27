"""
Script para consultar la base de datos vectorial
Usa filtros extraídos por DeepSeek para buscar candidatos
"""

import os
import sys
import django
import logging
from typing import List, Dict, Any, Optional

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itinerario_backend.settings')
django.setup()

from .vector_db import get_vector_db

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VectorQueryEngine:
    """Motor de consultas vectoriales para lugares"""
    
    def __init__(self):
        self.vector_db = get_vector_db()
    
    def buscar_lugares(self, 
                      consulta: str,
                      tipo_principal: Optional[str] = None,
                      top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Busca lugares usando consulta semántica y filtros
        
        Args:
            consulta: Consulta de texto del usuario
            tipo_principal: Filtro por tipo de establecimiento (considera tipo_principal y tipos_adicionales)
            top_k: Número máximo de resultados
            
        Returns:
            Lista de lugares con scores de similitud
        """
        try:
            logger.info(f"🔍 Buscando lugares con consulta: '{consulta}'")
            if tipo_principal:
                logger.info(f"📋 Filtro por tipo: {tipo_principal} (incluye tipos adicionales)")
            
            # Si se especifica un tipo, usar el método search_by_tipo que considera tipos_adicionales
            if tipo_principal:
                resultados = self.vector_db.search_by_tipo(
                    query=consulta,
                    tipo_principal=tipo_principal,
                    top_k=top_k
                )
            else:
                # Si no se especifica tipo, usar búsqueda general
                resultados = self.vector_db.search_similar(
                    query=consulta,
                    top_k=top_k,
                    filter_dict=None
                )
            
            logger.info(f"✅ Encontrados {len(resultados)} lugares")
            
            # Formatear resultados
            lugares_formateados = []
            for resultado in resultados:
                lugar_info = {
                    'id': resultado['lugar_id'],
                    'nombre': resultado['nombre'],
                    'tipo_principal': resultado['tipo_principal'],
                    'tipos_adicionales': resultado.get('tipos_adicionales', []),
                    'rating': resultado['rating'],
                    'score_similitud': resultado['score'],
                    'resumen_ia': resultado['resumen_ia'],
                    'palabras_clave_ia': resultado.get('palabras_clave_ia', ''),
                    'metadata': resultado['metadata']
                }
                lugares_formateados.append(lugar_info)
            
            return lugares_formateados
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda: {e}")
            raise
    
    def buscar_por_tipo(self, 
                       consulta: str,
                       tipo_principal: str,
                       top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Busca lugares de un tipo específico
        
        Args:
            consulta: Consulta de texto
            tipo_principal: Tipo de establecimiento
            top_k: Número máximo de resultados
            
        Returns:
            Lista de lugares del tipo especificado
        """
        return self.buscar_lugares(consulta, tipo_principal, top_k)
    
    def buscar_hoteles(self, consulta: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Busca hoteles específicamente"""
        return self.buscar_por_tipo(consulta, "hotel", top_k)
    
    def buscar_restaurantes(self, consulta: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Busca restaurantes específicamente"""
        return self.buscar_por_tipo(consulta, "restaurant", top_k)
    
    def buscar_atracciones(self, consulta: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Busca atracciones turísticas"""
        return self.buscar_por_tipo(consulta, "tourist_attraction", top_k)

def main():
    """Función principal para probar consultas"""
    try:
        logger.info("🚀 Iniciando pruebas de consulta vectorial...")
        
        # Crear motor de consultas
        query_engine = VectorQueryEngine()
        
        # Ejemplos de consultas
        consultas_prueba = [
            "hotel lujoso con piscina",
            "restaurante romántico para cena",
            "atracción turística histórica",
            "café acogedor para trabajar",
            "bar con música en vivo"
        ]
        
        for consulta in consultas_prueba:
            print(f"\n{'='*60}")
            print(f"🔍 Consulta: {consulta}")
            print(f"{'='*60}")
            
            # Buscar sin filtros
            resultados = query_engine.buscar_lugares(consulta, top_k=5)
            
            for i, lugar in enumerate(resultados, 1):
                print(f"{i}. {lugar['nombre']}")
                print(f"   Tipo: {lugar['tipo_principal']}")
                print(f"   Rating: {lugar['rating']}/5")
                print(f"   Score: {lugar['score_similitud']:.3f}")
                print()
        
        logger.info("✅ Pruebas de consulta completadas")
        
    except Exception as e:
        logger.error(f"❌ Error en pruebas: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 