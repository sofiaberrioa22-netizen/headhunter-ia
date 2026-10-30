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
  .letrero {animation: cae 1.1s 1.2s cubic-bezier(.3,1.6,.5,1) both;}
  @keyframes cae {from {opacity: 0; transform: translateY(-40px);} to {opacity: 1; transform: none;}}
  .cono {animation: cono 2.4s ease-in-out infinite;}
  @keyframes cono {0%, 100% {opacity: .85;} 50% {opacity: .55;}}
  .luz {animation: luz .9s steps(2, end) infinite;} .luz.par {animation-delay: .45s;}
  @keyframes luz {0% {opacity: 1;} 100% {opacity: .2;}}
  .haz {animation: fluye 1.6s linear infinite;}
  @keyframes fluye {to {stroke-dashoffset: -48;}}
  .latido {animation: latido 2.6s ease-in-out infinite;}
  @keyframes latido {0%, 100% {opacity: 1;} 50% {opacity: .82;}}
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


def _franja(F, largo, h0, alto, fondo, color, texto):
    """Franja de rótulo sobre la cara derecha, con el texto en perspectiva isométrica."""
    banda = _poly([_pt(F, 0, 0, h0), _pt(F, largo, 0, h0), _pt(F, largo, 0, h0 + alto), _pt(F, 0, 0, h0 + alto)], fondo,
                  f"stroke='{color}' stroke-width='1.5'")
    tam = min(alto * 0.6, (largo - 14) / (0.66 * len(texto)))  # que el texto quepa en la fachada
    x, y = _pt(F, 7, 0, h0 + (alto - tam) / 2)
    return (banda + f"<text transform='matrix({C30},{-S30},0,1,{x:.1f},{y:.1f})' font-size='{tam:.1f}' "
                    f"font-weight='800' fill='{color}' letter-spacing='1'>{texto}</text>")


def _chip_iso(P, lado, color, oscuro, brillo):
    """Chip en perspectiva: sustrato con pines y un die luminoso. Devuelve (svg, punto central del die)."""
    pines = ""
    for k in range(8, int(lado) - 4, 9):
        a, b = _pt(P, k, 0, 3), _pt(P, k, -9, 3)
        c, d = _pt(P, 0, k, 3), _pt(P, -9, k, 3)
        pines += (f"<line x1='{a[0]:.1f}' y1='{a[1]:.1f}' x2='{b[0]:.1f}' y2='{b[1]:.1f}' stroke='#fbbf24' stroke-width='2.5'/>"
                  f"<line x1='{c[0]:.1f}' y1='{c[1]:.1f}' x2='{d[0]:.1f}' y2='{d[1]:.1f}' stroke='#fbbf24' stroke-width='2.5'/>")
    sustrato = _caja(P, lado, lado, 8, oscuro, "#0b1220", "#111827", color)
    Pd = _pt(P, lado * 0.22, lado * 0.22, 8)
    die = _caja(Pd, lado * 0.56, lado * 0.56, 6, brillo, color, color)
    trazas = "".join(
        f"<line x1='{_pt(Pd, t, 0, 6)[0]:.1f}' y1='{_pt(Pd, t, 0, 6)[1]:.1f}' x2='{_pt(Pd, t, lado * 0.56, 6)[0]:.1f}' "
        f"y2='{_pt(Pd, t, lado * 0.56, 6)[1]:.1f}' stroke='{oscuro}' stroke-width='1' opacity='.5'/>"
        for t in range(6, int(lado * 0.56), 7))
    centro = _pt(Pd, lado * 0.28, lado * 0.28, 6)
    return (f"<g class='latido'>{pines}{sustrato}<g filter='url(#resplandor)'>{die}</g>{trazas}</g>", centro)


def _racks(F, largo, alto, rnd):
    """Fachada del anexo como filas de servidores con LEDs."""
    out = ""
    for h in range(10, int(alto) - 8, 14):
        out += _poly([_pt(F, 6, 0, h), _pt(F, largo - 6, 0, h), _pt(F, largo - 6, 0, h + 10), _pt(F, 6, 0, h + 10)], "#0f1a0a",
                     "stroke='#3f6212' stroke-width='1'")
        for u in range(12, int(largo) - 8, 9):
            x, y = _pt(F, u, 0, h + 5)
            out += (f"<circle class='tw d{rnd.randint(1, 3)}' cx='{x:.1f}' cy='{y:.1f}' r='1.8' "
                    f"fill='{rnd.choice(['#bef264', '#76B900', '#22d3ee'])}'/>")
    return out


