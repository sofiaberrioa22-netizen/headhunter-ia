import streamlit as st

from core import graficas
from core.datos import FRENTES
from core.ui import ALERTA, OK, config, encabezado, galeria, grafica, kpis, resultados, siguiente, tarjeta_persona

encabezado(4, "Comparación", "Selección y mandato de 100 días",
           "Un algoritmo genético busca la mejor combinación de <b>CEO + plan</b>. Un buen CEO con el plan equivocado "
           "fracasa, como Intel con IDM 2.0.")

res = resultados()
if not res["pool"]:
    st.error("Ningún candidato pasó el filtro. Baja el grado mínimo en el paso 3.")
    st.stop()

with st.expander("Parámetros y funcionamiento del algoritmo", icon=":material/genetics:"):
    p1, p2, p3, p4 = st.columns(4, gap="medium")
    p1.slider("Población", 10, 100, step=2, key="ga_pob")
    p2.slider("Generaciones", 10, 150, step=5, key="ga_gen")
    p3.slider("Mutación por gen", 0.0, 0.5, step=0.01, key="ga_mut")
    p4.number_input("Semilla", 1, 999, key="ga_seed")
    st.markdown("Cromosoma `[candidato, foundry, IA, CPU-DC, PC-IA, costos, alianzas]` con intensidades 0-3 (máximo 9). "
                "Torneo, cruce uniforme, mutación y elitismo.")
    st.latex(r"F = 0.45\,\tfrac{\text{ajuste}}{10} + 0.55\cdot 3\sum_f p_f\,\tfrac{\text{intensidad}_f}{3}\,"
             r"\tfrac{\text{competencia}_f}{10} - \text{penalizaciones} - 0.10\,(1-\text{grado})")

res = resultados()
cfg = config()
pool, ga, ex = res["pool"], res["ga"], res["exhaustivo"]
ganador = pool[ga["mejor"][0]]
optimo = abs(ex["fitness"] - ga["fitness"]) < 1e-9

izq, der = st.columns([1, 2.2], gap="large")
with izq:
    with st.container(border=True):
        st.markdown(tarjeta_persona(ganador, "Elegido por el algoritmo", tam=84), unsafe_allow_html=True)
    kpis([("Fitness", f"{ga['fitness']:.4f}", "óptimo global ✓" if optimo else "cerca del óptimo", OK if optimo else ALERTA),
          ("Combinaciones", f"{ex['total']:,}".replace(",", "."), "verificadas una por una", "#64748b")])
with der.container(border=True):
    st.markdown("### La evolución hacia la mejor solución")
    grafica(graficas.convergencia_animada(ga["hist"], ex["fitness"]))

with st.container(border=True):
    st.markdown(f"### El mandato de {ganador['nombre']} frente a las prioridades de Intel")
    grafica(graficas.mandato(dict(zip(FRENTES, ga["mejor"][1:])), cfg["prioridades"]))

st.markdown("## Los tres finalistas")
top = [pool[r["idx"]] for r in ex["ranking"][:3]]
fit = {pool[r["idx"]]["id"]: r["fitness"] for r in ex["ranking"]}
galeria(top, pie=lambda c: f"fitness {fit[c['id']]:.4f}")

siguiente("paginas/competencia.py", "Siguiente: ¿cómo reaccionaría la competencia?")
