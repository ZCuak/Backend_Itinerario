import requests

def obtener_fotos_lugar(nombre_lugar, api_key):
    # Buscar el lugar y obtener su Place ID
    url_busqueda = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params_busqueda = {
        'input': nombre_lugar,
        'inputtype': 'textquery',
        'fields': 'place_id',
        'key': api_key
    }
    respuesta_busqueda = requests.get(url_busqueda, params=params_busqueda)
    datos_busqueda = respuesta_busqueda.json()

    if datos_busqueda.get('candidates'):
        place_id = datos_busqueda['candidates'][0]['place_id']

        # Obtener detalles del lugar, incluyendo fotos
        url_detalles = f"https://maps.googleapis.com/maps/api/place/details/json"
        params_detalles = {
            'place_id': place_id,
            'fields': 'photo',
            'key': api_key
        }
        respuesta_detalles = requests.get(url_detalles, params=params_detalles)
        datos_detalles = respuesta_detalles.json()

        fotos = datos_detalles.get('result', {}).get('photos', [])
        urls_fotos = []
        for foto in fotos:
            photo_reference = foto['photo_reference']
            url_foto = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo_reference}&key={api_key}"
            urls_fotos.append(url_foto)

        return urls_fotos
    else:
        print("No se encontró el lugar.")
        return []

# Ejemplo de uso
api_key = 'AIzaSyDWFyOlDVNw2A8Q9s07cCPMnAOA139egf0'
nombre_lugar = 'Las Pirkas'
imagenes = obtener_fotos_lugar(nombre_lugar, api_key)
# for img in imagenes:
#     print(img)
