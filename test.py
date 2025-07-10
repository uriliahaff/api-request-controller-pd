import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

canvas = None  # Variable global para el canvas

def simular(R_val, ktp_val, ktd_val, a_val, b_val, d_val):
    global canvas  # Declarar global antes de usarla

    R = float(R_val)
    ktp = float(ktp_val)
    ktd = float(ktd_val)
    a = float(a_val)
    b = float(b_val)
    d = float(d_val)

    steps = 360
    Y = np.zeros(steps)
    Ym = np.zeros(steps)
    E = np.zeros(steps)
    U = np.zeros(steps)
    perturb = np.zeros(steps)
    I = np.zeros(steps)
    I_processed = np.zeros(steps)
    http_429 = np.zeros(steps)

    base_traffic = 4500
    min_traffic = base_traffic - base_traffic*0.15
    max_traffic = base_traffic + base_traffic*0.15
    I = [base_traffic]
    alpha = 0.9

    for _ in range(1, steps):
        change = np.random.randn() * 30
        next_val = alpha * I[-1] + (1 - alpha) * base_traffic + change
        next_val = np.clip(next_val, min_traffic, max_traffic)
        I.append(next_val)

    I = np.array(I)

    perturb[60:80] = 3000
    perturb[120:140] = 8000
    perturb[180:200] += np.random.normal(0, 2000, 20)
    perturb[240:260] += 4000 * np.sin(10 * np.arange(20))

    logs = []
    for kt in range(1, steps):
        E[kt] = R - Ym[kt-1]
        delta_E = E[kt] - E[kt-1]
        U[kt] = ktp * E[kt] + ktd * delta_E
        rate_limiter_factor = np.clip(1 + U[kt]/2000, 0, 1.0)
        I_processed[kt] = I[kt] * rate_limiter_factor
        http_429[kt] = max(0, I[kt] - I_processed[kt])
        Y[kt] = a * Y[kt-1] + b * I_processed[kt] + d * perturb[kt]
        Ym[kt] = Y[kt]
        logs.append({
            'Paso': kt,
            'Referencia R(kt)': R,
            'Entrada I(kt)': I[kt],
            'Procesado I_proc(kt)': I_processed[kt],
            'HTTP 429': http_429[kt],
            'Medición Ym(kt)': Ym[kt],
            'Error E(kt)': E[kt],
            'Delta Error': delta_E,
            'Control U(kt)': U[kt],
            'Salida Y(kt)': Y[kt],
            'Perturbación': perturb[kt]
        })

    df_logs = pd.DataFrame(logs)

    fig, axs = plt.subplots(9, 1, figsize=(18, 30), sharex=True)
    fig.subplots_adjust(hspace=5)

    eventos = [
        {"start": 60, "end": 80, "label": "Pico viral", "color": "orange"},
        {"start": 120, "end": 140, "label": "Ataque DDoS", "color": "red"},
        {"start": 180, "end": 200, "label": "EMI", "color": "green"},
        {"start": 240, "end": 260, "label": "RFI", "color": "green"},
    ]

    def resaltar_eventos(ax):
        for evento in eventos:
            ax.axvspan(evento["start"], evento["end"], color=evento["color"], alpha=0.2)
            y_pos = ax.get_ylim()[1]
            ax.text((evento["start"] + evento["end"]) / 2, y_pos * 0.9,
                    evento["label"], color=evento["color"], fontsize=11,
                    ha='center', va='center',
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

    axs[0].plot(df_logs['Paso'], df_logs['Referencia R(kt)'], label='R(kt): Referencia ≡ Θi', color='black')
    axs[0].set_ylabel("R(kt)")
    axs[0].legend()
    resaltar_eventos(axs[0])

    axs[1].plot(df_logs['Paso'], df_logs['Medición Ym(kt)'], label='Ym(kt): Salida Medida ≡ f', color='blue')
    axs[1].set_ylabel('Ym(kt)')
    axs[1].legend()
    resaltar_eventos(axs[1])

    axs[2].plot(df_logs['Paso'], df_logs['Error E(kt)'], label='E(kt): Señal de error ≡ e', color='darkred')
    axs[2].set_ylabel('E(kt)')
    axs[2].legend()
    resaltar_eventos(axs[2])

    axs[3].plot(df_logs['Paso'], df_logs['Control U(kt)'], label='U(kt): Señal de control', color='teal')
    axs[3].set_ylabel('U(kt)')
    axs[3].legend()
    resaltar_eventos(axs[3])

    axs[4].plot(df_logs['Paso'], df_logs['Entrada I(kt)'], label='I(kt): Solicitudes entrantes crudas', color='darkorange')
    axs[4].set_ylabel('I(kt)')
    axs[4].set_ylim(4000, 6000)
    axs[4].legend()
    resaltar_eventos(axs[4])

    axs[5].plot(df_logs['Paso'], df_logs['Procesado I_proc(kt)'], label='I_proc(kt): Flujo de Solicitudes Controlado', color='seagreen')
    axs[5].set_ylabel('I_processed(kt)')
    axs[5].axhline(y=5000, linestyle='--', color='gray', linewidth=1, label='Referencia: 5000')
    axs[5].set_ylim(0, 6000)
    axs[5].legend()
    resaltar_eventos(axs[5])

    axs[6].plot(df_logs['Paso'], df_logs['Perturbación'], label='Perturbación', color='darkviolet')
    axs[6].set_ylabel('Perturbación')
    axs[6].legend()
    resaltar_eventos(axs[6])

    axs[7].plot(df_logs['Paso'], df_logs['Salida Y(kt)'], label='Y(kt): Salida del proceso ≡ Θf', color='navy')
    axs[7].axhline(5000 * 0.85, color='gray', linestyle='--', linewidth=1, label='-15% tolerancia')
    axs[7].axhline(5000 * 1.15, color='gray', linestyle='--', linewidth=1, label='+15% tolerancia')
    axs[7].legend()
    axs[7].set_ylabel('Y(kt)')
    resaltar_eventos(axs[7])

    axs[8].plot(df_logs['Paso'], df_logs['HTTP 429'], label='HTTP 429: Solicitudes rechazadas', color='crimson')
    axs[8].set_ylabel('HTTP 429')
    axs[8].set_xlabel('Paso de tiempo (kt)')
    axs[8].legend()
    resaltar_eventos(axs[8])

    plt.tight_layout(rect=[0, 0, 1, 0.96])

    # Limpiar canvas viejo si existe
    if canvas:
        canvas.get_tk_widget().destroy()

    # Crear nuevo canvas dentro del frame scrollable
    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

    print(f"Máximo Ym: {np.max(Ym)}")
    print(f"Mínimo Ym: {np.min(Ym)}")

# Crear ventana principal
window = tk.Tk()
window.title("Simulador PD con Scroll")

# Frame para inputs
frame_inputs = tk.Frame(window)
frame_inputs.pack(pady=10)

params = {
    "R": tk.StringVar(value="5000"),
    "ktp": tk.StringVar(value="0.7"),
    "ktd": tk.StringVar(value="0.4"),
    "a": tk.StringVar(value="0.88"),
    "b": tk.StringVar(value="0.12"),
    "d": tk.StringVar(value="0.15")
}

# Aplico fuente grande (Arial 14) a todos los widgets
font_style = ("Arial", 14)

for idx, (name, var) in enumerate(params.items()):
    tk.Label(frame_inputs, text=name, font=font_style).grid(row=0, column=idx)
    tk.Entry(frame_inputs, textvariable=var, width=7, font=font_style).grid(row=1, column=idx)

tk.Button(
    frame_inputs,
    text="Simular",
    command=lambda: simular(
        params["R"].get(),
        params["ktp"].get(),
        params["ktd"].get(),
        params["a"].get(),
        params["b"].get(),
        params["d"].get()
    ),
    font=font_style
).grid(row=1, column=len(params), padx=10)

# Frame con scrollbar para el gráfico
canvas_container = tk.Frame(window)
canvas_container.pack(fill=tk.BOTH, expand=True)

canvas_scroll = tk.Canvas(canvas_container)
canvas_scroll.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=canvas_scroll.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

canvas_scroll.configure(yscrollcommand=scrollbar.set)

canvas_frame = tk.Frame(canvas_scroll)
canvas_scroll.create_window((0, 0), window=canvas_frame, anchor="nw")

def on_frame_configure(event):
    canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))

canvas_frame.bind("<Configure>", on_frame_configure)

# Simulación inicial
simular(*[var.get() for var in params.values()])

window.mainloop()

