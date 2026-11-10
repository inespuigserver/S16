from itertools import combinations
from heapq import heappush, heappop
from timeit import default_timer as timer

PRESUPUESTO = 100

jugadores = [
    ("Ortega","POR",9,5.8),
    ("Lunin","POR",6,4.6),
    ("Remiro","POR",4,3.9),

    ("Koundé","DEF",12,6.4),
    ("Mingueza","DEF",7,5.1),
    ("Vivian","DEF",5,4.2),
    ("Huijsen","DEF",9,5.4),
    ("Cucurella","DEF",11,5.9),
    ("Lejeune","DEF",3,3.1),
    ("Mosquera","DEF",6,4.5),

    ("Pedri","MED",18,8.1),
    ("Baena","MED",13,6.9),
    ("Sučić","MED",8,5.2),
    ("Barrios","MED",10,5.9),
    ("Fermín","MED",11,6.2),
    ("Gaya","MED",4,3.3),
    ("Arambarri","MED",6,4.4),

    ("Mbappé","DEL",24,9.6),
    ("Budimir","DEL",9,6.0),
    ("Oyarzabal","DEL",14,7.2),
    ("Iglesias","DEL",7,4.8),
]

CUPOS = {
    "POR": 1,
    "DEF": 4,
    "MED": 4,
    "DEL": 2
}


# =====================================================
# UTILIDADES
# =====================================================

def coste(equipo):
    return sum(j[2] for j in equipo)

def puntos(equipo):
    return sum(j[3] for j in equipo)


# =====================================================
# 1. VORAZ POR PUNTOS
# =====================================================

def voraz_puntos():
    equipo = []
    dinero = PRESUPUESTO

    for puesto, cantidad in CUPOS.items():
        disponibles = [j for j in jugadores if j[1] == puesto]
        disponibles.sort(key=lambda x: x[3], reverse=True)

        elegidos = []

        for jugador in disponibles:
            if len(elegidos) < cantidad:
                elegidos.append(jugador)

        equipo.extend(elegidos)

    if coste(equipo) <= PRESUPUESTO:
        return equipo

    return None


# =====================================================
# 1. VORAZ POR RATIO
# =====================================================

def voraz_ratio():
    equipo = []

    for puesto, cantidad in CUPOS.items():
        disponibles = [j for j in jugadores if j[1] == puesto]

        disponibles.sort(
            key=lambda x: x[3] / x[2],
            reverse=True
        )

        equipo.extend(disponibles[:cantidad])

    if coste(equipo) <= PRESUPUESTO:
        return equipo

    return None


# =====================================================
# 2. FUERZA BRUTA
# =====================================================

def fuerza_bruta():

    por = [j for j in jugadores if j[1] == "POR"]
    defs = [j for j in jugadores if j[1] == "DEF"]
    meds = [j for j in jugadores if j[1] == "MED"]
    dels = [j for j in jugadores if j[1] == "DEL"]

    mejor_equipo = None
    mejor_puntos = 0
    total_equipos = 0

    for p in combinations(por, 1):
        for d in combinations(defs, 4):
            for m in combinations(meds, 4):
                for dl in combinations(dels, 2):

                    equipo = list(p + d + m + dl)
                    total_equipos += 1

                    c = coste(equipo)

                    if c <= PRESUPUESTO:

                        pts = puntos(equipo)

                        if pts > mejor_puntos:
                            mejor_puntos = pts
                            mejor_equipo = equipo

    return mejor_equipo, mejor_puntos, total_equipos


# =====================================================
# BRANCH AND BOUND
# =====================================================

ordenados = sorted(
    jugadores,
    key=lambda x: x[3]/x[2],
    reverse=True
)

indice_puesto = {
    "POR": 0,
    "DEF": 1,
    "MED": 2,
    "DEL": 3
}


def cota_superior(i, presupuesto_restante, puntos_actuales):

    cota = puntos_actuales

    for k in range(i, len(ordenados)):
        nombre, puesto, precio, pts = ordenados[k]

        if presupuesto_restante >= precio:
            presupuesto_restante -= precio
            cota += pts
        else:
            cota += pts * (presupuesto_restante/precio)
            break

    return cota


def branch_and_bound():

    mejor_puntos = 0
    mejor_equipo = None
    nodos = 0

    raiz = (
        0,
        [],
        PRESUPUESTO,
        [0,0,0,0],
        0
    )

    cola = []

    heappush(
        cola,
        (-cota_superior(0, PRESUPUESTO, 0), raiz)
    )

    while cola:

        _, nodo = heappop(cola)

        i, equipo, dinero, cupos, pts_actuales = nodo

        nodos += 1

        if i == len(ordenados):

            if cupos == [1,4,4,2]:

                if pts_actuales > mejor_puntos:
                    mejor_puntos = pts_actuales
                    mejor_equipo = equipo

            continue

        if cota_superior(i, dinero, pts_actuales) <= mejor_puntos:
            continue

        jugador = ordenados[i]

        nombre, puesto, precio, pts = jugador

        idx = indice_puesto[puesto]

        # RAMA INCLUIR

        if (
            dinero >= precio
            and cupos[idx] < CUPOS[puesto]
        ):

            nuevos_cupos = cupos[:]
            nuevos_cupos[idx] += 1

            hijo = (
                i+1,
                equipo + [jugador],
                dinero-precio,
                nuevos_cupos,
                pts_actuales+pts
            )

            cota = cota_superior(
                i+1,
                dinero-precio,
                pts_actuales+pts
            )

            if cota > mejor_puntos:
                heappush(cola, (-cota, hijo))

        # RAMA NO INCLUIR

        hijo = (
            i+1,
            equipo,
            dinero,
            cupos,
            pts_actuales
        )

        cota = cota_superior(
            i+1,
            dinero,
            pts_actuales
        )

        if cota > mejor_puntos:
            heappush(cola, (-cota, hijo))

    return mejor_equipo, mejor_puntos, nodos


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    print("\n=== VORAZ POR PUNTOS ===")

    equipo = voraz_puntos()

    if equipo:
        print("Coste:", coste(equipo))
        print("Puntos:", puntos(equipo))

    print("\n=== VORAZ POR RATIO ===")

    equipo = voraz_ratio()

    if equipo:
        print("Coste:", coste(equipo))
        print("Puntos:", puntos(equipo))

    print("\n=== FUERZA BRUTA ===")

    t0 = timer()

    equipo_fb, pts_fb, total = fuerza_bruta()

    t1 = timer()

    print("Equipos posibles:", total)
    print("Óptimo:", pts_fb)
    print("Tiempo:", t1-t0)

    print("\n=== BRANCH AND BOUND ===")

    t0 = timer()

    equipo_bb, pts_bb, nodos = branch_and_bound()

    t1 = timer()

    print("Puntos:", pts_bb)
    print("Nodos abiertos:", nodos)
    print("Tiempo:", t1-t0)

    print("\nCoinciden:",
          abs(pts_fb - pts_bb) < 0.0001)