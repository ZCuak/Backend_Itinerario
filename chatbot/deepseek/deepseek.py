import os
import requests
import re

API_KEY = os.getenv("API_KEY_OPENAI")
API_URL = "https://api.deepseek.com/v1/chat/completions"

def enviar_prompt(prompt_usuario):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt_usuario}],
        "temperature": 0.7
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
