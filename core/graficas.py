"""Gráficas interactivas (Plotly) de la app. Todas admiten hover, zoom, leyenda clicable y descarga en PNG."""
import numpy as np
import plotly.graph_objects as go

from core.datos import CRIT_LBL, CRITERIOS
from core.juegos import EST_AMD, EST_INTEL, EST_NVIDIA
from core.datos import FR_LBL, FRENTES
from core.ui import LINEA, MAL, MARCA, MARCA_2, OK, SUAVE, TINTA, VIOLETA, estilo, foto_circular


def _alpha(hex_color, a):
    h = hex_color.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{a})"


def radar(candidatos, pesos):
    """Perfil de uno o varios candidatos frente a la importancia de cada cualidad para Intel."""
    etiquetas = [CRIT_LBL[k] for k in CRITERIOS]
    theta = etiquetas + etiquetas[:1]
    mx = max(pesos.values())
    fig = go.Figure()
    imp = [10 * pesos[k] / mx for k in CRITERIOS]
    fig.add_scatterpolar(r=imp + imp[:1], theta=theta, name="Importancia para Intel", fill="toself",
                         fillcolor="rgba(148,163,184,0.12)", line=dict(color="#94a3b8", dash="dot", width=2),
                         hovertemplate="%{theta}: importancia %{customdata:.0%}<extra></extra>",
                         customdata=[pesos[k] for k in CRITERIOS] + [pesos[CRITERIOS[0]]])
    for c in candidatos:
        r = [c[k] for k in CRITERIOS]
        fig.add_scatterpolar(r=r + r[:1], theta=theta, name=c["nombre"], fill="toself",
                             fillcolor=_alpha(c["color"], 0.14), line=dict(color=c["color"], width=2.5),
                             marker=dict(size=6), hovertemplate=f"<b>{c['nombre']}</b><br>%{{theta}}: %{{r}}/10<extra></extra>")
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, 10], showticklabels=False, gridcolor=LINEA),
                                 angularaxis=dict(gridcolor=LINEA, tickfont=dict(size=15, color=TINTA))))
    fig = estilo(fig, 540)
    fig.update_layout(margin=dict(l=70, r=70, t=30, b=10))
    return fig


def ranking_candidatos(candidatos, ajustes):
    """Ranking de ajuste al perfil, con la foto de cada candidato al final de su barra."""
    orden = sorted(candidatos, key=lambda c: ajustes[c["id"]], reverse=True)
    nombres = [c["nombre"] for c in orden]
    fig = go.Figure(go.Bar(
        y=nombres, x=[ajustes[c["id"]] for c in orden], orientation="h",
        marker=dict(color=[_alpha(c["color"], 0.85) for c in orden], cornerradius=10),
        text=[f"<b>{ajustes[c['id']]:.2f}</b>   ·   aceptaría {c['disponibilidad'] * 100:.0f}%" for c in orden],
        textposition="inside", insidetextanchor="start", textfont=dict(size=15, color="white"),
        customdata=[[c["cargo"], c["exp_ceo"], c["disponibilidad"] * 100, "sí" if c["conflicto"] else "no"] for c in orden],
        hovertemplate="<b>%{y}</b><br>%{customdata[0]}<br>Ajuste al perfil: %{x:.2f}/10<br>Años como CEO: %{customdata[1]}"
                      "<br>Aceptaría: %{customdata[2]:.0f}%<br>Conflicto de interés: %{customdata[3]}<extra></extra>"))
    for c in orden:
        fig.add_layout_image(source=foto_circular(c["id"]), x=ajustes[c["id"]], y=c["nombre"], xref="x", yref="y",
                             sizex=1.2, sizey=0.92, xanchor="left", yanchor="middle", sizing="contain", layer="above")
    fig.update_yaxes(autorange="reversed", tickfont=dict(size=16, color=TINTA), ticksuffix="   ")
    fig.update_xaxes(range=[0, 10.6], title="Ajuste al perfil que busca Intel (0-10)", dtick=2)
    fig.update_layout(bargap=0.28)
    return estilo(fig, 90 + 82 * len(orden), leyenda=False)


