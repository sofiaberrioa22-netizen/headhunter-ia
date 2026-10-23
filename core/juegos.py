"""Paso 3: teoría de juegos. Equilibrio de Nash (Intel vs. NVIDIA) y Minimax con poda Alfa-Beta (Intel → NVIDIA → AMD).

Los pagos son pedagógicos, como en la clase 07: los de Intel crecen con la competencia del CEO.
"""
import itertools
import math

from core.genetico import competencia

EST_INTEL = ["S1 Foundry abierta", "S2 Atacar IA", "S3 Defender CPU/costos"]
EST_NVIDIA = ["N1 Cooperar", "N2 Ignorar a Intel"]
EST_AMD = ["A1 Guerra de precios", "A2 Foco en GPU de IA"]


def matriz_pagos(c):
    cF = competencia(c, "foundry") / 10
    cIA = competencia(c, "aceleradores_ia") / 10
    cC = competencia(c, "eficiencia_costos") / 10
    return {
        (EST_INTEL[0], EST_NVIDIA[0]): (6 + 4 * cF, 7), (EST_INTEL[0], EST_NVIDIA[1]): (3.5 + 2 * cF, 6),
        (EST_INTEL[1], EST_NVIDIA[0]): (2 + 5 * cIA, 4), (EST_INTEL[1], EST_NVIDIA[1]): (1 + 5 * cIA, 8),
        (EST_INTEL[2], EST_NVIDIA[0]): (4 + 3 * cC, 6), (EST_INTEL[2], EST_NVIDIA[1]): (4 + 2 * cC, 7),
    }


def equilibrios_nash(pagos):
    """Equilibrios de Nash en estrategias puras: ningún jugador gana desviándose solo."""
    eq = []
    for s, n in itertools.product(EST_INTEL, EST_NVIDIA):
        ui, un = pagos[(s, n)]
        if all(ui >= pagos[(s2, n)][0] for s2 in EST_INTEL) and all(un >= pagos[(s, n2)][1] for n2 in EST_NVIDIA):
            eq.append((s, n, ui, un))
    return eq


def efecto_amd(s, a, c):
    """Impacto de la respuesta de AMD sobre Intel; un CEO más competente amortigua el golpe."""
    if a.startswith("A1"):
        return {"S1": -0.5, "S2": -1.0, "S3": -2.5 + 1.5 * competencia(c, "eficiencia_costos") / 10}[s[:2]]
    return {"S1": 0.0, "S2": -2.5 + 1.5 * competencia(c, "aceleradores_ia") / 10, "S3": 0.5}[s[:2]]


def minimax_alfa_beta(c, pagos):
    """Intel (MAX) → NVIDIA (MIN) → AMD (MIN). Registra los nodos evaluados para dibujar el árbol."""
    reg = {"hojas": {}, "nvidia": {}, "intel": {}}

    def nodo(nivel, s=None, n=None, alfa=-math.inf, beta=math.inf):
        if nivel == 0:
            mejor, jugada = -math.inf, None
            for s2 in EST_INTEL:
                v, _ = nodo(1, s2, None, alfa, beta)
                reg["intel"][s2] = v
                if v > mejor:
                    mejor, jugada = v, s2
                alfa = max(alfa, mejor)
                if alfa >= beta:
                    break
            return mejor, jugada
        peor = math.inf
        for o in (EST_NVIDIA if nivel == 1 else EST_AMD):
            if nivel == 1:
                v, _ = nodo(2, s, o, alfa, beta)
                reg["nvidia"][(s, o)] = v
            else:
                v = pagos[(s, n)][0] + efecto_amd(s, o, c)
                reg["hojas"][(s, n, o)] = v
            peor = min(peor, v)
            beta = min(beta, peor)
            if alfa >= beta:  # PODA: Intel ya tiene una alternativa mejor
                break
        return peor, None

    valor, jugada = nodo(0)
    return {"valor": valor, "jugada": jugada, **reg}


def arbol_dot(mm):
    """Árbol de juego en formato DOT; los nodos podados aparecen en gris punteado."""
    L = ['digraph G {', 'rankdir=TB; bgcolor="transparent"; nodesep=0.25; ranksep=0.5;',
         'node [fontname="Helvetica", fontsize=12, style="filled", penwidth=1.2];',
         'edge [color="#94a3b8", arrowsize=0.5];',
         f'root [label="Intel (MAX)\\n{mm["valor"]:.2f}", shape=box, fillcolor="#dbeafe", color="#2563eb"];']
    for i, s in enumerate(EST_INTEL):
        ev = s in mm["intel"]
        mejor = s == mm["jugada"]
        lbl = f'{s[:2]}\\n{mm["intel"][s]:.2f}' if ev else f'{s[:2]}\\npodado'
        fill, col = ("#dcfce7", "#059669") if mejor else (("#f1f5f9", "#64748b") if ev else ("#ffffff", "#cbd5e1"))
        L.append(f's{i} [label="{lbl}", shape=ellipse, fillcolor="{fill}", color="{col}", fontcolor="{"#0f172a" if ev else "#94a3b8"}"];')
        L.append(f'root -> s{i} [style={"solid" if ev else "dashed"}];')
        for j, n in enumerate(EST_NVIDIA):
            ev2 = (s, n) in mm["nvidia"]
            lbl2 = f'{n[:2]}\\n{mm["nvidia"][(s, n)]:.2f}' if ev2 else f'{n[:2]}\\npodado'
            L.append(f's{i}n{j} [label="{lbl2}", shape=ellipse, fillcolor="{"#fef2f2" if ev2 else "#ffffff"}", '
                     f'color="{"#dc2626" if ev2 else "#cbd5e1"}", fontcolor="{"#0f172a" if ev2 else "#94a3b8"}"];')
            L.append(f's{i} -> s{i}n{j} [style={"solid" if ev2 else "dashed"}];')
            for k, a in enumerate(EST_AMD):
                ev3 = (s, n, a) in mm["hojas"]
                lbl3 = f'{a[:2]}\\n{mm["hojas"][(s, n, a)]:.2f}' if ev3 else f'{a[:2]}\\npodado'
                L.append(f's{i}n{j}a{k} [label="{lbl3}", shape=box, fillcolor="{"#f8fafc" if ev3 else "#ffffff"}", '
                         f'color="{"#64748b" if ev3 else "#e2e8f0"}", fontcolor="{"#0f172a" if ev3 else "#cbd5e1"}", fontsize=11];')
                L.append(f's{i}n{j} -> s{i}n{j}a{k} [style={"solid" if ev3 else "dashed"}];')
    L.append("}")
    return "\n".join(L)
