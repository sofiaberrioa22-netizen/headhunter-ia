import streamlit as st

from core import graficas
from core.juegos import EST_AMD
from core.ui import MAL, MARCA, OK, VIOLETA, chip, encabezado, grafica, kpis, resultados, siguiente

encabezado(5, "Prueba de estrés", "Reacción de la competencia",
           "Un CEO no decide en el vacío: NVIDIA y AMD reaccionan. Con teoría de juegos medimos qué tan bien le iría a "
           "Intel con cada finalista frente a sus rivales.")

res = resultados()
if "finalistas" not in res:
    st.error("No hay finalistas. Revisa el filtro del paso 3.")
    st.stop()
fin = res["finalistas"]

a, b = st.columns(2)
with a.container(border=True):
    st.markdown(chip("Juego simultáneo", MARCA), unsafe_allow_html=True)
    st.markdown("#### Intel vs. NVIDIA")
    st.markdown("Ambos deciden a la vez. Buscamos el **equilibrio de Nash**: la combinación en la que ninguno gana "
                "cambiando solo su decisión.")
with b.container(border=True):
    st.markdown(chip("Juego secuencial", VIOLETA), unsafe_allow_html=True)
    st.markdown("#### Intel → NVIDIA → AMD")
    st.markdown("Intel mueve primero y los rivales responden de la peor forma para Intel. **Minimax con poda Alfa-Beta** "
                "da el valor que Intel tiene garantizado con ese CEO.")

st.write("")
nombres = [c["nombre"] for c in fin]
sel = st.pills("Finalista", nombres, default=nombres[0]) or nombres[0]
c = next(x for x in fin if x["nombre"] == sel)
mm = c["minimax"]
evaluadas = len(mm["hojas"])

kpis([
    ("Valor garantizado", f"{mm['valor']:.2f}", "lo mínimo que Intel asegura", VIOLETA),
    ("Mejor jugada de Intel", mm["jugada"].split(" ", 1)[1], mm["jugada"].split(" ", 1)[0], OK),
    ("Equilibrios de Nash", str(len(c["nash"])), "en estrategias puras", MARCA),
    ("Ramas podadas", f"{12 - evaluadas} de 12", "gracias a Alfa-Beta", MAL),
])

izq, der = st.columns([1, 1], gap="large")
with izq.container(border=True):
    st.markdown("**Matriz de pagos** (Intel , NVIDIA)")
    grafica(graficas.matriz_pagos(c["pagos"], c["nash"]))
    st.caption("Recuadro verde = equilibrio de Nash. Los pagos de Intel crecen con la competencia del CEO en foundry, IA y "
               "costos. Son pagos pedagógicos, como en la clase 07.")
with der:
    st.markdown("**Comparación de los finalistas** · valor garantizado con cada uno")
    for x in fin:
        with st.container(border=True):
            st.markdown(f"<div style='display:flex;justify-content:space-between;align-items:center'>"
                        f"<div><span style='display:inline-block;width:10px;height:10px;border-radius:50%;"
                        f"background:{x['color']};margin-right:8px'></span><b>{x['nombre']}</b><br>"
                        f"<span class='muted' style='font-size:0.85rem'>{x['minimax']['jugada']} · {len(x['nash'])} "
                        f"equilibrio(s) de Nash</span></div><div style='font-size:1.7rem;font-weight:800'>"
                        f"{x['minimax']['valor']:.2f}</div></div>", unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("**Árbol de decisión con poda Alfa-Beta** · pasa el mouse por los nodos")
    grafica(graficas.arbol_minimax(mm))
    st.caption("S = estrategias de Intel, N = NVIDIA, A = AMD (" + ", ".join(EST_AMD) + "). Verde: jugada elegida. "
               "Gris punteado: ramas podadas.")

siguiente("paginas/recomendacion.py", "Siguiente: la recomendación final", "CEO recomendado, plan B y memo para la junta.")
