"""Gráficas de la app (ECharts): animadas al aparecer, con texturas, degradados y fotos de los candidatos.

Todas son interactivas: tooltip al pasar el mouse, leyenda clicable, descarga como imagen y botón para repetir la animación.
"""
from core.datos import CRIT_LBL, CRITERIOS, FR_LBL, FRENTES
from core.echarts import (AMBAR, AZUL, AZUL_CLARO, JS, LEYENDA, REJILLA, ROJO, TEXTO, TEXTO_SUAVE, TURQUESA, VERDE,
                          VIOLETA, alpha, degradado, echart, eje_categoria, eje_valor)
from core.juegos import EST_AMD, EST_INTEL, EST_NVIDIA
from core.ui import foto_circular

TOOLTIP_DATOS = {"trigger": "item", "formatter": JS("function(p){return p.data && p.data.tip ? p.data.tip : p.name;}")}


# ---------------------------------------------------------------- página 1
def brecha_intel_nvidia(titulo, subtitulo=""):
    """Ingresos como pilas de obleas que crecen + anillos de margen bruto."""
    pilas = [
        {"value": 16.1, "symbol": "roundRect", "itemStyle": {"color": degradado(AZUL, AZUL_CLARO)},
         "tip": "<b>Intel</b><br>Ingresos Q2 2026: US$16,1 B<br>+25% interanual",
         "label": {"formatter": "US$16,1 B", "color": AZUL_CLARO}},
        {"value": 96.2, "symbol": "roundRect", "itemStyle": {"color": degradado("#4d7c0f", VERDE)},
         "tip": "<b>NVIDIA</b><br>Ingresos Q2 FY2027: US$96,2 B<br>+106% interanual",
         "label": {"formatter": "US$96,2 B", "color": VERDE}},
    ]

    def anillo(nombre, valor, color, centro):
        return {
            "type": "gauge", "center": centro, "radius": "25%", "startAngle": 90, "endAngle": -270, "min": 0, "max": 100,
            "pointer": {"show": False},
            "progress": {"show": True, "roundCap": True, "width": 16,
                         "itemStyle": {"color": color, "shadowBlur": 18, "shadowColor": color}},
            "axisLine": {"lineStyle": {"width": 16, "color": [[1, "rgba(148,163,184,0.12)"]]}},
            "splitLine": {"show": False}, "axisTick": {"show": False}, "axisLabel": {"show": False},
            "title": {"offsetCenter": [0, "150%"], "color": TEXTO, "fontSize": 15, "fontWeight": 700},
            "detail": {"valueAnimation": True, "offsetCenter": [0, 0], "fontSize": 22, "fontWeight": 800, "color": "#fff",
                       "formatter": "{value}%"},
            "data": [{"value": valor, "name": nombre}], "animationDuration": 2200,
            "tooltip": {"formatter": f"{nombre}: margen bruto {valor}%"}}

    opcion = {
        "tooltip": TOOLTIP_DATOS,
        "title": [{"text": "Ingresos del trimestre", "left": "4%", "top": 0, "textStyle": {"color": TEXTO_SUAVE, "fontSize": 13}},
                  {"text": "Margen bruto", "left": "62%", "top": 0, "textStyle": {"color": TEXTO_SUAVE, "fontSize": 13}}],
        "grid": {"left": "4%", "right": "48%", "top": 40, "bottom": 30},
        "xAxis": eje_categoria(["Intel", "NVIDIA"], axisLabel={"color": TEXTO, "fontSize": 16, "fontWeight": 700}),
        "yAxis": eje_valor(max=110, axisLabel={"show": False}),
        "series": [
            {"type": "pictorialBar", "data": pilas, "symbolRepeat": True, "symbolSize": ["68%", 12], "symbolMargin": 3,
             "barCategoryGap": "28%",
             "label": {"show": True, "position": "top", "fontSize": 18, "fontWeight": 800},
             "animationDelay": JS("function(dataIndex, params){return params.index * 22 + dataIndex * 250;}"),
             "animationDuration": 400},
            anillo("Intel", 40.4, AZUL_CLARO, ["66%", "50%"]),
            anillo("NVIDIA", 75.0, VERDE, ["87%", "50%"]),
        ],
    }
    echart(opcion, 380, titulo, subtitulo)