def mapa_grados(filas, requisitos):
    """Heatmap candidato × requisito con el grado de cumplimiento difuso."""
    nombres = [f["nombre"] for f in filas]
    z = [[f["grados"][r] for r in requisitos] + [f["grado"]] for f in filas]
    cols = [requisitos[r] for r in requisitos] + ["Grado total"]
    fig = go.Figure(go.Heatmap(
        z=z, x=cols, y=nombres, zmin=0, zmax=1, xgap=4, ygap=4,
        colorscale=[[0, "#fee2e2"], [0.5, "#fde68a"], [0.75, "#bfdbfe"], [1, "#a7f3d0"]],
        text=[[f"{v:.0%}" for v in fila] for fila in z], texttemplate="%{text}", textfont=dict(size=16, color=TINTA),
        hovertemplate="<b>%{y}</b><br>%{x}: %{z:.0%}<extra></extra>", showscale=False))
    fig.update_yaxes(autorange="reversed", showgrid=False, tickfont=dict(size=15, color=TINTA))
    fig.update_xaxes(side="top", showgrid=False, tickangle=0, tickfont=dict(size=14, color=TINTA))
    return estilo(fig, 80 + 62 * len(nombres), leyenda=False)


def pertenencia(candidatos, atrib, grados, u, t, etiqueta):
    """Función de pertenencia en rampa con los candidatos ubicados sobre ella."""
    xs = [c[atrib] for c in candidatos]
    lo, hi = min(min(xs), u - t) - 1, max(max(xs), u) + 1
    xx = np.linspace(lo, hi, 200)
    fig = go.Figure()
    fig.add_vrect(x0=u - t, x1=u, fillcolor="rgba(79,70,229,0.06)", line_width=0,
                  annotation_text="zona de tolerancia", annotation_position="top left",
                  annotation_font=dict(size=10, color=SUAVE))
    fig.add_scatter(x=xx, y=np.clip((xx - (u - t)) / t, 0, 1), mode="lines", name="Grado (lógica difusa)",
                    line=dict(color=MARCA, width=3.5, shape="linear"), hoverinfo="skip")
    fig.add_scatter(x=[lo, u, u, hi], y=[0, 0, 1, 1], mode="lines", name="Filtro clásico (todo o nada)",
                    line=dict(color="#94a3b8", width=2, dash="dot", shape="hv"), hoverinfo="skip")
    for c in candidatos:
        g = grados[c["id"]]
        fig.add_scatter(x=[c[atrib]], y=[g], mode="markers", name=c["nombre"], showlegend=False,
                        marker=dict(size=13, color=c["color"], line=dict(color="white", width=2)),
                        hovertemplate=f"<b>{c['nombre']}</b><br>{etiqueta}: {c[atrib]}<br>Grado: {g:.0%}<extra></extra>")
    grupos = {}  # candidatos con el mismo valor comparten una sola etiqueta
    for c in candidatos:
        grupos.setdefault(c[atrib], []).append(c["nombre"].split()[-1])
    for i, (x, ns) in enumerate(sorted(grupos.items())):
        arriba = i % 2 == 0
        fig.add_annotation(x=x, y=float(np.clip((x - (u - t)) / t, 0, 1)), text="<br>".join(ns), showarrow=False,
                           yshift=(16 + 7 * (len(ns) - 1)) * (1 if arriba else -1), font=dict(size=10, color="#334155"))
    fig.update_yaxes(range=[-0.25, 1.3], tickformat=".0%", title="Grado de cumplimiento")
    fig.update_xaxes(title=etiqueta)
    return estilo(fig, 470)


