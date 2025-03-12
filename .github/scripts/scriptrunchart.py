import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import locale
import os
import json

# Establecer la localización a español para los nombres de mes
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

# Definir un directorio de salida para los gráficos
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

# Leer el archivo issues.json generado por la acción de GitHub
issues_file = os.getenv('ISSUES_FILE', 'issues.json')
with open(issues_file, 'r') as file:
    issues = json.load(file)

def week_of_month(fecha):
    return (fecha.day - 1) // 7 + 1

# Diccionarios para agrupar datos
open_issues_daily = {}
closed_issues_daily = {}
open_issues_monthly = {}
closed_issues_monthly = {}
open_issues_weekly_custom = {}
closed_issues_weekly_custom = {}

# Procesar issues
for issue in issues:
    created_at_str = issue.get('created_at')
    if created_at_str:
        created_at = datetime.strptime(created_at_str, '%Y-%m-%dT%H:%M:%SZ').date()
        open_issues_daily[created_at] = open_issues_daily.get(created_at, 0) + 1
        month_key = created_at.strftime('%Y-%m')
        open_issues_monthly[month_key] = open_issues_monthly.get(month_key, 0) + 1
        key_custom = (created_at.year, created_at.month, week_of_month(created_at))
        open_issues_weekly_custom[key_custom] = open_issues_weekly_custom.get(key_custom, 0) + 1
    
    closed_at_str = issue.get('closed_at')
    if closed_at_str:
        closed_at = datetime.strptime(closed_at_str, '%Y-%m-%dT%H:%M:%SZ').date()
        closed_issues_daily[closed_at] = closed_issues_daily.get(closed_at, 0) + 1
        month_key_closed = closed_at.strftime('%Y-%m')
        closed_issues_monthly[month_key_closed] = closed_issues_monthly.get(month_key_closed, 0) + 1
        key_custom_closed = (closed_at.year, closed_at.month, week_of_month(closed_at))
        closed_issues_weekly_custom[key_custom_closed] = closed_issues_weekly_custom.get(key_custom_closed, 0) + 1

# Semana actual
fecha_actual = datetime.now()
start_week = fecha_actual.date() - timedelta(days=fecha_actual.weekday())
dias_semana = [start_week + timedelta(days=i) for i in range(7)]
open_weekly = [open_issues_daily.get(dia, 0) for dia in dias_semana]
closed_weekly = [closed_issues_daily.get(dia, 0) for dia in dias_semana]
fecha_str = fecha_actual.strftime('%Y-%m-%d')

# Gráfico semanal
plt.figure(figsize=(10, 5))
plt.plot(dias_semana, open_weekly, label='Issues Abiertas', color='blue')
plt.plot(dias_semana, closed_weekly, label='Issues Cerradas', color='green')
plt.xlabel('Día de la Semana')
plt.ylabel('Cantidad de Issues')
plt.title('Progresión Semanal')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f'{output_dir}/grafico_semanal_{fecha_str}.png')
plt.close()

# Verificar que los archivos fueron generados
print("Archivos generados en:", os.listdir(output_dir))
