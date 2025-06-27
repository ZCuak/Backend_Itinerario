"""
Integrador que conecta DeepSeek con el sistema de embeddings
1. DeepSeek extrae filtros del mensaje del usuario
2. Sistema de embeddings busca candidatos usando esos filtros
3. LLM selecciona los mejores candidatos
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

from chatbot.deepseek.deepseek import enviar_prompt
from .query import VectorQueryEngine

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ChatbotIntegrator:
    """Integrador principal del chatbot"""
    
    def __init__(self):
        self.query_engine = VectorQueryEngine()
    
    def extraer_filtros_deepseek(self, mensaje_usuario: str) -> Dict[str, Any]:
        """
        Usa DeepSeek para extraer filtros del mensaje del usuario
        
        Args:
            mensaje_usuario: Mensaje del usuario
            
        Returns:
            Diccionario con filtros extraídos
        """
        try:
            prompt = f"""
            Eres un asistente experto en turismo. Necesito que extraigas información específica del mensaje del usuario para buscar lugares turísticos.

            IMPORTANTE: Responde SOLO con un JSON válido. NO uses texto adicional, emojis ni explicaciones.

            Mensaje del usuario: "{mensaje_usuario}"

            Extrae la siguiente información y responde con un JSON que contenga:

            {{
                "tipo_establecimiento": "tipo principal (hotel, restaurant, tourist_attraction, cafe, bar, etc.)",
                "consulta_semantica": "consulta optimizada para búsqueda semántica que incluya características específicas mencionadas",
                "caracteristicas": ["características ESPECÍFICAS mencionadas en el mensaje"],
                "nivel_precio": "nivel de precio mencionado (económico, moderado, lujoso, etc.)",
                "ubicacion": "ubicación específica mencionada",
                "intencion": "intención del usuario (comer, dormir, visitar, etc.)"
            }}

            Reglas importantes:
            1. Si no se menciona un tipo específico, usa "point_of_interest"
            2. La consulta semántica debe incluir las características específicas mencionadas
            3. Las características deben ser ESPECÍFICAS del mensaje, no genéricas
            4. Para "hotel con piscina y casino" → características: ["piscina", "casino"]
            5. Para "restaurante romántico con terraza" → características: ["romántico", "terraza"]
            6. Para "café con wifi y buena comida" → características: ["wifi", "buena comida"]
            7. Si no hay información sobre una categoría, usa null
            8. Responde SOLO con el JSON, sin texto adicional

            JSON:
            """
            
            respuesta = enviar_prompt(prompt)
            
            if respuesta:
                import json
                # Limpiar la respuesta y parsear JSON
                respuesta_limpia = respuesta.strip()
                if respuesta_limpia.startswith('```json'):
                    respuesta_limpia = respuesta_limpia[7:]
                if respuesta_limpia.endswith('```'):
                    respuesta_limpia = respuesta_limpia[:-3]
                
                filtros = json.loads(respuesta_limpia)
                logger.info(f"✅ Filtros extraídos: {filtros}")
                return filtros
            else:
                logger.warning("⚠️ No se pudo extraer filtros con DeepSeek")
                return self._filtros_por_defecto(mensaje_usuario)
                
        except Exception as e:
            logger.error(f"❌ Error al extraer filtros: {e}")
            return self._filtros_por_defecto(mensaje_usuario)
    
    def _filtros_por_defecto(self, mensaje_usuario: str) -> Dict[str, Any]:
        """Filtros por defecto si falla la extracción"""
        return {
            "tipo_establecimiento": "point_of_interest",
            "consulta_semantica": mensaje_usuario,
            "caracteristicas": [],
            "nivel_precio": None,
            "ubicacion": None,
            "intencion": "buscar"
        }
    
    def _eliminar_duplicados(self, candidatos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Elimina candidatos duplicados basándose en el ID del lugar
        
        Args:
            candidatos: Lista de candidatos
            
        Returns:
            Lista de candidatos sin duplicados
        """
        candidatos_unicos = []
        ids_vistos = set()
        
        for candidato in candidatos:
            lugar_id = candidato.get('id')
            if lugar_id and lugar_id not in ids_vistos:
                candidatos_unicos.append(candidato)
                ids_vistos.add(lugar_id)
        
        logger.info(f"🔄 Eliminados {len(candidatos) - len(candidatos_unicos)} duplicados")
        return candidatos_unicos
    
    def buscar_candidatos(self, filtros: Dict[str, Any], top_k: int = 15) -> List[Dict[str, Any]]:
        """
        Busca candidatos usando los filtros extraídos
        
        Args:
            filtros: Filtros extraídos por DeepSeek
            top_k: Número máximo de candidatos
            
        Returns:
            Lista de candidatos encontrados
        """
        try:
            tipo_establecimiento = filtros.get('tipo_establecimiento')
            consulta_semantica = filtros.get('consulta_semantica', '')
            caracteristicas = filtros.get('caracteristicas', [])
            
            logger.info(f"🔍 Buscando candidatos con filtros: {filtros}")
            
            # Construir consulta semántica mejorada
            consulta_mejorada = consulta_semantica
            
            # Si hay características específicas, agregarlas explícitamente a la consulta
            if caracteristicas:
                caracteristicas_texto = " ".join(caracteristicas)
                # Combinar consulta original con características específicas
                consulta_mejorada = f"{consulta_semantica} {caracteristicas_texto}"
                logger.info(f"🔍 Consulta mejorada con características específicas: {consulta_mejorada}")
            else:
                logger.info(f"🔍 Consulta original: {consulta_mejorada}")
            
            # Buscar candidatos usando embeddings
            candidatos = self.query_engine.buscar_lugares(
                consulta=consulta_mejorada,
                tipo_principal=tipo_establecimiento,
                top_k=top_k
            )
            
            # Eliminar duplicados
            candidatos_unicos = self._eliminar_duplicados(candidatos)
            
            logger.info(f"✅ Encontrados {len(candidatos_unicos)} candidatos únicos")
            return candidatos_unicos
            
        except Exception as e:
            logger.error(f"❌ Error al buscar candidatos: {e}")
            return []
    
    def seleccionar_mejores_candidatos(self, 
                                     candidatos: List[Dict[str, Any]], 
                                     filtros: Dict[str, Any],
                                     max_candidatos: int = 5) -> List[Dict[str, Any]]:
        """
        Usa LLM para seleccionar los mejores candidatos
        
        Args:
            candidatos: Lista de candidatos encontrados
            filtros: Filtros originales del usuario
            max_candidatos: Número máximo de candidatos finales
            
        Returns:
            Lista de mejores candidatos seleccionados
        """
        try:
            if not candidatos:
                return []
            
            # Eliminar duplicados antes de la selección
            candidatos_unicos = self._eliminar_duplicados(candidatos)
            
            # Preparar información de candidatos para el LLM (usando palabras clave)
            candidatos_info = []
            for i, candidato in enumerate(candidatos_unicos[:10], 1):  # Top 10 para análisis
                info = f"{i}. {candidato['nombre']} ({candidato['tipo_principal']})"
                info += f" - Rating: {candidato['rating']}/5"
                info += f" - Score: {candidato['score_similitud']:.3f}"
                
                # Usar palabras clave en lugar del resumen completo
                if candidato.get('palabras_clave_ia'):
                    info += f" - Palabras clave: {candidato['palabras_clave_ia']}"
                elif candidato.get('resumen_ia'):
                    # Fallback: usar solo las primeras 50 caracteres del resumen
                    info += f" - Resumen: {candidato['resumen_ia'][:50]}..."
                
                candidatos_info.append(info)
            
            candidatos_texto = "\n".join(candidatos_info)
            
            prompt = f"""
            Eres un experto en turismo. Necesito que selecciones los mejores lugares basándote en las preferencias del usuario.

            PREFERENCIAS DEL USUARIO:
            - Tipo de establecimiento: {filtros.get('tipo_establecimiento', 'N/A')}
            - Características buscadas: {filtros.get('caracteristicas', [])}
            - Nivel de precio: {filtros.get('nivel_precio', 'N/A')}
            - Ubicación: {filtros.get('ubicacion', 'N/A')}
            - Intención: {filtros.get('intencion', 'N/A')}

            CANDIDATOS DISPONIBLES:
            {candidatos_texto}

            INSTRUCCIONES:
            1. Selecciona los {max_candidatos} MEJORES candidatos que mejor se ajusten a las preferencias
            2. Considera: relevancia semántica, rating, características mencionadas, y score de similitud
            3. Prioriza lugares cuyas palabras clave coincidan con las características buscadas
            4. NO selecciones el mismo lugar más de una vez
            5. Si hay pocos candidatos relevantes, selecciona los mejores disponibles

            Responde SOLO con los números de los candidatos seleccionados, separados por comas.
            Ejemplo: 1, 3, 5, 7, 9

            Selección:
            """
            
            respuesta = enviar_prompt(prompt)
            
            if respuesta:
                # Parsear números seleccionados
                numeros_texto = respuesta.strip().replace(',', ' ').split()
                indices_seleccionados = []
                
                for num_texto in numeros_texto:
                    try:
                        indice = int(num_texto) - 1  # Convertir a índice base 0
                        if 0 <= indice < len(candidatos_unicos):
                            indices_seleccionados.append(indice)
                    except ValueError:
                        continue
                
                # Obtener candidatos seleccionados
                candidatos_seleccionados = [candidatos_unicos[i] for i in indices_seleccionados]
                
                # Eliminar duplicados finales por si acaso
                candidatos_finales = self._eliminar_duplicados(candidatos_seleccionados)
                
                logger.info(f"✅ Seleccionados {len(candidatos_finales)} mejores candidatos únicos")
                return candidatos_finales[:max_candidatos]
            else:
                # Fallback: tomar los primeros con mejor score
                candidatos_ordenados = sorted(candidatos_unicos, key=lambda x: x['score_similitud'], reverse=True)
                return candidatos_ordenados[:max_candidatos]
                
        except Exception as e:
            logger.error(f"❌ Error al seleccionar candidatos: {e}")
            # Fallback: tomar los primeros con mejor score
            candidatos_unicos = self._eliminar_duplicados(candidatos)
            candidatos_ordenados = sorted(candidatos_unicos, key=lambda x: x['score_similitud'], reverse=True)
            return candidatos_ordenados[:max_candidatos]
    
    def procesar_mensaje_completo(self, mensaje_usuario: str) -> Dict[str, Any]:
        """
        Procesa un mensaje completo del usuario
        
        Args:
            mensaje_usuario: Mensaje del usuario
            
        Returns:
            Resultado completo con filtros, candidatos y selección final
        """
        try:
            logger.info(f"🚀 Procesando mensaje: {mensaje_usuario}")
            
            # 1. Extraer filtros con DeepSeek
            filtros = self.extraer_filtros_deepseek(mensaje_usuario)
            
            # 2. Buscar candidatos con embeddings
            candidatos = self.buscar_candidatos(filtros)
            
            # 3. Seleccionar mejores candidatos con LLM
            mejores_candidatos = self.seleccionar_mejores_candidatos(candidatos, filtros)
            
            resultado = {
                'mensaje_original': mensaje_usuario,
                'filtros_extraidos': filtros,
                'candidatos_encontrados': len(candidatos),
                'mejores_candidatos': mejores_candidatos,
                'total_seleccionados': len(mejores_candidatos)
            }
            
            logger.info(f"✅ Procesamiento completado: {len(mejores_candidatos)} candidatos seleccionados")
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Error en procesamiento completo: {e}")
            return {
                'mensaje_original': mensaje_usuario,
                'error': str(e),
                'mejores_candidatos': []
            }

