"""Tres en raya contra la IA en una ventana de escritorio (tkinter, biblioteca estandar).

Uso:  python ventana.py
Es la misma IA del servidor web (minimax con poda alfa-beta + tabla Q), pero sin navegador ni localhost.
"""
import os
import tkinter as tk

from juegos import tres_en_raya as ttt

RAIZ = os.path.dirname(os.path.abspath(__file__))
ROSA, AZUL, FONDO, TINTA = "#ff6fa5", "#3b82f6", "#f6f7fb", "#1f2937"
CELDA, GANA, GRIS = "#ffffff", "#fde68a", "#6b7280"


def cargar_ia():
    ruta = os.path.join(RAIZ, "modelos", "tres_en_raya_q.json")
    if os.path.exists(ruta):
        agente = ttt.AgenteQ.cargar(ruta)
    else:  # si falta el modelo, se entrena en segundos
        agente = ttt.AgenteQ(alfa=0.3, seed=2026).entrenar_rivales(20000)
    return ttt.jugador_seguro(agente)


class Partida:
    """Logica de una partida (sin interfaz). humano: 1 = X (empieza), 2 = O (empieza la IA)."""

    def __init__(self, ia_fn, humano=1):
        self.ia_fn = ia_fn
        self.nueva(humano)

    def nueva(self, humano):
        self.humano, self.ia = humano, ttt.otro(humano)
        self.t = ttt.VACIO

    @property
    def fin(self):
        return ttt.terminado(self.t)

    def turno_ia(self):
        return not self.fin and ttt.turno(self.t) == self.ia

    def mover_humano(self, pos):
        if self.fin or ttt.turno(self.t) != self.humano or self.t[pos] != 0:
            return False
        self.t = ttt.mover(self.t, pos, self.humano)
        return True

    def mover_ia(self):
        if not self.turno_ia():
            return None
        pos = self.ia_fn(self.t, self.ia)
        self.t = ttt.mover(self.t, pos, self.ia)
        return pos

    def resultado(self):
        """None si sigue, o 'humano', 'ia' o 'empate'."""
        if not self.fin:
            return None
        g = ttt.ganador(self.t)
        return "empate" if g == 0 else ("humano" if g == self.humano else "ia")

    def linea(self):
        return next((l for l in ttt.LINEAS if self.t[l[0]] and self.t[l[0]] == self.t[l[1]] == self.t[l[2]]), ())


class App:
    def __init__(self, raiz, ia_fn):
        self.raiz = raiz
        self.partida = Partida(ia_fn)
        self.marcador = {"humano": 0, "ia": 0, "empate": 0}
        self.bloqueado = False
        raiz.title("Tres en raya contra la IA")
        raiz.configure(bg=FONDO)
        raiz.resizable(False, False)

        tk.Label(raiz, text="Tres en raya contra la IA", font=("Arial", 20, "bold"), bg=FONDO, fg=TINTA).pack(pady=(14, 0))
        tk.Label(raiz, text="Una IA que aprendió jugando y que no se deja ganar", font=("Arial", 10), bg=FONDO, fg=GRIS).pack()

        barra = tk.Frame(raiz, bg=FONDO)
        barra.pack(pady=10)
        tk.Label(barra, text="Tú juegas con", bg=FONDO, fg=TINTA).pack(side="left")
        self.ficha = tk.StringVar(value="X (empiezas tú)")
        tk.OptionMenu(barra, self.ficha, "X (empiezas tú)", "O (empieza la IA)").pack(side="left", padx=6)
        tk.Button(barra, text="Nueva partida", command=self.nueva).pack(side="left")

        self.lbl_marcador = tk.Label(raiz, font=("Arial", 11), bg=FONDO, fg=TINTA)
        self.lbl_marcador.pack()
        self.lbl_estado = tk.Label(raiz, font=("Arial", 14, "bold"), bg=FONDO, fg=TINTA, height=2)
        self.lbl_estado.pack()

        tablero = tk.Frame(raiz, bg="#cbd5e1", padx=6, pady=6)
        tablero.pack()
        self.botones = []
        for i in range(9):
            b = tk.Button(tablero, text="", width=4, height=1, font=("Arial", 36, "bold"), bg=CELDA,
                          relief="flat", command=lambda i=i: self.click(i))
            b.grid(row=i // 3, column=i % 3, padx=3, pady=3)
            self.botones.append(b)

        tk.Label(raiz, text="Con juego perfecto el tres en raya termina en empate:\nla IA no pierde nunca y gana cuando el humano se equivoca.",
                 font=("Arial", 9), bg=FONDO, fg=GRIS).pack(pady=12)
        self.nueva()

    def dibujar(self):
        p = self.partida
        linea = p.linea()
        for i, b in enumerate(self.botones):
            v = p.t[i]
            b.configure(text={0: "", 1: "X", 2: "O"}[v], fg=ROSA if v == 1 else AZUL,
                        bg=GANA if i in linea else CELDA,
                        state="disabled" if (v or p.fin) else "normal")
        m = self.marcador
        self.lbl_marcador.configure(text=f"Tú: {m['humano']}   ·   IA: {m['ia']}   ·   Empates: {m['empate']}")

    def terminar(self):
        r = self.partida.resultado()
        self.marcador[r] += 1
        self.lbl_estado.configure(text={"humano": "¡Ganaste!", "ia": "Gana la IA", "empate": "Empate"}[r])
        self.dibujar()

    def nueva(self):
        self.partida.nueva(1 if self.ficha.get().startswith("X") else 2)
        self.lbl_estado.configure(text="Tu turno" if self.partida.humano == 1 else "La IA piensa...")
        self.dibujar()
        if self.partida.turno_ia():
            self.bloqueado = True
            self.raiz.after(350, self.mueve_ia)
        else:
            self.bloqueado = False

    def click(self, i):
        if self.bloqueado or not self.partida.mover_humano(i):
            return
        self.dibujar()
        if self.partida.fin:
            self.terminar()
            return
        self.bloqueado = True
        self.lbl_estado.configure(text="La IA piensa...")
        self.raiz.after(350, self.mueve_ia)

    def mueve_ia(self):
        self.partida.mover_ia()
        self.bloqueado = False
        self.dibujar()
        if self.partida.fin:
            self.terminar()
        else:
            self.lbl_estado.configure(text="Tu turno")


def main():
    raiz = tk.Tk()
    App(raiz, cargar_ia())
    raiz.mainloop()


if __name__ == "__main__":
    main()
