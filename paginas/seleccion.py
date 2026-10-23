import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.datos import FR_LBL, FRENTES
from core.ui import config, encabezado, estilo, puntos, resultados, siguiente

encabezado("PASO 4 · COMPARACIÓN", "Selección y mandato de 100 días",
           "No basta con saber quién es mejor: importa quién encaja mejor con los problemas de Intel y con qué plan. "
           "Un buen CEO con el plan equivocado fracasa, como le pasó a Intel con IDM 2.0. Un algoritmo genético busca "
           "la mejor combinación de candidato y plan.")

res = resultados()
if not res["pool"]:
    st.error("Ningún candidato pasó el filtro. Baja el grado mínimo o los requisitos en el paso 3.")
    st.stop()

pool, ga, ex = res["pool"], res["ga"], res["exhaustivo"]

with st.expander("Cómo funciona el algoritmo genético", expanded=False):
    st.markdown(
        "- **Cromosoma (7 genes):** `[candidato, foundry, IA, CPU-DC, PC-IA, costos, alianzas]`. Cada frente tiene una "
        "intensidad de 0 (ignorar) a 3 (prioridad máxima). La suma no puede pasar de **9**: ningún CEO puede priorizar todo.\n"
        "- **Aptitud (fitness):** combina el ajuste del candidato al perfil (45 %) con el valor del plan (55 %), que "
        "premia invertir en los frentes prioritarios donde el candidato es competente.\n"
        "- **Penalizaciones:** exceso de foco; riesgo de ejecución (intensidad 3 donde el candidato es débil); "
        "*foundry sin clientes* (foco alto en foundry sin alianzas, la lección de IDM 2.0); conflicto de interés "
        "(alerta R6); y, desde el Sprint 4, **la brecha difusa**: cuanto menos cumple los requisitos, más se penaliza.\n"
        "- **Operadores:** selección por torneo (k = 3), cruce uniforme, mutación y elitismo."
    )
    st.latex(r"F = 0.45\,\tfrac{\text{ajuste}}{10} + 0.55\cdot 3\sum_f p_f\,\tfrac{\text{intensidad}_f}{3}\,"
             r"\tfrac{\text{competencia}_f}{10} - \text{penalizaciones} - 0.10\,(1-\text{grado})")

with st.container(border=True):
    st.markdown("**Parámetros**")
    p1, p2, p3, p4 = st.columns(4)
    p1.slider("Población", 10, 100, step=2, key="ga_pob")
    p2.slider("Generaciones", 10, 150, step=5, key="ga_gen")
    p3.slider("Mutación por gen", 0.0, 0.5, step=0.01, key="ga_mut")
    p4.number_input("Semilla", 1, 999, key="ga_seed")
res = resultados()
pool, ga, ex = res["pool"], res["ga"], res["exhaustivo"]

ganador = pool[ga["mejor"][0]]
st.subheader("Mejor combinación encontrada")
g = st.columns([1.6] + [1] * len(FRENTES))
g[0].metric("CEO", ganador["nombre"])
for col, f, v in zip(g[1:], FRENTES, ga["mejor"][1:]):
    col.metric(FR_LBL[f], puntos(v))

if abs(ex["fitness"] - ga["fitness"]) < 1e-9:
    st.success(f"Fitness {ga['fitness']:.4f}. Una búsqueda exhaustiva sobre las {ex['total']:,} combinaciones "
               "posibles confirma que el algoritmo genético encontró el **óptimo global**.".replace(",", "."),
               icon=":material/verified:")
else:
    st.warning(f"El algoritmo quedó a {ex['fitness'] - ga['fitness']:.4f} del óptimo ({pool[ex['optimo'][0]]['nombre']}). "
               "Prueba con más generaciones o con otra semilla.", icon=":material/info:")

c1, c2 = st.columns(2)
gens = list(range(1, len(ga["hist"]["mejor"]) + 1))
with c1:
    fig = go.Figure()
    fig.add_scatter(x=gens, y=ga["hist"]["mejor"], name="Mejor", line=dict(color="#2563eb", width=3))
    fig.add_scatter(x=gens, y=ga["hist"]["promedio"], name="Promedio de la población", line=dict(color="#94a3b8", dash="dash"))
    fig.add_scatter(x=gens, y=[ex["fitness"]] * len(gens), name="Óptimo exhaustivo", line=dict(color="#059669", dash="dot", width=1))
    fig.update_xaxes(title="Generación")
    fig.update_yaxes(title="Fitness")
    st.markdown("**Convergencia**")
    st.plotly_chart(estilo(fig, 320), use_container_width=True)
with c2:
    fig = go.Figure()
    for i, c in enumerate(pool):
        fig.add_scatter(x=gens, y=[v * 100 for v in ga["hist"]["proporcion"][i]], name=c["nombre"], stackgroup="uno",
                        line=dict(color=c["color"], width=0.5))
    fig.update_yaxes(title="% de la población", range=[0, 100])
    fig.update_xaxes(title="Generación")
    st.markdown("**Qué candidato elige la población**")
    st.plotly_chart(estilo(fig, 320), use_container_width=True)

st.subheader("El mejor plan posible para cada candidato")
st.dataframe(pd.DataFrame([{
    "Candidato": pool[r["idx"]]["nombre"],
    "Grado difuso": pool[r["idx"]]["grado"],
    "Ajuste": round(pool[r["idx"]]["ajuste"], 2),
    **{FR_LBL[f]: puntos(v) for f, v in zip(FRENTES, r["plan"])},
    "Fitness": round(r["fitness"], 4),
    "Finalista": i < 3,
} for i, r in enumerate(ex["ranking"])]), hide_index=True, use_container_width=True, column_config={
    "Grado difuso": st.column_config.ProgressColumn(min_value=0, max_value=1, format="percent"),
    "Finalista": st.column_config.CheckboxColumn(),
})
st.caption("Los tres mejores pasan a la prueba de competencia.")

siguiente("paginas/competencia.py", "Siguiente: reacción de la competencia")
