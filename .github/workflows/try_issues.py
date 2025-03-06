import requests
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import os

# Obtener token desde el entorno (correcto en GitHub Actions)
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_OWNER = 'gilito11'
REPO_NAME = 'BetterHealth4'

# Autenticación usando el token
headers = {
    'Authorization': f'token {GITHUB_TOKEN}'
}

# Endpoint de GitHub API para obtener issues
url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues?state=all&per_page=100'

# Request a la API de GitHub
response = requests.get(url, headers=headers)
response.raise_for_status()  # Por si falla la request
issues = response.json()

# Fechas de inicio y fin de la semana actual
today = datetime.now().date()
start_week = today - timedelta(days=today.weekday())  # lunes
end_week = start_week + timedelta(days=6)  # domingo

# Calcular número de semana y nombre del mes (manual en español)
meses_es = [
    'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
]
week_number = (today.day - 1) // 7 + 1
month_name = meses_es[today.month - 1]

# Arrays para contar issues abiertas/cerradas por día
open_issues_count = np.zeros(7)
closed_issues_count = np.zeros(7)

# Procesar cada issue y ver en qué día de la semana cae
for issue in issues:
    created_at = datetime.strptime(issue['created_at'], '%Y-%m-%dT%H:%M:%SZ').date()
    closed_at = issue.get('closed_at')
    if closed_at:
        closed_at = datetime.strptime(closed_at, '%Y-%m-%dT%H:%M:%SZ').date()

    if start_week <= created_at <= end_week:
        open_issues_count[(created_at - start_week).days] += 1

    if closed_at and start_week <= closed_at <= end_week:
        closed_issues_count[(closed_at - start_week).days] += 1

# Días de la semana en formato fecha
days_of_week = [start_week + timedelta(days=i) for i in range(7)]

# Crear gráfico
plt.figure(figsize=(10, 5))
plt.plot(days_of_week, open_issues_count, label='Issues Abiertas', color='blue')
plt.plot(days_of_week, closed_issues_count, label='Issues Cerradas', color='green')
plt.xlabel('Día de la Semana')
plt.ylabel('Cantidad de Issues')

# Título con número de semana y mes
plt.title(f'Progresión Semanal de Issues - Semana {week_number} de {month_name.capitalize()}')

plt.legend()
plt.grid(True)
plt.xticks(rotation=45)

# Ajustar eje Y para mostrar solo enteros
max_issues = max(max(open_issues_count), max(closed_issues_count))
plt.yticks(range(0, int(max_issues) + 1))

plt.tight_layout()

# Guardar el gráfico como PDF (para el commit/push)
plt.savefig('grafico_issues_semanal.pdf')

print("✅ Gráfico generado correctamente: grafico_issues_semanal.pdf")
