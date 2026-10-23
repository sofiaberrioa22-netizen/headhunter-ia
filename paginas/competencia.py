import pandas as pd
import streamlit as st

from core.juegos import EST_AMD, EST_INTEL, EST_NVIDIA, arbol_dot
from core.ui import encabezado, resultados, siguiente

encabezado("PASO 5 · PRUEBA DE ESTRÉS", "Reacción de la competencia",
           "Un CEO no decide en el vacío: NVIDIA y AMD reaccionan. Con teoría de juegos medimos qué tan bien le iría a "
           "Intel con cada finalista frente a sus rivales.")

res = resultados()
if "finalistas" not in res:
    st.error("No hay finalistas. Revisa el filtro del paso 3.")
    st.stop()
fin = res["finalistas"]

a, b = st.columns(2)
with a.container(border=True):
    st.markdown("**Juego simultáneo · Intel vs. NVIDIA**")
    st.markdown("Ambos deciden a la vez. Buscamos el **equilibrio de Nash**: la combinación en la que ninguno gana "
                "cambiando solo su decisión.")
with b.container(border=True):
    st.markdown("**Juego secuencial · Intel → NVIDIA → AMD**")
    st.markdown("Intel mueve primero y los rivales responden de la peor forma para Intel. **Minimax con poda "
                "Alfa-Beta** da el valor que Intel tiene garantizado con ese CEO.")

nombres = [c["nombre"] for c in fin]
sel = st.pills("Finalista", nombres, default=nombres[0]) or nombres[0]
c = next(x for x in fin if x["nombre"] == sel)
mm = c["minimax"]

izq, der = st.columns([1.2, 1])
with izq:
    st.markdown("**Matriz de pagos** (Intel, NVIDIA)")
    nash = {(s, n) for s, n, *_ in c["nash"]}
    df = pd.DataFrame([[f"{c['pagos'][(s, n)][0]:.2f} , {c['pagos'][(s, n)][1]}" for n in EST_NVIDIA] for s in EST_INTEL],
                      index=EST_INTEL, columns=EST_NVIDIA)
    estilo_celdas = pd.DataFrame([["background-color:#dcfce7;color:#065f46;font-weight:700" if (s, n) in nash else ""
                                   for n in EST_NVIDIA] for s in EST_INTEL], index=EST_INTEL, columns=EST_NVIDIA)
    st.dataframe(df.style.apply(lambda _: estilo_celdas, axis=None), use_container_width=True)
    st.caption("En verde, los equilibrios de Nash. Los pagos de Intel crecen con la competencia del CEO en foundry, IA "
               "y costos. Son pagos pedagógicos, como en la clase 07.")
with der:
    eq = " y ".join(f"({s}, {n})" for s, n, *_ in c["nash"]) or "sin equilibrio en estrategias puras"
    with st.container(border=True):
        st.markdown(f"**Equilibrio(s) de Nash**  \n{eq}")
    with st.container(border=True):
        st.metric("Valor garantizado (Minimax)", f"{mm['valor']:.2f}")
        evaluadas = len(mm["hojas"])
        st.markdown(f"Mejor jugada de Intel: **{mm['jugada']}**  \nHojas evaluadas: {evaluadas} de 12 "
                    f"(la poda evitó {12 - evaluadas}).")

st.markdown("**Árbol de decisión con poda Alfa-Beta**")
st.graphviz_chart(arbol_dot(mm), use_container_width=True)
st.caption("S = estrategias de Intel, N = NVIDIA, A = AMD (" + ", ".join(EST_AMD) + "). En verde, la jugada "
           "elegida; en gris punteado, las ramas podadas.")

st.subheader("Comparación de los finalistas")
st.dataframe(pd.DataFrame([{
    "Finalista": x["nombre"], "Estrategia Minimax": x["minimax"]["jugada"],
    "Valor garantizado": round(x["minimax"]["valor"], 2),
    "Equilibrios de Nash": len(x["nash"]),
} for x in fin]), hide_index=True, use_container_width=True)

siguiente("paginas/recomendacion.py", "Siguiente: recomendación")