def barras_pesos(etiquetas, valores, titulo, subtitulo=""):
    """Importancia de cada cualidad: barras de energía con degradado sobre un riel."""
    orden = sorted(zip(etiquetas, valores), key=lambda x: x[1], reverse=True)
    opcion = {
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"},
                    "valueFormatter": JS("function(v){return (v*100).toFixed(0)+'%';}")},
        "grid": {"left": 10, "right": 60, "top": 10, "bottom": 10, "containLabel": True},
        "xAxis": eje_valor(show=False, max=max(valores) * 1.15),
        "yAxis": eje_categoria([e for e, _ in orden], inverse=True, axisLine={"show": False},
                               axisLabel={"color": TEXTO, "fontSize": 15}),
        "series": [{
            "type": "bar", "data": [v for _, v in orden], "barWidth": 22, "showBackground": True,
            "backgroundStyle": {"color": "rgba(148,163,184,0.08)", "borderRadius": 11},
            "itemStyle": {"borderRadius": 11, "color": degradado(TURQUESA, VERDE),
                          "shadowBlur": 14, "shadowColor": alpha(VERDE, 0.45)},
            "label": {"show": True, "position": "right", "color": "#fff", "fontWeight": 800, "fontSize": 14,
                      "formatter": JS("function(p){return (p.value*100).toFixed(0)+'%';}")},
            "animationDelay": JS("function(i){return i * 120;}")}],
    }
    echart(opcion, 400, titulo, subtitulo)


# ---------------------------------------------------------------- página 2
def ranking_candidatos(candidatos, ajustes, titulo, subtitulo=""):
    """Ranking de ajuste al perfil: barras con degradado que terminan en la foto de cada candidato."""
    orden = sorted(candidatos, key=lambda c: ajustes[c["id"]], reverse=True)
    barras, fotos = [], []
    for c in orden:
        tip = (f"<b>{c['nombre']}</b><br>{c['cargo']}<br>Ajuste al perfil: <b>{ajustes[c['id']]:.2f}</b>/10<br>"
               f"Años como CEO: {c['exp_ceo']} · Aceptaría: {c['disponibilidad'] * 100:.0f}%")
        barras.append({"value": round(ajustes[c["id"]], 2), "tip": tip,
                       "itemStyle": {"color": degradado(alpha(c["color"], 0.25), c["color"]),
                                     "shadowBlur": 16, "shadowColor": alpha(c["color"], 0.5)},
                       "label": {"formatter": f"{ajustes[c['id']]:.2f}  ·  {c['disponibilidad'] * 100:.0f}% acepta"}})
        fotos.append({"value": [round(ajustes[c["id"]], 2), c["nombre"]], "symbol": "image://" + foto_circular(c["id"]),
                      "tip": tip})
    opcion = {
        "tooltip": TOOLTIP_DATOS,
        "grid": {"left": 10, "right": 50, "top": 10, "bottom": 30, "containLabel": True},
        "xAxis": eje_valor(min=0, max=10.4, name="Ajuste al perfil (0-10)", nameLocation="middle", nameGap=26,
                           axisLabel={"color": TEXTO_SUAVE, "showMaxLabel": False}),
        "yAxis": eje_categoria([c["nombre"] for c in orden], inverse=True, axisLine={"show": False},
                               axisLabel={"color": TEXTO, "fontSize": 15, "fontWeight": 600, "margin": 14}),
        "series": [
            {"type": "bar", "data": barras, "barWidth": "56%", "showBackground": True,
             "backgroundStyle": {"color": "rgba(148,163,184,0.06)", "borderRadius": 14},
             "itemStyle": {"borderRadius": 14},
             "label": {"show": True, "position": "insideLeft", "color": "#fff", "fontSize": 14, "fontWeight": 700,
                       "distance": 14},
             "animationDelay": JS("function(i){return i * 140;}"), "animationDuration": 1300},
            {"type": "scatter", "data": fotos, "symbolSize": 58, "symbolOffset": [26, 0], "z": 5,
             "animationDelay": JS("function(i){return 900 + i * 140;}"), "animationDuration": 600,
             "animationEasing": "backOut"},
        ],
    }
    echart(opcion, 90 + 72 * len(orden), titulo, subtitulo)


