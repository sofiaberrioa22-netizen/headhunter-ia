"""Paso 2: algoritmo genético que elige al CEO junto con su mandato de 100 días.

Cromosoma (7 genes): [candidato, foundry, IA, CPU-DC, PC-IA, costos, alianzas], intensidades 0..3.
"""
import itertools
import random

import numpy as np

from core.datos import CRITERIOS, FRENTES

MAPA_COMPETENCIA = {  # cómo se combinan los criterios del candidato en la competencia de cada frente
    "foundry": {"manufactura": 0.6, "ecosistema": 0.25, "tecnologia": 0.15},
    "aceleradores_ia": {"ia": 0.6, "tecnologia": 0.4},
    "cpu_data_center": {"tecnologia": 0.5, "ecosistema": 0.3, "ia": 0.2},
    "pc_ia": {"tecnologia": 0.5, "ecosistema": 0.5},
    "eficiencia_costos": {"finanzas": 0.6, "transformacion": 0.4},
    "alianzas": {"ecosistema": 0.6, "gobernanza": 0.4},
}
MAX_FOCO, NIVELES = 9, 4
PLANES = np.array(list(itertools.product(range(NIVELES), repeat=len(FRENTES))))  # 4.096 planes posibles


def ajuste_estrategico(c, pesos):
    """Promedio ponderado (0-10) de los 8 criterios con los pesos que definió el LLM en el Paso 0."""
    return sum(pesos[k] * c[k] for k in CRITERIOS)


def competencia(c, frente):
    return sum(w * c[k] for k, w in MAPA_COMPETENCIA[frente].items())


def indice_plan(plan):
    return int(sum(v * NIVELES ** (len(plan) - 1 - j) for j, v in enumerate(plan)))


def tabla_fitness(pool, prioridades):
    """Fitness de las 4.096 combinaciones de plan para cada candidato del pool (matriz n × 4.096).

    F = 0.45·ajuste/10 + 0.55·3·Σ p_f·(intensidad_f/3)·(competencia_f/10)
        − 0.15·exceso_foco − 0.05·riesgo_ejecución − 0.06·foundry_sin_clientes − 0.05·conflicto
        − 0.10·(1 − grado difuso)
    """
    prior = np.array([prioridades[f] for f in FRENTES])
    tabla = np.zeros((len(pool), len(PLANES)))
    for i, c in enumerate(pool):
        comp = np.array([competencia(c, f) for f in FRENTES])
        valor_plan = (PLANES / 3 * prior * comp / 10).sum(axis=1)
        exceso = np.maximum(0, PLANES.sum(axis=1) - MAX_FOCO)
        riesgo_ejec = ((PLANES == 3) & (comp < 6)).sum(axis=1)
        # Lección de IDM 2.0: invertir fuerte en foundry sin un frente de alianzas/clientes es un error
        foundry_sin_clientes = ((PLANES[:, 0] >= 2) & (PLANES[:, 5] == 0)).astype(float)
        conflicto = 1.0 if "riesgo_conflicto" in c["hechos"] else 0.0
        brecha = 1.0 - c.get("grado", 1.0)  # Sprint 4: cuánto le falta para cumplir los requisitos
        tabla[i] = (0.45 * c["ajuste"] / 10 + 0.55 * valor_plan * 3 - 0.15 * exceso - 0.05 * riesgo_ejec
                    - 0.06 * foundry_sin_clientes - 0.05 * conflicto - 0.10 * brecha)
    return tabla


def algoritmo_genetico(tabla, tam_pob=40, generaciones=60, p_mut=0.15, p_cand=0.10, elite=2, semilla=42):
    """Torneo (k=3), cruce uniforme, mutación (cambio de candidato o ±1 en un frente) y elitismo."""
    rnd = random.Random(semilla)
    n = tabla.shape[0]
    fit = lambda ind: float(tabla[ind[0], indice_plan(ind[1:])])

    poblacion = [[rnd.randrange(n)] + [rnd.randrange(NIVELES) for _ in FRENTES] for _ in range(tam_pob)]
    hist = {"mejor": [], "promedio": [], "proporcion": [[] for _ in range(n)], "mejor_ind": []}
    for _ in range(generaciones):
        aptitudes = [fit(ind) for ind in poblacion]
        orden = sorted(range(tam_pob), key=lambda i: aptitudes[i], reverse=True)
        hist["mejor"].append(aptitudes[orden[0]])
        hist["promedio"].append(sum(aptitudes) / tam_pob)
        hist["mejor_ind"].append(poblacion[orden[0]][:])
        for i in range(n):
            hist["proporcion"][i].append(sum(ind[0] == i for ind in poblacion) / tam_pob)

        def torneo():
            elegidos = rnd.sample(range(tam_pob), 3)
            return poblacion[max(elegidos, key=lambda i: aptitudes[i])]

        nueva = [poblacion[i][:] for i in orden[:elite]]
        while len(nueva) < tam_pob:
            p1, p2 = torneo(), torneo()
            h1, h2 = p1[:], p2[:]
            if rnd.random() < 0.9:  # cruce uniforme: cada gen se intercambia con probabilidad 0.5
                for j in range(len(h1)):
                    if rnd.random() < 0.5:
                        h1[j], h2[j] = p2[j], p1[j]
            for h in (h1, h2):
                if rnd.random() < p_cand:
                    h[0] = rnd.randrange(n)
                for j in range(1, len(h)):
                    if rnd.random() < p_mut:
                        h[j] = min(NIVELES - 1, max(0, h[j] + rnd.choice([-1, 1])))
                nueva.append(h)
        poblacion = nueva[:tam_pob]

    aptitudes = [fit(ind) for ind in poblacion]
    k = int(np.argmax(aptitudes))
    return {"mejor": poblacion[k], "fitness": aptitudes[k], "hist": hist}


def busqueda_exhaustiva(tabla):
    """Verificación: el espacio es pequeño, así que se puede recorrer completo."""
    i, j = np.unravel_index(int(np.argmax(tabla)), tabla.shape)
    optimo = [int(i)] + PLANES[j].tolist()
    ranking = []
    for c in range(tabla.shape[0]):
        k = int(np.argmax(tabla[c]))
        ranking.append({"idx": c, "plan": PLANES[k].tolist(), "fitness": float(tabla[c, k])})
    ranking.sort(key=lambda r: r["fitness"], reverse=True)
    return {"optimo": optimo, "fitness": float(tabla.max()), "ranking": ranking, "total": tabla.size}
