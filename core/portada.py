"""Ilustración de la portada: la carrera entre NVIDIA e Intel (SVG propio, animado con CSS)."""
import base64

_ANIMACION = """<style>
    .nv {animation: nv 2.4s cubic-bezier(.2,.8,.2,1) both;}
    .it {animation: it 2.4s cubic-bezier(.2,.8,.2,1) both;}
    .gap {animation: aparecer 1s 2s both;}
    @keyframes nv {from {transform: translateX(-880px);} to {transform: translateX(0);}}
    @keyframes it {from {transform: translateX(-260px);} to {transform: translateX(0);}}
    @keyframes aparecer {from {opacity: 0;} to {opacity: 1;}}
  </style>"""


def _chip(x, y, escala, color, oscuro, nombre, cifra):
    """Chip con pines, dibujado en el origen y ubicado con translate/scale."""
    pines = "".join(
        f"<rect x='{18 + i * 22}' y='-12' width='10' height='12' rx='2' fill='{color}' opacity='.75'/>"
        f"<rect x='{18 + i * 22}' y='86' width='10' height='12' rx='2' fill='{color}' opacity='.75'/>"
        for i in range(6))
    return (
        f"<g transform='translate({x} {y}) scale({escala})'>{pines}"
        f"<rect width='150' height='86' rx='16' fill='{oscuro}' stroke='{color}' stroke-width='3'/>"
        f"<rect x='12' y='12' width='126' height='62' rx='10' fill='none' stroke='{color}' stroke-opacity='.35'/>"
        f"<text x='75' y='44' text-anchor='middle' font-size='26' font-weight='800' fill='white'>{nombre}</text>"
        f"<text x='75' y='66' text-anchor='middle' font-size='15' font-weight='700' fill='{color}'>{cifra}</text></g>")


def carrera_svg():
    verde, azul = "#76b900", "#3b9bf5"
    rapidez = "".join(
        f"<line x1='{520 + i * 40}' y1='{58 + (i % 3) * 26}' x2='{800 + i * 10}' y2='{58 + (i % 3) * 26}' "
        f"stroke='{verde}' stroke-width='3' stroke-linecap='round' opacity='{0.15 + 0.07 * i}'/>" for i in range(5))
    meta = "".join(
        f"<rect x='{1140 + (j % 2) * 12}' y='{30 + j * 12}' width='12' height='12' fill='{'#ffffff' if j % 2 == 0 else '#0b1437'}' "
        f"opacity='.9'/>" for j in range(20))
    return f"""
<svg viewBox='0 0 1200 290' xmlns='http://www.w3.org/2000/svg' font-family='Segoe UI, Helvetica, Arial, sans-serif'>
  {_ANIMACION}
  <defs>
    <linearGradient id='pista' x1='0' x2='1'><stop offset='0' stop-color='#ffffff' stop-opacity='.02'/>
      <stop offset='1' stop-color='#ffffff' stop-opacity='.09'/></linearGradient>
    <filter id='brillo'><feGaussianBlur stdDeviation='10' result='b'/><feMerge><feMergeNode in='b'/>
      <feMergeNode in='SourceGraphic'/></feMerge></filter>
  </defs>
  <rect x='20' y='20' width='1160' height='250' rx='22' fill='url(#pista)'/>
  <line x1='40' y1='145' x2='1130' y2='145' stroke='white' stroke-opacity='.18' stroke-width='2' stroke-dasharray='18 14'/>
  {meta}
  <text x='1125' y='286' text-anchor='end' font-size='13' fill='#94a3b8' letter-spacing='3'>META · LIDERAZGO EN IA</text>
  <g class='nv'>
    {rapidez}
    <g filter='url(#brillo)'>{_chip(840, 30, 1.45, verde, '#13240a', 'NVIDIA', 'US$96,2 B')}</g>
  </g>
  <g class='it'>{_chip(200, 170, 1.0, azul, '#0b2340', 'Intel', 'US$16,1 B')}</g>
  <text x='610' y='242' text-anchor='middle' font-size='20' fill='#cbd5e1' class='gap'>
    ← NVIDIA factura <tspan font-weight='800' fill='white'>6 veces más</tspan> por trimestre →</text>
</svg>"""


def carrera_img():
    """Streamlit filtra los <svg> incrustados en HTML; como imagen (data URI) se muestra y conserva la animación."""
    datos = base64.b64encode(carrera_svg().encode("utf-8")).decode()
    return (f"<img class='carrera' src='data:image/svg+xml;base64,{datos}' "
            f"alt='Carrera de chips: NVIDIA va muy por delante de Intel'>")


CSS_CARRERA = """
<style>
.carrera {width: 100%; height: auto; display: block; margin-top: 18px;}
</style>
"""