def radar(candidatos, pesos, titulo, subtitulo=""):
    mx = max(pesos.values())
    indicadores = [{"name": CRIT_LBL[k], "max": 10} for k in CRITERIOS]
    datos = [{"name": "Importancia para Intel", "value": [round(10 * pesos[k] / mx, 2) for k in CRITERIOS],
              "symbol": "none", "lineStyle": {"color": TEXTO_SUAVE, "type": "dashed", "width": 2},
              "areaStyle": {"color": "rgba(148,163,184,0.10)"}, "itemStyle": {"color": TEXTO_SUAVE}}]
    for c in candidatos:
        datos.append({"name": c["nombre"], "value": [c[k] for k in CRITERIOS], "symbolSize": 6,
                      "lineStyle": {"color": c["color"], "width": 3, "shadowBlur": 12, "shadowColor": c["color"]},
                      "itemStyle": {"color": c["color"]},
                      "areaStyle": {"color": {"type": "radial", "x": 0.5, "y": 0.5, "r": 0.6, "colorStops": [
                          {"offset": 0, "color": alpha(c["color"], 0.05)}, {"offset": 1, "color": alpha(c["color"], 0.35)}]}}})
    opcion = {
        "legend": {**LEYENDA, "data": [d["name"] for d in datos]},
        "tooltip": {"trigger": "item"},
        "radar": {"indicator": indicadores, "radius": "66%", "center": ["50%", "57%"], "splitNumber": 5,
                  "axisName": {"color": TEXTO, "fontSize": 14, "fontWeight": 600},
                  "splitLine": {"lineStyle": {"color": REJILLA}}, "axisLine": {"lineStyle": {"color": REJILLA}},
                  "splitArea": {"areaStyle": {"color": ["rgba(255,255,255,0.015)", "rgba(255,255,255,0.04)"]}}},
        "series": [{"type": "radar", "data": datos, "animationDuration": 1600, "animationEasing": "elasticOut"}],
    }
    echart(opcion, 480, titulo, subtitulo)


# ---------------------------------------------------------------- página 3
def _etiquetas_con_foto(candidatos, tam=30):
    """Rich text para mostrar foto + nombre en un eje de categorías."""
    rich = {"n": {"color": TEXTO, "fontSize": 14, "fontWeight": 600, "padding": [0, 0, 0, 8]}}
    mapa = {}
    for c in candidatos:
        rich[c["id"]] = {"height": tam, "width": tam, "borderRadius": tam / 2,
                         "backgroundColor": {"image": foto_circular(c["id"])}}
        mapa[c["nombre"]] = c["id"]
    formato = JS("function(v){var m=" + str(mapa).replace("'", '"') + ";return '{'+m[v]+'|}{n|'+v+'}';}")
    return rich, formato


