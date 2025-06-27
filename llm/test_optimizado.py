#!/usr/bin/env python3
"""
Script de prueba optimizado para el integrador
Usa palabras clave en lugar de resúmenes completos para ahorrar tokens
"""

import sys
import os
import logging

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.integrator import ChatbotIntegrator

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_extraccion_filtros_optimizada():
    """Prueba la extracción de filtros con ejemplos específicos"""
    print("🧪 Probando extracción de filtros optimizada...")
    
    integrator = ChatbotIntegrator()
    
    # Casos de prueba específicos
    casos_prueba = [
        "Quiero un hotel con piscina",
        "Busco un restaurante romántico para cenar",
        "Necesito un café con wifi y buena comida",
        "Hotel de lujo con spa y gimnasio",
        "Restaurante familiar con parque infantil"
    ]
    
    for caso in casos_prueba:
        print(f"\n📝 Caso: '{caso}'")
        try:
            filtros = integrator.extraer_filtros_deepseek(caso)
            print(f"✅ Filtros extraídos:")
            print(f"   Tipo: {filtros.get('tipo_establecimiento', 'N/A')}")
            print(f"   Consulta semántica: {filtros.get('consulta_semantica', 'N/A')}")
            print(f"   Características: {filtros.get('caracteristicas', [])}")
            print(f"   Nivel precio: {filtros.get('nivel_precio', 'N/A')}")
            print(f"   Intención: {filtros.get('intencion', 'N/A')}")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_busqueda_con_palabras_clave():
    """Prueba la búsqueda usando palabras clave"""
    print("\n🧪 Probando búsqueda con palabras clave...")
    
    integrator = ChatbotIntegrator()
    
    # Caso de prueba
    mensaje = "Quiero un hotel con piscina"
    print(f"📝 Mensaje: '{mensaje}'")
    
    try:
        # Solo extraer filtros y buscar candidatos (sin selección final para ahorrar tokens)
        filtros = integrator.extraer_filtros_deepseek(mensaje)
        candidatos = integrator.buscar_candidatos(filtros, top_k=5)
        
        print(f"\n✅ Resultados:")
        print(f"   Filtros extraídos: {filtros.get('caracteristicas', [])}")
        print(f"   Candidatos encontrados: {len(candidatos)}")
        
        # Mostrar candidatos con palabras clave
        for i, candidato in enumerate(candidatos[:3], 1):
            print(f"\n   {i}. {candidato.get('nombre', 'N/A')}")
            print(f"      Tipo: {candidato.get('tipo_principal', 'N/A')}")
            print(f"      Rating: {candidato.get('rating', 'N/A')}")
            print(f"      Score: {candidato.get('score_similitud', 'N/A')}")
            
            # Mostrar palabras clave si están disponibles
            palabras_clave = candidato.get('palabras_clave_ia', '')
            if palabras_clave:
                print(f"      Palabras clave: {palabras_clave}")
            else:
                resumen = candidato.get('resumen_ia', '')
                if resumen:
                    print(f"      Resumen (truncado): {resumen[:50]}...")
                else:
                    print(f"      Sin información adicional")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_eliminacion_duplicados():
    """Prueba la eliminación de duplicados"""
    print("\n🧪 Probando eliminación de duplicados...")
    
    integrator = ChatbotIntegrator()
    
    # Crear candidatos de prueba con duplicados
    candidatos_prueba = [
        {'id': 1, 'nombre': 'Hotel A', 'tipo_principal': 'hotel', 'rating': 4.5, 'score_similitud': 0.9, 'palabras_clave_ia': 'lujo, piscina, spa'},
        {'id': 2, 'nombre': 'Hotel B', 'tipo_principal': 'hotel', 'rating': 4.2, 'score_similitud': 0.8, 'palabras_clave_ia': 'familiar, piscina'},
        {'id': 1, 'nombre': 'Hotel A', 'tipo_principal': 'hotel', 'rating': 4.5, 'score_similitud': 0.9, 'palabras_clave_ia': 'lujo, piscina, spa'},  # Duplicado
        {'id': 3, 'nombre': 'Hotel C', 'tipo_principal': 'hotel', 'rating': 4.0, 'score_similitud': 0.7, 'palabras_clave_ia': 'económico, básico'},
        {'id': 2, 'nombre': 'Hotel B', 'tipo_principal': 'hotel', 'rating': 4.2, 'score_similitud': 0.8, 'palabras_clave_ia': 'familiar, piscina'},  # Duplicado
    ]
    
    print(f"📊 Candidatos originales: {len(candidatos_prueba)}")
    candidatos_unicos = integrator._eliminar_duplicados(candidatos_prueba)
    print(f"✅ Candidatos únicos: {len(candidatos_unicos)}")
    
    for candidato in candidatos_unicos:
        print(f"   - {candidato['nombre']} (ID: {candidato['id']}) - {candidato['palabras_clave_ia']}")

def main():
    """Función principal de pruebas optimizadas"""
    print("🚀 Iniciando pruebas optimizadas del integrador...")
    print("💡 Usando palabras clave en lugar de resúmenes completos para ahorrar tokens")
    
    # Prueba 1: Extracción de filtros optimizada
    test_extraccion_filtros_optimizada()
    
    # Prueba 2: Eliminación de duplicados
    test_eliminacion_duplicados()
    
    # Prueba 3: Búsqueda con palabras clave (solo si hay datos en Pinecone)
    try:
        test_busqueda_con_palabras_clave()
    except Exception as e:
        print(f"⚠️ Búsqueda con palabras clave no disponible: {e}")
        print("   (Puede ser porque no hay datos en Pinecone)")
    
    print("\n✅ Pruebas optimizadas completadas!")
    print("💡 Optimizaciones implementadas:")
    print("   - Uso de palabras_clave_ia en lugar de resúmenes completos")
    print("   - Eliminación de duplicados en múltiples puntos")
    print("   - Consulta semántica mejorada con características")
    print("   - Ahorro significativo de tokens en LLM")

if __name__ == "__main__":
    main() 