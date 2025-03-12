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
        
        # Semana del mes
        semana = week_of_month(created_at)
        week_key = f"{created_at.year}-{created_at.month}-S{semana}"
        open_issues_weekly[week_key] = open_issues_weekly.get(week_key, 0) + 1
    
    closed_at_str = issue.get('closed_at')
    if closed_at_str:
        closed_at = datetime.strptime(closed_at_str, '%Y-%m-%dT%H:%M:%SZ').date()
        closed_issues_daily[closed_at] = closed_issues_daily.get(closed_at, 0) + 1
        month_key_closed = closed_at.strftime('%Y-%m')
        closed_issues_monthly[month_key_closed] = closed_issues_monthly.get(month_key_closed, 0) + 1
        
        # Semana del mes
        semana_closed = week_of_month(closed_at)
        week_key_closed = f"{closed_at.year}-{closed_at.month}-S{semana_closed}"
        closed_issues_weekly[week_key_closed] = closed_issues_weekly.get(week_key_closed, 0) + 1

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

# GRÁFICO 3: Run Chart por semanas del mes actual y meses anteriores
print("Generando gráfico 3: Run Chart por Semanas")

# Obtener datos de los últimos 3 meses por semana
meses_analisis = 3
semanas = []
etiquetas_semanas = []

# Obtener año y mes actual
ano_actual = fecha_actual.year
mes_actual = fecha_actual.month

# Generar las semanas para los últimos 3 meses
for m in range(meses_analisis):
    mes = mes_actual - m
    ano = ano_actual
    
    # Ajustar el año si es necesario
    if mes <= 0:
        mes += 12
        ano -= 1
    
    # Determinar número de semanas en el mes
    _, dias_en_mes = calendar.monthrange(ano, mes)
    num_semanas = (dias_en_mes - 1) // 7 + 1
    
    # Agregar semanas al listado
    for s in range(1, num_semanas + 1):
        semana_key = f"{ano}-{mes}-S{s}"
        semanas.append(semana_key)
        
        # Crear etiqueta amigable
        nombre_mes = datetime(ano, mes, 1).strftime('%b')
        etiquetas_semanas.append(f"{nombre_mes} S{s}")

# Invertir para mostrar cronológicamente
semanas.reverse()
etiquetas_semanas.reverse()

# Obtener datos para cada semana
open_por_semana = [open_issues_weekly.get(semana, 0) for semana in semanas]
closed_por_semana = [closed_issues_weekly.get(semana, 0) for semana in semanas]

plt.figure()
plt.plot(range(len(semanas)), open_por_semana, label='Issues Abiertas', color='blue', marker='o', linestyle='-', linewidth=2)
plt.plot(range(len(semanas)), closed_por_semana, label='Issues Cerradas', color='green', marker='s', linestyle='-', linewidth=2)

# Calcular y agregar líneas de tendencia (regresión lineal simple)
if len(semanas) > 1:
    import numpy as np
    from scipy.stats import linregress
    
    try:
        # Para issues abiertas
        x = np.array(range(len(semanas)))
        y_open = np.array(open_por_semana)
        slope_open, intercept_open, _, _, _ = linregress(x, y_open)
        trend_open = intercept_open + slope_open * x
        plt.plot(x, trend_open, 'b--', label='Tendencia Issues Abiertas', alpha=0.7)
        
        # Para issues cerradas
        y_closed = np.array(closed_por_semana)
        slope_closed, intercept_closed, _, _, _ = linregress(x, y_closed)
        trend_closed = intercept_closed + slope_closed * x
        plt.plot(x, trend_closed, 'g--', label='Tendencia Issues Cerradas', alpha=0.7)
    except:
        print("No se pudo calcular las líneas de tendencia, se omitirán")

plt.xlabel('Semana')
plt.ylabel('Cantidad de Issues')
plt.title('Run Chart: Issues por Semana (Últimos 3 Meses)')
plt.legend()
plt.grid(True)
plt.xticks(range(len(semanas)), etiquetas_semanas, rotation=45)
plt.tight_layout()

output_path = os.path.join(output_dir, f'runchart_issues_semanal_{fecha_str}.png')
print(f"Guardando run chart en: {output_path}")
plt.savefig(output_path, dpi=300)
print(f"¿El archivo fue creado? {os.path.exists(output_path)}")
plt.close()

# Verificar que los archivos fueron generados
archivos_generados = os.listdir(output_dir)
print(f"Archivos generados en {output_dir}:", archivos_generados)
print(f"Total de archivos generados: {len(archivos_generados)}")