def mapa_grados(filas, requisitos, candidatos, titulo, subtitulo=""):
    """Heatmap candidato × requisito con el grado de cumplimiento difuso."""
    cols = list(requisitos.values()) + ["Grado total"]
    nombres = [f["nombre"] for f in filas]
    datos = []
    for i, f in enumerate(filas):
        valores = [f["grados"][r] for r in requisitos] + [f["grado"]]
        for j, v in enumerate(valores):
            total = j == len(cols) - 1
            datos.append({"value": [j, i, round(v, 2)], "tip": f"<b>{f['nombre']}</b><br>{cols[j]}: {v:.0%}",
                          **({"itemStyle": {"borderColor": "#e2e8f0", "borderWidth": 2}} if total else {})})
    rich, formato = _etiquetas_con_foto([c for c in candidatos if c["nombre"] in nombres])
    opcion = {
        "tooltip": TOOLTIP_DATOS,
        "grid": {"left": 10, "right": 10, "top": 36, "bottom": 10, "containLabel": True},
        "xAxis": eje_categoria(cols, position="top", axisLine={"show": False},
                               axisLabel={"color": TEXTO, "fontSize": 14, "fontWeight": 700}),
        "yAxis": eje_categoria(nombres, inverse=True, axisLine={"show": False},
                               axisLabel={"formatter": formato, "rich": rich, "margin": 12}),
        "visualMap": {"show": False, "type": "piecewise", "dimension": 2, "pieces": [
            {"min": 0.999, "color": VERDE}, {"min": 0.5, "max": 0.999, "color": AZUL_CLARO},
            {"min": 0.001, "max": 0.5, "color": AMBAR}, {"max": 0.001, "color": ROJO}]},
        "series": [{"type": "heatmap", "data": datos,
                    "label": {"show": True, "color": "#fff", "fontSize": 15, "fontWeight": 800,
                              "formatter": JS("function(p){return Math.round(p.value[2]*100)+'%';}")},
                    "itemStyle": {"borderRadius": 10, "borderColor": "#0f172a", "borderWidth": 5, "opacity": 0.92},
                    "emphasis": {"itemStyle": {"shadowBlur": 20, "shadowColor": "rgba(255,255,255,0.4)"}},
                    "animationDelay": JS("function(i){return i * 35;}"), "animationDuration": 700}],
    }
    echart(opcion, 70 + 60 * len(filas), titulo, subtitulo)


def pertenencia(candidatos, atrib, grados, u, t, etiqueta, titulo, subtitulo=""):
    """Rampa difusa vs. escalón clásico, con la foto de cada candidato sobre la curva."""
    xs = [c[atrib] for c in candidatos]
    lo, hi = min(min(xs), u - t) - 1, max(max(xs), u) + 1
    grupos = {}
    for c in candidatos:
        grupos.setdefault(c[atrib], []).append(c["id"])
    puntos = []
    for c in candidatos:
        grupo = grupos[c[atrib]]
        desplaz = (grupo.index(c["id"]) - (len(grupo) - 1) / 2) * 44  # separa a quienes tienen el mismo valor
        g = grados[c["id"]]
        puntos.append({"value": [c[atrib], g], "symbol": "image://" + foto_circular(c["id"]),
                       "symbolOffset": [desplaz, 0],
                       "tip": f"<b>{c['nombre']}</b><br>{etiqueta}: {c[atrib]}<br>Grado de cumplimiento: <b>{g:.0%}</b>"})
    opcion = {
        "legend": {**LEYENDA, "data": ["Lógica difusa (grado)", "Filtro clásico (todo o nada)"]},
        "tooltip": TOOLTIP_DATOS,
        "grid": {"left": 10, "right": 30, "top": 60, "bottom": 36, "containLabel": True},
        "xAxis": eje_valor(min=round(lo, 1), max=round(hi, 1), name=etiqueta, nameLocation="middle", nameGap=28),
        "yAxis": eje_valor(min=0, max=1.25, interval=0.25,
                           axisLabel={"color": TEXTO_SUAVE,
                                      "formatter": JS("function(v){return v>1?'':Math.round(v*100)+'%';}")}),
        "series": [
            {"name": "Lógica difusa (grado)", "type": "line", "data": [[lo, 0], [u - t, 0], [u, 1], [hi, 1]],
             "symbol": "none", "itemStyle": {"color": VERDE},
             "lineStyle": {"width": 5, "color": degradado(AMBAR, VERDE), "shadowBlur": 16, "shadowColor": alpha(VERDE, 0.6)},
             "areaStyle": {"color": degradado(alpha(VERDE, 0.35), alpha(VERDE, 0.0), vertical=True)},
             "markArea": {"silent": True, "itemStyle": {"color": "rgba(245,158,11,0.08)"},
                          "label": {"color": AMBAR, "fontSize": 12},
                          "data": [[{"name": "zona de tolerancia", "xAxis": u - t}, {"xAxis": u}]]},
             "animationDuration": 1800, "z": 2},
            {"name": "Filtro clásico (todo o nada)", "type": "line", "step": "end",
             "data": [[lo, 0], [u, 1], [hi, 1]], "symbol": "none", "itemStyle": {"color": TEXTO_SUAVE},
             "lineStyle": {"width": 2, "type": "dashed", "color": TEXTO_SUAVE}, "z": 1},
            {"type": "scatter", "data": puntos, "symbolSize": 44, "z": 5,
             "animationDelay": JS("function(i){return 1200 + i * 120;}"), "animationEasing": "backOut"},
        ],
    }
    echart(opcion, 440, titulo, subtitulo)


