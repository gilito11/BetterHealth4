
import matplotlib.pyplot as plt
import numpy as np

# Datos de ejemplo para el gráfico (puedes reemplazarlos con los reales)
time = np.arange(1, 11)
data = np.random.random(10) * 100  # Generando datos aleatorios para el ejemplo

# Crear el Run Chart
plt.figure(figsize=(10, 6))
plt.plot(time, data, marker='o', linestyle='-', color='b', label='Mediciones')

# Añadir etiquetas y título
plt.title('Run Chart de Ejemplo')
plt.xlabel('Tiempo')
plt.ylabel('Valor')
plt.grid(True)
plt.legend()

# Guardar el gráfico como un archivo PNG
plt.savefig('run_chart.png', format='png')
plt.close()
