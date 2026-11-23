"""Tres en raya, segunda ronda: Q-learning contra rivales imperfectos + filtro minimax.
Guarda el modelo del producto (modelos/tres_en_raya_q.json) y resultados_rivales.json. Requiere antes
modelos/tres_en_raya_q_autojuego.json (lo genera entrenar_autojuego.py)."""
import json
import random
import statistics as st
import time

from juegos import tres_en_raya as ttt

SEMILLAS = [11, 22, 33, 44, 55]


def pct(x, n):
    return round(100.0 * x / n, 1)


def evalua(f, n=1000, n_min=300):
    random.seed(4321)
    out = {}
    for nombre, rival, k in (("azar", ttt.jugador_azar(), n),
                             ("humano20", ttt.jugador_humano_simulado(0.2), n),
                             ("humano40", ttt.jugador_humano_simulado(0.4), n),
                             ("minimax", ttt.jugador_minimax(), n_min)):
        w, d, l = ttt.torneo(f, rival, k)
        out[nombre] = (pct(w, k), pct(d, k), pct(l, k))
    return out


def media(filas, rival, i):
    return round(st.mean(f[rival][i] for f in filas), 1)


R = {}
t0 = time.time()
print("== referencias (con humano40)", flush=True)
R["base"] = {"azar": evalua(ttt.jugador_azar(), 2000, 500), "reglas": evalua(ttt.jugador_reglas(), 2000, 500),
             "minimax": evalua(ttt.jugador_minimax(), 2000, 500)}

print("== comparacion por episodios y seeds", flush=True)
comp = {}
for ep in (5000, 20000, 50000):
    for variante in ("autojuego_puro", "rivales_puro", "rivales_seguro"):
        filas = []
        for s in SEMILLAS:
            if variante == "autojuego_puro":
                ag = ttt.AgenteQ(alfa=0.3, seed=s).entrenar(ep)
                f = ttt.jugador_q(ag)
            else:
                ag = ttt.AgenteQ(alfa=0.3, seed=s).entrenar_rivales(ep)
                f = ttt.jugador_q(ag) if variante == "rivales_puro" else ttt.jugador_seguro(ag)
            filas.append(evalua(f))
        comp[f"{variante}|{ep}"] = {
            "azar_gana": media(filas, "azar", 0), "azar_pierde": media(filas, "azar", 2),
            "h20_gana": media(filas, "humano20", 0), "h20_pierde": media(filas, "humano20", 2),
            "h40_gana": media(filas, "humano40", 0), "h40_pierde": media(filas, "humano40", 2),
            "min_pierde": media(filas, "minimax", 2)}
        print(variante, ep, comp[f"{variante}|{ep}"], flush=True)
R["comparacion"] = comp

print("== modelos finales", flush=True)
ag_auto = ttt.AgenteQ.cargar("modelos/tres_en_raya_q_autojuego.json")  # primera ronda (auto-juego, 50 000 episodios)
ag_riv = ttt.AgenteQ(alfa=0.3, seed=2026).entrenar_rivales(20000)
ag_riv.guardar("modelos/tres_en_raya_q.json")
R["estados_q_final"] = len(ag_riv.q)
R["final"] = {
    "autojuego_puro": evalua(ttt.jugador_q(ag_auto), 5000, 2000),
    "rivales_puro": evalua(ttt.jugador_q(ag_riv), 5000, 2000),
    "producto_seguro": evalua(ttt.jugador_seguro(ag_riv), 5000, 2000),
}
for k, v in R["final"].items():
    print(k, v, flush=True)
R["segundos"] = round(time.time() - t0)
json.dump(R, open("resultados_rivales.json", "w"), indent=1)
print("FIN", R["segundos"], "s")
