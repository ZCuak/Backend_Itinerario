import os
import requests

API_KEY = os.getenv("API_KEY_OPENAI")
API_URL = "https://api.openai.com/v1/chat/completions"

def enviar_prompt(prompt_usuario):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-3.5-turbo",  # Puedes usar "gpt-3.5-turbo" si quieres ahorrar
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
