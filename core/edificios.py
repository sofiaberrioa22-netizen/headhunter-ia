"""Ilustración isométrica de la portada: la sede de NVIDIA domina el horizonte y la de Intel necesita un nuevo CEO.

SVG propio. Se entrega como imagen (data URI) porque Streamlit filtra los <svg> incrustados; las animaciones CSS
van dentro del propio SVG.
"""
import base64
import random

C30, S30 = 0.866, 0.5

_ESTILO = """<style>
  .sube {transform-box: fill-box; transform-origin: 50% 100%; animation: sube 1.6s cubic-bezier(.2,.8,.2,1) both;}
  .sube.b {animation-delay: .35s;} .sube.c {animation-delay: .7s;}
  @keyframes sube {from {transform: scaleY(0);} to {transform: scaleY(1);}}
  .tw {animation: tw 3s ease-in-out infinite;}
  .tw.d1 {animation-duration: 2.2s;} .tw.d2 {animation-duration: 3.7s; animation-delay: .8s;}
  .tw.d3 {animation-duration: 4.6s; animation-delay: 1.5s;}
  @keyframes tw {0%, 100% {opacity: 1;} 50% {opacity: .35;}}
  .baliza {animation: baliza 1.4s steps(2, end) infinite;}
  @keyframes baliza {0% {opacity: 1;} 100% {opacity: .15;}}
  .letrero {transform-box: fill-box; transform-origin: 50% 0%; animation: vaiven 2.8s ease-in-out infinite alternate,
            aparecer 1s 1.4s both;}
  @keyframes vaiven {from {transform: rotate(-7deg);} to {transform: rotate(7deg);}}
  .flecha {animation: flecha 2.2s 1.6s ease-in-out infinite;}
  @keyframes flecha {0%, 100% {transform: translateY(0); opacity: .9;} 50% {transform: translateY(-10px); opacity: 1;}}
  .aparece {animation: aparecer 1s 1.2s both;}
  @keyframes aparecer {from {opacity: 0;} to {opacity: 1;}}
  .estrella {animation: tw 4s ease-in-out infinite;}
</style>"""


def _pt(F, u, v, h):
    """Punto isométrico: F es la esquina frontal en el piso; u avanza a la derecha, v a la izquierda, h hacia arriba."""
    return (F[0] + u * C30 - v * C30, F[1] - u * S30 - v * S30 - h)


def _poly(puntos, fill, extra=""):
    return f"<polygon points='{' '.join(f'{x:.1f},{y:.1f}' for x, y in puntos)}' fill='{fill}' {extra}/>"


def _caja(F, w, d, h, arriba, izq, der, borde="none"):
    e = f"stroke='{borde}' stroke-width='1'" if borde != "none" else ""
    return (_poly([_pt(F, 0, 0, 0), _pt(F, w, 0, 0), _pt(F, w, 0, h), _pt(F, 0, 0, h)], der, e)
            + _poly([_pt(F, 0, 0, 0), _pt(F, 0, d, 0), _pt(F, 0, d, h), _pt(F, 0, 0, h)], izq, e)
            + _poly([_pt(F, 0, 0, h), _pt(F, w, 0, h), _pt(F, w, d, h), _pt(F, 0, d, h)], arriba, e))