def main():
    """Función principal para probar el integrador"""
    try:
        logger.info("🚀 Iniciando pruebas del integrador...")
        
        # Crear integrador
        integrator = ChatbotIntegrator()
        
        # Mensajes de prueba
        mensajes_prueba = [
            "Necesito un hotel lujoso con piscina para mi luna de miel",
            "Busco un restaurante romántico para cenar con mi pareja",
            "Quiero visitar atracciones turísticas históricas en la ciudad",
            "Necesito un café acogedor donde pueda trabajar con mi laptop"
        ]
        
        for mensaje in mensajes_prueba:
            print(f"\n{'='*80}")
            print(f"💬 Mensaje: {mensaje}")
            print(f"{'='*80}")
            
            # Procesar mensaje completo
            resultado = integrator.procesar_mensaje_completo(mensaje)
            
            print(f"📋 Filtros extraídos: {resultado['filtros_extraidos']}")
            print(f"🔍 Candidatos encontrados: {resultado['candidatos_encontrados']}")
            print(f"✅ Mejores candidatos seleccionados:")
            
            for i, candidato in enumerate(resultado['mejores_candidatos'], 1):
                print(f"  {i}. {candidato['nombre']}")
                print(f"     Tipo: {candidato['tipo_principal']}")
                print(f"     Rating: {candidato['rating']}/5")
                print(f"     Score: {candidato['score_similitud']:.3f}")
                print()
        
        logger.info("✅ Pruebas del integrador completadas")
        
    except Exception as e:
        logger.error(f"❌ Error en pruebas: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 