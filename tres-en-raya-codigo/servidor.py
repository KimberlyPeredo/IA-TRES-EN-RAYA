"""Servidor local del tres en raya. Solo usa la biblioteca estandar de Python.

Uso:  python servidor.py     y abrir http://localhost:8000 en el navegador.
El servidor aplica las reglas, valida cada jugada y calcula la respuesta de la IA; la pagina solo dibuja.
"""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from juegos import tres_en_raya as ttt

RAIZ = os.path.dirname(os.path.abspath(__file__))


def cargar_modelo():
    ruta = os.path.join(RAIZ, "modelos", "tres_en_raya_q.json")
    if os.path.exists(ruta):
        return ttt.AgenteQ.cargar(ruta)
    return ttt.AgenteQ(alfa=0.3, seed=2026).entrenar_rivales(20000)  # si falta el modelo, se entrena en segundos


Q = cargar_modelo()
IA = ttt.jugador_seguro(Q)


def estado(t):
    g = ttt.ganador(t)
    linea = next((l for l in ttt.LINEAS if t[l[0]] and t[l[0]] == t[l[1]] == t[l[2]]), None)
    return {"tablero": list(t), "fin": ttt.terminado(t), "ganador": g, "linea": linea}


def jugar(body):
    """body: tablero (9 enteros), ia (1 o 2: la ficha de la IA) y pos (casilla del humano, opcional).
    Valida el tablero (debe ser una posicion legal), la ficha, el turno y la casilla."""
    if not isinstance(body, dict) or not isinstance(body.get("tablero"), list):
        raise ValueError("tablero no valido")
    t = tuple(body["tablero"])
    if not ttt.tablero_legal(t):
        raise ValueError("tablero no valido")
    ia = body.get("ia", 2)
    if type(ia) is not int or ia not in (1, 2):
        raise ValueError("ficha no valida")
    pos = body.get("pos")
    if pos is not None:
        if type(pos) is not int or not 0 <= pos <= 8 or t[pos] != 0 or ttt.terminado(t):
            raise ValueError("jugada no valida")
        if ttt.turno(t) == ia:
            raise ValueError("no es el turno del humano")
        t = ttt.mover(t, pos, ttt.otro(ia))
    ia_pos = None
    if not ttt.terminado(t) and ttt.turno(t) == ia:
        ia_pos = IA(t, ia)
        t = ttt.mover(t, ia_pos, ia)
    r = estado(t)
    r["ia_pos"] = ia_pos
    return r


class Manejador(BaseHTTPRequestHandler):
    def _enviar(self, codigo, tipo, datos):
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            with open(os.path.join(RAIZ, "static", "index.html"), "rb") as f:
                self._enviar(200, "text/html; charset=utf-8", f.read())
        else:
            self._enviar(404, "text/plain", b"no encontrado")

    def do_POST(self):
        if self.path != "/api/ttt":
            return self._enviar(404, "text/plain", b"no encontrado")
        try:
            n = int(self.headers.get("Content-Length", 0))
            if not 0 <= n <= 4096:
                raise ValueError("cuerpo no valido")
            body = json.loads(self.rfile.read(n) or b"{}")
            self._enviar(200, "application/json", json.dumps(jugar(body)).encode())
        except (ValueError, KeyError, TypeError) as e:
            self._enviar(400, "application/json", json.dumps({"error": str(e)}).encode())

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    puerto = int(os.environ.get("PUERTO", 8000))
    print(f"Juego listo en http://localhost:{puerto}  (Ctrl+C para salir)")
    ThreadingHTTPServer(("127.0.0.1", puerto), Manejador).serve_forever()