# ---------------------------------------------------------------- página 4
def convergencia(hist, optimo, titulo, subtitulo=""):
    """La línea del mejor individuo se dibuja sola, generación a generación."""
    gens = list(range(1, len(hist["mejor"]) + 1))
    opcion = {
        "legend": {**LEYENDA, "data": ["Mejor individuo", "Promedio de la población"]},
        "tooltip": {"trigger": "axis", "valueFormatter": JS("function(v){return v.toFixed(4);}")},
        "grid": {"left": 10, "right": 20, "top": 50, "bottom": 40, "containLabel": True},
        "dataZoom": [{"type": "inside"}],
        "xAxis": eje_categoria(gens, boundaryGap=False, name="Generación", nameLocation="middle", nameGap=28,
                               axisLabel={"color": TEXTO_SUAVE}, nameTextStyle={"color": TEXTO_SUAVE}),
        "yAxis": eje_valor(min=round(min(hist["promedio"]) - 0.05, 2), max=round(optimo + 0.05, 2), scale=True),
        "series": [
            {"name": "Mejor individuo", "type": "line", "data": [round(v, 4) for v in hist["mejor"]], "showSymbol": False,
             "smooth": 0.3, "itemStyle": {"color": VERDE},
             "lineStyle": {"width": 4, "color": degradado(TURQUESA, VERDE), "shadowBlur": 18, "shadowColor": alpha(VERDE, 0.6)},
             "areaStyle": {"color": degradado(alpha(VERDE, 0.30), alpha(VERDE, 0.0), vertical=True)},
             "markLine": {"silent": True, "symbol": "none", "lineStyle": {"color": AMBAR, "type": "dashed", "width": 2},
                          "label": {"formatter": "óptimo global", "color": AMBAR, "position": "insideEndTop"},
                          "data": [{"yAxis": round(optimo, 4)}]},
             "animationDuration": 3500, "animationEasing": "linear"},
            {"name": "Promedio de la población", "type": "line", "data": [round(v, 4) for v in hist["promedio"]],
             "showSymbol": False, "smooth": 0.3, "itemStyle": {"color": AZUL_CLARO},
             "lineStyle": {"width": 2, "type": "dashed", "color": AZUL_CLARO},
             "animationDuration": 3500, "animationEasing": "linear"},
        ],
    }
    echart(opcion, 400, titulo, subtitulo)


def mandato(plan, prioridades, titulo, subtitulo=""):
    """Cada frente es una batería de 3 celdas que se llena según la intensidad del mandato."""
    etiquetas = [FR_LBL[f] for f in FRENTES]
    colores = [alpha(TURQUESA, 0.75), TURQUESA, VERDE]
    series = [{"type": "bar", "data": [3] * len(FRENTES), "barWidth": 30, "barGap": "-100%", "silent": True,
               "itemStyle": {"color": "rgba(148,163,184,0.08)", "borderRadius": 8}, "z": 1, "animation": False}]
    for k in range(3):
        series.append({
            "type": "bar", "stack": "foco", "barWidth": 30, "z": 2,
            "data": [{"value": 1 if plan[f] > k else 0,
                      "tip": f"<b>{FR_LBL[f]}</b><br>Intensidad del mandato: {plan[f]}/3<br>Prioridad para Intel: "
                             f"{prioridades[f] * 100:.0f}%"} for f in FRENTES],
            "itemStyle": {"color": colores[k], "borderColor": "#0f172a", "borderWidth": 4, "borderRadius": 8,
                          "shadowBlur": 12, "shadowColor": alpha(VERDE, 0.5)},
            "animationDelay": JS(f"function(i){{return {k} * 450 + i * 90;}}"), "animationDuration": 450})
    opcion = {
        "tooltip": TOOLTIP_DATOS,
        "grid": {"left": 10, "right": 10, "top": 10, "bottom": 10, "containLabel": True},
        "xAxis": eje_valor(max=3, show=False),
        "yAxis": [eje_categoria(etiquetas, inverse=True, axisLine={"show": False},
                                axisLabel={"color": TEXTO, "fontSize": 15, "fontWeight": 600}),
                  eje_categoria([f"prioridad {prioridades[f] * 100:.0f}%" for f in FRENTES], inverse=True,
                                position="right", axisLine={"show": False},
                                axisLabel={"color": AMBAR, "fontSize": 13, "fontWeight": 700})],
        "series": series,
    }
    echart(opcion, 380, titulo, subtitulo)