def convergencia_animada(hist, optimo):
    """Convergencia del AG con botón de reproducción: se ve cómo evoluciona generación a generación."""
    G = len(hist["mejor"])
    gens = list(range(1, G + 1))
    mejor, prom = hist["mejor"], hist["promedio"]
    y0, y1 = min(prom) - 0.05, optimo + 0.05

    def trazas(k):
        return [go.Scatter(x=gens[:k], y=mejor[:k]), go.Scatter(x=gens[:k], y=prom[:k])]

    fig = go.Figure()
    fig.add_scatter(x=gens, y=mejor, name="Mejor individuo", line=dict(color=MARCA, width=3),
                    hovertemplate="Generación %{x}<br>Mejor: %{y:.4f}<extra></extra>")
    fig.add_scatter(x=gens, y=prom, name="Promedio de la población", line=dict(color=MARCA_2, width=2, dash="dash"),
                    fill="tonexty", fillcolor="rgba(14,165,233,0.06)",
                    hovertemplate="Generación %{x}<br>Promedio: %{y:.4f}<extra></extra>")
    fig.add_scatter(x=[1, G], y=[optimo, optimo], name="Óptimo (búsqueda exhaustiva)", mode="lines",
                    line=dict(color=OK, width=1.5, dash="dot"), hoverinfo="skip")
    paso = max(1, G // 60)
    fig.frames = [go.Frame(data=trazas(k), traces=[0, 1], name=str(k)) for k in list(range(1, G + 1, paso)) + [G]]
    fig.update_layout(
        hovermode="x unified",
        updatemenus=[dict(type="buttons", direction="left", x=0, y=1.16, xanchor="left", yanchor="top",
                          pad=dict(r=6, t=0), showactive=False, bgcolor="white", bordercolor=LINEA,
                          buttons=[dict(label="▶ Reproducir evolución", method="animate",
                                        args=[None, dict(frame=dict(duration=45, redraw=False), fromcurrent=False,
                                                         transition=dict(duration=0), mode="immediate")]),
                                   dict(label="❚❚ Pausa", method="animate",
                                        args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate")])])])
    fig.update_xaxes(range=[0.5, G + 0.5], ticksuffix="  ", tickprefix="gen ")
    fig.update_yaxes(title="Fitness", range=[y0, y1])
    fig = estilo(fig, 500)
    fig.update_layout(margin=dict(t=52, b=8), legend=dict(yanchor="top", y=-0.12))
    return fig


def matriz_pagos(pagos, nash):
    """Matriz Intel vs. NVIDIA como heatmap: color = pago de Intel; recuadro verde = equilibrio de Nash."""
    z = [[pagos[(s, n)][0] for n in EST_NVIDIA] for s in EST_INTEL]
    texto = [[f"<b>{pagos[(s, n)][0]:.2f}</b> , {pagos[(s, n)][1]}" for n in EST_NVIDIA] for s in EST_INTEL]
    fig = go.Figure(go.Heatmap(
        z=z, x=EST_NVIDIA, y=EST_INTEL, colorscale=[[0, "#eef2ff"], [1, "#818cf8"]], showscale=False, xgap=5, ygap=5,
        text=texto, texttemplate="%{text}", textfont=dict(size=18, color=TINTA),
        customdata=[[pagos[(s, n)][1] for n in EST_NVIDIA] for s in EST_INTEL],
        hovertemplate="Intel: <b>%{y}</b><br>NVIDIA: <b>%{x}</b><br>Pago Intel: %{z:.2f}<br>"
                      "Pago NVIDIA: %{customdata}<extra></extra>"))
    nash_set = {(s, n) for s, n, *_ in nash}
    for i, s in enumerate(EST_INTEL):
        for j, n in enumerate(EST_NVIDIA):
            if (s, n) in nash_set:
                fig.add_shape(type="rect", x0=j - 0.47, x1=j + 0.47, y0=i - 0.45, y1=i + 0.45,
                              line=dict(color=OK, width=3), fillcolor="rgba(0,0,0,0)")
                fig.add_annotation(x=j, y=i - 0.3, text="Nash", showarrow=False, font=dict(size=10, color="#047857"))
    fig.update_yaxes(autorange="reversed", showgrid=False, title="Intel")
    fig.update_xaxes(side="top", showgrid=False, title="NVIDIA", tickangle=0, tickfont=dict(size=14))
    fig.update_yaxes(tickfont=dict(size=14))
    return estilo(fig, 420, leyenda=False)


def arbol_minimax(mm):
    """Árbol Intel (MAX) → NVIDIA (MIN) → AMD (MIN). Ramas podadas en gris punteado; hover con la explicación."""
    hoja_x = lambda i, j, k: i * 4 + j * 2 + k
    nodos, aristas = [], []  # nodo: (x, y, etiqueta, valor, estado, hover)
    raiz_x = 5.5
    nodos.append((raiz_x, 3, "Intel", mm["valor"], "raiz",
                  f"<b>Intel (MAX)</b><br>Valor garantizado: {mm['valor']:.2f}<br>Elige: {mm['jugada']}"))
    for i, s in enumerate(EST_INTEL):
        sx = (hoja_x(i, 0, 0) + hoja_x(i, 1, 1)) / 2
        ev = s in mm["intel"]
        estado = "mejor" if s == mm["jugada"] else ("ok" if ev else "podado")
        nodos.append((sx, 2, s[:2], mm["intel"].get(s), estado,
                      f"<b>{s}</b><br>" + (f"Lo peor que le puede pasar a Intel: {mm['intel'][s]:.2f}" if ev else "Podado")))
        aristas.append((raiz_x, 3, sx, 2, ev))
        for j, n in enumerate(EST_NVIDIA):
            nx = (hoja_x(i, j, 0) + hoja_x(i, j, 1)) / 2
            ev2 = (s, n) in mm["nvidia"]
            nodos.append((nx, 1, n[:2], mm["nvidia"].get((s, n)), "min" if ev2 else "podado",
                          f"<b>{s} → {n}</b><br>" + (f"Valor tras la respuesta de AMD: {mm['nvidia'][(s, n)]:.2f}"
                                                     if ev2 else "Rama podada: Intel ya tenía una opción mejor")))
            aristas.append((sx, 2, nx, 1, ev2))
            for k, a in enumerate(EST_AMD):
                lx = hoja_x(i, j, k)
                ev3 = (s, n, a) in mm["hojas"]
                nodos.append((lx, 0, a[:2], mm["hojas"].get((s, n, a)), "hoja" if ev3 else "podado",
                              f"<b>{s} → {n} → {a}</b><br>" + (f"Pago de Intel: {mm['hojas'][(s, n, a)]:.2f}"
                                                               if ev3 else "Hoja podada: no hizo falta evaluarla")))
                aristas.append((nx, 1, lx, 0, ev3))

    fig = go.Figure()
    for ok in (False, True):
        xs, ys = [], []
        for x0, y0, x1, y1, ev in aristas:
            if ev == ok:
                xs += [x0, x1, None]
                ys += [y0, y1, None]
        fig.add_scatter(x=xs, y=ys, mode="lines", hoverinfo="skip", showlegend=False,
                        line=dict(color="#94a3b8" if ok else "#d6dbe4", width=1.8 if ok else 1.2, dash=None if ok else "dot"))
    colores = {"raiz": MARCA, "mejor": OK, "ok": "#64748b", "min": MAL, "hoja": "#334155", "podado": "#cbd5e1"}
    for estado in colores:
        sel = [n for n in nodos if n[4] == estado]
        if not sel:
            continue
        hoja = estado in ("hoja",) or (estado == "podado")
        fig.add_scatter(
            x=[n[0] for n in sel], y=[n[1] for n in sel], mode="markers+text", showlegend=False,
            marker=dict(size=[58 if n[1] > 0 else 50 for n in sel], symbol=["square" if n[1] == 0 else "circle" for n in sel],
                        color=["white" if estado == "podado" else _alpha(colores[estado], 0.12) for _ in sel],
                        line=dict(color=colores[estado], width=2 if estado != "podado" else 1.2)),
            text=[(f"{n[2]}<br>{n[3]:.2f}" if n[3] is not None else f"{n[2]}<br>✂") for n in sel],
            textfont=dict(size=12 if hoja else 14, color="#94a3b8" if estado == "podado" else TINTA),
            hovertemplate="%{customdata}<extra></extra>", customdata=[n[5] for n in sel])
    for y, txt, col in ((3, "MAX · Intel", MARCA), (2, "Estrategia de Intel", "#64748b"), (1, "MIN · NVIDIA", MAL),
                        (0, "MIN · AMD", MAL)):
        fig.add_annotation(x=-1.3, y=y, text=f"<b>{txt}</b>", showarrow=False, xanchor="right",
                           font=dict(size=14, color=col))
    fig.update_xaxes(visible=False, range=[-4.2, 11.8])
    fig.update_yaxes(visible=False, range=[-0.55, 3.5])
    return estilo(fig, 540, leyenda=False)


def decision(fin, pesos):
    fig = go.Figure()
    for clave, nombre, color in (("ag", f"Algoritmo genético ({pesos['ag']:.0%})", MARCA),
                                 ("minimax", f"Minimax ({pesos['minimax']:.0%})", VIOLETA),
                                 ("disponibilidad", f"Disponibilidad ({pesos['disponibilidad']:.0%})", OK)):
        fig.add_bar(y=[c["nombre"] for c in fin], x=[c["aporte"][clave] for c in fin], name=nombre, orientation="h",
                    marker=dict(color=color, cornerradius=4),
                    hovertemplate="<b>%{y}</b><br>" + nombre + ": %{x:.3f}<extra></extra>")
    for c in fin:
        fig.add_annotation(x=c["puntaje"], y=c["nombre"], text=f"<b>{c['puntaje']:.3f}</b>", showarrow=False,
                           xanchor="left", xshift=8, font=dict(color=TINTA, size=16))
        fig.add_layout_image(source=foto_circular(c["id"]), x=c["puntaje"] + 0.1, y=c["nombre"], xref="x", yref="y",
                             sizex=0.2, sizey=0.75, xanchor="left", yanchor="middle", sizing="contain")
    fig.update_layout(barmode="stack")
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(title="Puntaje final", range=[0, 1.25])
    fig.update_yaxes(tickfont=dict(size=15, color=TINTA))
    return estilo(fig, 160 + 80 * len(fin))


def brecha_intel_nvidia():
    cats = ["Ingresos del trimestre (US$ B)", "Margen bruto (%)"]
    fig = go.Figure()
    fig.add_bar(name="Intel", x=cats, y=[16.1, 40.4], marker=dict(color=MARCA, cornerradius=6),
                text=["16,1", "40,4 %"], textposition="outside", hovertemplate="Intel · %{x}: %{y}<extra></extra>")
    fig.add_bar(name="NVIDIA", x=cats, y=[96.2, 75.0], marker=dict(color="#94a3b8", cornerradius=6),
                text=["96,2", "75 %"], textposition="outside", hovertemplate="NVIDIA · %{x}: %{y}<extra></extra>")
    fig.update_layout(bargap=0.35)
    fig.update_yaxes(range=[0, 112], visible=False)
    fig.update_xaxes(tickfont=dict(size=15, color=TINTA))
    fig.update_traces(textfont=dict(size=18))
    return estilo(fig, 420)


def barras_pesos(etiquetas, valores, color):
    fig = go.Figure(go.Bar(
        y=etiquetas, x=[v * 100 for v in valores], orientation="h", marker=dict(color=color, cornerradius=5),
        text=[f"{v * 100:.0f}%" for v in valores], textposition="outside",
        hovertemplate="%{y}: %{x:.1f}%<extra></extra>"))
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(range=[0, max(valores) * 130], ticksuffix="%")
    fig.update_yaxes(tickfont=dict(size=15, color=TINTA))
    return estilo(fig, 420, leyenda=False)


def mandato(plan, prioridades):
    """Mandato de 100 días del CEO (reparto de su foco) frente a la prioridad que el analista dio a cada frente."""
    total = sum(plan.values()) or 1
    etiquetas = [FR_LBL[f] for f in FRENTES]
    fig = go.Figure()
    fig.add_bar(y=etiquetas, x=[prioridades[f] * 100 for f in FRENTES], name="Prioridad para Intel", orientation="h",
                marker=dict(color="#cbd5e1", cornerradius=5), hovertemplate="%{y}: prioridad %{x:.0f}%<extra></extra>")
    fig.add_bar(y=etiquetas, x=[plan[f] / total * 100 for f in FRENTES], name="Foco del nuevo CEO", orientation="h",
                marker=dict(color=MARCA, cornerradius=5), customdata=[plan[f] for f in FRENTES],
                hovertemplate="%{y}: %{x:.0f}% del foco (intensidad %{customdata}/3)<extra></extra>")
    fig.update_layout(barmode="group", bargap=0.25, bargroupgap=0.08)
    fig.update_yaxes(autorange="reversed", tickfont=dict(size=15, color=TINTA))
    fig.update_xaxes(ticksuffix="%")
    return estilo(fig, 460)
