import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Button
from matplotlib.animation import FuncAnimation
import numpy as np
from matplotlib.gridspec import GridSpec
import matplotlib.ticker as ticker  

matplotlib.use("TkAgg")



# Parámetros
R = 5000
ktp, ktd = 0.7, 0.4
a, b, d = 0.88, 0.12, 0.15
steps = 300
window = 100
kt_actual = 0

# Inicializaciones
Y = np.zeros(steps)
Ym = np.zeros(steps)
E = np.zeros(steps)
U = np.zeros(steps)
I = np.zeros(steps)
I_processed = np.zeros(steps)
perturb = np.zeros(steps)

base_traffic = 4500

# Inicializaciones dinámicas
def init_arrays(n):
    return (np.zeros(n), np.zeros(n), np.zeros(n),
            np.zeros(n), np.zeros(n), np.zeros(n), np.zeros(n))

I[0:steps] = base_traffic

# Crear figura y layout
fig = plt.figure(figsize=(16, 10))
gs = GridSpec(nrows=1, ncols=2, width_ratios=[1, 3])
control_panel = plt.subplot(gs[0])
control_panel.axis('off')

# Subgráficos
axs = [plt.subplot(gs[1]).inset_axes([0, (5 - i) * 1 / 6, 1, 1 / 6]) for i in range(6)]

labels = [
    "R(kt): Referencia ≡ Θi",
    "Ym(kt): Salida Medida ≡ f",
    "E(kt): Señal de error ≡ e",
    "I_proc(kt): Flujo de Solicitudes Controlado",
    "Perturbación",
    "Y(kt): Salida del proceso ≡ Θf",
]
colors = ['black', 'blue', 'darkred', 'teal', 'darkorange', 'seagreen']
ylims = [(1500, 10000), (0, 15000), (-5000, 5000), (0, 11000), (0, 10000), (0, 15000)]
lines = []

for i, ax in enumerate(axs):
    line, = ax.plot([], [], label=labels[i], color=colors[i])
    ax.set_ylabel(labels[i], fontsize=6)
    ax.set_xlim(0, steps)
    ax.set_ylim(*ylims[i])
    ax.legend(loc='upper right', fontsize=9)
    
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(ticker.AutoLocator())
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x)}'))
    
    lines.append(line)

axs[-1].set_xlabel("Paso de tiempo (kt)", fontsize=8)

eventos = []

def update(kt):
    global kt_actual
    kt_actual = kt
    if kt == 0:
        return lines

    E[kt] = R - Ym[kt - 1]
    delta_E = E[kt] - E[kt - 1]
    U[kt] = ktp * E[kt] + ktd * delta_E
    rate_limiter = np.clip(1 + U[kt] / 2000, 0, 1.0)
    I_processed[kt] = I[kt] * rate_limiter
    Y[kt] = a * Y[kt - 1] + b * I_processed[kt] + d * perturb[kt]
    Ym[kt] = Y[kt]

    x_vals = np.arange(kt + 1)


    datos = [
        np.full_like(x_vals, R),
        Ym[:kt + 1],
        E[:kt + 1],
        I_processed[:kt + 1],
        perturb[:kt + 1],
        Y[:kt + 1],
    ]

    for evento in eventos:
        if evento["active"] and kt > evento["end"]:
            for txt in evento["text_objs"]:
                txt.remove()
            for span in evento["spans"]:
                span.remove()
            evento["active"] = False

    for line, y_vals in zip(lines, datos):
        line.set_data(x_vals, y_vals)

    return lines

# === PANEL IZQUIERDO COMPLETO ===
# --- TÍTULO PRINCIPAL ---
fig.text(0.06, 0.97, "Panel de Simulación", fontsize=13, fontweight='bold', color='darkblue')

# --- PARÁMETROS DE SIMULACIÓN ---
ax_r = plt.axes([0.06, 0.93, 0.15, 0.035])
textbox_r = TextBox(ax_r, "Referencia R", initial=str(R))

