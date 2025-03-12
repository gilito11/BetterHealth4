import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import locale
import os
import json
import sys
import calendar

# Establecer la localización a español para los nombres de mes
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    print("Advertencia: No se pudo configurar la localización es_ES.UTF-8")

# Definir un directorio de salida para los gráficos
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

# Leer el archivo issues.json generado por la acción de GitHub
issues_file = os.getenv('ISSUES_FILE', 'issues.json')
try:
    with open(issues_file, 'r') as file:
        issues = json.load(file)
except Exception as e:
    print(f"Error al leer el archivo de issues: {e}")
    sys.exit(1)

def week_of_month(fecha):
    return (fecha.day - 1) // 7 + 1

# Diccionarios para agrupar datos
open_issues_daily = {}
closed_issues_daily = {}
open_issues_monthly = {}
closed_issues_monthly = {}
open_issues_weekly = {}
closed_issues_weekly = {}

# Procesar issues
for issue in issues:
    created_at_str = issue.get('created_at')
    if created_at_str:
        created_at = datetime.strptime(created_at_str, '%Y-%m-%dT%H:%M:%SZ').date()
        open_issues_daily[created_at] = open_issues_daily.get(created_at, 0) + 1
        month_key = created_at.strftime('%Y-%m')
        open_issues_monthly[month_key] = open_issues_monthly.get(month_key, 0) + 1
        semana = week_of_month(created_at)
        week_key = f"{created_at.year}-{created_at.month}-S{semana}"
        open_issues_weekly[week_key] = open_issues_weekly.get(week_key, 0) + 1
    
    closed_at_str = issue.get('closed_at')
    if closed_at_str:
        closed_at = datetime.strptime(closed_at_str, '%Y-%m-%dT%H:%M:%SZ').date()
        closed_issues_daily[closed_at] = closed_issues_daily.get(closed_at, 0) + 1
        month_key_closed = closed_at.strftime('%Y-%m')
        closed_issues_monthly[month_key_closed] = closed_issues_monthly.get(month_key_closed, 0) + 1
        semana_closed = week_of_month(closed_at)
        week_key_closed = f"{closed_at.year}-{closed_at.month}-S{semana_closed}"
        closed_issues_weekly[week_key_closed] = closed_issues_weekly.get(week_key_closed, 0) + 1

fecha_actual = datetime.now()
fecha_str = fecha_actual.strftime('%Y-%m-%d')

# GRÁFICO GLOBAL (Mensual consolidado)
plt.figure()
meses = sorted(open_issues_monthly.keys())
open_monthly = [open_issues_monthly.get(mes, 0) for mes in meses]
closed_monthly = [closed_issues_monthly.get(mes, 0) for mes in meses]
nombres_meses = [datetime.strptime(mes, '%Y-%m').strftime('%b %Y') for mes in meses]
plt.plot(nombres_meses, open_monthly, label='Issues Abiertas', marker='o', linestyle='-')
plt.plot(nombres_meses, closed_monthly, label='Issues Cerradas', marker='s', linestyle='-')
plt.xlabel('Mes')
plt.ylabel('Cantidad de Issues')
plt.title('Estadísticas Globales de Issues')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, f'grafico_global_{fecha_str}.png'), dpi=300)
plt.close()

# GRÁFICOS MENSUALES POR SEMANA
for mes in meses:
    plt.figure()
    semanas_mes = [f"{mes}-S{s}" for s in range(1, 6)]
    open_semanal = [open_issues_weekly.get(semana, 0) for semana in semanas_mes]
    closed_semanal = [closed_issues_weekly.get(semana, 0) for semana in semanas_mes]
    etiquetas_semanas = [f"Semana {s}" for s in range(1, 6)]
    plt.plot(etiquetas_semanas, open_semanal, label='Issues Abiertas', marker='o', linestyle='-')
    plt.plot(etiquetas_semanas, closed_semanal, label='Issues Cerradas', marker='s', linestyle='-')
    plt.xlabel('Semana')
    plt.ylabel('Cantidad de Issues')
    plt.title(f'Issues en {datetime.strptime(mes, "%Y-%m").strftime("%B %Y")} por Semana')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'grafico_mensual_{mes}.png'), dpi=300)
    plt.close()

# GRÁFICO SEMANAL (Última semana)
start_week = fecha_actual.date() - timedelta(days=fecha_actual.weekday())
dias_semana = [start_week + timedelta(days=i) for i in range(7)]
open_weekly = [open_issues_daily.get(dia, 0) for dia in dias_semana]
closed_weekly = [closed_issues_daily.get(dia, 0) for dia in dias_semana]
etiquetas_dias = [dia.strftime('%a %d/%m') for dia in dias_semana]
plt.figure()
plt.plot(etiquetas_dias, open_weekly, label='Issues Abiertas', marker='o', linestyle='-')
plt.plot(etiquetas_dias, closed_weekly, label='Issues Cerradas', marker='s', linestyle='-')
plt.xlabel('Día de la Semana')
plt.ylabel('Cantidad de Issues')
plt.title('Progresión Semanal de Issues')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, f'grafico_semanal_{fecha_str}.png'), dpi=300)
plt.close()

# Verificación de archivos generados
print(f"Archivos generados en {output_dir}: {os.listdir(output_dir)}")