# ---------------------------------------------------------------- página 5
def matriz_pagos(pagos, nash, titulo, subtitulo=""):
    nash_set = {(s, n) for s, n, *_ in nash}
    datos = []
    for i, s in enumerate(EST_INTEL):
        for j, n in enumerate(EST_NVIDIA):
            ui, un = pagos[(s, n)]
            es = (s, n) in nash_set
            datos.append({"value": [j, i, round(ui, 2)], "un": un,
                          "tip": f"Intel: <b>{s}</b><br>NVIDIA: <b>{n}</b><br>Pago Intel: {ui:.2f} · Pago NVIDIA: {un}"
                                 + ("<br><b style='color:#76B900'>Equilibrio de Nash</b>" if es else ""),
                          **({"itemStyle": {"borderColor": VERDE, "borderWidth": 4, "shadowBlur": 22,
                                            "shadowColor": alpha(VERDE, 0.7)}} if es else {})})
    opcion = {
        "tooltip": TOOLTIP_DATOS,
        "grid": {"left": 10, "right": 10, "top": 40, "bottom": 10, "containLabel": True},
        "xAxis": eje_categoria(EST_NVIDIA, position="top", axisLine={"show": False},
                               axisLabel={"color": TEXTO, "fontSize": 14, "fontWeight": 700}),
        "yAxis": eje_categoria(EST_INTEL, inverse=True, axisLine={"show": False},
                               axisLabel={"color": TEXTO, "fontSize": 14, "fontWeight": 700}),
        "visualMap": {"show": False, "min": 4, "max": 10, "dimension": 2,
                      "inRange": {"color": ["#13233f", AZUL, AZUL_CLARO]}},
        "series": [{"type": "heatmap", "data": datos,
                    "label": {"show": True, "fontSize": 20, "fontWeight": 800, "color": "#fff",
                              "formatter": JS("function(p){return p.value[2].toFixed(2)+'  ,  '+p.data.un;}")},
                    "itemStyle": {"borderRadius": 14, "borderColor": "#0f172a", "borderWidth": 6},
                    "animationDelay": JS("function(i){return i * 150;}")}],
    }
    echart(opcion, 360, titulo, subtitulo)


