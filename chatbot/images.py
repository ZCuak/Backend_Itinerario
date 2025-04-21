import requests

def sugerir_lugar(nombre_lugar, api_key):
    url_autocomplete = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
    params_autocomplete = {
        'input': nombre_lugar,
        'types': 'geocode',  # puedes usar 'establishment' si prefieres solo negocios
        'key': api_key
    }
    respuesta = requests.get(url_autocomplete, params=params_autocomplete)
    data = respuesta.json()

    if data.get('predictions'):
        return data['predictions'][0]['description']
    return None

def buscar_lugares_relacionados(nombre_lugar, api_key):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"{nombre_lugar} playa OR turismo OR atracción",
        "key": api_key
    }
    r = requests.get(url, params=params).json()
    resultados = r.get('results', [])

    # Filtrar solo los bien valorados
    lugares_filtrados = [
        lugar for lugar in resultados
        if lugar.get('rating', 0) >= 4.0 and lugar.get('user_ratings_total', 0) >= 30 and 'photos' in lugar
    ]

    # Ordenar por rating y cantidad de reseñas
    lugares_ordenados = sorted(
        lugares_filtrados,
        key=lambda x: (x['rating'], x['user_ratings_total']),
        reverse=True
    )
    return lugares_ordenados

def obtener_fotos_lugar_mejoradas(nombre_lugar, api_key, max_fotos=5):
    # Buscar el lugar original
    url_busqueda = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params_busqueda = {
        'input': nombre_lugar,
        'inputtype': 'textquery',
        'fields': 'place_id',
        'key': api_key
    }
    resp_busqueda = requests.get(url_busqueda, params=params_busqueda).json()

    if not resp_busqueda.get('candidates'):
        sugerido = sugerir_lugar(nombre_lugar, api_key)
        if sugerido:
            print(f"⚠️ No se encontró '{nombre_lugar}'. Usando sugerencia: '{sugerido}'")
            return obtener_fotos_lugar_mejoradas(sugerido, api_key, max_fotos)
        else:
            print("❌ No se encontró el lugar ni sugerencias.")
            return []

    place_id = resp_busqueda['candidates'][0]['place_id']

    # Detalles del lugar
    url_detalles = "https://maps.googleapis.com/maps/api/place/details/json"
    params_detalles = {
        'place_id': place_id,
        'fields': 'photo,rating,user_ratings_total',
        'key': api_key
    }
    datos = requests.get(url_detalles, params=params_detalles).json()
    result = datos.get('result', {})

    if result.get('rating', 0) >= 4.0 and result.get('user_ratings_total', 0) >= 30:
        fotos = result.get('photos', [])
        fotos_ordenadas = sorted(fotos, key=lambda x: x.get('width', 0), reverse=True)
        return [
            f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={foto['photo_reference']}&key={api_key}"
            for foto in fotos_ordenadas[:max_fotos]
        ]
    else:
        print("⚠️ Lugar con baja calificación o pocas reseñas. Buscando lugares cercanos destacados...")
        lugares_populares = buscar_lugares_relacionados(nombre_lugar, api_key)

        urls_fotos = []
        for lugar in lugares_populares:
            for foto in lugar.get('photos', [])[:1]:  # solo 1 foto por lugar para diversidad
                url_foto = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={foto['photo_reference']}&key={api_key}"
                urls_fotos.append(url_foto)
                if len(urls_fotos) >= max_fotos:
                    return urls_fotos
        return urls_fotos

# Ejemplo de uso
api_key = ''
nombre_lugar = 'Pimentel'  # error de escritura
imagenes = obtener_fotos_lugar_mejoradas(nombre_lugar, api_key)
# for img in imagenes:
#     print(img)


