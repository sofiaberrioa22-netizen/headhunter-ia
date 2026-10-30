import streamlit as st

from core import graficas
from core.portada import CSS_CARRERA, carrera_img
from core.ui import MARCA, OK, VIOLETA, avatar, encabezado, kpis, resultados, siguiente

encabezado(5, "Prueba de estrés", "Reacción de la competencia",
           "NVIDIA y AMD reaccionan. La teoría de juegos mide cuánto le garantiza cada finalista a Intel.")

st.html(CSS_CARRERA + "<div class='hero' style='padding:22px 26px'><span class='tag'>La carrera por el liderazgo "
        "en IA</span>" + carrera_img() + "</div>")

res = resultados()
if "finalistas" not in res:
    st.error("No hay finalistas. Revisa el filtro del paso 3.")
    st.stop()
fin = res["finalistas"]

cols = st.columns(len(fin))
nombres = [c["nombre"] for c in fin]
for col, x in zip(cols, fin):
    with col.container(border=True):
        st.markdown(f"<div class='persona'>{avatar(x, 64)}<div><div class='pn'>{x['nombre']}</div>"
                    f"<div class='pc'>{x['minimax']['jugada']}</div></div><div style='margin-left:auto;text-align:right'>"
                    f"<div style='font-size:2rem;font-weight:800;color:#0f172a;line-height:1'>{x['minimax']['valor']:.2f}</div>"
                    f"<div class='pc'>garantizado</div></div></div>", unsafe_allow_html=True)

sel = st.segmented_control("Ver el juego con", nombres, default=nombres[0]) or nombres[0]
c = next(x for x in fin if x["nombre"] == sel)
mm = c["minimax"]

graficas.arbol_minimax(mm, f"Intel → NVIDIA → AMD con {c['nombre']}",
                       f"Minimax con poda Alfa-Beta · verde: jugada elegida · punteado: {12 - len(mm['hojas'])} ramas podadas")

izq, der = st.columns([1.5, 1], gap="large")
with izq:
    graficas.matriz_pagos(c["pagos"], c["nash"], "Intel vs. NVIDIA · equilibrio de Nash",
                          "Pagos (Intel , NVIDIA) · recuadro verde = equilibrio")
with der:
    kpis([("Valor garantizado", f"{mm['valor']:.2f}", "lo mínimo que Intel asegura", VIOLETA)])
    kpis([("Mejor jugada", mm["jugada"].split(" ", 1)[1], "estrategia Minimax", OK)])
    kpis([("Equilibrios de Nash", str(len(c["nash"])), "recuadros verdes en la matriz", MARCA)])

siguiente("paginas/recomendacion.py", "Siguiente: la recomendación")