ax_steps = plt.axes([0.06, 0.88, 0.15, 0.035])
textbox_steps = TextBox(ax_steps, "Steps", initial=str(steps))

ax_kp = plt.axes([0.06, 0.83, 0.15, 0.035])
textbox_kp = TextBox(ax_kp, "Kp", initial=str(ktp))

ax_kd = plt.axes([0.06, 0.78, 0.15, 0.035])
textbox_kd = TextBox(ax_kd, "Kd", initial=str(ktd))

ax_i = plt.axes([0.06, 0.73, 0.15, 0.035])
textbox_i = TextBox(ax_i, "Flujo base I", initial=str(base_traffic))

# --- TÍTULO PERTURBACIONES ---
fig.text(0.06, 0.68, "Panel de Perturbaciones", fontsize=12, fontweight='bold', color='darkgreen')

# --- PARÁMETROS DE PERTURBACIÓN ---
ax_dur = plt.axes([0.06, 0.63, 0.15, 0.035])
textbox_duracion = TextBox(ax_dur, "Duración", initial="20")

ax_val = plt.axes([0.06, 0.58, 0.15, 0.035])
textbox_valor = TextBox(ax_val, "Valor", initial="8000")

ax_deriva_dur = plt.axes([0.06, 0.53, 0.15, 0.035])
textbox_tiempo_deriva = TextBox(ax_deriva_dur, "Tiempo Deriva", initial="10")

# --- BOTONES DE PERTURBACIÓN ---
ax_escalon = plt.axes([0.06, 0.47, 0.15, 0.045])
btn_escalon = Button(ax_escalon, "Agregar Escalón")

ax_rfi = plt.axes([0.06, 0.41, 0.15, 0.045])
btn_rfi = Button(ax_rfi, "Agregar RFI")

ax_emi = plt.axes([0.06, 0.35, 0.15, 0.045])
btn_emi = Button(ax_emi, "Agregar EMI")

ax_btn_deriva = plt.axes([0.06, 0.29, 0.15, 0.045])
btn_deriva = Button(ax_btn_deriva, "Agregar Deriva")

# --- TÍTULO INICIO SIMULACIÓN ---
fig.text(0.06, 0.24, "Inicio Simulación", fontsize=12, fontweight='bold', color='purple')

# --- BOTÓN PARA INICIAR SIMULACIÓN ---
ax_start = plt.axes([0.06, 0.18, 0.15, 0.05])
btn_start = Button(ax_start, "Iniciar Simulación")

ax_pause = plt.axes([0.06, 0.11, 0.15, 0.05])
btn_pause = Button(ax_pause, "Pausar/Reanudar")

ax_reset = plt.axes([0.06, 0.04, 0.15, 0.05])
btn_reset = Button(ax_reset, "Reiniciar")


