"""Tres en raya: reglas, IA clasica (minimax con poda alfa-beta) e IA aprendida (Q-learning).

Representacion: tupla de 9 enteros. 0 = vacia, 1 = jugador 1 (X), 2 = jugador 2 (O).
Las posiciones van de 0 a 8, por filas (arriba-izquierda = 0, abajo-derecha = 8).
"""
import json
import random
from functools import lru_cache

LINEAS = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))
VACIO = (0,) * 9


def otro(j):
    return 3 - j


def ganador(t):
    """Devuelve 1 o 2 si hay linea completa, 0 si no."""
    for a, b, c in LINEAS:
        if t[a] and t[a] == t[b] == t[c]:
            return t[a]
    return 0


def jugadas(t):
    return [i for i in range(9) if t[i] == 0]


def terminado(t):
    return ganador(t) != 0 or 0 not in t


def turno(t):
    """Quien mueve segun las fichas puestas (X empieza): 1 si hay igual cantidad, 2 si hay una X de mas."""
    return 1 if t.count(1) == t.count(2) else 2


def tablero_legal(t):
    """True si t es una posicion alcanzable jugando bien las reglas: 9 casillas con 0, 1 o 2 (sin
    booleanos), X con igual o una ficha mas que O, y sin ganadores imposibles."""
    if len(t) != 9 or any(type(x) is not int or x not in (0, 1, 2) for x in t):
        return False
    x, o = t.count(1), t.count(2)
    if x not in (o, o + 1):
        return False
    gana_x = any(t[a] == t[b] == t[c] == 1 for a, b, c in LINEAS)
    gana_o = any(t[a] == t[b] == t[c] == 2 for a, b, c in LINEAS)
    if gana_x and gana_o:
        return False
    return not (gana_x and x != o + 1) and not (gana_o and x != o)


def mover(t, pos, j):
    l = list(t)
    l[pos] = j
    return tuple(l)


# ------------------------------------------------------------------ IA clasica
@lru_cache(maxsize=None)
def _valor(t, j):
    """Valor minimax (+1 gana j, 0 empate, -1 pierde j) con j a mover. Poda alfa-beta en _ab."""
    return _ab(t, j, -2, 2)


def _ab(t, j, alfa, beta):
    g = ganador(t)
    if g:
        return 1 if g == j else -1
    if 0 not in t:
        return 0
    mejor = -2
    for p in jugadas(t):
        v = -_ab(mover(t, p, j), otro(j), -beta, -alfa)
        if v > mejor:
            mejor = v
        if mejor > alfa:
            alfa = mejor
        if alfa >= beta:
            break
    return mejor


def minimax_valores(t, j):
    """Valor exacto de cada jugada posible para j (sin poda en la raiz, para poder comparar)."""
    return {p: -_valor(mover(t, p, j), otro(j)) for p in jugadas(t)}


def jugada_minimax(t, j, rng=random):
    v = minimax_valores(t, j)
    m = max(v.values())
    return rng.choice([p for p, x in v.items() if x == m])


# ------------------------------------------------------------- IA aprendida (Q-learning)
def _vista(t, j):
    """Estado visto desde j: sus fichas = 1, las del rival = 2."""
    if j == 1:
        return t
    return tuple({0: 0, 1: 2, 2: 1}[x] for x in t)