def arbol_minimax(mm, titulo, subtitulo=""):
    """Árbol Intel (MAX) → NVIDIA (MIN) → AMD (MIN); las ramas podadas aparecen apagadas y punteadas."""
    apagado = {"color": "#1e293b", "borderColor": "#475569", "borderType": "dashed"}

    def nodo(nombre, valor, estilo, tip, hijos=None, podado=False):
        return {"name": nombre if valor is None else f"{nombre}\n{valor:.2f}", "tip": tip,
                "itemStyle": apagado if podado else estilo,
                "label": {"color": "#64748b" if podado else "#fff"},
                "lineStyle": {"type": "dashed", "color": "#334155", "width": 1} if podado else {},
                "children": hijos or []}

    hijos_intel = []
    for s in EST_INTEL:
        hijos_n = []
        for n in EST_NVIDIA:
            hojas = []
            for a in EST_AMD:
                v = mm["hojas"].get((s, n, a))
                hojas.append(nodo(a[:2], v, {"color": "#334155", "borderColor": TEXTO_SUAVE},
                                  f"<b>{s} → {n} → {a}</b><br>" + (f"Pago de Intel: {v:.2f}" if v is not None else "Hoja podada"),
                                  podado=v is None))
            v2 = mm["nvidia"].get((s, n))
            hijos_n.append(nodo(n[:2], v2, {"color": alpha(ROJO, 0.35), "borderColor": ROJO},
                                f"<b>{s} → {n}</b><br>" + (f"Lo peor tras la respuesta de AMD: {v2:.2f}"
                                                           if v2 is not None else "Rama podada"),
                                hojas, podado=v2 is None))
        v1 = mm["intel"].get(s)
        estilo = ({"color": alpha(VERDE, 0.45), "borderColor": VERDE, "shadowBlur": 20, "shadowColor": VERDE}
                  if s == mm["jugada"] else {"color": "#1e3a5f", "borderColor": AZUL_CLARO})
        hijos_intel.append(nodo(s[:2], v1, estilo,
                                f"<b>{s}</b><br>Lo mínimo garantizado: {v1:.2f}" if v1 is not None else "Podado",
                                hijos_n, podado=v1 is None))
    raiz = nodo("Intel", mm["valor"], {"color": AZUL, "borderColor": AZUL_CLARO, "shadowBlur": 24, "shadowColor": AZUL_CLARO},
                f"<b>Intel (MAX)</b><br>Valor garantizado: {mm['valor']:.2f}<br>Elige: {mm['jugada']}", hijos_intel)
    opcion = {
        "tooltip": TOOLTIP_DATOS,
        "series": [{"type": "tree", "data": [raiz], "orient": "TB", "top": 40, "bottom": 40, "left": 90, "right": 30,
                    "symbol": "circle", "symbolSize": 50, "expandAndCollapse": False, "initialTreeDepth": -1,
                    "edgeShape": "polyline", "edgeForkPosition": "55%",
                    "lineStyle": {"color": "#64748b", "width": 2, "curveness": 0},
                    "label": {"position": "inside", "fontSize": 12, "fontWeight": 700, "lineHeight": 14},
                    "leaves": {"label": {"position": "inside"}},
                    "animationDuration": 900, "animationDurationUpdate": 600}],
        "graphic": [{"type": "text", "left": 0, "top": t, "style": {"text": txt, "fill": col, "font": "700 13px sans-serif"}}
                    for t, txt, col in ((32, "MAX · Intel", AZUL_CLARO), (155, "Estrategia", TEXTO_SUAVE),
                                        (278, "MIN · NVIDIA", ROJO), (402, "MIN · AMD", ROJO))],
    }
    echart(opcion, 470, titulo, subtitulo)


