"""Tres en raya, primera ronda: Q-learning por auto-juego (curva por episodios y eleccion de hiperparametros).

Uso:  python entrenar_autojuego.py            (unos 4 minutos)
      python entrenar_autojuego.py --rapido   (version corta)
"""
import json
import random
import statistics as st
import sys
import time

from juegos import tres_en_raya as ttt

RAPIDO = "--rapido" in sys.argv
SEMILLAS = [11, 22, 33, 44, 55] if not RAPIDO else [11, 22]
R = {}


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def pct(x, n):
    return round(100.0 * x / n, 1)


# =============================================================== TRES EN RAYA
def evalua_ttt(f, n_azar=2000, n_hum=2000, n_min=500):
    random.seed(1234)
    w, d, l = ttt.torneo(f, ttt.jugador_azar(), n_azar)
    wh, dh, lh = ttt.torneo(f, ttt.jugador_humano_simulado(0.2), n_hum)
    wm, dm, lm = ttt.torneo(f, ttt.jugador_minimax(), n_min)
    return {"azar": (pct(w, n_azar), pct(d, n_azar), pct(l, n_azar)),
            "humano20": (pct(wh, n_hum), pct(dh, n_hum), pct(lh, n_hum)),
            "minimax": (pct(wm, n_min), pct(dm, n_min), pct(lm, n_min))}


def bloque_ttt():
    log("== Tres en raya: referencias")
    R["ttt_estados"] = ttt.contar_estados()
    R["ttt_base"] = {
        "azar": evalua_ttt(ttt.jugador_azar()),
        "reglas": evalua_ttt(ttt.jugador_reglas()),
        "minimax": evalua_ttt(ttt.jugador_minimax()),
    }
    log(R["ttt_base"])

    log("== Tres en raya: curva por episodios")
    eps_lista = [200, 500, 1000, 2000, 5000, 10000, 20000, 50000] if not RAPIDO else [500, 5000]
    curva = {}
    for ep in eps_lista:
        filas = []
        for s in SEMILLAS:
            ag = ttt.AgenteQ(alfa=0.3, seed=s).entrenar(ep)
            filas.append(evalua_ttt(ttt.jugador_q(ag), 1000, 1000, 300))
        curva[ep] = {
            "vs_azar_gana": round(st.mean(f["azar"][0] for f in filas), 1),
            "vs_azar_pierde": round(st.mean(f["azar"][2] for f in filas), 1),
            "vs_hum_gana": round(st.mean(f["humano20"][0] for f in filas), 1),
            "vs_hum_pierde": round(st.mean(f["humano20"][2] for f in filas), 1),
            "vs_min_pierde": round(st.mean(f["minimax"][2] for f in filas), 1),
            "vs_min_pierde_max": max(f["minimax"][2] for f in filas),
        }
        log("episodios", ep, curva[ep])
    R["ttt_curva"] = curva

    log("== Tres en raya: eleccion de alfa (20000 episodios)")
    alfas = {}
    for alfa in (0.1, 0.3, 0.5, 0.9):
        filas = []
        for s in SEMILLAS:
            ag = ttt.AgenteQ(alfa=alfa, seed=s).entrenar(20000 if not RAPIDO else 3000)
            filas.append(evalua_ttt(ttt.jugador_q(ag), 1000, 1000, 300))
        alfas[alfa] = {"vs_azar_gana": round(st.mean(f["azar"][0] for f in filas), 1),
                       "vs_min_pierde": round(st.mean(f["minimax"][2] for f in filas), 1),
                       "vs_hum_gana": round(st.mean(f["humano20"][0] for f in filas), 1)}
        log("alfa", alfa, alfas[alfa])
    R["ttt_alfa"] = alfas

    log("== Tres en raya: fraccion de partidas contra rival aleatorio (20000 episodios, alfa 0.3)")
    opos = {}
    for fr in (0.0, 0.3, 0.6):
        filas = []
        for s in SEMILLAS:
            ag = ttt.AgenteQ(alfa=0.3, seed=s).entrenar(20000 if not RAPIDO else 3000, oponente_aleatorio=fr)
            filas.append(evalua_ttt(ttt.jugador_q(ag), 1000, 1000, 300))
        opos[fr] = {"vs_azar_gana": round(st.mean(f["azar"][0] for f in filas), 1),
                    "vs_azar_pierde": round(st.mean(f["azar"][2] for f in filas), 1),
                    "vs_min_pierde": round(st.mean(f["minimax"][2] for f in filas), 1),
                    "vs_hum_gana": round(st.mean(f["humano20"][0] for f in filas), 1),
                    "vs_hum_pierde": round(st.mean(f["humano20"][2] for f in filas), 1)}
        log("fraccion azar", fr, opos[fr])
    R["ttt_oponente"] = opos

    log("== Tres en raya: modelo final")
    ag = ttt.AgenteQ(alfa=0.3, seed=2026).entrenar(50000 if not RAPIDO else 5000)
    ag.guardar("modelos/tres_en_raya_q_autojuego.json")
    R["ttt_final_estados_q"] = len(ag.q)
    R["ttt_final"] = {
        "q": evalua_ttt(ttt.jugador_q(ag), 5000, 5000, 2000),
        "hibrido": evalua_ttt(ttt.jugador_hibrido(ag), 5000, 5000, 2000),
    }
    # el producto: IA = O (segundo) o X (primero) contra humano simulado, con/sin error
    log(R["ttt_final"])



if __name__ == "__main__":
    t0 = time.time()
    bloque_ttt()
    R["segundos_total"] = round(time.time() - t0)
    json.dump(R, open("resultados_autojuego.json", "w"), indent=1, default=str)
    log("FIN", R["segundos_total"], "s")