class AgenteQ:
    """Q-learning tabular. Un solo Q para ambos jugadores gracias a la vista normalizada y la
    actualizacion tipo negamax: Q(s,a) <- Q + alfa * (r - max_a' Q(s',a') - Q)."""

    def __init__(self, alfa=0.3, gamma=1.0, epsilon=1.0, eps_min=0.05, seed=None):
        self.q = {}
        self.alfa, self.gamma = alfa, gamma
        self.epsilon, self.eps_min = epsilon, eps_min
        self.rng = random.Random(seed)

    def _qs(self, s):
        return self.q.setdefault(s, {})

    def valor(self, s, a):
        return self._qs(s).get(a, 0.0)

    def mejor(self, t, j, explorar=False):
        s = _vista(t, j)
        libres = jugadas(t)
        if explorar and self.rng.random() < self.epsilon:
            return self.rng.choice(libres)
        qs = [(self.valor(s, a), a) for a in libres]
        m = max(v for v, _ in qs)
        return self.rng.choice([a for v, a in qs if v == m])

    def conocido(self, t, j):
        return _vista(t, j) in self.q

    def entrenar(self, episodios, oponente_aleatorio=0.3, decaer=True):
        """Auto-juego (y una fraccion de partidas contra un rival aleatorio para ver mas errores)."""
        for ep in range(episodios):
            if decaer:
                self.epsilon = max(self.eps_min, 1.0 - ep / (0.8 * episodios))
            vs_azar = self.rng.random() < oponente_aleatorio
            azar_es = self.rng.choice((1, 2)) if vs_azar else 0
            t, j = VACIO, 1
            previo = {1: None, 2: None}  # (estado, accion) pendiente de cada jugador
            while True:
                if j == azar_es:
                    a = self.rng.choice(jugadas(t))
                    t = mover(t, a, j)
                else:
                    s = _vista(t, j)
                    a = self.mejor(t, j, explorar=True)
                    previo[j] = (s, a)
                    t = mover(t, a, j)
                g = ganador(t)
                if g or 0 not in t:
                    # recompensa final: +1 quien gana, -1 quien pierde, 0 empate
                    for jj in (1, 2):
                        if previo[jj] and jj != azar_es:
                            r = 0.0 if g == 0 else (1.0 if g == jj else -1.0)
                            s0, a0 = previo[jj]
                            old = self.valor(s0, a0)
                            self._qs(s0)[a0] = old + self.alfa * (r - old)
                    break
                # actualizacion del jugador que acaba de mover (bootstrap con el valor del rival)
                if previo[j] and j != azar_es:
                    s0, a0 = previo[j]
                    s1 = _vista(t, otro(j))
                    mx = max(self.valor(s1, b) for b in jugadas(t))
                    old = self.valor(s0, a0)
                    self._qs(s0)[a0] = old + self.alfa * (self.gamma * (-mx) - old)
                j = otro(j)
        return self

    def guardar(self, ruta):
        data = {"".join(map(str, s)): {str(a): v for a, v in d.items()} for s, d in self.q.items()}
        with open(ruta, "w") as f:
            json.dump(data, f)

    @classmethod
    def cargar(cls, ruta):
        ag = cls(epsilon=0.0)
        with open(ruta) as f:
            data = json.load(f)
        ag.q = {tuple(int(c) for c in k): {int(a): v for a, v in d.items()} for k, d in data.items()}
        return ag


def jugadas_seguras(t, j):
    """Jugadas con el mejor valor minimax: las que no empeoran el resultado perfecto."""
    v = minimax_valores(t, j)
    m = max(v.values())
    return [p for p, x in v.items() if x == m]


def _rival_ruidoso(error, rng):
    """Rival del entrenamiento: perfecto salvo que, con probabilidad `error`, mueve al azar."""
    def f(t, j):
        if rng.random() < error:
            return rng.choice(jugadas(t))
        return jugada_minimax(t, j, rng)
    return f


