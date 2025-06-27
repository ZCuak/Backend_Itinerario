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

def test_filtrado_por_tipos():
    """Prueba el filtrado que considera tanto tipo_principal como tipos_adicionales"""
    print("\n🧪 Probando filtrado por tipos (tipo_principal + tipos_adicionales)...")
    
    integrator = ChatbotIntegrator()
    
    # Casos de prueba para diferentes tipos
    casos_tipos = [
        ("hotel", "Quiero un hotel con piscina"),
        ("restaurant", "Busco un restaurante romántico"),
        ("cafe", "Necesito un café con wifi"),
        ("bar", "Quiero un bar con música en vivo"),
        ("tourist_attraction", "Busco atracciones turísticas")
    ]
    
    for tipo_buscar, consulta in casos_tipos:
        print(f"\n📝 Buscando tipo '{tipo_buscar}' con consulta: '{consulta}'")
        try:
            # Extraer filtros
            filtros = integrator.extraer_filtros_deepseek(consulta)
            print(f"   Filtros extraídos: {filtros.get('tipo_establecimiento', 'N/A')}")
            
            # Buscar candidatos con filtro de tipo
            candidatos = integrator.buscar_candidatos(filtros, top_k=5)
            
            print(f"   Candidatos encontrados: {len(candidatos)}")
            
            # Verificar que los candidatos tengan el tipo buscado
            candidatos_correctos = 0
            for candidato in candidatos[:3]:  # Solo verificar los primeros 3
                tipo_principal = candidato.get('tipo_principal', '')
                tipos_adicionales = candidato.get('tipos_adicionales', [])
                
                tiene_tipo = (tipo_principal == tipo_buscar or 
                             tipo_buscar in tipos_adicionales)
                
                if tiene_tipo:
                    candidatos_correctos += 1
                    print(f"   ✅ {candidato.get('nombre', 'N/A')} - Tipo: {tipo_principal}, Adicionales: {tipos_adicionales}")
                else:
                    print(f"   ❌ {candidato.get('nombre', 'N/A')} - Tipo: {tipo_principal}, Adicionales: {tipos_adicionales}")
            
            print(f"   📊 Candidatos con tipo correcto: {candidatos_correctos}/3")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas de extracción de características específicas...")
    
    # Prueba 1: Extracción de características específicas
    test_extraccion_caracteristicas_especificas()
    
    # Prueba 2: Caso específico mencionado
    test_casos_especificos()
    
    # Prueba 3: Filtrado por tipos (nueva funcionalidad)
    test_filtrado_por_tipos()
    
    print("\n✅ Pruebas completadas!")
    print("💡 Verificando que se extraigan características específicas del mensaje")
    print("💡 Verificando que el filtrado considere tanto tipo_principal como tipos_adicionales")

if __name__ == "__main__":
    main() 