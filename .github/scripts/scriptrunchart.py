import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import locale
import os
import json
import sys

# Establecer la localización a español para los nombres de mes
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    print("Advertencia: No se pudo configurar la localización es_ES.UTF-8")

# Definir un directorio de salida para los gráficos
output_dir = 'output'
print(f"Creando directorio de salida: {output_dir}")
os.makedirs(output_dir, exist_ok=True)
print(f"¿Directorio '{output_dir}' existe? {os.path.exists(output_dir)}")

# Leer el archivo issues.json generado por la acción de GitHub
issues_file = os.getenv('ISSUES_FILE', 'issues.json')
print(f"Leyendo archivo de issues: {issues_file}")

try:
    with open(issues_file, 'r') as file:
        issues = json.load(file)
    print(f"Se cargaron {len(issues)} issues")
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

fecha_actual = datetime.now()
fecha_str = fecha_actual.strftime('%Y-%m-%d')

# Configuración común para todos los gráficos
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7

# GRÁFICO 1: Gráfico semanal (lineal con puntos)
print("Generando gráfico 1: Progresión Semanal de Issues")
start_week = fecha_actual.date() - timedelta(days=fecha_actual.weekday())
dias_semana = [start_week + timedelta(days=i) for i in range(7)]
open_weekly = [open_issues_daily.get(dia, 0) for dia in dias_semana]
closed_weekly = [closed_issues_daily.get(dia, 0) for dia in dias_semana]

# Convertir fechas a etiquetas para el eje X
etiquetas_dias = [dia.strftime('%a %d/%m') for dia in dias_semana]

plt.figure()
plt.plot(range(len(dias_semana)), open_weekly, label='Issues Abiertas', color='blue', marker='o', linestyle='-', linewidth=2)
plt.plot(range(len(dias_semana)), closed_weekly, label='Issues Cerradas', color='green', marker='s', linestyle='-', linewidth=2)
plt.xlabel('Día de la Semana')
plt.ylabel('Cantidad de Issues')
plt.title('Progresión Semanal de Issues')
plt.legend()
plt.xticks(range(len(dias_semana)), etiquetas_dias, rotation=45)
plt.tight_layout()

output_path = os.path.join(output_dir, f'grafico_semanal_{fecha_str}.png')
print(f"Guardando gráfico en: {output_path}")
plt.savefig(output_path, dpi=300)
print(f"¿El archivo fue creado? {os.path.exists(output_path)}")
plt.close()

# GRÁFICO 2: Gráfico mensual (últimos 6 meses) - ahora lineal con puntos
print("Generando gráfico 2: Estadísticas Mensuales de Issues")
meses = []
for i in range(5, -1, -1):
    fecha_mes = fecha_actual - timedelta(days=30*i)
    meses.append(fecha_mes.strftime('%Y-%m'))

open_monthly = [open_issues_monthly.get(mes, 0) for mes in meses]
closed_monthly = [closed_issues_monthly.get(mes, 0) for mes in meses]

# Nombres de meses en español
nombres_meses = []
for mes in meses:
    year, month = mes.split('-')
    fecha = datetime(int(year), int(month), 1)
    nombres_meses.append(fecha.strftime('%b %Y'))

plt.figure()
plt.plot(range(len(meses)), open_monthly, label='Issues Abiertas', color='blue', marker='o', linestyle='-', linewidth=2)
plt.plot(range(len(meses)), closed_monthly, label='Issues Cerradas', color='green', marker='s', linestyle='-', linewidth=2)
plt.xlabel('Mes')
plt.ylabel('Cantidad de Issues')
plt.title('Estadísticas Mensuales de Issues')
plt.legend()
plt.xticks(range(len(meses)), nombres_meses, rotation=45)
plt.tight_layout()

output_path = os.path.join(output_dir, f'grafico_mensual_{fecha_str}.png')
print(f"Guardando gráfico mensual en: {output_path}")
plt.savefig(output_path, dpi=300)
print(f"¿El archivo fue creado? {os.path.exists(output_path)}")
plt.close()

# GRÁFICO 3: Run Chart acumulativo (tendencia de issues a lo largo del tiempo)
print("Generando gráfico 3: Run Chart de Issues Acumulados")
# Obtener un rango de fechas para el período de análisis (últimos 30 días)
fecha_inicio = fecha_actual.date() - timedelta(days=30)
fechas = [fecha_inicio + timedelta(days=i) for i in range(31)]

# Calcular issues acumulados
open_acumulados = []
closed_acumulados = []
total_open = 0
total_closed = 0

for fecha in fechas:
    total_open += open_issues_daily.get(fecha, 0)
    total_closed += closed_issues_daily.get(fecha, 0)
    open_acumulados.append(total_open)
    closed_acumulados.append(total_closed)

# Convertir fechas a etiquetas para el eje X
etiquetas_fechas = [fecha.strftime('%d/%m') for fecha in fechas]
indices_mostrar = [0, 10, 20, 30] if len(fechas) > 30 else list(range(len(fechas)))

plt.figure()
plt.plot(range(len(fechas)), open_acumulados, label='Issues Abiertas Acumuladas', color='blue', marker='o', linestyle='-', linewidth=2, markevery=5)
plt.plot(range(len(fechas)), closed_acumulados, label='Issues Cerradas Acumuladas', color='green', marker='s', linestyle='-', linewidth=2, markevery=5)

# Añadir línea de referencia (media)
media_open = sum(open_acumulados) / len(open_acumulados)
media_closed = sum(closed_acumulados) / len(closed_acumulados)
plt.axhline(y=media_open, color='blue', linestyle='--', alpha=0.5, label='Media Issues Abiertas')
plt.axhline(y=media_closed, color='green', linestyle='--', alpha=0.5, label='Media Issues Cerradas')

plt.xlabel('Fecha')
plt.ylabel('Cantidad Acumulada de Issues')
plt.title('Run Chart: Tendencia de Issues en los Últimos 30 Días')
plt.legend()
plt.xticks([i for i in indices_mostrar], [etiquetas_fechas[i] for i in indices_mostrar], rotation=45)
plt.tight_layout()

output_path = os.path.join(output_dir, f'runchart_issues_{fecha_str}.png')
print(f"Guardando run chart en: {output_path}")
plt.savefig(output_path, dpi=300)
print(f"¿El archivo fue creado? {os.path.exists(output_path)}")
plt.close()

# Verificar que los archivos fueron generados
archivos_generados = os.listdir(output_dir)
print(f"Archivos generados en {output_dir}:", archivos_generados)
print(f"Total de archivos generados: {len(archivos_generados)}")