def _valla(x, y, ancho=210, alto=104):
    """Valla publicitaria con marco en 3D, reflectores, bombillos alternos y la lupa del headhunter."""
    prof = 10  # grosor del marco hacia atrás (en perspectiva)
    # estructura: dos patas con refuerzos cruzados
    pie_y = y + alto + 62
    patas = ""
    for px in (x + 46, x + ancho - 54):
        patas += f"<rect x='{px}' y='{y + alto}' width='8' height='{pie_y - y - alto}' fill='#334155'/>"
    patas += (f"<line x1='{x + 54}' y1='{y + alto + 8}' x2='{x + ancho - 54}' y2='{pie_y - 6}' stroke='#475569' stroke-width='3'/>"
              f"<line x1='{x + ancho - 54}' y1='{y + alto + 8}' x2='{x + 54}' y2='{pie_y - 6}' stroke='#475569' stroke-width='3'/>"
              f"<ellipse cx='{x + ancho / 2}' cy='{pie_y + 2}' rx='{ancho * 0.45:.0f}' ry='7' fill='#000' opacity='.35'/>")
    # grosor del marco (lado y techo en perspectiva)
    grosor = (f"<polygon points='{x + ancho},{y} {x + ancho + prof},{y - prof * .6} {x + ancho + prof},{y + alto - prof * .6} "
              f"{x + ancho},{y + alto}' fill='#0f172a'/>"
              f"<polygon points='{x},{y} {x + prof},{y - prof * .6} {x + ancho + prof},{y - prof * .6} {x + ancho},{y}' fill='#1e293b'/>")
    # reflectores con conos de luz
    focos = ""
    for fx in (x + 52, x + ancho - 52):
        focos += (f"<polygon class='cono' points='{fx - 6},{y - 20} {fx + 6},{y - 20} {fx + 46},{y + alto - 14} {fx - 46},{y + alto - 14}' "
                  f"fill='url(#luzfoco)'/>"
                  f"<line x1='{fx}' y1='{y - 2}' x2='{fx}' y2='{y - 18}' stroke='#64748b' stroke-width='3'/>"
                  f"<rect x='{fx - 9}' y='{y - 28}' width='18' height='10' rx='3' fill='#1e293b' stroke='#94a3b8'/>"
                  f"<rect x='{fx - 7}' y='{y - 20}' width='14' height='3' fill='#fef9c3'/>")
    # bombillos en todo el borde, encendidos en forma alterna
    bombillos = []
    paso = 15
    for t in range(0, ancho - 8, paso):
        bombillos += [(x + 8 + t, y + 7), (x + 8 + t, y + alto - 7)]
    for t in range(paso + 7, alto - 14, paso):
        bombillos += [(x + 7, y + t), (x + ancho - 7, y + t)]
    luces = "".join(
        f"<circle class='luz {'par' if n % 2 else ''}' cx='{bx:.0f}' cy='{by:.0f}' r='3.4' fill='#fef3c7' "
        f"filter='url(#resplandor)'/>" for n, (bx, by) in enumerate(bombillos))
    # contenido
    cx = x + ancho / 2
    contenido = (
        f"<rect x='{x}' y='{y}' width='{ancho}' height='{alto}' rx='8' fill='#1c1917'/>"
        f"<rect x='{x + 13}' y='{y + 13}' width='{ancho - 26}' height='{alto - 26}' rx='4' fill='url(#valla)'/>"
        f"<rect x='{x + 13}' y='{y + 13}' width='{ancho - 26}' height='{(alto - 26) * .45:.0f}' rx='4' fill='#fff' opacity='.12'/>"
        f"<text x='{cx}' y='{y + 37}' text-anchor='middle' font-size='13' font-weight='800' letter-spacing='6' "
        f"fill='#78350f'>SE BUSCA</text>"
        f"<text x='{cx}' y='{y + 82}' text-anchor='middle' font-size='46' font-weight='900' letter-spacing='3' "
        f"fill='#1c1917'>CEO</text>")
    return (f"<g class='letrero'>{patas}{grosor}{contenido}{luces}{focos}</g>")


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

    # --- Sede de NVIDIA: centro de datos de IA, con la GPU Blackwell en la azotea
    Fn = (850, 410)
    nv = _caja(Fn, 120, 110, 280, "#5a8f00", "#16260b", "#1f3a0d", "#76B900")
    nv += _ventanas(Fn, 120, 280, "der", "#d9f99d", "#2b4413", 0.85, rnd)
    nv += _ventanas(Fn, 110, 280, "izq", "#bef264", "#1d2f0e", 0.7, rnd)
    nv += _franja(Fn, 120, 236, 22, "#0b1406", "#76B900", "CENTRO DE DATOS IA")
    chip_nv, die_nv = _chip_iso(_pt(Fn, 22, 17, 280), 80, "#76B900", "#14240a", "#bef264")
    nv += chip_nv
    haces = "".join(
        f"<line class='haz' x1='{die_nv[0] + dx:.0f}' y1='{die_nv[1] - 6:.0f}' x2='{die_nv[0] + dx * 2.2:.0f}' y2='0' "
        f"stroke='#bef264' stroke-width='{w}' stroke-opacity='.55' stroke-dasharray='10 14' "
        f"style='animation-delay:{k * .3:.1f}s'/>" for k, (dx, w) in enumerate(((-18, 2), (-6, 3), (6, 3), (18, 2))))
    anexo_n = _caja((990, 420), 70, 60, 120, "#4d7c0f", "#142209", "#1b300c", "#65a30d")
    anexo_n += _racks((990, 420), 70, 120, rnd)

    # --- Sede de Intel: fábrica de chips (fab) con el procesador Panther Lake en el techo
    Fi = (420, 430)
    it = _caja(Fi, 160, 110, 115, "#1e4f80", "#0b1a2e", "#102a48", "#3B9BF5")
    it += _ventanas(Fi, 160, 115, "der", "#7cc4f5", "#16273d", 0.22, rnd)
    it += _ventanas(Fi, 110, 115, "izq", "#7cc4f5", "#13223a", 0.15, rnd)
    it += _franja(Fi, 160, 78, 20, "#081322", "#3B9BF5", "FÁBRICA DE CHIPS")
    oblea = _pt(Fi, 128, 0, 40)
    it += (f"<g transform='matrix({C30},{-S30},0,1,{oblea[0]:.1f},{oblea[1]:.1f})'>"
           f"<circle r='17' fill='#cbd5e1' stroke='#3B9BF5' stroke-width='2'/>"
           + "".join(f"<line x1='-15' y1='{y}' x2='15' y2='{y}' stroke='#64748b' stroke-width='.8'/>" for y in range(-12, 13, 6))
           + "".join(f"<line x1='{x}' y1='-15' x2='{x}' y2='15' stroke='#64748b' stroke-width='.8'/>" for x in range(-12, 13, 6))
           + "</g>")
    for u, v in ((126, 12), (140, 12), (126, 92)):  # equipos de ventilación de la sala limpia
        it += _caja(_pt(Fi, u, v, 115), 12, 12, 16, "#94a3b8", "#334155", "#475569")
    chip_it, die_it = _chip_iso(_pt(Fi, 30, 30, 115), 66, "#3B9BF5", "#0b2340", "#7cc4f5")
    it += chip_it
    techo_i = _pt(Fi, 80, 55, 115)

    # Valla "SE BUSCA CEO" frente a Intel: reflectores, bombillos de marquesina y lupa de headhunter
    letrero = _valla(118, 286)

    # Etiquetas de los chips insignia
    def etiqueta_chip(x, y, titulo, detalle, color, destino):
        ancla = x + 150 if destino[0] > x + 150 else x
        return (f"<g class='aparece'><line x1='{ancla:.0f}' y1='{y + 22:.0f}' x2='{destino[0]:.0f}' "
                f"y2='{destino[1]:.0f}' stroke='{color}' stroke-width='1.5' stroke-dasharray='4 4'/>"
                f"<circle cx='{destino[0]:.0f}' cy='{destino[1]:.0f}' r='4' fill='{color}'/>"
                f"<rect x='{x}' y='{y}' width='150' height='44' rx='10' fill='rgba(15,23,42,.9)' stroke='{color}' stroke-width='1.5'/>"
                f"<text x='{x + 75}' y='{y + 19}' text-anchor='middle' font-size='15' font-weight='800' fill='#fff'>{titulo}</text>"
                f"<text x='{x + 75}' y='{y + 36}' text-anchor='middle' font-size='12' fill='{color}'>{detalle}</text></g>")

    chips = (etiqueta_chip(640, 40, "GPU Blackwell", "el motor de la IA", "#76B900", die_nv)
             + etiqueta_chip(205, 215, "CPU Panther Lake", "proceso Intel 18A", "#3B9BF5", die_it))

    # Brecha: cota vertical
    tope_nv = _pt(Fn, 120, 0, 280)
    cota_x = tope_nv[0] + 40
    cota = (f"<g class='aparece'><line x1='{cota_x:.0f}' y1='{techo_i[1]:.0f}' x2='{cota_x:.0f}' y2='{tope_nv[1]:.0f}' "
            f"stroke='#e2e8f0' stroke-width='2' stroke-dasharray='5 5'/>"
            f"<line x1='{cota_x - 8:.0f}' y1='{tope_nv[1]:.0f}' x2='{cota_x + 8:.0f}' y2='{tope_nv[1]:.0f}' stroke='#e2e8f0' stroke-width='2'/>"
            f"<line x1='{techo_i[0]:.0f}' y1='{techo_i[1]:.0f}' x2='{cota_x + 8:.0f}' y2='{techo_i[1]:.0f}' stroke='#e2e8f0' "
            f"stroke-width='1.5' stroke-dasharray='3 6' opacity='.6'/>"
            f"<text x='{cota_x + 14:.0f}' y='{(techo_i[1] + tope_nv[1]) / 2:.0f}' font-size='30' font-weight='900' fill='#fff'>6×</text>"
            f"<text x='{cota_x + 14:.0f}' y='{(techo_i[1] + tope_nv[1]) / 2 + 22:.0f}' font-size='14' fill='#cbd5e1'>más ingresos</text></g>")

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
    <linearGradient id='valla' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#fde68a'/>
      <stop offset='1' stop-color='#f59e0b'/></linearGradient>
    <linearGradient id='luzfoco' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#fef9c3' stop-opacity='.55'/>
      <stop offset='1' stop-color='#fef9c3' stop-opacity='0'/></linearGradient>
    <filter id='resplandor'><feGaussianBlur stdDeviation='6' result='b'/><feMerge><feMergeNode in='b'/>
      <feMergeNode in='SourceGraphic'/></feMerge></filter>
  </defs>
  <rect width='1200' height='470' fill='url(#cielo)'/>
  <rect width='1200' height='470' fill='url(#halo)'/>
  {estrellas}
  <circle cx='110' cy='70' r='26' fill='#fef3c7' opacity='.9'/><circle cx='122' cy='62' r='24' fill='#0a1024'/>
  {lejanos}
  {piso}{rejilla}
  <g class='aparece'>{haces}</g>
  <g class='sube c'>{anexo_n}</g>
  <g class='sube'>{nv}</g>
  <g class='sube b'>{it}</g>
  {letrero}
  {chips}
  {cota}
  {rotulo(_pt(Fn, 60, 0, 0)[0], 400, 'NVIDIA', 'US$96,2 B por trimestre', '#76B900')}
  {rotulo(_pt(Fi, 80, 0, 0)[0] - 20, 400, 'Intel', 'US$16,1 B por trimestre', '#3B9BF5')}
</svg>"""


def edificios_img():
    datos = base64.b64encode(edificios_svg().encode("utf-8")).decode()
    return (f"<img class='carrera' src='data:image/svg+xml;base64,{datos}' "
            f"alt='El centro de datos de IA de NVIDIA, con la GPU Blackwell, domina el horizonte; la fábrica de chips de Intel, con el procesador Panther Lake, busca un nuevo CEO'>")
