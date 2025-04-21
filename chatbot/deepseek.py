# deepseek.py
import requests

API_KEY = "sk-2ce16076392141bf9f3e0b4a0524920c"
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
