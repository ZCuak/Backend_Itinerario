import os
import requests
import re
import json

API_KEY = os.getenv("API_KEY_OPENAI")
API_URL = "https://api.deepseek.com/v1/chat/completions"

class DeepSeekClient:
    """
    Cliente para interactuar con la API de DeepSeek
    """
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("API_KEY_OPENAI")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    def generate_response(self, prompt: str, temperature: float = 0.3) -> str:
        """
        Genera una respuesta usando DeepSeek
        
        Args:
            prompt: El prompt a enviar
            temperature: Temperatura para la generación (0.0-1.0)
        
        Returns:
            La respuesta generada
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature
            }

            response = requests.post(self.api_url, headers=headers, json=data)

            if response.status_code == 200:
                respuesta = response.json()
                return respuesta['choices'][0]['message']['content']
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error en DeepSeekClient: {e}")
            return None

def enviar_prompt(prompt_usuario):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt_usuario}],
        "temperature": 0.3  # Reducir temperatura para respuestas más consistentes
    }

    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code == 200:
        respuesta = response.json()
        return respuesta['choices'][0]['message']['content']
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def limpiar_texto(texto):
    """
    Limpia el texto eliminando emojis y caracteres especiales problemáticos.
    """
    if not texto:
        return texto
    
    # Eliminar emojis y caracteres Unicode problemáticos
    texto_limpio = re.sub(r'[^\x00-\x7F\u00A0-\u00FF\u0100-\u017F\u0180-\u024F\u1E00-\u1EFF\u2C60-\u2C7F\uA720-\uA7FF]+', '', texto)
    
    # Eliminar caracteres de control excepto saltos de línea y tabulaciones
    texto_limpio = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', texto_limpio)
    
    # Normalizar espacios múltiples
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio)
    
    # Eliminar espacios al inicio y final
    texto_limpio = texto_limpio.strip()
    
    return texto_limpio

def generar_resumen_lugar(lugar_data):
    """
    Genera un resumen por IA para un lugar específico usando DeepSeek.
    
    Args:
        lugar_data (dict): Datos del lugar incluyendo nombre, descripción, rating, etc.
    
    Returns:
        str: Resumen generado por IA o None si hay error
    """
    try:
        # Construir el prompt para DeepSeek
        prompt = f"""
        Eres un experto en turismo y viajes. Necesito que generes un resumen atractivo y útil para un lugar turístico.

        IMPORTANTE: Responde SOLO con texto plano en español. NO uses emojis, símbolos especiales, caracteres Unicode, ni formato HTML. Usa solo letras, números, puntos, comas y espacios.

        Información del lugar:
        - Nombre: {lugar_data.get('nombre', 'N/A')}
        - Dirección: {lugar_data.get('direccion', 'N/A')}
        - Categoría: {lugar_data.get('categoria', 'N/A')}
        - Tipo principal: {lugar_data.get('tipo_principal', 'N/A')}
        - Rating: {lugar_data.get('rating', 0)}/5 ({lugar_data.get('total_ratings', 0)} reseñas)
        - Nivel de precios: {lugar_data.get('nivel_precios', 'N/A')}
        - Descripción original: {lugar_data.get('descripcion', 'Sin descripción disponible')}
        - Horarios: {lugar_data.get('horarios', [])}
        - Website: {lugar_data.get('website', 'No disponible')}
        - Teléfono: {lugar_data.get('telefono', 'No disponible')}

        Genera un resumen que incluya:
        1. Una descripción general del lugar (2-3 oraciones)
        2. Qué tipo de experiencia ofrece
        3. Por qué vale la pena visitarlo
        4. Información práctica (horarios, precios, contacto)
        5. Recomendaciones para visitantes

        El resumen debe ser:
        - Atractivo y persuasivo
        - Informativo y útil
        - Escrito en español
        - Máximo 200 palabras
        - Con un tono amigable y profesional
        - SOLO texto plano, sin emojis ni caracteres especiales

        Resumen:
        """
        
        # Enviar el prompt a DeepSeek
        resumen = enviar_prompt(prompt)
        
        if resumen:
            # Limpiar el texto de emojis y caracteres problemáticos
            resumen_limpio = limpiar_texto(resumen)
            return resumen_limpio.strip()
        else:
            return None
            
    except Exception as e:
        print(f"Error al generar resumen para {lugar_data.get('nombre', 'lugar desconocido')}: {str(e)}")
        return None

def generar_resumenes_lotes(lugares_data, max_lotes=5):
    """
    Genera resúmenes para múltiples lugares en lotes para evitar sobrecarga de la API.
    
    Args:
        lugares_data (list): Lista de diccionarios con datos de lugares
        max_lotes (int): Número máximo de lugares a procesar por lote
    
    Returns:
        dict: Diccionario con los resúmenes generados por lugar_id
    """
    resumenes = {}
    
    for i in range(0, len(lugares_data), max_lotes):
        lote = lugares_data[i:i + max_lotes]
        print(f"Procesando lote {i//max_lotes + 1} de {(len(lugares_data) + max_lotes - 1) // max_lotes}")
        
        for lugar in lote:
            lugar_id = lugar.get('id')
            if lugar_id:
                resumen = generar_resumen_lugar(lugar)
                if resumen:
                    resumenes[lugar_id] = resumen
                    print(f"Resumen generado para: {lugar.get('nombre', 'Lugar desconocido')}")
                else:
                    print(f"Error al generar resumen para: {lugar.get('nombre', 'Lugar desconocido')}")
        
        # Pausa entre lotes para evitar límites de rate
        if i + max_lotes < len(lugares_data):
            import time
            time.sleep(2)
    
    return resumenes

def extraer_caracteristicas_lugar(lugar_data):
    """
    Extrae características específicas de un lugar usando DeepSeek.
    
    Args:
        lugar_data (dict): Datos del lugar incluyendo nombre, descripción, resumen IA, etc.
    
    Returns:
        dict: Diccionario con características extraídas
    """
    try:
        # Construir el prompt para DeepSeek
        prompt = f"""
        Eres un experto en análisis de establecimientos turísticos. Necesito que extraigas las características específicas de un lugar.

        IMPORTANTE: Responde SOLO con un JSON válido. NO uses texto adicional, emojis ni explicaciones.

        Información del lugar:
        - Nombre: {lugar_data.get('nombre', 'N/A')}
        - Tipo: {lugar_data.get('tipo_principal', 'N/A')}
        - Descripción: {lugar_data.get('descripcion', 'N/A')}
        - Resumen IA: {lugar_data.get('resumen_ia', 'N/A')}
        - Rating: {lugar_data.get('rating', 0)}/5
        - Nivel de precios: {lugar_data.get('nivel_precios', 'N/A')}

        Extrae las siguientes características y responde con un JSON que contenga:

        {{
            "amenidades": ["lista de amenidades como piscina, gimnasio, wifi, etc."],
            "servicios": ["lista de servicios como restaurante, bar, spa, etc."],
            "caracteristicas_especiales": ["características únicas o destacadas"],
            "tipo_experiencia": "tipo de experiencia que ofrece (ej: familiar, romántico, de negocios)",
            "nivel_lujo": "nivel de lujo (económico, moderado, lujoso, premium)",
            "horario_servicio": "tipo de horario (24h, diurno, nocturno)",
            "publico_objetivo": ["tipos de público objetivo"],
            "palabras_clave": ["palabras clave para búsquedas semánticas"]
        }}

        Reglas importantes:
        1. Solo incluye características que se mencionen EXPLÍCITAMENTE en la información
        2. Para amenidades, incluye solo instalaciones físicas (piscina, gimnasio, spa, etc.)
        3. Para servicios, incluye servicios ofrecidos (restaurante, bar, room service, etc.)
        4. Las palabras clave deben ser términos que un usuario usaría para buscar este lugar
        5. Si no hay información sobre una categoría, usa array vacío []
        6. Responde SOLO con el JSON, sin texto adicional

        JSON:
        """
        
        # Enviar el prompt a DeepSeek
        respuesta = enviar_prompt(prompt)
        
        if respuesta:
            # Limpiar la respuesta
            respuesta_limpia = limpiar_texto(respuesta)
            
            # Intentar parsear el JSON
            try:
                # Buscar el JSON en la respuesta (por si hay texto adicional)
                json_match = re.search(r'\{.*\}', respuesta_limpia, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    caracteristicas = json.loads(json_str)
                    
                    # Validar que tenga la estructura esperada
                    estructura_esperada = {
                        "amenidades": [],
                        "servicios": [],
                        "caracteristicas_especiales": [],
                        "tipo_experiencia": "",
                        "nivel_lujo": "",
                        "horario_servicio": "",
                        "publico_objetivo": [],
                        "palabras_clave": []
                    }
                    
                    # Asegurar que todas las claves existan
                    for key in estructura_esperada:
                        if key not in caracteristicas:
                            caracteristicas[key] = estructura_esperada[key]
                    
                    print(f"✅ Características extraídas para {lugar_data.get('nombre', 'N/A')}: {len(caracteristicas.get('amenidades', []))} amenidades")
                    return caracteristicas
                else:
                    print(f"❌ No se encontró JSON válido en la respuesta para {lugar_data.get('nombre', 'N/A')}")
                    return None
                    
            except json.JSONDecodeError as e:
                print(f"❌ Error al parsear JSON para {lugar_data.get('nombre', 'N/A')}: {e}")
                print(f"Respuesta recibida: {respuesta_limpia[:200]}...")
                return None
        else:
            print(f"❌ No se recibió respuesta de DeepSeek para {lugar_data.get('nombre', 'N/A')}")
            return None
            
    except Exception as e:
        print(f"❌ Error al extraer características para {lugar_data.get('nombre', 'lugar desconocido')}: {str(e)}")
        return None

def extraer_caracteristicas_lotes(lugares_data, max_lotes=3):
    """
    Extrae características para múltiples lugares en lotes.
    
    Args:
        lugares_data (list): Lista de diccionarios con datos de lugares
        max_lotes (int): Número máximo de lugares a procesar por lote
    
    Returns:
        dict: Diccionario con las características extraídas por lugar_id
    """
    caracteristicas = {}
    
    for i in range(0, len(lugares_data), max_lotes):
        lote = lugares_data[i:i + max_lotes]
        print(f"🔍 Procesando lote {i//max_lotes + 1} de {(len(lugares_data) + max_lotes - 1) // max_lotes}")
        
        for lugar in lote:
            lugar_id = lugar.get('id')
            if lugar_id:
                caracteristicas_lugar = extraer_caracteristicas_lugar(lugar)
                if caracteristicas_lugar:
                    caracteristicas[lugar_id] = caracteristicas_lugar
                    print(f"✅ Características extraídas para: {lugar.get('nombre', 'Lugar desconocido')}")
                else:
                    print(f"❌ Error al extraer características para: {lugar.get('nombre', 'Lugar desconocido')}")
        
        # Pausa entre lotes para evitar límites de rate
        if i + max_lotes < len(lugares_data):
            import time
            time.sleep(3)  # Pausa más larga para evitar límites
    
    return caracteristicas

def extraer_palabras_clave_resumen(resumen_ia: str) -> str:
    """
    Extrae palabras clave del resumen IA para embeddings eficientes.
    
    Args:
        resumen_ia (str): Resumen IA completo
        
    Returns:
        str: Palabras clave separadas por comas (máximo 50-100 palabras)
    """
    try:
        if not resumen_ia or not resumen_ia.strip():
            return ""
        
        prompt = f"""
        Eres un experto en extracción de palabras clave para búsquedas semánticas.
        
        Extrae las palabras clave más importantes del siguiente resumen de un lugar turístico.
        Las palabras clave deben ser términos que un usuario usaría para buscar este lugar.
        
        RESUMEN: {resumen_ia}
        
        REGLAS IMPORTANTES:
        1. Extrae solo las palabras clave más relevantes (máximo 50-100 palabras)
        2. Incluye características físicas, servicios, ambiente, público objetivo
        3. Usa términos específicos y descriptivos
        4. Incluye sinónimos y términos relacionados
        5. Separa las palabras clave con comas
        6. NO uses frases largas, solo palabras o términos cortos
        7. Enfócate en términos que ayuden a encontrar el lugar
        
        EJEMPLOS DE PALABRAS CLAVE:
        - Para hoteles: lujo, piscina, spa, gimnasio, restaurante, bar, wifi, familia, romántico, negocios
        - Para restaurantes: gourmet, italiano, romántico, familiar, terraza, música, vegetariano
        - Para bares: música en vivo, cocteles, fiesta, terraza, deportes, karaoke
        
        Palabras clave extraídas:
        """
        
        # Enviar el prompt a DeepSeek
        respuesta = enviar_prompt(prompt)
        
        if respuesta:
            # Limpiar y formatear la respuesta
            palabras_clave = limpiar_texto(respuesta)
            
            # Asegurar que no exceda un límite razonable
            palabras = [palabra.strip() for palabra in palabras_clave.split(',') if palabra.strip()]
            palabras_clave_final = ', '.join(palabras[:100])  # Máximo 100 palabras
            
            return palabras_clave_final.strip()
        else:
            return ""
            
    except Exception as e:
        print(f"Error al extraer palabras clave: {str(e)}")
        return ""

def extraer_palabras_clave_lotes(resumenes_data: list, max_lotes: int = 10) -> dict:
    """
    Extrae palabras clave para múltiples resúmenes en lotes.
    
    Args:
        resumenes_data: Lista de diccionarios con 'id' y 'resumen_ia'
        max_lotes: Número máximo de resúmenes a procesar por lote
    
    Returns:
        dict: Diccionario con las palabras clave extraídas por lugar_id
    """
    palabras_clave = {}
    
    for i in range(0, len(resumenes_data), max_lotes):
        lote = resumenes_data[i:i + max_lotes]
        print(f"🔍 Procesando lote {i//max_lotes + 1} de {(len(resumenes_data) + max_lotes - 1) // max_lotes}")
        
        for item in lote:
            lugar_id = item.get('id')
            resumen_ia = item.get('resumen_ia', '')
            
            if lugar_id and resumen_ia:
                palabras_clave_texto = extraer_palabras_clave_resumen(resumen_ia)
                if palabras_clave_texto:
                    palabras_clave[lugar_id] = palabras_clave_texto
                    print(f"✅ Palabras clave extraídas para lugar {lugar_id}: {len(palabras_clave_texto.split(','))} términos")
                else:
                    print(f"⚠️ No se pudieron extraer palabras clave para lugar {lugar_id}")
        
        # Pausa entre lotes para evitar límites de rate
        if i + max_lotes < len(resumenes_data):
            import time
            time.sleep(2)
    
    return palabras_clave
