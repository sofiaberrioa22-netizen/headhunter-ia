"""Render de gráficas ECharts en paneles oscuros con textura.

Cada gráfica arranca su animación cuando entra en pantalla (IntersectionObserver) y tiene un botón para repetirla.
Las opciones se arman como dict en Python; las funciones de JavaScript se pasan con JS("...").
"""
import itertools
import json
import re

import streamlit.components.v1 as components

ECHARTS_CDN = "https://cdn.jsdelivr.net/npm/echarts@5.5.1/dist/echarts.min.js"

# Paleta "Rivalidad"
VERDE, AZUL, AZUL_CLARO = "#76B900", "#0071C5", "#3B9BF5"
TURQUESA, AMBAR, VIOLETA, ROJO, GRIS = "#14B8A6", "#F59E0B", "#8B5CF6", "#EF4444", "#64748B"
TEXTO, TEXTO_SUAVE, REJILLA, PANEL = "#e2e8f0", "#94a3b8", "rgba(148,163,184,0.12)", "#0f172a"

_contador = itertools.count()
_JS = {}


def JS(codigo):
    """Marca un fragmento de código JavaScript para insertarlo sin comillas en las opciones."""
    clave = f"__JS_{next(_contador)}__"
    _JS[clave] = codigo
    return clave


def _serializar(opcion):
    texto = json.dumps(opcion, ensure_ascii=False)
    return re.sub(r'"(__JS_\d+__)"', lambda m: _JS.get(m.group(1), "null"), texto)


def degradado(c1, c2, vertical=False):
    return {"type": "linear", "x": 0, "y": 0, "x2": 0 if vertical else 1, "y2": 1 if vertical else 0,
            "colorStops": [{"offset": 0, "color": c1}, {"offset": 1, "color": c2}]}


def alpha(hex_color, a):
    h = hex_color.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{a})"


def eje_categoria(datos, **kw):
    base = {"type": "category", "data": datos, "axisLine": {"lineStyle": {"color": REJILLA}}, "axisTick": {"show": False},
            "axisLabel": {"color": TEXTO, "fontSize": 14}}
    base.update(kw)
    return base


def eje_valor(**kw):
    base = {"type": "value", "splitLine": {"lineStyle": {"color": REJILLA, "type": "dashed"}},
            "axisLabel": {"color": TEXTO_SUAVE, "fontSize": 12}, "nameTextStyle": {"color": TEXTO_SUAVE, "fontSize": 12}}
    base.update(kw)
    return base


TOOLTIP = {"backgroundColor": "rgba(15,23,42,0.96)", "borderColor": "rgba(148,163,184,0.25)", "borderWidth": 1,
           "padding": [10, 14], "textStyle": {"color": "#f8fafc", "fontSize": 13},
           "extraCssText": "border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,.45);"}

LEYENDA = {"top": 0, "left": 0, "textStyle": {"color": TEXTO, "fontSize": 13}, "itemGap": 18, "icon": "roundRect"}

_PLANTILLA = """<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700;800&display=swap" rel="stylesheet">
<script src="__CDN__"></script>
<style>
html, body {margin: 0; background: transparent; font-family: 'Source Sans 3', 'Segoe UI', sans-serif;}
.panel {position: relative; overflow: hidden; border-radius: 20px; padding: 18px 20px 10px;
  background: radial-gradient(900px 260px at 100% 0%, rgba(118,185,0,.13), transparent 60%),
              radial-gradient(700px 300px at 0% 100%, rgba(0,113,197,.20), transparent 60%),
              linear-gradient(160deg, #0b1220 0%, #121b31 100%);
  border: 1px solid rgba(148,163,184,.14); box-shadow: 0 18px 40px -24px rgba(2,6,23,.8);}
.panel::before {content: ""; position: absolute; inset: 0; pointer-events: none; opacity: .55;
  background-image: radial-gradient(rgba(255,255,255,.07) 1px, transparent 1.2px); background-size: 16px 16px;}
.panel::after {content: ""; position: absolute; inset: 0; pointer-events: none;
  background: repeating-linear-gradient(115deg, rgba(255,255,255,.012) 0 2px, transparent 2px 9px);}
.cab {position: relative; z-index: 2; display: flex; justify-content: space-between; align-items: flex-start; gap: 12px;}
.cab > div {min-width: 0;}
h3, p {white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
h3 {margin: 0; color: #f8fafc; font-size: clamp(15px, 3.6vw, 20px); font-weight: 800; letter-spacing: -.01em;}
p {margin: 3px 0 0; color: #94a3b8; font-size: 13.5px;}
@media (max-width: 520px) {.panel {padding: 14px 12px 8px;} p {font-size: 12px;}}
button {flex: none; cursor: pointer; border: 1px solid rgba(148,163,184,.3); background: rgba(255,255,255,.04);
  color: #cbd5e1; border-radius: 10px; padding: 5px 11px; font: 600 12px 'Source Sans 3', sans-serif;}
button:hover {border-color: #76B900; color: #fff;}
#c {position: relative; z-index: 1; width: 100%; height: __ALTO__px;}
</style></head><body>
<div class="panel">
  <div class="cab"><div>__TITULO__</div><button onclick="repetir()" title="Repetir la animación">↻ Animar</button></div>
  <div id="c"></div>
</div>
<script>
const el = document.getElementById('c');
const chart = echarts.init(el, null, {renderer: 'canvas'});
const opt = __OPCION__;
function repetir() { chart.clear(); chart.setOption(opt, true); }
let visto = false;
const io = new IntersectionObserver((e) => {
  if (e[0].isIntersecting && !visto) { visto = true; chart.setOption(opt, true); }
}, {threshold: 0.2});
io.observe(el);
setTimeout(() => { if (!visto) { visto = true; chart.setOption(opt, true); } }, 4000);
window.addEventListener('resize', () => chart.resize());
__EXTRA__
</script></body></html>"""


def echart(opcion, alto=420, titulo="", subtitulo="", extra_js=""):
    """Dibuja la gráfica en un panel oscuro. `alto` es el alto del área de la gráfica en píxeles."""
    base = {"backgroundColor": "transparent", "animationDuration": 1400, "animationEasing": "cubicOut",
            "animationDurationUpdate": 700, "textStyle": {"fontFamily": "Source Sans 3, Segoe UI, sans-serif"},
            "tooltip": TOOLTIP,
            "toolbox": {"right": 0, "top": 0, "itemSize": 14, "iconStyle": {"borderColor": TEXTO_SUAVE},
                        "feature": {"saveAsImage": {"title": "Descargar", "backgroundColor": PANEL, "pixelRatio": 2}}}}
    for k, v in base.items():
        if k == "tooltip" and "tooltip" in opcion:
            opcion["tooltip"] = {**TOOLTIP, **opcion["tooltip"]}
        else:
            opcion.setdefault(k, v)
    cab = (f"<h3>{titulo}</h3>" if titulo else "") + (f"<p>{subtitulo}</p>" if subtitulo else "")
    html = (_PLANTILLA.replace("__CDN__", ECHARTS_CDN).replace("__ALTO__", str(alto)).replace("__TITULO__", cab)
            .replace("__OPCION__", _serializar(opcion)).replace("__EXTRA__", extra_js))
    alto_cab = 0 if not cab else (62 if subtitulo else 40)
    components.html(html, height=alto + alto_cab + 34, scrolling=False)
