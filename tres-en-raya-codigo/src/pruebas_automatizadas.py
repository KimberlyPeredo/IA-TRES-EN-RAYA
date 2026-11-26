"""
Suite de Pruebas Automatizadas - Proyecto Integrador Tres en Raya IA
Verifica casos de prueba unitarios (Fase 1) y simulaciones de 1.500 partidas (Fase 3).
"""

import random
from ia_engine import TresEnRayaIA


def ejecutar_pruebas():
    print("=== SUITE DE PRUEBAS AUTOMATIZADAS: TRES EN RAYA IA ===")
    ia = TresEnRayaIA(dificultad="Invencible (IA Híbrida)")

    # CP-01: Bloqueo de amenaza inmediata del humano
    b1 = [-1, -1, 0, 0, 1, 0, 0, 0, 0]
    j1, _ = ia.elegir_jugada(b1)
    assert j1 == 2, f"Fallo CP-01: esperado 2, obtenido {j1}"
    print("[OK] CP-01 (Bloqueo amenaza en casilla 2): Esperado=2, Obtenido=2")

    # CP-02: Victoria inmediata en 1 movimiento
    b2 = [1, 1, 0, -1, -1, 0, 0, 0, 0]
    j2, _ = ia.elegir_jugada(b2)
    assert j2 == 2, f"Fallo CP-02: esperado 2, obtenido {j2}"
    print("[OK] CP-02 (Victoria directa en casilla 2): Esperado=2, Obtenido=2")

    # CP-03: Respuesta óptima ante apertura humana en esquina (debe tomar el centro = 4)
    b3 = [-1, 0, 0, 0, 0, 0, 0, 0, 0]
    j3, _ = ia.elegir_jugada(b3)
    assert j3 == 4, f"Fallo CP-03: esperado 4, obtenido {j3}"
    print("[OK] CP-03 (Control estratégico del centro ante esquina): Esperado=4, Obtenido=4")

    # CP-04: Simulación de 1.500 partidas (500 vs Aleatorio, 500 vs Subóptimo, 500 vs Óptimo)
    random.seed(42)
    for perfil in ["aleatorio", "suboptimo", "optimo"]:
        v_ia, emp, d_ia = 0, 0, 0
        for g in range(500):
            b = [0] * 9
            turno = 1 if g % 2 == 0 else -1
            while True:
                res = TresEnRayaIA.check_winner(b)
                if res is not None:
                    if res == 1:
                        v_ia += 1
                    elif res == 0:
                        emp += 1
                    else:
                        d_ia += 1
                    break
                if turno == 1:
                    mv, _ = ia.elegir_jugada(b)
                    b[mv] = 1
                else:
                    libres = [i for i in range(9) if b[i] == 0]
                    if perfil == "aleatorio":
                        mv = random.choice(libres)
                    elif perfil == "suboptimo":
                        if random.random() < 0.70:
                            mv, _ = ia.elegir_jugada([-x for x in b])
                        else:
                            mv = random.choice(libres)
                    else:
                        mv, _ = ia.elegir_jugada([-x for x in b])
                    b[mv] = -1
                turno = -turno
        print(f"[OK] Simulación 500 partidas vs {perfil.upper():<9}: Victorias IA={v_ia}, Empates={emp}, Derrotas IA={d_ia}")


if __name__ == "__main__":
    ejecutar_pruebas()
