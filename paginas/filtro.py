import pandas as pd
import streamlit as st

from core import graficas
from core.datos import CANDIDATOS, REQ_ATRIB, REQ_LBL
from core.difuso import tolerancia_de
from core.experto import construir_reglas
from core.ui import (MAL, MARCA, MODO_CLASICO, MODO_DIFUSO, OK, chip, config, encabezado, grafica, kpis, resultados,
                     siguiente)

encabezado(3, "Descarte", "Filtro de requisitos",
           "Descartamos a quienes no cumplen lo mínimo que Intel necesita. Desde el Sprint 4 el filtro usa lógica difusa: "
           "ya no pregunta si el candidato cumple, sino qué tanto cumple.")

antes, ahora = st.columns(2)
with antes.container(border=True):
    st.markdown(f"{chip('Antes · Sprint 3', '#64748b')}", unsafe_allow_html=True)
    st.markdown("#### Un portero estricto")
    st.markdown("*Si tienes 8 o más en tecnología, entras; si no, te quedas afuera.* Trata igual a quien tiene 7,9 y a "
                "quien tiene 2. Cuando nadie pasaba, había que usar una **regla de relajación** que bajaba la exigencia.")
with ahora.container(border=True):
    st.markdown(f"{chip('Ahora · Sprint 4', OK)}", unsafe_allow_html=True)
    st.markdown("#### Un headhunter que matiza")
    st.markdown("Cada requisito se cumple en un **grado** de 0 a 100 %. El grado total es el del requisito **menos "
                "cumplido**: una cadena es tan fuerte como su eslabón más débil.")

st.write("")
with st.container(border=True):
    st.segmented_control("Filtro que usa el resto del sistema", [MODO_DIFUSO, MODO_CLASICO], key="modo")
    cfg = config()
    if cfg["modo"] == "difuso":
        c1, c2, c3 = st.columns(3, gap="large")
        c1.slider("Tolerancia en puntajes", 0.5, 4.0, step=0.5, key="tol_puntos",
                  help="Cuántos puntos por debajo del mínimo empieza a contar el grado. Con 2: el mínimo de tecnología "
                       "es 8, así que 6 vale 0 %, 7 vale 50 % y 8 vale 100 %.")
        c2.slider("Tolerancia en años como CEO", 1.0, 4.0, step=1.0, key="tol_anos")
        c3.slider("Grado mínimo para seguir en el proceso", 0.1, 1.0, step=0.05, key="corte",
                  help="Corte α: solo los candidatos con un grado igual o mayor pasan a la comparación (paso 4).")

cfg = config()
res = resultados()
por_id = {c["id"]: c for c in CANDIDATOS}
clasico = {r["id"]: r for r in res["clasico"]["resultados"]}
difuso = {r["id"]: r for r in res["difuso"]}
req = cfg["requisitos"]

# ---------------------------------------------------------------- resumen
n_clas = sum(k["apto"] for k in clasico.values())
if cfg["modo"] == "difuso":
    pasan = [i for i, d in difuso.items() if d["grado"] >= cfg["corte"]]
    recuperados = [por_id[i]["nombre"] for i in pasan if not clasico[i]["apto"]]
    kpis([
        ("Aptos con el filtro clásico", f"{n_clas} de 7", "todo o nada", "#64748b"),
        ("Siguen con lógica difusa", f"{len(pasan)} de 7", f"grado ≥ {cfg['corte']:.0%}", OK),
        ("Recuperados", str(len(recuperados)), "estaban cerca del mínimo", MARCA),
        ("Regla de relajación", "No se necesita", f"el clásico la usó {res['clasico']['relajaciones']} veces", "#8b5cf6"),
    ])
    if recuperados:
        st.success("**Candidatos que el filtro clásico habría perdido:** " + ", ".join(recuperados) + ". Siguen en el "
                   "proceso, pero con una penalización proporcional a lo que les falta (paso 4).", icon=":material/person_add:")
else:
    kpis([("Aptos con el filtro clásico", f"{n_clas} de 7", "todo o nada", "#64748b"),
          ("Reglas de relajación aplicadas", str(res["clasico"]["relajaciones"]), "bajan la exigencia si nadie pasa", MAL)])

# ---------------------------------------------------------------- mapa de grados
st.markdown("## Qué tanto cumple cada candidato")
orden = sorted(CANDIDATOS, key=lambda c: -difuso[c["id"]]["grado"])
izq, der = st.columns([1.35, 1], gap="large")
with izq:
    with st.container(border=True):
        filas = [{"nombre": c["nombre"], "grados": difuso[c["id"]]["grados"], "grado": difuso[c["id"]]["grado"]}
                 for c in orden]
        grafica(graficas.mapa_grados(filas, {r: REQ_LBL[r] for r in req}))
        st.caption("Verde = cumple del todo · azul y amarillo = cumple en parte · rojo = no cumple. "
                   "Pasa el mouse sobre una celda para ver el detalle.")
