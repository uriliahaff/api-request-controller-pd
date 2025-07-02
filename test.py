import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Parámetros del sistema
R = 1500  # Valor de referencia
Kp = 0.7
Kd = 0.4
a = 0.88
b = 0.12
d = 0.15

steps = 300
Y = np.zeros(steps)
Ym = np.zeros(steps)
E = np.zeros(steps)
U = np.zeros(steps)
perturb = np.zeros(steps)
I = np.zeros(steps)
I_processed = np.zeros(steps)
http_429 = np.zeros(steps) 

# Simulación de I(k) = tráfico entrante
np.random.seed(42)
base_traffic = 1600
I = base_traffic + 300 * np.random.randn(steps)  # ruido gaussiano
I[60:80] += 1800                                  # Pico viral
I[100:120] += 3000                                # DDoS
I = np.clip(I, 0, 6000)

# Definición de perturbaciones realistas
perturb[30:50] = 800
perturb[60:80] = 2000
perturb[100:120] = 4000
perturb[140:160] = -0.5 * Y[139:159] + 300 * np.sin(0.3 * np.arange(140,160))
perturb[180:200] = 800 * np.exp(-0.2 * (np.arange(180,200)-180))
perturb[220:240] = 1000 * np.abs(np.sin(0.4 * np.arange(220,240)))

# Simulación principal
logs = []
for k in range(1, steps):
    # Controlador PD
    E[k] = R - Ym[k-1]
    delta_E = E[k] - E[k-1]
    U[k] = Kp * E[k] + Kd * delta_E

    # Rate limiter basado en el control
    rate_limiter_factor = np.clip(1 + U[k]/2000, 0, 1.0)
    I_processed[k] = I[k] * rate_limiter_factor

    # Estimación de respuestas HTTP 429
    http_429[k] = max(0, I[k] - I_processed[k])

    # Dinámica del sistema
    Y[k] = a * Y[k-1] + b * I_processed[k] + d * perturb[k]

    # Salida medida
    Ym[k] = Y[k]

    logs.append({
        'Paso': k,
        'Referencia R(k)': R,
        'Entrada I(k)': I[k],
        'Procesado I_proc(k)': I_processed[k],
        'HTTP 429': http_429[k],
        'Medición Ym(k)': Ym[k],
        'Error E(k)': E[k],
        'Delta Error': delta_E,
        'Control U(k)': U[k],
        'Salida Y(k)': Y[k],
        'Perturbación': perturb[k]
    })

df_logs = pd.DataFrame(logs)

# ------------------------ VISUALIZACIÓN ------------------------
fig, axs = plt.subplots(9, 1, figsize=(18, 80), sharex=True)  # Aumentamos altura total
fig.subplots_adjust(hspace=20)  # Más separación vertical


# Evento destacados
eventos = [
    {"start": 60, "end": 80, "label": "Pico viral", "color": "orange"},
    {"start": 100, "end": 120, "label": "Ataque DDoS", "color": "red"},
    {"start": 180, "end": 200, "label": "Decay exponencial", "color": "green"},
    {"start": 220, "end": 240, "label": "Ruido senoidal", "color": "purple"},
]

def resaltar_eventos(ax):
    for evento in eventos:
        ax.axvspan(evento["start"], evento["end"], color=evento["color"], alpha=0.2)
        y_pos = ax.get_ylim()[1]
        ax.text((evento["start"] + evento["end"]) / 2, y_pos * 0.9,
                evento["label"], color=evento["color"], fontsize=11,
                ha='center', va='center',
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

# 1. Referencia
axs[0].plot(df_logs['Paso'], df_logs['Referencia R(k)'], label='R(k)', color='black')
axs[0].set_ylabel("R(kt)")
resaltar_eventos(axs[0])

# 2. Ym(k)
axs[1].plot(df_logs['Paso'], df_logs['Medición Ym(k)'], label='Ym(kt)', color='blue')
axs[1].axhline(1500 * 0.85, color='gray', linestyle='--', linewidth=1, label='-15% tolerancia')
axs[1].axhline(1500 * 1.15, color='gray', linestyle='--', linewidth=1, label='+15% tolerancia')
axs[1].set_ylabel('Ym(kt)')
axs[1].legend()
resaltar_eventos(axs[1])

# 3. Error E(k)
axs[2].plot(df_logs['Paso'], df_logs['Error E(k)'], label='E(k)', color='darkred')
axs[2].axhline(0, color='black', linestyle='--', linewidth=1)
axs[2].set_ylabel('E(kt)')
resaltar_eventos(axs[2])

# 4. Control U(k)
axs[3].plot(df_logs['Paso'], df_logs['Control U(k)'], label='U(k)', color='teal')
axs[3].set_ylabel('U(kt)')
resaltar_eventos(axs[3])

# 5. I(k)
axs[4].plot(df_logs['Paso'], df_logs['Entrada I(k)'], label='I(k)', color='darkorange')
axs[4].set_ylabel('I(kt)')
resaltar_eventos(axs[4])

# 6. I procesado
axs[5].plot(df_logs['Paso'], df_logs['Procesado I_proc(k)'], label='I_proc(k)', color='seagreen')
axs[5].set_ylabel('I_processed(kt)')
resaltar_eventos(axs[5])

# 7. Perturbaciones
axs[6].plot(df_logs['Paso'], df_logs['Perturbación'], label='Perturbación', color='darkviolet')
axs[6].set_ylabel('Perturbación')
resaltar_eventos(axs[6])

# 8. Salida Y(k)
axs[7].plot(df_logs['Paso'], df_logs['Salida Y(k)'], label='Y(k)', color='navy')
axs[7].set_ylabel('Y(kt)')
resaltar_eventos(axs[7])

# 9. HTTP 429
axs[8].plot(df_logs['Paso'], df_logs['HTTP 429'], label='HTTP 429', color='crimson')
axs[8].set_ylabel('HTTP 429')
resaltar_eventos(axs[8])
axs[8].set_xlabel('Paso de tiempo (k)')

# Deja espacio arriba para el título
plt.tight_layout(rect=[0, 0, 1, 0.96])  # Reservamos espacio para el título
plt.show()
print(f"Máximo Ym: {np.max(Ym)}")
print(f"Mínimo Ym: {np.min(Ym)}")
