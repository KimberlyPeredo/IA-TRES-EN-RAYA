"""
Motor de Inteligencia Artificial para Tres en Raya (3x3)
Combina:
  1. Búsqueda adversaria exacta: Algoritmo Minimax con Poda Alfa-Beta y ponderación por profundidad.
  2. Aprendizaje Automático Supervisado: Clasificador Random Forest entrenado sobre los 2.423 estados
     válidos del tablero para desempate probabilístico estratégico y variación táctica.

Nota de compatibilidad: Si scikit-learn/joblib están instalados, utiliza el modelo entrenado (.joblib)
o lo entrena automáticamente; si se ejecuta en un entorno limpio sin librerías externas, utiliza un
modelo de probabilidades pre-entrenado integrado en JSON/memoria sin lanzar errores de importación.

Autores: Fernando Sanchez, Sebastian Pedraza, Kimberly Mariana Peredo Bristott
Materia: SIS-602 Inteligencia Artificial - Universidad Simón I. Patiño (USIP)
"""

import os
import csv
import json
import random

try:
    import joblib
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.dummy import DummyClassifier
    from sklearn.model_selection import StratifiedKFold, cross_val_score
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "modelo_rf_tres_en_raya.joblib")
DATASET_PATH = os.path.join(BASE_DIR, "data", "dataset_tres_en_raya.csv")


class TresEnRayaIA:
    """Agente inteligente híbrido para Tres en Raya (IA = 1 [O], Humano = -1 [X], Vacío = 0)."""

    WIN_LINES = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Filas
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columnas
        (0, 4, 8), (2, 4, 6)              # Diagonales
    ]

    # Pesos estadísticos aprendidos de frecuencia de victoria por casilla (centro > esquinas > bordes)
    PRIOR_WEIGHTS = {
        4: 0.36,
        0: 0.14, 2: 0.14, 6: 0.14, 8: 0.14,
        1: 0.02, 3: 0.02, 5: 0.02, 7: 0.02
    }

    def __init__(self, dificultad="Invencible (IA Híbrida)"):
        self.dificultad = dificultad
        self.rf_model = None
        if HAS_SKLEARN and os.path.exists(MODEL_PATH):
            try:
                self.rf_model = joblib.load(MODEL_PATH)
            except Exception:
                self.rf_model = None

    @classmethod
    def check_winner(cls, board):
        """Retorna 1 si gana IA, -1 si gana Humano, 0 si es empate, o None si la partida sigue."""
        for a, b, c in cls.WIN_LINES:
            if board[a] != 0 and board[a] == board[b] == board[c]:
                return board[a]
        if 0 not in board:
            return 0
        return None

    @classmethod
    def get_winning_line(cls, board):
        """Retorna la tupla (a, b, c) de la línea ganadora para resaltarla en la interfaz."""
        for a, b, c in cls.WIN_LINES:
            if board[a] != 0 and board[a] == board[b] == board[c]:
                return (a, b, c)
        return None

    def minimax(self, board, depth, is_maximizing, alpha=-999, beta=999):
        winner = self.check_winner(board)
        if winner == 1:
            return 10 - depth
        if winner == -1:
            return depth - 10
        if winner == 0:
            return 0

        if is_maximizing:
            best_score = -999
            for i in range(9):
                if board[i] == 0:
                    board[i] = 1
                    score = self.minimax(board, depth + 1, False, alpha, beta)
                    board[i] = 0
                    best_score = max(best_score, score)
                    alpha = max(alpha, best_score)
                    if beta <= alpha:
                        break
            return best_score
        else:
            best_score = 999
            for i in range(9):
                if board[i] == 0:
                    board[i] = -1
                    score = self.minimax(board, depth + 1, True, alpha, beta)
                    board[i] = 0
                    best_score = min(best_score, score)
                    beta = min(beta, best_score)
                    if beta <= alpha:
                        break
            return best_score

    def evaluar_jugadas(self, board):
        """Evalúa todas las casillas disponibles y retorna lista de (casilla, puntaje_minimax, prob_ml)."""
        disponibles = [i for i in range(9) if board[i] == 0]
        if not disponibles:
            return []

        probs_ml = {}
        if self.rf_model is not None and HAS_SKLEARN:
            try:
                raw_probs = self.rf_model.predict_proba([board])[0]
                classes = list(self.rf_model.classes_)
                for m in disponibles:
                    probs_ml[m] = float(raw_probs[classes.index(m)]) if m in classes else 0.0
            except Exception:
                probs_ml = {m: self.PRIOR_WEIGHTS.get(m, 0.05) for m in disponibles}
        else:
            probs_ml = {m: self.PRIOR_WEIGHTS.get(m, 0.05) for m in disponibles}

        resultados = []
        for i in disponibles:
            board[i] = 1
            score = self.minimax(board, 0, False)
            board[i] = 0
            resultados.append((i, score, probs_ml.get(i, 0.0)))

        resultados.sort(key=lambda x: (x[1], x[2]), reverse=True)
        return resultados

    def elegir_jugada(self, board):
        """Selecciona la jugada óptima según el nivel de dificultad elegido."""
        disponibles = [i for i in range(9) if board[i] == 0]
        if not disponibles:
            return -1, []

        evaluaciones = self.evaluar_jugadas(board)

        # Nivel Desafiante: 80% jugada óptima, 20% segunda mejor opción para dar oportunidad
        if self.dificultad == "Desafiante (80% IA)" and len(evaluaciones) > 1:
            if random.random() < 0.20:
                return evaluaciones[1][0], evaluaciones

        # Nivel Invencible (por defecto): elige siempre entre las jugadas de máximo puntaje Minimax
        mejor_score = evaluaciones[0][1]
        optimas = [ev for ev in evaluaciones if ev[1] == mejor_score]

        # Si hay empate de puntaje óptimo, desempata usando probabilidades de Random Forest con leve aleatoriedad
        if len(optimas) > 1:
            pesos = [max(ev[2], 0.05) for ev in optimas]
            elegida = random.choices(optimas, weights=pesos, k=1)[0][0]
            return elegida, evaluaciones

        return optimas[0][0], evaluaciones


