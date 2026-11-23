# Tres en raya contra una IA entrenada

Proyecto integrador SIS-602 (Inteligencia Artificial). El producto (servidor y página) solo usa la
biblioteca estándar de Python 3; el análisis de resultados usa librerías vistas en clase.

## Jugar
**En una ventana (recomendado, sin navegador):**

    python ventana.py

**En el navegador (opcional):**

    python servidor.py
y abrir http://localhost:8000. (Otro puerto: `PUERTO=8010 python servidor.py`.)

En ambos se puede jugar con X (empieza el humano) o con O (empieza la IA).

## Cómo decide la IA
1. Minimax con poda alfa-beta calcula las jugadas que no empeoran el resultado perfecto (las "seguras").
2. Un agente de Q-learning, entrenado contra rivales que se equivocan, elige entre ellas la de mayor valor.

## Validación del servidor
Cada solicitud se rechaza con error 400 si el tablero no es una posición legal (9 casillas, X con igual
o una ficha más que O, sin ganadores imposibles), si la ficha de la IA no es 1 o 2, si la casilla no es un
entero entre 0 y 8 y está libre, si el humano mueve fuera de su turno o si el cuerpo pesa más de 4 096 bytes.

## Estructura
- `juegos/tres_en_raya.py`: reglas, validador de tableros, minimax con poda alfa-beta, Q-learning, IA segura.
- `ventana.py`: juego en una ventana de escritorio (tkinter, viene con Python).
- `servidor.py` y `static/index.html`: versión opcional en el navegador (servidor local).
- `modelos/`: tabla Q del producto (`tres_en_raya_q.json`) y la de auto-juego (`tres_en_raya_q_autojuego.json`).
- `tests/test_juegos.py`: 13 pruebas (`python -m unittest tests.test_juegos`).
- `entrenar_autojuego.py` (1.ª ronda, ~1 min) y `entrenar_rivales.py` (2.ª ronda, ~4 min): experimentos del
  documento; resultados en `resultados_autojuego.json` y `resultados_rivales.json`.
- `analisis.py`: grafo del juego con **networkx**, tablas con **pandas** y gráficos con **matplotlib**.
  Requiere `pip install networkx pandas matplotlib`. Escribe tablas en `analisis/` y figuras en `figuras/`.
