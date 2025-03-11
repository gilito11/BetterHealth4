import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import locale

# Establecer la localización a español para los nombres de mes
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

# Datos del repositorio público
REPO_OWNER = 'gilito11'
REPO_NAME = 'BetterHealth4'
url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues?state=all&per_page=100'

# Solicitud GET a la API de GitHub
response = requests.get(url)
issues = response.json()

# --- Función auxiliar para calcular la semana del mes ---
def week_of_month(fecha):
    # Calcula la semana del mes de forma sencilla: (día - 1) // 7 + 1
    return (fecha.day - 1) // 7 + 1

# --- Inicialización de diccionarios para agrupar datos ---
# Para el gráfico Weekly (por día)
open_issues_daily = {}
closed_issues_daily = {}

# Global: agrupado por mes (clave: "YYYY-MM")
open_issues_monthly = {}
closed_issues_monthly = {}

# Global: agrupado por semana, pero con etiqueta "Week X - Month"
# Usaremos como clave una tupla: (año, mes, semana_del_mes)
open_issues_weekly_custom = {}
closed_issues_weekly_custom = {}

# --- Procesamiento de cada issue ---
for issue in issues:
    # Procesar la fecha de creación
    created_at_str = issue.get('created_at')
    if created_at_str:
        created_at = datetime.strptime(created_at_str, '%Y-%m-%dT%H:%M:%SZ').date()
        # Acumular por día
        open_issues_daily[created_at] = open_issues_daily.get(created_at, 0) + 1
        # Acumular por mes
        month_key = created_at.strftime('%Y-%m')
        open_issues_monthly[month_key] = open_issues_monthly.get(month_key, 0) + 1
        # Acumular por semana (custom)
        key_custom = (created_at.year, created_at.month, week_of_month(created_at))
        open_issues_weekly_custom[key_custom] = open_issues_weekly_custom.get(key_custom, 0) + 1

    # Procesar la fecha de cierre
    closed_at_str = issue.get('closed_at')
    if closed_at_str:
        closed_at = datetime.strptime(closed_at_str, '%Y-%m-%dT%H:%M:%SZ').date()
        # Acumular por día
        closed_issues_daily[closed_at] = closed_issues_daily.get(closed_at, 0) + 1
        # Acumular por mes
        month_key_closed = closed_at.strftime('%Y-%m')
        closed_issues_monthly[month_key_closed] = closed_issues_monthly.get(month_key_closed, 0) + 1
        # Acumular por semana (custom)
        key_custom_closed = (closed_at.year, closed_at.month, week_of_month(closed_at))
        closed_issues_weekly_custom[key_custom_closed] = closed_issues_weekly_custom.get(key_custom_closed, 0) + 1

# ========================
# 1. Gráfico Weekly (Semana Actual)
# ========================
today = datetime.now().date()
start_week = today - timedelta(days=today.weekday())  # Lunes de la semana actual
dias_semana = [start_week + timedelta(days=i) for i in range(7)]
open_weekly = [open_issues_daily.get(dia, 0) for dia in dias_semana]
closed_weekly = [closed_issues_daily.get(dia, 0) for dia in dias_semana]

# Para el título: semana del mes y nombre del mes
start_of_month = today.replace(day=1)
week_number = (today - start_of_month).days // 7 + 1
month_name = today.strftime('%B').capitalize()

fig1 = plt.figure(figsize=(10, 5))
plt.plot(dias_semana, open_weekly, label='Issues Abiertas', color='blue')
plt.plot(dias_semana, closed_weekly, label='Issues Cerradas', color='green')
plt.xlabel('Día de la Semana')
plt.ylabel('Cantidad de Issues')
plt.title(f'Progresión Semanal de Issues Abiertas y Cerradas - Semana {week_number} {month_name}')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('grafico_semanal.png')
plt.close(fig1)

# ========================
# 2. Gráfico Global (Dividido por Meses)
# ========================
meses = sorted(set(list(open_issues_monthly.keys()) + list(closed_issues_monthly.keys())))
open_monthly = [open_issues_monthly.get(mes, 0) for mes in meses]
closed_monthly = [closed_issues_monthly.get(mes, 0) for mes in meses]

fig2 = plt.figure(figsize=(10, 5))
plt.plot(meses, open_monthly, label='Issues Abiertas', color='blue')
plt.plot(meses, closed_monthly, label='Issues Cerradas', color='green')
plt.xlabel('Mes')
plt.ylabel('Cantidad de Issues')
plt.title('Progresión Global de Issues Abiertas y Cerradas (por Mes)')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('grafico_global_mensual.png')
plt.close(fig2)

# ========================
# 3. Gráfico Global (Dividido por Semanas con etiqueta "Week X - Month")
# ========================
# Obtenemos la unión de claves (tuplas: (año, mes, semana))
keys_custom = set(list(open_issues_weekly_custom.keys()) + list(closed_issues_weekly_custom.keys()))
# Ordenamos las claves por año, mes y semana
keys_custom = sorted(keys_custom, key=lambda k: (k[0], k[1], k[2]))

labels_custom = []
open_custom = []
closed_custom = []
for key in keys_custom:
    year, month, week = key
    # Obtenemos el nombre del mes usando la fecha del primer día del mes
    month_name_custom = datetime(year, month, 1).strftime('%B').capitalize()
    label = f"Week {week} - {month_name_custom}"
    labels_custom.append(label)
    open_custom.append(open_issues_weekly_custom.get(key, 0))
    closed_custom.append(closed_issues_weekly_custom.get(key, 0))

fig3 = plt.figure(figsize=(10, 5))
x_positions = range(len(labels_custom))
plt.plot(x_positions, open_custom, label='Issues Abiertas', color='blue', marker='o')
plt.plot(x_positions, closed_custom, label='Issues Cerradas', color='green', marker='o')
plt.xlabel('Semana')
plt.ylabel('Cantidad de Issues')
plt.title('Progresión Global de Issues Abiertas y Cerradas (por Semana)')
plt.xticks(x_positions, labels_custom, rotation=45)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('grafico_global_semanal.png')
plt.close(fig3)
