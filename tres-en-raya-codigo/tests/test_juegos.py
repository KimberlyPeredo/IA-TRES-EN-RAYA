import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from juegos import tres_en_raya as ttt


class TresEnRaya(unittest.TestCase):
    def test_detecta_ganador_fila(self):
        self.assertEqual(ttt.ganador((1, 1, 1, 2, 2, 0, 0, 0, 0)), 1)

    def test_detecta_ganador_diagonal(self):
        self.assertEqual(ttt.ganador((2, 1, 1, 0, 2, 0, 1, 0, 2)), 2)

    def test_empate(self):
        t = (1, 2, 1, 1, 2, 2, 2, 1, 1)
        self.assertTrue(ttt.terminado(t))
        self.assertEqual(ttt.ganador(t), 0)

    def test_minimax_gana_si_puede(self):
        t = (1, 1, 0, 2, 2, 0, 0, 0, 0)
        self.assertEqual(ttt.jugada_minimax(t, 1), 2)

    def test_minimax_bloquea(self):
        t = (2, 2, 0, 0, 1, 0, 0, 0, 1)  # O amenaza ganar en la casilla 2; X debe bloquear ahi
        self.assertEqual(ttt.jugada_minimax(t, 1), 2)

    def test_minimax_empata_contra_minimax(self):
        random.seed(0)
        self.assertEqual(ttt.torneo(ttt.jugador_minimax(), ttt.jugador_minimax(), 50), (0, 50, 0))

    def test_ia_segura_no_pierde_contra_minimax(self):
        ag = ttt.AgenteQ(alfa=0.3, seed=7).entrenar_rivales(20000)
        random.seed(0)
        w, d, l = ttt.torneo(ttt.jugador_seguro(ag), ttt.jugador_minimax(), 200)
        self.assertEqual(l, 0)

    def test_ia_segura_gana_a_jugador_que_se_equivoca(self):
        ag = ttt.AgenteQ(alfa=0.3, seed=7).entrenar_rivales(20000)
        random.seed(0)
        w, d, l = ttt.torneo(ttt.jugador_seguro(ag), ttt.jugador_azar(), 500)
        self.assertGreater(w / 500, 0.90)
        self.assertEqual(l, 0)

    def test_estados_legales(self):
        self.assertEqual(ttt.contar_estados(), 5478)

    def test_tablero_legal_coincide_con_los_estados_alcanzables(self):
        from itertools import product
        legales = sum(ttt.tablero_legal(t) for t in product((0, 1, 2), repeat=9))
        self.assertEqual(legales, 5478)

    def test_tablero_imposible(self):
        self.assertFalse(ttt.tablero_legal((1, 1, 1, 1, 0, 0, 0, 0, 0)))   # 4 X y 0 O
        self.assertFalse(ttt.tablero_legal((1, 1, 1, 2, 2, 2, 0, 0, 0)))   # dos ganadores
        self.assertFalse(ttt.tablero_legal((True, 0, 0, 0, 0, 0, 0, 0, 0)))  # booleano

    def test_servidor_rechaza_jugada_fuera_de_turno(self):
        import servidor
        with self.assertRaises(ValueError):  # la IA es O pero le toca a O: el humano no puede mover
            servidor.jugar({"tablero": [1, 0, 0, 0, 0, 0, 0, 0, 0], "ia": 2, "pos": 4})

    def test_servidor_rechaza_tablero_imposible_y_casilla_booleana(self):
        import servidor
        with self.assertRaises(ValueError):
            servidor.jugar({"tablero": [1, 1, 0, 1, 0, 0, 0, 0, 0], "ia": 2, "pos": 8})
        with self.assertRaises(ValueError):
            servidor.jugar({"tablero": [0] * 9, "ia": 2, "pos": True})


if __name__ == "__main__":
    unittest.main(verbosity=2)
