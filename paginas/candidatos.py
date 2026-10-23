import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.datos import CANDIDATOS, CRIT_LBL, CRITERIOS
from core.genetico import ajuste_estrategico
from core.ui import config, encabezado, estilo, lista, siguiente

encabezado("PASO 2 · BÚSQUEDA", "Candidatos",
           "Siete ejecutivos reales y reconocidos de la industria de semiconductores. Para cada uno revisamos qué "
           "logró y qué no logró en las empresas que ha dirigido.")

st.info("Los puntajes de 0 a 10 son **estimaciones del equipo** a partir de información pública (uso académico). "
        "Pat Gelsinger, el CEO anterior de Intel, se incluye como **candidato de control**: el sistema debería "
        "detectar que su perfil no resuelve los problemas actuales.", icon=":material/info:")

cfg = config()
nombres = [c["nombre"] for c in CANDIDATOS]
sel = st.pills("Candidato", nombres, default=nombres[0], label_visibility="collapsed") or nombres[0]
c = next(x for x in CANDIDATOS if x["nombre"] == sel)

izq, der = st.columns([1.15, 1])
with izq:
    with st.container(border=True):
        st.markdown(f"### {c['nombre']}")
        st.caption(f"{c['cargo']} · {c['exp_ceo']} años como CEO")
        m1, m2, m3 = st.columns(3)
        m1.metric("Ajuste al perfil", f"{ajuste_estrategico(c, cfg['pesos']):.2f}", help="Promedio de sus 8 cualidades "
                  "ponderado con la importancia que definió el analista (0 a 10).")
        m2.metric("Disponibilidad", f"{c['disponibilidad']*100:.0f}%", help="Probabilidad estimada de que acepte el cargo.")
        m3.metric("Conflicto de interés", "Sí" if c["conflicto"] else "No", help="Dirige hoy a un competidor o proveedor.")
        st.markdown("**Lo que logró**")
        st.markdown(lista(c["logros"]))
        st.markdown("**Lo que no logró**")
        st.markdown(lista(c["no_logros"]))
with der:
    mx = max(cfg["pesos"].values())
    etiquetas = [CRIT_LBL[k] for k in CRITERIOS]
    fig = go.Figure()
    fig.add_scatterpolar(r=[c[k] for k in CRITERIOS] + [c[CRITERIOS[0]]], theta=etiquetas + etiquetas[:1],
                         fill="toself", name=c["nombre"], line_color=c["color"], opacity=0.85)
    fig.add_scatterpolar(r=[10 * cfg["pesos"][k] / mx for k in CRITERIOS] + [10 * cfg["pesos"][CRITERIOS[0]] / mx],
                         theta=etiquetas + etiquetas[:1], name="Importancia para Intel (escalada a 10)",
                         line=dict(color="#94a3b8", dash="dash"))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, 10], showticklabels=False, gridcolor="#e2e8f0"),
                                 angularaxis=dict(gridcolor="#e2e8f0"), bgcolor="rgba(0,0,0,0)"))
    st.markdown("**Su perfil frente a lo que Intel necesita**")
    st.plotly_chart(estilo(fig, 400), use_container_width=True)

st.subheader("Todos los candidatos")
tabla = pd.DataFrame([{
    "Candidato": x["nombre"], "Años CEO": x["exp_ceo"], **{CRIT_LBL[k]: x[k] for k in CRITERIOS},
    "Ajuste": round(ajuste_estrategico(x, cfg["pesos"]), 2), "Disponibilidad": x["disponibilidad"],
} for x in CANDIDATOS]).sort_values("Ajuste", ascending=False)
st.dataframe(tabla, hide_index=True, use_container_width=True, column_config={
    "Ajuste": st.column_config.ProgressColumn("Ajuste", min_value=0, max_value=10, format="%.2f"),
    "Disponibilidad": st.column_config.NumberColumn(format="percent"),
})

siguiente("paginas/filtro.py", "Siguiente: filtro de requisitos")
