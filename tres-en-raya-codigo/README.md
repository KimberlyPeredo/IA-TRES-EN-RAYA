# 🎮 Tres en Raya con Inteligencia Artificial Híbrida (SIS-602)

Proyecto integrador desarrollado para la materia de **Inteligencia Artificial (SIS-602)** de la Facultad de Ingeniería — **Universidad Simón I. Patiño (USIP)**, Cochabamba, Bolivia.

* **Estudiantes:** Fernando Sanchez, Sebastian Pedraza y Kimberly Mariana Peredo Bristott
* **Docente:** Ing. Erlanger Santos Calle Guzmán

---

## 🧠 ¿De qué trata este proyecto y por qué es un sistema Híbrido?

Este juego de **Tres en Raya (3×3)** cuenta con un agente inteligente **híbrido**, lo que significa que combina **dos técnicas diferentes de Inteligencia Artificial** trabajando juntas para decidir dónde jugar:

1. **IA Clásica / Búsqueda Adversaria (Algoritmo Minimax con Poda Alfa-Beta):**
   Es el "cerebro matemático" del juego. Antes de mover, la IA analiza el árbol de jugadas posibles hasta el final de la partida, descartando ramas innecesarias gracias a la poda Alfa-Beta. Así garantiza no cometer errores y bloquea cualquier amenaza.
2. **Aprendizaje Automático Supervisado (Random Forest):**
   Es un modelo de Machine Learning entrenado con **2.423 estados válidos del tablero** (`data/dataset_tres_en_raya.csv`). Cuando hay dos o más casillas igual de buenas según Minimax (por ejemplo, al inicio del juego), Random Forest utiliza las probabilidades aprendidas para desempatar estratégicamente y variar sus aperturas.

> **Enfoque de IA utilizado:** El sistema articula exclusivamente **Minimax con poda Alfa-Beta** (búsqueda adversaria exacta) y **Aprendizaje Supervisado (Random Forest)**, garantizando **0 % de derrotas** y respuestas en milisegundos sobre el espacio de 2.423 estados legales.

### Modos de dificultad disponibles
* **Invencible (IA Híbrida):** Combina Minimax + Random Forest al 100 %. Nunca pierde (en el mejor caso para el jugador humano, se logra un empate).
* **Desafiante (80 % IA):** El 80 % de las veces realiza la jugada óptima y el 20 % elige la segunda mejor opción, dando oportunidad de ganar si se aprovecha el error.

---

## 📁 Estructura del Proyecto (¿Qué hay en cada carpeta?)

```text
IA-TRES-EN-RAYA/
├── assets/
│   ├── logo_usip.png            # Logotipo oficial USIP (800×480 px)
│   └── logo_usip.ico            # Ícono oficial USIP para la ventana en Windows
├── data/
│   └── dataset_tres_en_raya.csv # Base de datos con los 2.423 estados legales del tablero
├── docs/
│   └── SIS-602_PROYECTO-INTEGRADOR_TresEnRaya.docx # Informe técnico completo (APA 7)
├── evidencias/
│   ├── logo_usip.png            # Logotipo oficial USIP (800×480 px)
│   ├── fig1_comparacion_modelos.png
│   ├── fig2_simulacion_1500.png
│   └── fig_distribucion_clases.png
├── models/
│   └── modelo_rf_tres_en_raya.joblib # Modelo Random Forest entrenado (150 árboles)
├── notebooks/
│   ├── 01_Datos_y_IA_Clasica_Minimax.ipynb
│   ├── 02_Entrenamiento_y_Evaluacion_ML.ipynb
│   └── 03_Simulacion_Pruebas_y_Analisis_Errores.ipynb
├── src/
│   ├── app_juegos.py            # Interfaz gráfica interactiva (ventana del juego)
│   ├── ia_engine.py             # Motor lógico híbrido (Minimax + Random Forest)
│   └── pruebas_automatizadas.py # Pruebas unitarias y simulación de 1.500 partidas
├── README.md                    # Esta guía explicativa
└── requirements.txt             # Librerías de Python necesarias
```

---

## 🚀 Cómo instalar y ejecutar el juego paso a paso

### Paso 1: Abrir la terminal en la carpeta del proyecto
Abre Visual Studio Code (o la terminal de Windows) dentro de la carpeta `IA-TRES-EN-RAYA`.

### Paso 2: Instalar las librerías necesarias (solo la primera vez)
```bash
pip install -r requirements.txt
```
*(Si ejecutas el juego en una computadora sin librerías externas instaladas, el programa igual funciona gracias a un respaldo de pesos estadísticos integrado en `ia_engine.py`).*

### Paso 3: Iniciar el juego
Para abrir la ventana gráfica y jugar contra la IA, ejecuta:
```bash
python src/app_juegos.py
```

### Paso 4 (Opcional): Ejecutar las pruebas automáticas
Para comprobar que la IA supera los casos de prueba (bloqueo, victoria directa, control del centro) y gana o empata el **100 % de 1.500 partidas simuladas**:
```bash
python src/pruebas_automatizadas.py
```

### Cambiar el ícono de la ventana por otra imagen USIP
La ventana carga automáticamente `assets/logo_usip.ico` (o `assets/logo_usip.png`). Si deseas usar otro escudo oficial de la USIP, simplemente reemplaza esos archivos manteniendo el mismo nombre.
