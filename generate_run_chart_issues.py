import requests
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Reemplaza con tu token de GitHub y el repositorio que estás utilizando
GITHUB_TOKEN = 'tu_token_aqui'
REPO_OWNER = 'nombre_del_owner_del_repositorio'  # Ejemplo: 'octocat'
REPO_NAME = 'nombre_del_repositorio'  # Ejemplo: 'Hello-World'

# Autenticación básica con el token
headers = {
    'Authorization': f'token {GITHUB_TOKEN}'
}

# URL para obtener los issues
url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues?state=all'

# Realizamos la solicitud GET a la API de GitHub
response = requests.get(url, headers=headers)
issues = response.json()

# Procesar los datos: contar issues abiertos y cerrados por fecha
open_dates = []
closed_dates = []

for issue in issues:
    if 'created_at' in issue:
        created_at = issue['created_at']
        created_date = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ').date()
        open_dates.append(created_date)
    
    if 'closed_at' in issue and issue['state'] == 'closed':
        closed_at = issue['closed_at']
        closed_date = datetime.strptime(closed_at, '%Y-%m-%dT%H:%M:%SZ').date()
        closed_dates.append(closed_date)

"""
# Agrupar los datos por fecha
open_count_by_date = {}
closed_count_by_date = {}

for date in open_dates:
    open_count_by_date[date] = open_count_by_date.get(date, 0) + 1

for date in closed_dates:
    closed_count_by_date[date] = closed_count_by_date.get(date, 0) + 1

# Ordenar las fechas
dates = sorted(set(open_count_by_date.keys()).union(set(closed_count_by_date.keys())))

# Preparar los datos para el gráfico
open_data = [open_count_by_date.get(date, 0) for date in dates]
closed_data = [closed_count_by_date.get(date, 0) for date in dates]

# Crear el gráfico
plt.figure(figsize=(10, 6))
plt.plot(dates, open_data, marker='o', linestyle='-', color='b', label='Issues abiertos')
plt.plot(dates, closed_data, marker='x', linestyle='-', color='g', label='Issues cerrados')

# Etiquetas y título
plt.title('Run Chart de Issues (Abiertos y Cerrados)')
plt.xlabel('Fecha')
plt.ylabel('Número de Issues')
plt.grid(True)
plt.legend()

# Guardar el gráfico como un archivo PNG
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('run_chart_issues.png', format='png')
plt.close()
"""
