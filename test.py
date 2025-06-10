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
fig, axs = plt.subplots(7, 1, figsize=(18, 29), sharex=True)

axs[0].plot(df_logs['Paso'], df_logs['Salida Y(k)'], label="Y(k) - Salida", linewidth=2)
axs[0].plot(df_logs['Paso'], df_logs['Referencia R(k)'], '--', label="R(k) - Referencia", color='orange')
axs[0].set_ylabel("Salida (req/s)")
axs[0].legend()
axs[0].grid(True)
axs[0].annotate('Pico viral', xy=(65, Y[65]), xytext=(70, Y[65]+800),
                arrowprops=dict(arrowstyle='->'), fontsize=10, color='purple')
axs[0].annotate('Ataque DDoS', xy=(110, Y[110]), xytext=(115, Y[110]+800),
                arrowprops=dict(arrowstyle='->'), fontsize=10, color='red')
axs[0].annotate('Recuperación con control', xy=(130, Y[130]), xytext=(135, Y[130]-1000),
                arrowprops=dict(arrowstyle='->'), fontsize=10, color='green')

axs[1].plot(df_logs['Paso'], df_logs['Error E(k)'], label="E(k) - Error", color='crimson')
axs[1].set_ylabel("Error")
axs[1].legend()
axs[1].grid(True)
axs[1].annotate('Error alto por DDoS', xy=(110, E[110]), xytext=(120, E[110]+100),
                arrowprops=dict(arrowstyle='->'), fontsize=10, color='red')

axs[2].plot(df_logs['Paso'], df_logs['Control U(k)'], label="U(k) - Controlador", color='darkblue')
axs[2].set_ylabel("Control")
axs[2].legend()
axs[2].grid(True)
axs[2].annotate('Control sube por tráfico', xy=(65, U[65]), xytext=(70, U[65]+50),
                arrowprops=dict(arrowstyle='->'), fontsize=10)
axs[2].annotate('Máxima acción de control', xy=(110, U[110]), xytext=(115, U[110]-100),
                arrowprops=dict(arrowstyle='->'), fontsize=10)

axs[3].plot(df_logs['Paso'], df_logs['Perturbación'], label="Perturbación", color='black', linestyle='dotted')
axs[3].set_ylabel("Perturbación")
axs[3].legend()
axs[3].grid(True)
axs[3].annotate('Pico viral', xy=(65, perturb[65]), xytext=(70, perturb[65]+500),
                arrowprops=dict(arrowstyle='->'), fontsize=10)
axs[3].annotate('DDoS', xy=(110, perturb[110]), xytext=(115, perturb[110]+500),
                arrowprops=dict(arrowstyle='->'), fontsize=10)
axs[3].annotate('Perturbación senoidal', xy=(145, perturb[145]), xytext=(150, perturb[145]-300),
                arrowprops=dict(arrowstyle='->'), fontsize=10)

axs[4].plot(df_logs['Paso'], df_logs['Entrada I(k)'], label="I(k) - Entrante", color='gray')
axs[4].plot(df_logs['Paso'], df_logs['Procesado I_proc(k)'], label="I_proc(k) - Procesado", color='green')
axs[4].set_ylabel("Solicitudes (req/s)")
axs[4].legend()
axs[4].grid(True)
axs[4].annotate('Tráfico entrante sin filtrar', xy=(65, I[65]), xytext=(70, I[65]+400),
                arrowprops=dict(arrowstyle='->'), fontsize=10)
axs[4].annotate('Limitación activa', xy=(110, I_processed[110]), xytext=(115, I_processed[110]-500),
                arrowprops=dict(arrowstyle='->'), fontsize=10, color='green')

axs[5].plot(df_logs['Paso'], df_logs['HTTP 429'], label="Respuestas HTTP 429", color='red')
axs[5].set_ylabel("HTTP 429 (req/s)")
axs[5].legend()
axs[5].grid(True)
axs[5].annotate('Muchos 429 por DDoS', xy=(110, http_429[110]), xytext=(120, http_429[110]+500),
                arrowprops=dict(arrowstyle='->'), fontsize=10, color='red')
axs[5].annotate('Alivio tras control', xy=(140, http_429[140]), xytext=(145, http_429[140]-300),
                arrowprops=dict(arrowstyle='->'), fontsize=10, color='green')

axs[6].plot(df_logs['Paso'], df_logs['Referencia R(k)'], label="R(k) - Referencia", color='orange', linewidth=2)
axs[6].set_ylabel("Referencia (req/s)")
axs[6].set_xlabel("Paso")
axs[6].legend()
axs[6].grid(True)

plt.suptitle("Simulación de control de flujo utilizando políticas de rate limiting aplicadas en el backend de una API RESTful", fontsize=14)
plt.tight_layout(rect=[0, 0, 1, 0.965])
plt.show()
