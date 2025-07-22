## 🎯 Requisitos

Antes de ejecutar el script, asegurate de tener **Python 3** y las siguientes bibliotecas instaladas:

- `matplotlib`
- `numpy`

Instalación rápida:

```bash
pip install matplotlib numpy
```

⚠️ Este script usa el backend TkAgg de matplotlib, por lo que también necesitás tener Tkinter instalado

En Linux:
```bash
sudo apt-get install python3-tk
```

## 🚀 Cómo correr

1. Cloná este repositorio:

```bash
git clone https://github.com/uriliahaff/api-request-controller-pd.git
cd api-request-controller-pd
```

2. Ejecutá el script:

```bash
python test.py
```

## 📌 Características principales

- Controlador PID configurable: `Kp`, `Kd`, `Referencia R`, `Flujo Base I`
- Animación en tiempo real de:
  - Salida del sistema
  - Señal de error
  - Flujo procesado
  - Perturbaciones aplicadas
- Perturbaciones dinámicas:
  - Escalón
  - Deriva
  - RFI (ruido senoidal)
  - EMI (ruido aleatorio)
- Botones para:
  - Iniciar simulación
  - Pausar y reanudar
  - Reiniciar
- Configuración de pasos (`steps`) para definir la duración total de la simulación
