#!/usr/bin/env python3
"""
Script de prueba para el integrador mejorado
"""

import sys
import os
import logging

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.integrator import ChatbotIntegrator
from chatbot.deepseek.deepseek import enviar_prompt

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_extraccion_filtros():
    """Prueba la extracción de filtros"""
    print("🧪 Probando extracción de filtros...")
    
    integrator = ChatbotIntegrator()
    
    # Casos de prueba
    casos_prueba = [
        "Quiero un hotel con piscina",
        "Busco un restaurante romántico para cenar",
        "Necesito un café con wifi",
        "¿Dónde puedo encontrar atracciones turísticas?",
        "Hotel de lujo con spa"
    ]
    
    for caso in casos_prueba:
        print(f"\n📝 Caso: '{caso}'")
        try:
            filtros = integrator.extraer_filtros_deepseek(caso)
            print(f"✅ Filtros extraídos:")
            for key, value in filtros.items():
                print(f"   {key}: {value}")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_busqueda_completa():
    """Prueba la búsqueda completa"""
    print("\n🧪 Probando búsqueda completa...")
    
    integrator = ChatbotIntegrator()
    
    # Caso de prueba
    mensaje = "Quiero un hotel con piscina"
    print(f"📝 Mensaje: '{mensaje}'")
    
    try:
        resultado = integrator.procesar_mensaje_completo(mensaje)
        
        print(f"\n✅ Resultado completo:")
        print(f"   Filtros: {resultado.get('filtros', {})}")
        print(f"   Candidatos encontrados: {len(resultado.get('candidatos', []))}")
        print(f"   Candidatos seleccionados: {len(resultado.get('mejores_candidatos', []))}")
        
        # Mostrar mejores candidatos
        print(f"\n🏆 Mejores candidatos:")
        for i, candidato in enumerate(resultado.get('mejores_candidatos', [])[:3], 1):
            print(f"   {i}. {candidato.get('nombre', 'N/A')}")
            print(f"      Tipo: {candidato.get('tipo_principal', 'N/A')}")
            print(f"      Rating: {candidato.get('rating', 'N/A')}")
            print(f"      Score: {candidato.get('score_similitud', 'N/A')}")
            if candidato.get('resumen_ia'):
                print(f"      Resumen: {candidato['resumen_ia'][:100]}...")
            print()
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_eliminacion_duplicados():
    """Prueba la eliminación de duplicados"""
    print("\n🧪 Probando eliminación de duplicados...")
    
    integrator = ChatbotIntegrator()
    
    # Crear candidatos de prueba con duplicados
    candidatos_prueba = [
        {'id': 1, 'nombre': 'Hotel A', 'tipo_principal': 'hotel', 'rating': 4.5, 'score_similitud': 0.9},
        {'id': 2, 'nombre': 'Hotel B', 'tipo_principal': 'hotel', 'rating': 4.2, 'score_similitud': 0.8},
        {'id': 1, 'nombre': 'Hotel A', 'tipo_principal': 'hotel', 'rating': 4.5, 'score_similitud': 0.9},  # Duplicado
        {'id': 3, 'nombre': 'Hotel C', 'tipo_principal': 'hotel', 'rating': 4.0, 'score_similitud': 0.7},
        {'id': 2, 'nombre': 'Hotel B', 'tipo_principal': 'hotel', 'rating': 4.2, 'score_similitud': 0.8},  # Duplicado
    ]
    
    print(f"📊 Candidatos originales: {len(candidatos_prueba)}")
    candidatos_unicos = integrator._eliminar_duplicados(candidatos_prueba)
    print(f"✅ Candidatos únicos: {len(candidatos_unicos)}")
    
    for candidato in candidatos_unicos:
        print(f"   - {candidato['nombre']} (ID: {candidato['id']})")

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas del integrador mejorado...")
    
    # Prueba 1: Extracción de filtros
    test_extraccion_filtros()
    
    # Prueba 2: Eliminación de duplicados
    test_eliminacion_duplicados()
    
    # Prueba 3: Búsqueda completa (solo si hay datos en Pinecone)
    try:
        test_busqueda_completa()
    except Exception as e:
        print(f"⚠️ Búsqueda completa no disponible: {e}")
        print("   (Puede ser porque no hay datos en Pinecone)")
    
    print("\n✅ Pruebas completadas!")

if __name__ == "__main__":
    main() 