with der:
    with st.container(border=True):
        for c in orden:
            d, k = difuso[c["id"]], clasico[c["id"]]
            sigue = d["grado"] >= cfg["corte"] if cfg["modo"] == "difuso" else k["apto"]
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;align-items:center;gap:8px;padding:7px 0;"
                f"border-bottom:1px solid #eef1f6'><div><b>{c['nombre']}</b><br><span class='muted' style='font-size:0.8rem'>"
                f"{('Lo frena: ' + d['limitante']) if d['limitante'] else 'Cumple todo'} · clásico: "
                f"{'apto' if k['apto'] else 'no apto'}</span></div><div style='text-align:right'>{chip(d['etiqueta'], d['color'])}"
                f"<br><span style='font-size:0.78rem;color:{OK if sigue else MAL};font-weight:600'>"
                f"{'sigue en el proceso' if sigue else 'queda afuera'}</span></div></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------- función de pertenencia
st.markdown("## Cómo se calcula el grado")
izq, der = st.columns([1, 1.45], gap="large")
with izq:
    req_sel = st.radio("Requisito", list(req), format_func=lambda r: REQ_LBL[r], horizontal=True)
    u = req[req_sel]
    t = tolerancia_de(req_sel, cfg["tol_puntos"], cfg["tol_anos"])
    with st.container(border=True):
        st.markdown(f"Mínimo pedido **{u:g}** · tolerancia **{t:g}**")
        st.markdown(f"- Con **{u - t:g} o menos** → grado 0 %\n"
                    f"- Entre **{u - t:g} y {u:g}** → el grado sube en línea recta\n"
                    f"- Con **{u:g} o más** → grado 100 %")

    def debilidades(d):
        return ", ".join(f"{REQ_LBL[r].lower()} ({g:.0%})" for r, g in sorted(d["grados"].items(), key=lambda x: x[1])
                         if g < 1) or "ninguna"

    for cid, nota in (("C6", "El filtro clásico lo descartaba por completo aunque estaba cerca."),
                      ("C7", "Es el candidato de control: el sistema debe seguir descartando a quien debe descartar.")):
        d = difuso[cid]
        st.markdown(f"{chip(d['etiqueta'], d['color'])} **{por_id[cid]['nombre']}** · grado {d['grado']:.0%}  \n"
                    f"<span class='muted' style='font-size:0.9rem'>No cumple del todo: {debilidades(d)}. {nota}</span>",
                    unsafe_allow_html=True)
with der:
    with st.container(border=True):
        grados = {c["id"]: difuso[c["id"]]["grados"][req_sel] for c in CANDIDATOS}
        grafica(graficas.pertenencia(CANDIDATOS, REQ_ATRIB[req_sel], grados, u, t, REQ_LBL[req_sel]))
        st.caption("Línea azul: lógica difusa. Línea punteada: el filtro clásico salta de 0 a 100 % en el mínimo.")

with st.expander("Base de reglas del sistema experto (Sprints 2 y 3)", icon=":material/rule:"):
    st.write("El sistema experto se conserva. Sus reglas de alerta (R5 y R6) siguen activas en los dos modos: no "
             "descartan, pero penalizan en el paso 4.")
    for r in construir_reglas(res["clasico"]["req"]):
        st.markdown(f"`{r.id_regla}` {r.descripcion}")
    st.markdown("**Regla difusa (Sprint 4)**")
    st.markdown("`D1` SI experiencia ES suficiente Y tecnología ES suficiente Y gobernanza ES suficiente Y "
                "transformación ES suficiente ENTONCES candidato ES apto  \n"
                "Y difuso = mínimo de los grados. Etiquetas: **Apto** (100 %), **Parcialmente apto** (50 % o más), "
                "**Poco apto** (más de 0 %), **No apto** (0 %).")
    st.markdown("**Traza del encadenamiento hacia adelante (filtro clásico)**")
    st.dataframe(pd.DataFrame([{"Candidato": por_id[i]["nombre"], "Reglas disparadas": " → ".join(k["traza"]) or "—",
                                "Dictamen": "APTO" if k["apto"] else "NO APTO"} for i, k in clasico.items()]),
                 hide_index=True, width="stretch")

siguiente("paginas/seleccion.py", "Siguiente: comparar a los que siguen", "Algoritmo genético: candidato + mandato de 100 días.")
