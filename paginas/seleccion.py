import streamlit as st

from core import graficas
from core.datos import FR_LBL, FRENTES
from core.ui import MARCA, OK, ALERTA, barra_intensidad, encabezado, grafica, kpis, resultados, siguiente

encabezado(4, "Comparación", "Selección y mandato de 100 días",
           "No basta con saber quién es mejor: importa quién encaja mejor con los problemas de Intel y con qué plan. Un "
           "buen CEO con el plan equivocado fracasa, como le pasó a Intel con IDM 2.0. Un algoritmo genético busca la "
           "mejor combinación de candidato y plan.")

res = resultados()
if not res["pool"]:
    st.error("Ningún candidato pasó el filtro. Baja el grado mínimo o los requisitos en el paso 3.")
    st.stop()

with st.expander("Cómo funciona el algoritmo genético", icon=":material/genetics:"):
    st.markdown(
        "- **Cromosoma (7 genes):** `[candidato, foundry, IA, CPU-DC, PC-IA, costos, alianzas]`. Cada frente tiene una "
        "intensidad de 0 (ignorar) a 3 (prioridad máxima). La suma no puede pasar de **9**: ningún CEO puede priorizar todo.\n"
        "- **Aptitud (fitness):** combina el ajuste del candidato al perfil (45 %) con el valor del plan (55 %), que premia "
        "invertir en los frentes prioritarios donde el candidato es competente.\n"
        "- **Penalizaciones:** exceso de foco; riesgo de ejecución (intensidad 3 donde el candidato es débil); *foundry sin "
        "clientes* (foco alto en foundry sin alianzas, la lección de IDM 2.0); conflicto de interés (alerta R6); y, desde "
        "el Sprint 4, **la brecha difusa**: cuanto menos cumple los requisitos, más se penaliza.\n"
        "- **Operadores:** selección por torneo (k = 3), cruce uniforme, mutación y elitismo.")
    st.latex(r"F = 0.45\,\tfrac{\text{ajuste}}{10} + 0.55\cdot 3\sum_f p_f\,\tfrac{\text{intensidad}_f}{3}\,"
             r"\tfrac{\text{competencia}_f}{10} - \text{penalizaciones} - 0.10\,(1-\text{grado})")

with st.container(border=True):
    st.markdown("**Parámetros del algoritmo** · cámbialos y observa cómo cambia la evolución")
    p1, p2, p3, p4 = st.columns(4, gap="medium")
    p1.slider("Población", 10, 100, step=2, key="ga_pob")
    p2.slider("Generaciones", 10, 150, step=5, key="ga_gen")
    p3.slider("Mutación por gen", 0.0, 0.5, step=0.01, key="ga_mut")
    p4.number_input("Semilla", 1, 999, key="ga_seed")

res = resultados()
pool, ga, ex = res["pool"], res["ga"], res["exhaustivo"]
ganador = pool[ga["mejor"][0]]
optimo = abs(ex["fitness"] - ga["fitness"]) < 1e-9

st.markdown("## Mejor combinación encontrada")
izq, der = st.columns([1, 1.3], gap="large")
with izq:
    kpis([
        ("CEO elegido por el algoritmo", ganador["nombre"], ganador["etiqueta"], ganador["color"]),
        ("Fitness", f"{ga['fitness']:.4f}", "óptimo global ✓" if optimo else "cerca del óptimo", OK if optimo else ALERTA),
    ])
    if optimo:
        st.success(f"Una búsqueda exhaustiva sobre las {ex['total']:,} combinaciones posibles confirma que el algoritmo "
                   "encontró el **mejor resultado posible**.".replace(",", "."), icon=":material/verified:")
    else:
        st.warning(f"El algoritmo quedó a {ex['fitness'] - ga['fitness']:.4f} del óptimo ({pool[ex['optimo'][0]]['nombre']}). "
                   "Prueba con más generaciones o con otra semilla.", icon=":material/info:")
with der:
    with st.container(border=True):
        st.markdown("**Mandato de 100 días** · intensidad de foco en cada frente (0 a 3)")
        for f, v in zip(FRENTES, ga["mejor"][1:]):
            st.markdown(f"<div style='display:flex;justify-content:space-between;align-items:center;padding:6px 0;"
                        f"border-bottom:1px solid #eef1f6'><span>{FR_LBL[f]}</span>"
                        f"<span>{barra_intensidad(v, MARCA)} &nbsp;<b>{v}</b></span></div>", unsafe_allow_html=True)

c1, c2 = st.columns(2, gap="large")
with c1.container(border=True):
    st.markdown("**Convergencia** · pulsa *Reproducir* para ver la evolución")
    grafica(graficas.convergencia_animada(ga["hist"], ex["fitness"]))
with c2.container(border=True):
    st.markdown("**Qué candidato elige la población** en cada generación")
    grafica(graficas.poblacion(ga["hist"], pool))

st.markdown("## El mejor plan posible para cada candidato")
st.markdown("<p class='muted'>Los tres primeros pasan a la prueba de competencia (en color).</p>", unsafe_allow_html=True)
with st.container(border=True):
    filas = [(pool[r["idx"]]["nombre"], r["fitness"], pool[r["idx"]]["color"], i < 3) for i, r in enumerate(ex["ranking"])]
    grafica(graficas.ranking_fitness(filas))

siguiente("paginas/competencia.py", "Siguiente: ¿cómo reaccionaría la competencia?", "Teoría de juegos con los 3 finalistas.")
