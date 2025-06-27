#!/usr/bin/env python3
"""
Script de prueba para verificar extracción de características específicas
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

def test_extraccion_caracteristicas_especificas():
    """Prueba la extracción de características específicas"""
    print("🧪 Probando extracción de características específicas...")
    
    integrator = ChatbotIntegrator()
    
    # Casos de prueba específicos
    casos_prueba = [
        "Quiero un hotel con piscina y casino",
        "Busco un restaurante romántico con terraza",
        "Necesito un café con wifi y buena comida",
        "Hotel de lujo con spa y gimnasio",
        "Restaurante familiar con parque infantil y wifi",
        "Café con terraza y música en vivo",
        "Bar con karaoke y comida rápida"
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
            
            # Verificar que las características sean específicas
            caracteristicas = filtros.get('caracteristicas', [])
            if caracteristicas:
                print(f"   ✅ Características específicas encontradas: {len(caracteristicas)}")
            else:
                print(f"   ⚠️ No se extrajeron características específicas")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_casos_especificos():
    """Prueba casos específicos que mencionaste"""
    print("\n🧪 Probando casos específicos mencionados...")
    
    integrator = ChatbotIntegrator()
    
    # Caso específico que mencionaste
    caso_especifico = "Quiero un hotel con piscina y casino"
    print(f"📝 Caso específico: '{caso_especifico}'")
    
    try:
        filtros = integrator.extraer_filtros_deepseek(caso_especifico)
        print(f"✅ Resultado:")
        print(f"   Tipo: {filtros.get('tipo_establecimiento', 'N/A')}")
        print(f"   Características: {filtros.get('caracteristicas', [])}")
        
        # Verificar que contenga "piscina" y "casino"
        caracteristicas = filtros.get('caracteristicas', [])
        tiene_piscina = any('piscina' in car.lower() for car in caracteristicas)
        tiene_casino = any('casino' in car.lower() for car in caracteristicas)
        
        print(f"   ✅ Contiene 'piscina': {tiene_piscina}")
        print(f"   ✅ Contiene 'casino': {tiene_casino}")
        
        if tiene_piscina and tiene_casino:
            print(f"   🎉 ¡Extracción correcta!")
        else:
            print(f"   ❌ Extracción incorrecta - faltan características específicas")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas de extracción de características específicas...")
    
    # Prueba 1: Extracción de características específicas
    test_extraccion_caracteristicas_especificas()
    
    # Prueba 2: Caso específico mencionado
    test_casos_especificos()
    
    print("\n✅ Pruebas completadas!")
    print("💡 Verificando que se extraigan características específicas del mensaje")

if __name__ == "__main__":
    main() 