import requests
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Reemplaza con tu token de GitHub y el repositorio que estás utilizando
GITHUB_TOKEN = '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'
REPO_OWNER = 'gilito11'  # Ejemplo: 'octocat'
REPO_NAME = 'BetterHealth4'  # Ejemplo: 'Hello-World'

# Autenticación básica con el token
headers = {
    'Authorization': f'token {GITHUB_TOKEN}'
}

# URL para obtener los issues
url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues?state=all'

# Realizamos la solicitud GET a la API de GitHub
response = requests.get(url, headers=headers)
if response.status_code == 200:
    issues = response.json()
    print(f"Total de issues obtenidos: {len(issues)}")
    
    # Mostrar algunos datos de los issues
    for issue in issues[:5]:  # Mostrar solo los primeros 5 issues como ejemplo
        title = issue.get('title', 'No title')
        state = issue.get('state', 'No state')
        created_at = issue.get('created_at', 'No creation date')
        created_date = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ').date()
        print(f"Issue Title: {title}, State: {state}, Created At: {created_date}")
else:
    print(f"Error al obtener los issues. Código de respuesta: {response.status_code}")