# ---------------------------------------------------------------- página 6
def decision(fin, pesos, titulo, subtitulo=""):
    """Barras apiladas con una textura distinta por componente; al final, la foto y el puntaje."""
    nombres = [c["nombre"] for c in fin]
    texturas = {
        "ag": {"symbol": "rect", "dashArrayX": [1, 0], "dashArrayY": [3, 6], "rotation": -0.7,
               "color": "rgba(255,255,255,0.18)"},
        "minimax": {"symbol": "circle", "symbolSize": 0.7, "dashArrayX": [[3, 5]], "dashArrayY": [5],
                    "color": "rgba(255,255,255,0.22)"},
        "disponibilidad": {"symbol": "rect", "dashArrayX": [1, 0], "dashArrayY": [2, 4], "rotation": 0,
                           "color": "rgba(255,255,255,0.15)"},
    }
    series = []
    for clave, nombre, color in (("ag", f"Algoritmo genético ({pesos['ag']:.0%})", VERDE),
                                 ("minimax", f"Minimax ({pesos['minimax']:.0%})", VIOLETA),
                                 ("disponibilidad", f"Disponibilidad ({pesos['disponibilidad']:.0%})", AMBAR)):
        series.append({"name": nombre, "type": "bar", "stack": "total", "barWidth": "52%",
                       "data": [{"value": round(c["aporte"][clave], 3),
                                 "tip": f"<b>{c['nombre']}</b><br>{nombre}: {c['aporte'][clave]:.3f}"} for c in fin],
                       "itemStyle": {"color": degradado(alpha(color, 0.7), color), "decal": texturas[clave],
                                     "borderColor": "#0f172a", "borderWidth": 2, "borderRadius": 6},
                       "animationDelay": JS("function(i){return i * 200;}"), "animationDuration": 1200})
    series.append({"type": "scatter", "z": 5, "symbolSize": 62, "symbolOffset": [40, 0],
                   "data": [{"value": [round(c["puntaje"], 3), c["nombre"]], "symbol": "image://" + foto_circular(c["id"]),
                             "tip": f"<b>{c['nombre']}</b><br>Puntaje final: {c['puntaje']:.3f}",
                             "label": {"show": True, "position": "right", "distance": 46, "formatter": f"{c['puntaje']:.3f}",
                                       "color": "#fff", "fontSize": 20, "fontWeight": 800}} for c in fin],
                   "animationDelay": JS("function(i){return 1100 + i * 200;}"), "animationEasing": "backOut"})
    opcion = {
        "legend": {**LEYENDA, "data": [s["name"] for s in series if "name" in s]},
        "tooltip": TOOLTIP_DATOS,
        "grid": {"left": 10, "right": 10, "top": 50, "bottom": 30, "containLabel": True},
        "xAxis": eje_valor(min=0, max=1.35, name="Puntaje final", nameLocation="middle", nameGap=26),
        "yAxis": eje_categoria(nombres, inverse=True, axisLine={"show": False},
                               axisLabel={"color": TEXTO, "fontSize": 16, "fontWeight": 700}),
        "series": series,
    }
    echart(opcion, 130 + 90 * len(fin), titulo, subtitulo)


# ---------------------------------------------------------------- bitácora
def rutas_sprint1(solucion, ubicaciones, titulo, subtitulo=""):
    """Rutas A* con un punto luminoso que recorre cada ruta."""
    colores = {"Base_Norte": AZUL_CLARO, "Base_Centro": VERDE, "Base_Sur": AMBAR}
    series = []
    for base, s in solucion.items():
        nombre = base.replace("_", " ")
        coords = [list(ubicaciones[n]) for n in s["ruta"]]
        series.append({"name": nombre, "type": "lines", "coordinateSystem": "cartesian2d", "polyline": True,
                       "data": [{"coords": coords}], "lineStyle": {"color": colores[base], "width": 3, "opacity": 0.75},
                       "effect": {"show": True, "period": 5, "trailLength": 0.35, "symbol": "circle", "symbolSize": 9,
                                  "color": "#fff"}, "tooltip": {"show": False}})
        info = ["Salida 08:00"] + [f"{i}. {p['lugar']} · {p['hora']}" for i, p in enumerate(s["pasos"], start=1)]
        series.append({"name": nombre, "type": "scatter", "symbolSize": 14,
                       "itemStyle": {"color": colores[base], "borderColor": "#fff", "borderWidth": 2,
                                     "shadowBlur": 12, "shadowColor": colores[base]},
                       "data": [{"value": c, "tip": f"<b>{nombre}</b><br>{t}"} for c, t in zip(coords, info)]})
    series.append({"type": "scatter", "symbolSize": 1, "silent": True, "itemStyle": {"color": "transparent"},
                   "label": {"show": True, "position": "top", "color": TEXTO_SUAVE, "fontSize": 12, "distance": 10,
                             "formatter": JS("function(p){return p.data.n;}")},
                   "data": [{"value": list(v), "n": k.split("_", 1)[1]} for k, v in ubicaciones.items()]})
    opcion = {
        "legend": {**LEYENDA, "data": [b.replace("_", " ") for b in solucion]},
        "tooltip": TOOLTIP_DATOS,
        "grid": {"left": 10, "right": 20, "top": 50, "bottom": 30, "containLabel": True},
        "xAxis": eje_valor(name="km  Oeste ← → Este", nameLocation="middle", nameGap=26, min=-5, max=6),
        "yAxis": eje_valor(name="km  Sur ← → Norte", nameLocation="middle", nameGap=34, min=-12, max=16),
        "series": series,
    }
    echart(opcion, 560, titulo, subtitulo)