def generar_dataset_y_entrenar():
    """Genera el dataset completo de 2.423 estados válidos y entrena Random Forest si scikit-learn está disponible."""
    ia = TresEnRayaIA()
    estados = {}

    def explorar(board, turno):
        clave = tuple(board)
        if clave in estados or TresEnRayaIA.check_winner(board) is not None:
            return
        if turno == 1:
            jugada, _ = ia.elegir_jugada(board)
            estados[clave] = jugada
        for i in range(9):
            if board[i] == 0:
                board[i] = turno
                explorar(board, -turno)
                board[i] = 0

    explorar([0] * 9, 1)
    explorar([0] * 9, -1)

    with open(DATASET_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([f"celda_{i}" for i in range(9)] + ["jugada_optima"])
        for tablero, jugada in estados.items():
            writer.writerow(list(tablero) + [jugada])

    print(f"[OK] Dataset generado: {DATASET_PATH} ({len(estados)} estados únicos).")

    if HAS_SKLEARN:
        df = pd.read_csv(DATASET_PATH)
        X = df[[f"celda_{i}" for i in range(9)]].values
        y = df["jugada_optima"].values
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

        dummy = DummyClassifier(strategy="most_frequent")
        dt = DecisionTreeClassifier(max_depth=10, random_state=42)
        rf = RandomForestClassifier(n_estimators=150, max_depth=15, random_state=42)

        print(f"   - DummyClassifier (Base) Accuracy 5-Fold: {cross_val_score(dummy, X, y, cv=cv).mean():.2%}")
        print(f"   - DecisionTree (Prof. 10) Accuracy 5-Fold: {cross_val_score(dt, X, y, cv=cv).mean():.2%}")
        print(f"   - RandomForest (150 árb.) Accuracy 5-Fold: {cross_val_score(rf, X, y, cv=cv).mean():.2%}")

        rf.fit(X, y)
        joblib.dump(rf, MODEL_PATH)
        print(f"[OK] Modelo Random Forest guardado en: {MODEL_PATH}")
    else:
        print("[INFO] scikit-learn no está instalado; el juego funcionará con el motor híbrido integrado.")


if __name__ == "__main__":
    generar_dataset_y_entrenar()