def aplicar_perturbacion(tipo):
    try:
        duracion = int(textbox_duracion.text)
        valor = float(textbox_valor.text)
        start = kt_actual
        end = min(kt_actual + duracion, steps)

        if tipo == "Escalón":
            perturb[start:end] = valor
            etiqueta = f"Escalón {valor}"
            color = "purple"
        elif tipo == "Deriva":
            tiempo_deriva = int(textbox_tiempo_deriva.text)
            total_dur = 3 * tiempo_deriva
            end = min(start + total_dur, steps)
            subida = np.linspace(0, valor, tiempo_deriva)
            meseta = np.full(tiempo_deriva, valor)
            bajada = np.linspace(valor, 0, end - start - 2 * tiempo_deriva)
            perturb[start:end] = np.concatenate((subida, meseta, bajada))
            etiqueta = f"Deriva {valor}"
            color = "orange"
        elif tipo == "RFI":
            ruido = valor/4 * np.sin(10 * np.linspace(0, np.pi, end - start))
            perturb[start:end] = ruido
            etiqueta = f"RFI {valor}"
            color = "green"
        elif tipo == "EMI":
            ruido = valor/4 * np.random.randn(end - start)
            perturb[start:end] = ruido
            etiqueta = f"EMI {valor}"
            color = "red"

        text_objs = []
        spans = []

        for ax in axs:
            span = ax.axvspan(start, end, color=color, alpha=0.2)
            spans.append(span)
            y_top = ax.get_ylim()[1]
            text = ax.text((start + end) / 2, y_top * 0.9, etiqueta,
                           color=color, fontsize=8, ha='center', va='center',
                           bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
            text_objs.append(text)

        eventos.append({
            "start": start,
            "end": end,
            "label": etiqueta,
            "color": color,
            "text_objs": text_objs,
            "spans": spans,
            "active": True
        })

        fig.canvas.draw_idle()
    except ValueError:
        print("Entradas inválidas")

btn_escalon.on_clicked(lambda event: aplicar_perturbacion("Escalón"))
btn_rfi.on_clicked(lambda event: aplicar_perturbacion("RFI"))
btn_emi.on_clicked(lambda event: aplicar_perturbacion("EMI"))
btn_deriva.on_clicked(lambda event: aplicar_perturbacion("Deriva"))

ani = None  # inicializamos vacío

def iniciar_simulacion(event):
    global R, ktp, ktd, base_traffic, I, ani, simulacion_iniciada

    try:
        # Parámetros
        R = float(textbox_r.text)
        ktp = float(textbox_kp.text)
        ktd = float(textbox_kd.text)
        base_traffic = float(textbox_i.text)
        steps = int(textbox_steps.text)

        Y, Ym, E, U, I, I_processed, perturb = init_arrays(steps)
        I[:] = base_traffic  # reinicia entrada

        axs[3].axhline(y=R, linestyle='--', color='gray', linewidth=1, label='Referencia')
        axs[3].legend(loc='upper right', fontsize=9)
        axs[5].axhline(R * 0.85, color='gray', linestyle='--', linewidth=1, label='-15% tolerancia')
        axs[5].axhline(R * 1.15, color='gray', linestyle='--', linewidth=1, label='+15% tolerancia')
        axs[5].legend(loc='upper right', fontsize=9)
        for i, ax in enumerate(axs):
            ax.set_xlim(0, steps)
        if ani is None:
            ani = FuncAnimation(fig, update, frames=steps, interval=80, repeat=False)
        simulacion_iniciada = True

        fig.canvas.draw_idle()
    except ValueError:
        print("⚠️ Parámetros inválidos")

paused = False

def pausar_simulacion(event):
    global paused
    if ani is None:
        return
    if paused:
        ani.event_source.start()
        paused = False
        print("▶ Simulación reanudada")
    else:
        ani.event_source.stop()
        paused = True
        print("⏸ Simulación pausada")

def reiniciar_simulacion(event):
    global ani, paused, eventos, Y, Ym, E, U, I, I_processed, perturb

    if ani:
        ani.event_source.stop()
        ani = None
    paused = False

    # Reset arrays con tamaño steps actual
    steps_val = int(textbox_steps.text)
    Y, Ym, E, U, I, I_processed, perturb = init_arrays(steps_val)
    I[:] = float(textbox_i.text)

    # Limpiar gráficos
    for line in lines:
        line.set_data([], [])
    for evento in eventos:
        for txt in evento["text_objs"]:
            txt.remove()
        for span in evento["spans"]:
            span.remove()
    eventos.clear()

    # Reset ejes
    for i, ax in enumerate(axs):
        ax.set_xlim(0, steps_val)

    fig.canvas.draw_idle()
    print("🔄 Simulación reiniciada. Ajusta parámetros y presiona Iniciar Simulación.")


btn_start.on_clicked(iniciar_simulacion)
btn_pause.on_clicked(pausar_simulacion)
btn_reset.on_clicked(reiniciar_simulacion)

plt.tight_layout()
plt.show()