def _ventanas(F, largo, alto, cara, encendida, apagada, prob, rnd, ancho=9, alto_v=11, margen=8, sep=6):
    """Rejilla de ventanas en una cara ('der' a lo largo de u, 'izq' a lo largo de v)."""
    out = []
    cols = int((largo - 2 * margen + sep) // (ancho + sep))
    filas = int((alto - 2 * margen + sep) // (alto_v + sep))
    for i in range(cols):
        for j in range(filas):
            a0 = margen + i * (ancho + sep)
            h0 = margen + j * (alto_v + sep)
            if cara == "der":
                pts = [_pt(F, a0, 0, h0), _pt(F, a0 + ancho, 0, h0), _pt(F, a0 + ancho, 0, h0 + alto_v), _pt(F, a0, 0, h0 + alto_v)]
            else:
                pts = [_pt(F, 0, a0, h0), _pt(F, 0, a0 + ancho, h0), _pt(F, 0, a0 + ancho, h0 + alto_v), _pt(F, 0, a0, h0 + alto_v)]
            if rnd.random() < prob:
                out.append(_poly(pts, encendida, f"class='tw d{rnd.randint(1, 3)}'"))
            else:
                out.append(_poly(pts, apagada))
    return "".join(out)


def edificios_svg():
    rnd = random.Random(7)
    estrellas = "".join(
        f"<circle class='estrella' cx='{rnd.randint(10, 1190)}' cy='{rnd.randint(8, 190)}' r='{rnd.choice([0.8, 1.1, 1.5])}' "
        f"fill='#fff' opacity='{rnd.uniform(.3, .9):.2f}' style='animation-delay:{rnd.uniform(0, 4):.1f}s'/>"
        for _ in range(70))
    lejanos = "".join(
        f"<rect x='{x}' y='{440 - h}' width='{w}' height='{h}' fill='#1b2747' opacity='.55'/>"
        for x, w, h in ((0, 60, 90), (70, 40, 140), (120, 70, 70), (600, 50, 110), (660, 35, 160), (1000, 60, 120),
                        (1070, 45, 180), (1125, 75, 95), (230, 50, 60), (950, 40, 80)))

    # Piso isométrico
    piso = _poly([(600, 470), (1180, 135), (600, -200), (20, 135)], "url(#piso)")
    rejilla = "".join(
        f"<line x1='{600 - k * 58 * C30:.0f}' y1='{470 - k * 58 * S30:.0f}' x2='{1180 - k * 58 * C30:.0f}' "
        f"y2='{135 - k * 58 * S30:.0f}' stroke='rgba(148,163,184,.10)'/>" for k in range(0, 12))

    # --- Sede de NVIDIA: torre alta, verde, ventanas encendidas
    Fn = (850, 410)
    nv = _caja(Fn, 120, 110, 280, "#5a8f00", "#16260b", "#1f3a0d", "#76B900")
    nv += _ventanas(Fn, 120, 280, "der", "#d9f99d", "#2b4413", 0.85, rnd)
    nv += _ventanas(Fn, 110, 280, "izq", "#bef264", "#1d2f0e", 0.7, rnd)
    techo = _pt(Fn, 60, 55, 280)
    nv += (f"<line x1='{techo[0]:.0f}' y1='{techo[1]:.0f}' x2='{techo[0]:.0f}' y2='{techo[1] - 46:.0f}' stroke='#cbd5e1' "
           f"stroke-width='3'/><circle class='baliza' cx='{techo[0]:.0f}' cy='{techo[1] - 48:.0f}' r='6' fill='#ef4444'/>")
    anexo_n = _caja((990, 420), 70, 60, 120, "#4d7c0f", "#142209", "#1b300c", "#65a30d")
    anexo_n += _ventanas((990, 420), 70, 120, "der", "#d9f99d", "#2b4413", 0.75, rnd)

    # --- Sede de Intel: edificio bajo, azul apagado, en obra
    Fi = (420, 430)
    it = _caja(Fi, 160, 110, 115, "#1e4f80", "#0b1a2e", "#102a48", "#3B9BF5")
    it += _ventanas(Fi, 160, 115, "der", "#7cc4f5", "#16273d", 0.22, rnd)
    it += _ventanas(Fi, 110, 115, "izq", "#7cc4f5", "#13223a", 0.15, rnd)
    andamio = "".join(
        f"<line x1='{_pt(Fi, 0, v, 0)[0]:.0f}' y1='{_pt(Fi, 0, v, 0)[1]:.0f}' x2='{_pt(Fi, 0, v, 132)[0]:.0f}' "
        f"y2='{_pt(Fi, 0, v, 132)[1]:.0f}' stroke='#f59e0b' stroke-width='2' opacity='.8'/>" for v in range(-6, 116, 24))
    andamio += "".join(
        f"<line x1='{_pt(Fi, 0, -6, h)[0]:.0f}' y1='{_pt(Fi, 0, -6, h)[1]:.0f}' x2='{_pt(Fi, 0, 114, h)[0]:.0f}' "
        f"y2='{_pt(Fi, 0, 114, h)[1]:.0f}' stroke='#f59e0b' stroke-width='2' opacity='.8'/>" for h in (30, 66, 102, 132))
    techo_i = _pt(Fi, 80, 55, 115)

    # Grúa con el letrero que se balancea
    mx, base_y, top_y = 215, 420, 150
    grua = (f"<line x1='{mx}' y1='{base_y}' x2='{mx}' y2='{top_y}' stroke='#f59e0b' stroke-width='6'/>"
            + "".join(f"<line x1='{mx - 6}' y1='{y}' x2='{mx + 6}' y2='{y + 14}' stroke='#b45309' stroke-width='2'/>"
                      for y in range(top_y + 6, base_y, 18))
            + f"<line x1='{mx - 40}' y1='{top_y}' x2='{mx + 210}' y2='{top_y}' stroke='#f59e0b' stroke-width='6'/>"
            + f"<line x1='{mx}' y1='{top_y - 30}' x2='{mx + 210}' y2='{top_y}' stroke='#f59e0b' stroke-width='2'/>"
            + f"<line x1='{mx}' y1='{top_y - 30}' x2='{mx - 40}' y2='{top_y}' stroke='#f59e0b' stroke-width='2'/>"
            + f"<rect x='{mx - 52}' y='{top_y}' width='26' height='18' fill='#78350f'/>")
    cx = mx + 175
    letrero = (f"<g class='letrero'><line x1='{cx}' y1='{top_y}' x2='{cx}' y2='{top_y + 60}' stroke='#e2e8f0' stroke-width='2'/>"
               f"<line x1='{cx}' y1='{top_y + 60}' x2='{cx - 70}' y2='{top_y + 80}' stroke='#e2e8f0' stroke-width='1.5'/>"
               f"<line x1='{cx}' y1='{top_y + 60}' x2='{cx + 70}' y2='{top_y + 80}' stroke='#e2e8f0' stroke-width='1.5'/>"
               f"<rect x='{cx - 82}' y='{top_y + 80}' width='164' height='50' rx='8' fill='#fbbf24' stroke='#78350f' "
               f"stroke-width='3'/><text x='{cx}' y='{top_y + 112}' text-anchor='middle' font-size='21' font-weight='900' "
               f"fill='#1c1917' letter-spacing='1'>SE BUSCA CEO</text></g>")

    # Brecha: cota vertical y flecha de crecimiento
    tope_nv = _pt(Fn, 120, 0, 280)
    cota_x = tope_nv[0] + 40
    cota = (f"<g class='aparece'><line x1='{cota_x:.0f}' y1='{techo_i[1]:.0f}' x2='{cota_x:.0f}' y2='{tope_nv[1]:.0f}' "
            f"stroke='#e2e8f0' stroke-width='2' stroke-dasharray='5 5'/>"
            f"<line x1='{cota_x - 8:.0f}' y1='{tope_nv[1]:.0f}' x2='{cota_x + 8:.0f}' y2='{tope_nv[1]:.0f}' stroke='#e2e8f0' stroke-width='2'/>"
            f"<line x1='{techo_i[0]:.0f}' y1='{techo_i[1]:.0f}' x2='{cota_x + 8:.0f}' y2='{techo_i[1]:.0f}' stroke='#e2e8f0' "
            f"stroke-width='1.5' stroke-dasharray='3 6' opacity='.6'/>"
            f"<text x='{cota_x + 14:.0f}' y='{(techo_i[1] + tope_nv[1]) / 2:.0f}' font-size='30' font-weight='900' fill='#fff'>6×</text>"
            f"<text x='{cota_x + 14:.0f}' y='{(techo_i[1] + tope_nv[1]) / 2 + 22:.0f}' font-size='14' fill='#cbd5e1'>más ingresos</text></g>")
    flecha = (f"<g class='flecha'><path d='M {Fn[0] - 170} 150 Q {Fn[0] - 110} 120 {Fn[0] - 80} 60' fill='none' stroke='#76B900' "
              f"stroke-width='5' stroke-linecap='round'/><polygon points='{Fn[0] - 92},{62} {Fn[0] - 72},{48} {Fn[0] - 70},{74}' "
              f"fill='#76B900'/></g>")

    # Rótulos
    def rotulo(x, y, nombre, cifra, color):
        return (f"<g class='aparece'><rect x='{x - 90}' y='{y}' width='180' height='54' rx='12' fill='rgba(15,23,42,.85)' "
                f"stroke='{color}' stroke-width='2'/><text x='{x}' y='{y + 24}' text-anchor='middle' font-size='20' "
                f"font-weight='900' fill='#fff'>{nombre}</text><text x='{x}' y='{y + 44}' text-anchor='middle' "
                f"font-size='14' font-weight='700' fill='{color}'>{cifra}</text></g>")

    return f"""<svg viewBox='0 0 1200 470' xmlns='http://www.w3.org/2000/svg' font-family='Segoe UI, Helvetica, Arial, sans-serif'>
  {_ESTILO}
  <defs>
    <linearGradient id='cielo' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#060b1a'/>
      <stop offset='1' stop-color='#13204a'/></linearGradient>
    <linearGradient id='piso' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#111c38'/>
      <stop offset='1' stop-color='#0a1124'/></linearGradient>
    <radialGradient id='halo' cx='.72' cy='.35' r='.45'><stop offset='0' stop-color='#76B900' stop-opacity='.35'/>
      <stop offset='1' stop-color='#76B900' stop-opacity='0'/></radialGradient>
  </defs>
  <rect width='1200' height='470' fill='url(#cielo)'/>
  <rect width='1200' height='470' fill='url(#halo)'/>
  {estrellas}
  <circle cx='110' cy='70' r='26' fill='#fef3c7' opacity='.9'/><circle cx='122' cy='62' r='24' fill='#0a1024'/>
  {lejanos}
  {piso}{rejilla}
  <g class='sube c'>{anexo_n}</g>
  <g class='sube'>{nv}</g>
  {flecha}
  <g class='sube b'>{it}{andamio}</g>
  {grua}{letrero}
  {cota}
  {rotulo(_pt(Fn, 60, 0, 0)[0], 400, 'NVIDIA', 'US$96,2 B por trimestre', '#76B900')}
  {rotulo(_pt(Fi, 80, 0, 0)[0] - 20, 400, 'Intel', 'US$16,1 B por trimestre', '#3B9BF5')}
</svg>"""


def edificios_img():
    datos = base64.b64encode(edificios_svg().encode("utf-8")).decode()
    return (f"<img class='carrera' src='data:image/svg+xml;base64,{datos}' "
            f"alt='La sede de NVIDIA domina el horizonte; Intel, más baja y en obra, busca un nuevo CEO'>")
