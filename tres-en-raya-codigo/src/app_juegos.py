"""
Interfaz Gráfica Moderna - Tres en Raya con Inteligencia Artificial (3x3)
Diseño visual limpio con tablero Canvas vectorial, animaciones de trazado,
línea de victoria animada, panel de estadísticas y visualización de evaluación de la IA.

Ejecución directa (funciona al instante sin requerir instalaciones extra):
  python app_juegos.py

Autores: Fernando Sanchez, Sebastian Pedraza, Kimberly Mariana Peredo Bristott
Docente: Ing. Erlanger Santos Calle Guzmán
Universidad Simón I. Patiño - Cochabamba, Bolivia
"""

import os
import tkinter as tk
from ia_engine import TresEnRayaIA


class TresEnRayaApp:
    # Paleta de colores moderna (Slate Dark + Cyan/Rose Neon suave)
    BG_MAIN = "#0B1120"
    BG_CARD = "#131C31"
    BG_CELL = "#1E293B"
    BG_CELL_HOVER = "#283548"
    BG_WIN_CELL = "#1E3A5F"
    BORDER_GRID = "#334155"

    COLOR_HUMAN = "#F43F5E"     # Rosado/Coral vibrante (X)
    COLOR_AI = "#38BDF8"        # Azul Cian brillante (O)
    COLOR_WIN_LINE = "#FBBF24"  # Dorado para línea ganadora
    COLOR_TEXT = "#F8FAFC"
    COLOR_MUTED = "#94A3B8"
    COLOR_ACCENT = "#2563EB"
    COLOR_ACCENT_HOVER = "#1D4ED8"
    COLOR_SUCCESS = "#10B981"

    def __init__(self, root):
        self.root = root
        self.root.title("Tres en Raya IA - Proyecto Integrador SIS-602 (USIP)")
        self.root.geometry("820x600")
        self.root.configure(bg=self.BG_MAIN)
        self.root.resizable(False, False)

        # Configurar ícono institucional USIP en la ventana (reemplaza la hoja por defecto de Tkinter)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ruta_ico = os.path.join(base_dir, "assets", "logo_usip.ico")
        ruta_png = os.path.join(base_dir, "assets", "logo_usip.png")
        try:
            if os.path.exists(ruta_ico):
                self.root.iconbitmap(ruta_ico)
            elif os.path.exists(ruta_png):
                self.icono_app = tk.PhotoImage(file=ruta_png)
                self.root.iconphoto(False, self.icono_app)
        except Exception:
            if os.path.exists(ruta_png):
                self.icono_app = tk.PhotoImage(file=ruta_png)
                self.root.iconphoto(False, self.icono_app)

        # Centrar ventana en pantalla
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 820) // 2
        y = (self.root.winfo_screenheight() - 600) // 2
        self.root.geometry(f"820x600+{x}+{y}")

        self.dificultad_var = tk.StringVar(value="Invencible (IA Híbrida)")
        self.quien_inicia_var = tk.StringVar(value="Humano")  # "Humano" o "IA"

        self.ia = TresEnRayaIA(dificultad=self.dificultad_var.get())
        self.board = [0] * 9
        self.game_over = False
        self.turno_humano = True
        self.hover_cell = None
        self.win_line = None

        self.stats = {"Humano": 0, "IA": 0, "Empates": 0}
        self.ultimas_evals = []

        self._construir_interfaz()
        self.nueva_partida()

    def _construir_interfaz(self):
        # 1. Barra superior elegante
        top_bar = tk.Frame(self.root, bg=self.BG_CARD, height=64)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        title_box = tk.Frame(top_bar, bg=self.BG_CARD)
        title_box.pack(side="left", padx=24, pady=10)

        tk.Label(
            title_box,
            text="TRES EN RAYA · AGENTE DE INTELIGENCIA ARTIFICIAL",
            font=("Segoe UI", 13, "bold"),
            fg=self.COLOR_TEXT,
            bg=self.BG_CARD
        ).pack(anchor="w")

        tk.Label(
            title_box,
            text="Fernando Sanchez · Sebastian Pedraza · Kimberly Peredo  |  SIS-602 USIP",
            font=("Segoe UI", 9),
            fg=self.COLOR_MUTED,
            bg=self.BG_CARD
        ).pack(anchor="w")

        badge = tk.Label(
            top_bar,
            text="MINIMAX ALFA-BETA + RANDOM FOREST",
            font=("Segoe UI", 8, "bold"),
            fg="#93C5FD",
            bg="#1E3A8A",
            padx=10,
            pady=4
        )
        badge.pack(side="right", padx=24)

        # 2. Contenedor principal de dos columnas
        main_container = tk.Frame(self.root, bg=self.BG_MAIN)
        main_container.pack(fill="both", expand=True, padx=24, pady=18)

        # --- COLUMNA IZQUIERDA: TABLERO VECTORIAL ---
        left_panel = tk.Frame(main_container, bg=self.BG_MAIN)
        left_panel.pack(side="left", fill="both")

        # Banner de estado de turno
        self.status_frame = tk.Frame(left_panel, bg=self.BG_CARD, padx=14, pady=10)
        self.status_frame.pack(fill="x", pady=(0, 12))

        self.lbl_estado = tk.Label(
            self.status_frame,
            text="Tu turno · Juegas con X",
            font=("Segoe UI", 11, "bold"),
            fg=self.COLOR_HUMAN,
            bg=self.BG_CARD
        )
        self.lbl_estado.pack()

        # Canvas vectorial para dibujar celdas, fichas X/O y línea ganadora
        self.cell_size = 122
        self.gap = 10
        canvas_dim = self.cell_size * 3 + self.gap * 4
        self.canvas = tk.Canvas(
            left_panel,
            width=canvas_dim,
            height=canvas_dim,
            bg=self.BG_CARD,
            highlightthickness=1,
            highlightbackground=self.BORDER_GRID,
            cursor="hand2"
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<Motion>", self._on_canvas_hover)
        self.canvas.bind("<Leave>", self._on_canvas_leave)

        # --- COLUMNA DERECHA: MARCADOR, CONTROLES Y TELEMETRÍA DE LA IA ---
        right_panel = tk.Frame(main_container, bg=self.BG_MAIN)
        right_panel.pack(side="right", fill="both", expand=True, padx=(22, 0))

        # Tarjetas de Marcador
        score_card = tk.Frame(right_panel, bg=self.BG_CARD, padx=16, pady=14)
        score_card.pack(fill="x", pady=(0, 12))

        tk.Label(
            score_card,
            text="MARCADOR DE SESION",
            font=("Segoe UI", 9, "bold"),
            fg=self.COLOR_MUTED,
            bg=self.BG_CARD
        ).pack(anchor="w", pady=(0, 8))

        cols = tk.Frame(score_card, bg=self.BG_CARD)
        cols.pack(fill="x")

        self.lbl_score_human = self._crear_caja_score(cols, "TU (X)", "0", self.COLOR_HUMAN, 0)
        self.lbl_score_draw = self._crear_caja_score(cols, "EMPATES", "0", self.COLOR_MUTED, 1)
        self.lbl_score_ai = self._crear_caja_score(cols, "IA (O)", "0", self.COLOR_AI, 2)

        # Configuración de partida
        config_card = tk.Frame(right_panel, bg=self.BG_CARD, padx=16, pady=14)
        config_card.pack(fill="x", pady=(0, 12))

        tk.Label(
            config_card,
            text="CONFIGURACION DE PARTIDA",
            font=("Segoe UI", 9, "bold"),
            fg=self.COLOR_MUTED,
            bg=self.BG_CARD
        ).pack(anchor="w", pady=(0, 8))

        # Quién inicia
        row_ini = tk.Frame(config_card, bg=self.BG_CARD)
        row_ini.pack(fill="x", pady=3)
        tk.Label(row_ini, text="Primer turno:", font=("Segoe UI", 10), fg=self.COLOR_TEXT, bg=self.BG_CARD).pack(side="left")

        for texto, val in [("Tu (X)", "Humano"), ("IA (O)", "IA")]:
            rb = tk.Radiobutton(
                row_ini,
                text=texto,
                variable=self.quien_inicia_var,
                value=val,
                font=("Segoe UI", 10, "bold"),
                fg=self.COLOR_TEXT,
                bg=self.BG_CARD,
                selectcolor=self.BG_CELL,
                activebackground=self.BG_CARD,
                activeforeground=self.COLOR_TEXT,
                command=self.nueva_partida
            )
            rb.pack(side="right", padx=(8, 0))

        # Nivel de IA
        row_dif = tk.Frame(config_card, bg=self.BG_CARD)
        row_dif.pack(fill="x", pady=(8, 2))
        tk.Label(row_dif, text="Modo IA:", font=("Segoe UI", 10), fg=self.COLOR_TEXT, bg=self.BG_CARD).pack(side="left")

        opt_dif = tk.OptionMenu(
            row_dif,
            self.dificultad_var,
            "Invencible (IA Híbrida)",
            "Desafiante (80% IA)",
            command=self._cambiar_dificultad
        )
        opt_dif.config(
            font=("Segoe UI", 9),
            bg=self.BG_CELL,
            fg=self.COLOR_TEXT,
            activebackground=self.BG_CELL_HOVER,
            activeforeground=self.COLOR_TEXT,
            highlightthickness=0,
            relief="flat",
            width=19
        )
        opt_dif["menu"].config(bg=self.BG_CELL, fg=self.COLOR_TEXT, font=("Segoe UI", 9))
        opt_dif.pack(side="right")

        # Panel de decisión de la IA (explicabilidad en vivo)
        ai_card = tk.Frame(right_panel, bg=self.BG_CARD, padx=16, pady=12)
        ai_card.pack(fill="both", expand=True, pady=(0, 12))

        tk.Label(
            ai_card,
            text="ANALISIS DE DECISION DE LA IA (ULTIMO TURNO)",
            font=("Segoe UI", 9, "bold"),
            fg=self.COLOR_MUTED,
            bg=self.BG_CARD
        ).pack(anchor="w", pady=(0, 6))

        self.lbl_ai_thought = tk.Label(
            ai_card,
            text="Esperando movimiento...",
            font=("Consolas", 9),
            fg="#CBD5E1",
            bg=self.BG_CARD,
            justify="left",
            anchor="nw"
        )
        self.lbl_ai_thought.pack(fill="both", expand=True)

        # Botón Nueva Partida
        btn_frame = tk.Frame(right_panel, bg=self.BG_MAIN)
        btn_frame.pack(fill="x")

        self.btn_reset = tk.Button(
            btn_frame,
            text="Nueva Partida",
            font=("Segoe UI", 11, "bold"),
            bg=self.COLOR_ACCENT,
            fg="white",
            activebackground=self.COLOR_ACCENT_HOVER,
            activeforeground="white",
            relief="flat",
            pady=9,
            cursor="hand2",
            command=self.nueva_partida
        )
        self.btn_reset.pack(side="left", fill="x", expand=True, padx=(0, 6))

        btn_clear_stats = tk.Button(
            btn_frame,
            text="Reiniciar Marcador",
            font=("Segoe UI", 10),
            bg=self.BG_CELL,
            fg=self.COLOR_MUTED,
            activebackground=self.BG_CELL_HOVER,
            activeforeground=self.COLOR_TEXT,
            relief="flat",
            pady=9,
            padx=12,
            cursor="hand2",
            command=self._reset_stats
        )
        btn_clear_stats.pack(side="right")

    def _crear_caja_score(self, parent, titulo, valor, color, col_idx):
        box = tk.Frame(parent, bg=self.BG_CELL, padx=10, pady=8)
        box.grid(row=0, column=col_idx, sticky="nsew", padx=4)
        parent.columnconfigure(col_idx, weight=1)

        tk.Label(box, text=titulo, font=("Segoe UI", 8, "bold"), fg=self.COLOR_MUTED, bg=self.BG_CELL).pack()
        lbl_val = tk.Label(box, text=valor, font=("Segoe UI", 16, "bold"), fg=color, bg=self.BG_CELL)
        lbl_val.pack()
        return lbl_val

    def _cambiar_dificultad(self, _):
        self.ia = TresEnRayaIA(dificultad=self.dificultad_var.get())
        self.nueva_partida()

    def _reset_stats(self):
        self.stats = {"Humano": 0, "IA": 0, "Empates": 0}
        self._actualizar_marcador()
        self.nueva_partida()

    def _actualizar_marcador(self):
        self.lbl_score_human.config(text=str(self.stats["Humano"]))
        self.lbl_score_draw.config(text=str(self.stats["Empates"]))
        self.lbl_score_ai.config(text=str(self.stats["IA"]))

    def nueva_partida(self):
        self.board = [0] * 9
        self.game_over = False
        self.win_line = None
        self.hover_cell = None
        self._dibujar_tablero()

        if self.quien_inicia_var.get() == "IA":
            self.turno_humano = False
            self.lbl_estado.config(text="Turno de la IA (O) · Calculando...", fg=self.COLOR_AI)
            self.lbl_ai_thought.config(
                text="IA inicia la partida: evaluando aperturas\noptimas (centro y esquinas)..."
            )
            self.root.after(260, self._ejecutar_turno_ia)
        else:
            self.turno_humano = True
            self.lbl_estado.config(text="Tu turno · Haz clic en una casilla (X)", fg=self.COLOR_HUMAN)
            self.lbl_ai_thought.config(
                text="Esperando tu primer movimiento.\nLa IA respondera con Minimax Alfa-Beta."
            )

    def _coords_celda(self, idx):
        r, c = divmod(idx, 3)
        x1 = self.gap + c * (self.cell_size + self.gap)
        y1 = self.gap + r * (self.cell_size + self.gap)
        return x1, y1, x1 + self.cell_size, y1 + self.cell_size

    def _celda_desde_xy(self, x, y):
        for i in range(9):
            x1, y1, x2, y2 = self._coords_celda(i)
            if x1 <= x <= x2 and y1 <= y <= y2:
                return i
        return None

    def _on_canvas_hover(self, event):
        if self.game_over or not self.turno_humano:
            return
        idx = self._celda_desde_xy(event.x, event.y)
        if idx != self.hover_cell:
            self.hover_cell = idx
            self._dibujar_tablero()

    def _on_canvas_leave(self, _):
        if self.hover_cell is not None:
            self.hover_cell = None
            self._dibujar_tablero()

    def _on_canvas_click(self, event):
        if self.game_over or not self.turno_humano:
            return
        idx = self._celda_desde_xy(event.x, event.y)
        if idx is None or self.board[idx] != 0:
            return

        self.board[idx] = -1
        self.turno_humano = False
        self.hover_cell = None
        self._dibujar_tablero()

        if self._verificar_fin_partida():
            return

        self.lbl_estado.config(text="IA analizando arbol de jugadas...", fg=self.COLOR_AI)
        self.root.after(220, self._ejecutar_turno_ia)

    def _ejecutar_turno_ia(self):
        if self.game_over:
            return
        jugada, evals = self.ia.elegir_jugada(self.board)
        if jugada != -1:
            self.board[jugada] = 1
            self._mostrar_telemetria(jugada, evals)
            self._dibujar_tablero()

        if not self._verificar_fin_partida():
            self.turno_humano = True
            self.lbl_estado.config(text="Tu turno · Haz clic en una casilla (X)", fg=self.COLOR_HUMAN)

    def _mostrar_telemetria(self, elegida, evals):
        nombres = ["F1-C1", "F1-C2", "F1-C3", "F2-C1", "Centro", "F2-C3", "F3-C1", "F3-C2", "F3-C3"]
        lineas = [f"Jugada elegida: {nombres[elegida]} (Casilla {elegida + 1})"]
        lineas.append("Top evaluaciones (Minimax | RF):")
        for idx, score, prob in evals[:3]:
            estado_txt = "Gana" if score > 0 else ("Empate" if score == 0 else "Pierde")
            lineas.append(f"  - {nombres[idx]:<6}: {score:+3d} ({estado_txt}) | {prob*100:4.1f}%")
        self.lbl_ai_thought.config(text="\n".join(lineas))

    def _verificar_fin_partida(self):
        ganador = TresEnRayaIA.check_winner(self.board)
        if ganador is None:
            return False

        self.game_over = True
        self.win_line = TresEnRayaIA.get_winning_line(self.board)
        self._dibujar_tablero()

        if ganador == 1:
            self.stats["IA"] += 1
            self.lbl_estado.config(text="La IA (O) gano esta partida!", fg=self.COLOR_AI)
        elif ganador == -1:
            self.stats["Humano"] += 1
            self.lbl_estado.config(text="Felicidades! Lograste vencer a la IA", fg=self.COLOR_SUCCESS)
        else:
            self.stats["Empates"] += 1
            self.lbl_estado.config(text="Empate tecnico · Tablero completo", fg=self.COLOR_WIN_LINE)

        self._actualizar_marcador()
        return True

    def _dibujar_tablero(self):
        self.canvas.delete("all")
        win_set = set(self.win_line) if self.win_line else set()

        for i in range(9):
            x1, y1, x2, y2 = self._coords_celda(i)
            bg = self.BG_CELL
            if i in win_set:
                bg = self.BG_WIN_CELL
            elif i == self.hover_cell and self.board[i] == 0 and self.turno_humano and not self.game_over:
                bg = self.BG_CELL_HOVER

            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=bg,
                outline=self.BORDER_GRID,
                width=1
            )

            pad = 32

            if self.board[i] == -1:
                self.canvas.create_line(x1 + pad, y1 + pad, x2 - pad, y2 - pad, fill=self.COLOR_HUMAN, width=8, capstyle="round")
                self.canvas.create_line(x2 - pad, y1 + pad, x1 + pad, y2 - pad, fill=self.COLOR_HUMAN, width=8, capstyle="round")
            elif self.board[i] == 1:
                self.canvas.create_oval(x1 + pad, y1 + pad, x2 - pad, y2 - pad, outline=self.COLOR_AI, width=8)
            elif i == self.hover_cell and self.turno_humano and not self.game_over:
                self.canvas.create_line(x1 + pad, y1 + pad, x2 - pad, y2 - pad, fill="#475569", width=4, capstyle="round")
                self.canvas.create_line(x2 - pad, y1 + pad, x1 + pad, y2 - pad, fill="#475569", width=4, capstyle="round")

        if self.win_line:
            a, _, c = self.win_line
            ax1, ay1, ax2, ay2 = self._coords_celda(a)
            cx1, cy1, cx2, cy2 = self._coords_celda(c)
            self.canvas.create_line(
                (ax1 + ax2) / 2, (ay1 + ay2) / 2,
                (cx1 + cx2) / 2, (cy1 + cy2) / 2,
                fill=self.COLOR_WIN_LINE,
                width=7,
                capstyle="round"
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = TresEnRayaApp(root)
    root.mainloop()
