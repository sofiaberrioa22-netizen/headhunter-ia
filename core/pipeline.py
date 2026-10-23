"""Orquesta los pasos 1 a 4 a partir de la configuración que produjo el Paso 0."""
import numpy as np

from core.datos import CANDIDATOS, FRENTES
from core.difuso import filtro_difuso
from core.experto import alertas, filtro_clasico
from core.genetico import ajuste_estrategico, algoritmo_genetico, busqueda_exhaustiva, tabla_fitness
from core.juegos import equilibrios_nash, matriz_pagos, minimax_alfa_beta

PESOS_DECISION = {"ag": 0.55, "minimax": 0.30, "disponibilidad": 0.15}


def _normalizar(vals):
    vals = np.array(vals, dtype=float)
    return np.ones_like(vals) if vals.max() == vals.min() else (vals - vals.min()) / (vals.max() - vals.min())


def ejecutar(cfg):
    """cfg: requisitos, pesos, prioridades, modo ('difuso' | 'clasico'), tol_puntos, tol_anos, corte, ga."""
    por_id = {c["id"]: c for c in CANDIDATOS}

    # ---- Paso 1: filtro (se calculan ambos para poder compararlos) ----
    clasico = filtro_clasico(CANDIDATOS, cfg["requisitos"])
    difuso = filtro_difuso(CANDIDATOS, cfg["requisitos"], cfg["tol_puntos"], cfg["tol_anos"])

    if cfg["modo"] == "difuso":
        pool = [{**por_id[r["id"]], "hechos": r["hechos"], "grado": r["grado"], "etiqueta": r["etiqueta"]}
                for r in difuso if r["grado"] >= cfg["corte"]]
    else:
        pool = [{**por_id[r["id"]], "hechos": r["hechos"], "grado": 1.0, "etiqueta": "Apto"}
                for r in clasico["resultados"] if r["apto"]]
    for c in pool:
        c["ajuste"] = ajuste_estrategico(c, cfg["pesos"])
        c["alertas"] = alertas(c["hechos"])

    res = {"clasico": clasico, "difuso": difuso, "pool": pool}
    if not pool:
        return res

    # ---- Paso 2: algoritmo genético + verificación exhaustiva ----
    tabla = tabla_fitness(pool, cfg["prioridades"])
    res["ga"] = algoritmo_genetico(tabla, **cfg["ga"])
    res["exhaustivo"] = busqueda_exhaustiva(tabla)

    # ---- Paso 3: teoría de juegos para los 3 mejores ----
    finalistas = []
    for r in res["exhaustivo"]["ranking"][:3]:
        c = dict(pool[r["idx"]])
        c["plan"] = dict(zip(FRENTES, r["plan"]))
        c["fitness"] = r["fitness"]
        c["pagos"] = matriz_pagos(c)
        c["nash"] = equilibrios_nash(c["pagos"])
        c["minimax"] = minimax_alfa_beta(c, c["pagos"])
        finalistas.append(c)

    # ---- Decisión del headhunter ----
    nf = _normalizar([c["fitness"] for c in finalistas])
    nv = _normalizar([c["minimax"]["valor"] for c in finalistas])
    for c, f_, v_ in zip(finalistas, nf, nv):
        c["aporte"] = {"ag": PESOS_DECISION["ag"] * f_, "minimax": PESOS_DECISION["minimax"] * v_,
                       "disponibilidad": PESOS_DECISION["disponibilidad"] * c["disponibilidad"]}
        c["puntaje"] = sum(c["aporte"].values())
    finalistas.sort(key=lambda c: c["puntaje"], reverse=True)
    res["finalistas"] = finalistas
    res["ceo"] = finalistas[0]
    return res
