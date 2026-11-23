"""Analisis del espacio de juego y de los resultados (herramientas vistas en clase).

Usa networkx (grafo del juego), pandas (tablas) y matplotlib (graficos). El producto (servidor.py)
NO las necesita: este script es solo para el analisis del documento.
    pip install networkx pandas matplotlib
    python analisis.py        ->  escribe tablas en analisis/ y figuras en figuras/
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from juegos import tres_en_raya as ttt

os.makedirs("analisis", exist_ok=True)
os.makedirs("figuras", exist_ok=True)

# ---------------------------------------------------------------- 1. grafo del juego (networkx)
# Nodo = posicion legal; arista = una jugada legal. Se construye desde el tablero vacio.
G = nx.DiGraph()
G.add_node(ttt.VACIO)
pila = [ttt.VACIO]
while pila:
    t = pila.pop()
    if ttt.terminado(t):
        continue
    j = ttt.turno(t)
    for p in ttt.jugadas(t):
        n = ttt.mover(t, p, j)
        if n not in G:
            pila.append(n)
        G.add_edge(t, n)

terminales = [t for t in G if G.out_degree(t) == 0]
resumen = {
    "posiciones (nodos)": G.number_of_nodes(),
    "jugadas (aristas)": G.number_of_edges(),
    "posiciones terminales": len(terminales),
    "terminales: gana X": sum(ttt.ganador(t) == 1 for t in terminales),
    "terminales: gana O": sum(ttt.ganador(t) == 2 for t in terminales),
    "terminales: empate": sum(ttt.ganador(t) == 0 for t in terminales),
    "es un grafo sin ciclos": nx.is_directed_acyclic_graph(G),
    "partida mas larga (jugadas)": nx.dag_longest_path_length(G),
}
# numero de partidas distintas = caminos desde el tablero vacio hasta una terminal (DP sobre el DAG)
caminos = {t: 1 if G.out_degree(t) == 0 else 0 for t in G}
for t in reversed(list(nx.topological_sort(G))):
    if G.out_degree(t):
        caminos[t] = sum(caminos[h] for h in G.successors(t))
resumen["partidas distintas posibles"] = caminos[ttt.VACIO]
for k, v in resumen.items():
    print(f"{k}: {v}")
pd.Series(resumen, name="valor").to_csv("analisis/espacio_de_juego.csv", header=True)

# posiciones por numero de fichas puestas (profundidad)
prof = pd.Series([9 - t.count(0) for t in G]).value_counts().sort_index()
tabla_prof = pd.DataFrame({"fichas": prof.index, "posiciones": prof.values})
print(tabla_prof.to_string(index=False))
tabla_prof.to_csv("analisis/posiciones_por_profundidad.csv", index=False)

# posiciones del arbol de la IA: cuantas jugadas "seguras" tiene en cada posicion del grafo
seguras = [len(ttt.jugadas_seguras(t, ttt.turno(t))) for t in G if not ttt.terminado(t)]
print("jugadas seguras por posicion (media):", round(sum(seguras) / len(seguras), 2))

fig, ax = plt.subplots(figsize=(6.5, 3.6))
ax.bar(tabla_prof["fichas"], tabla_prof["posiciones"], color="#3b82f6")
ax.set_xlabel("Fichas en el tablero")
ax.set_ylabel("Posiciones legales")
ax.set_title("Espacio de juego del tres en raya: 5 478 posiciones")
ax.set_xticks(range(10))
plt.tight_layout()
plt.savefig("figuras/posiciones_por_profundidad.png", dpi=150)
plt.close()

# ---------------------------------------------------------------- 2. resultados (pandas + matplotlib)
auto = json.load(open("resultados_autojuego.json"))
curva = pd.DataFrame(auto["ttt_curva"]).T
curva.index = curva.index.astype(int)
curva = curva.sort_index()
curva.to_csv("analisis/curva_autojuego.csv", index_label="episodios")

fig, ax = plt.subplots(figsize=(6.5, 3.8))
ax.plot(curva.index, curva["vs_min_pierde"], "o-", color="#d9534f", label="Derrotas contra minimax")
ax.plot(curva.index, curva["vs_azar_gana"], "s-", color="#2e8b57", label="Victorias contra aleatorio")
ax.plot(curva.index, curva["vs_hum_gana"], "^-", color="#3b82f6", label="Victorias contra humano 20 %")
ax.set_xscale("log")
ax.set_xlabel("Episodios de entrenamiento (auto-juego)")
ax.set_ylabel("%")
ax.set_title("Curva de aprendizaje del Q-learning por auto-juego")
ax.legend(fontsize=8)
ax.grid(alpha=.3)
plt.tight_layout()
plt.savefig("figuras/curva_aprendizaje.png", dpi=150)
plt.close()

riv = json.load(open("resultados_rivales.json"))
comp = pd.DataFrame(riv["comparacion"]).T
comp.index = pd.MultiIndex.from_tuples([tuple(k.split("|")) for k in comp.index], names=["variante", "episodios"])
comp = comp.reset_index().astype({"episodios": int}).sort_values(["episodios", "variante"])
comp.to_csv("analisis/comparacion_variantes.csv", index=False)
print(comp[["variante", "episodios", "min_pierde", "azar_gana", "h20_gana", "h40_gana"]].to_string(index=False))

pivote = comp.pivot(index="episodios", columns="variante", values="min_pierde")
ax = pivote.plot(kind="bar", figsize=(6.5, 3.8), color=["#d9534f", "#f0ad4e", "#2e8b57"])
ax.set_ylabel("Derrotas contra minimax (%)")
ax.set_title("Derrotas contra minimax por variante y episodios")
ax.legend(fontsize=8)
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("figuras/derrotas_por_variante.png", dpi=150)
plt.close()
print("Listo: tablas en analisis/ y figuras en figuras/")