def entrenar_rivales(self, episodios, errores=(0.1, 0.2, 0.3, 0.5, 1.0)):
    """Q-learning de un solo agente: el rival (con distintos niveles de error) forma parte del
    entorno. Q(s,a) <- Q + alfa * (r + gamma * max_a' Q(s',a') - Q), con s' el siguiente estado en
    el que le toca mover al agente. El agente aprende que jugadas dejan mas oportunidades de error."""
    for ep in range(episodios):
        self.epsilon = max(self.eps_min, 1.0 - ep / (0.8 * episodios))
        rival = _rival_ruidoso(self.rng.choice(errores), self.rng)
        yo = self.rng.choice((1, 2))
        t, j = VACIO, 1
        previo = None  # (estado, accion) del agente pendiente de actualizar
        while True:
            if j == yo:
                s = _vista(t, yo)
                if previo is not None:  # recibe el estado en el que vuelve a mover
                    s0, a0 = previo
                    mx = max(self.valor(s, b) for b in jugadas(t))
                    old = self.valor(s0, a0)
                    self._qs(s0)[a0] = old + self.alfa * (self.gamma * mx - old)
                a = self.mejor(t, yo, explorar=True)
                previo = (s, a)
                t = mover(t, a, yo)
            else:
                t = mover(t, rival(t, j), j)
            g = ganador(t)
            if g or 0 not in t:
                r = 0.0 if g == 0 else (1.0 if g == yo else -1.0)
                s0, a0 = previo
                old = self.valor(s0, a0)
                self._qs(s0)[a0] = old + self.alfa * (r - old)
                break
            j = otro(j)
    return self


AgenteQ.entrenar_rivales = entrenar_rivales


def jugador_seguro(agente, rng=random):
    """Producto: minimax filtra las jugadas que no pierden terreno (nunca se pierde si se puede
    evitar) y el agente aprendido elige, entre ellas, la de mayor valor Q."""
    def f(t, j):
        seg = jugadas_seguras(t, j)
        s = _vista(t, j)
        qs = [(agente.valor(s, a), a) for a in seg]
        m = max(v for v, _ in qs)
        return rng.choice([a for v, a in qs if v == m])
    return f


# --------------------------------------------------------------- jugadores para pruebas
def jugador_azar(rng=random):
    return lambda t, j: rng.choice(jugadas(t))


def jugador_reglas(rng=random):
    """Modelo base heuristico: gana si puede, bloquea si debe, si no centro > esquinas > lados."""
    def f(t, j):
        for obj in (j, otro(j)):
            for p in jugadas(t):
                if ganador(mover(t, p, obj)) == obj:
                    return p
        for p in (4, 0, 2, 6, 8, 1, 3, 5, 7):
            if t[p] == 0:
                return p
    return f


def jugador_humano_simulado(error, rng=random):
    """Juega perfecto salvo que, con probabilidad `error`, mueve al azar (proxy de un humano)."""
    def f(t, j):
        if rng.random() < error:
            return rng.choice(jugadas(t))
        return jugada_minimax(t, j, rng)
    return f


def jugador_minimax(rng=random):
    return lambda t, j: jugada_minimax(t, j, rng)


def jugador_q(agente):
    return lambda t, j: agente.mejor(t, j, explorar=False)


def jugador_hibrido(agente, rng=random):
    """Producto final: usa la tabla Q; si el estado nunca se vio en el entrenamiento, delega
    en minimax (componente clasico)."""
    def f(t, j):
        if agente.conocido(t, j):
            return agente.mejor(t, j)
        return jugada_minimax(t, j, rng)
    return f


def partida(f1, f2):
    """Juega f1 (jugador 1) contra f2 (jugador 2). Devuelve ganador (0 = empate)."""
    t, j = VACIO, 1
    fs = {1: f1, 2: f2}
    while not terminado(t):
        t = mover(t, fs[j](t, j), j)
        j = otro(j)
    return ganador(t)


def torneo(fa, fb, n=2000):
    """fa contra fb, mitad de partidas con fa como X y mitad como O. Devuelve (gana_a, empates, pierde_a)."""
    w = d = l = 0
    for i in range(n):
        if i % 2 == 0:
            g, mia = partida(fa, fb), 1
        else:
            g, mia = partida(fb, fa), 2
        if g == 0:
            d += 1
        elif g == mia:
            w += 1
        else:
            l += 1
    return w, d, l


def contar_estados():
    """Cuenta las posiciones legales alcanzables (para el analisis del dominio)."""
    vistos, pila = {VACIO}, [VACIO]
    while pila:
        t = pila.pop()
        if terminado(t):
            continue
        j = turno(t)
        for p in jugadas(t):
            n = mover(t, p, j)
            if n not in vistos:
                vistos.add(n)
                pila.append(n)
    return len(vistos)
