import requests
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import locale

# Establecer la localización a español para obtener el nombre del mes en español
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

# Reemplaza con tu token de GitHub y el repositorio que estás utilizando
GITHUB_TOKEN = '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'
REPO_OWNER = 'gilito11'
REPO_NAME = 'BetterHealth4'

# Autenticación básica con el token
headers = {
    'Authorization': f'token {GITHUB_TOKEN}'
}

# URL para obtener los issues
url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues?state=all&per_page=100'

# Realizamos la solicitud GET a la API de GitHub
response = requests.get(url, headers=headers)
issues = response.json()

# Establece el rango de fechas para la semana deseada
today = datetime.now().date()
start_week = today - timedelta(days=today.weekday())  # Ajusta al inicio de la semana (lunes)
end_week = start_week + timedelta(days=6)  # Final de la semana (domingo)

# Calculamos el número de la semana
start_of_month = today.replace(day=1)  # Primer día del mes
week_number = (today - start_of_month).days // 7 + 1  # Calcula la semana del mes

# Obtén el nombre del mes en español
month_name = today.strftime('%B')  # Nombre completo del mes en español

# Contadores diarios para issues abiertas y cerradas
open_issues_count = np.zeros(7)
closed_issues_count = np.zeros(7)

# Procesa cada issue para contar abiertas y cerradas por día
for issue in issues:
    created_at = datetime.strptime(issue.get('created_at'), '%Y-%m-%dT%H:%M:%SZ').date()
    closed_at = issue.get('closed_at')
    if closed_at:
        closed_at = datetime.strptime(closed_at, '%Y-%m-%dT%H:%M:%SZ').date()

    if start_week <= created_at <= end_week:
        open_issues_count[(created_at - start_week).days] += 1

    if closed_at and start_week <= closed_at <= end_week:
        closed_issues_count[(closed_at - start_week).days] += 1

# Días de la semana para el eje x
days_of_week = [start_week + timedelta(days=i) for i in range(7)]

# Crear el gráfico
plt.figure(figsize=(10, 5))
plt.plot(days_of_week, open_issues_count, label='Issues Abiertas', color='blue')
plt.plot(days_of_week, closed_issues_count, label='Issues Cerradas', color='green')
plt.xlabel('Día de la Semana')
plt.ylabel('Cantidad de Issues')

# Título personalizado con el número de semana y el mes
plt.title(f'Progresión Semanal de Issues Abiertas y Cerradas - Semana {week_number} {month_name.capitalize()}')

plt.legend()
plt.grid(True)
plt.xticks(rotation=45)

# Ajustar los ticks del eje y para que solo muestren enteros
max_issues = max(max(open_issues_count), max(closed_issues_count))
plt.yticks(range(0, int(max_issues) + 1))

plt.tight_layout()
plt.show()
