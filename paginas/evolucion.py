import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.sprints import BASES, CANDIDATOS_S2, REGLAS_S2, UBICACIONES, VACANTES, evaluar_sprint2, resolver_sprint1
from core.ui import encabezado, estilo, grafica

encabezado(None, "Bitácora", "Cómo lo construimos", "Cuatro sprints, una técnica de IA en cada uno.")

linea = [
    ("Sprint 1", "Búsqueda A*", "Rutas de menor costo"),
    ("Sprint 2", "Sistema experto", "La lista de chequeo"),
    ("Sprint 3", "LLM + AG + juegos", "El headhunter completo"),
    ("Sprint 4", "Lógica difusa", "¿Qué tanto cumple?"),
]
cols = st.columns(4)
for col, (s, t, d) in zip(cols, linea):
    col.markdown(f"<div class='paso'><div class='ic'>{s[-1]}</div><div class='sec' style='color:#4f46e5'>{s}</div>"
                 f"<div class='t'>{t}</div><div class='d'>{d}</div></div>", unsafe_allow_html=True)
st.write("")

t1, t2, t3, t4 = st.tabs([":material/route: Sprint 1 · A*", ":material/checklist: Sprint 2 · Sistema experto",
                          ":material/hub: Sprint 3 · Pipeline", ":material/blur_on: Sprint 4 · Lógica difusa"])

with t1:
    st.markdown("#### Rutas de supervisión en el Valle de Aburrá")
    st.caption("A* busca la ruta de menor costo f = g + h para cada base, respeta horarios y penaliza visitas predecibles.")
    sol = resolver_sprint1()
    colores = {"Base_Norte": "#4f46e5", "Base_Centro": "#10b981", "Base_Sur": "#f59e0b"}
    with st.container(border=True):
        fig = go.Figure()
        for base, s in sol.items():
            xs = [UBICACIONES[n][0] for n in s["ruta"]]
            ys = [UBICACIONES[n][1] for n in s["ruta"]]
            info = ["Salida de la base 08:00"] + [
                f"{i}. {p['lugar']} · {p['hora']}" + (f" · sorpresa {p['sorpresa'].lower()}" if p["sorpresa"] else "")
                for i, p in enumerate(s["pasos"], start=1)]
            fig.add_scatter(x=xs, y=ys, mode="lines+markers", name=base.replace("_", " "), customdata=info,
                            line=dict(color=colores[base], width=2.5), marker=dict(size=10, line=dict(color="white", width=1.5)),
                            hovertemplate="<b>" + base.replace("_", " ") + "</b><br>%{customdata}<extra></extra>")
        for n, (x, y) in UBICACIONES.items():
            fig.add_annotation(x=x, y=y, text=n.split("_", 1)[1], showarrow=False, yshift=14, font=dict(size=12))
        fig.update_xaxes(title="km (Oeste ← → Este)")
        fig.update_yaxes(title="km (Sur ← → Norte)", scaleanchor="x")
        grafica(estilo(fig, 640))
    with st.expander("Horario de cada ruta"):
        base = st.radio("Base", BASES, horizontal=True, format_func=lambda b: b.replace("_", " "))
        st.dataframe(pd.DataFrame(sol[base]["pasos"]).rename(columns={
            "hora": "Hora", "lugar": "Visita", "espera_min": "Espera (min)", "sorpresa": "Sorpresa",
            "historial": "Hora anterior"}), hide_index=True, width="stretch")

with t2:
    st.markdown("#### El sistema experto de reclutamiento")
    st.caption("Reglas SI → ENTONCES con encadenamiento hacia adelante: la base del filtro de hoy.")
    a, b = st.columns(2)
    iv = a.selectbox("Vacante", range(len(VACANTES)), format_func=lambda i: f"{VACANTES[i].cargo} ({VACANTES[i].nivel_cargo})")
    ic = b.selectbox("Candidato", range(3), format_func=lambda i: CANDIDATOS_S2[iv][i].nombre)
    v, c = VACANTES[iv], CANDIDATOS_S2[iv][ic]
    r = evaluar_sprint2(c, v)
    izq, der = st.columns(2)
    with izq.container(border=True):
        st.markdown(f"**{c.nombre}** → {'✅ CUMPLE (APTO)' if r['apto'] else '❌ NO CUMPLE (NO APTO)'}")
        st.markdown("Reglas disparadas\n" + "\n".join(f"- `{rid}` → {h}" for rid, h in r["traza"]))
        if r["fallos"]:
            st.markdown("Requisitos no cumplidos\n" + "\n".join(f"- {f}" for f in r["fallos"]))
    with der.container(border=True):
        st.markdown("**Base de reglas**")
        st.markdown("\n".join(f"- `{rid}` {desc}" for rid, desc, *_ in REGLAS_S2))

with t3:
    st.markdown("#### El headhunter completo")
    st.caption("Versión 2: LLM externo, algoritmo genético real verificado y teoría de juegos (Nash + Minimax).")
    st.markdown("| Paso de la app | Rol | Técnica |\n|---|---|---|\n"
                "| 1 · Entender a Intel | Analista de la industria | LLM externo + dossier de hechos |\n"
                "| 3 · Filtro | Headhunter: descarte | Sistema experto (Sprint 2) + lógica difusa (Sprint 4) |\n"
                "| 4 · Selección | Headhunter: comparación | Algoritmo genético |\n"
                "| 5 · Competencia | Prueba de estrés | Nash + Minimax con poda Alfa-Beta |\n"
                "| 6 · Recomendación | Decisión | Puntaje ponderado + memo del LLM |")

with t4:
    st.markdown("#### Del portero estricto al headhunter que matiza")
    st.markdown("- Cada requisito se cumple en un **grado** de 0 a 100 %; el total es el **mínimo** (eslabón más débil).\n"
                "- Siguen quienes superan el grado mínimo (50 %); el algoritmo genético penaliza lo que les falta.\n"
                "- Ya no hace falta la regla de relajación.")
    st.page_link("paginas/filtro.py", label="Ver el filtro difuso en acción", icon=":material/arrow_forward:")

st.divider()
st.caption("Herramientas de IA que apoyaron el desarrollo: ChatGPT y Gemini (figuras y código de los Sprints 1 y 2), "
           "Claude (Sprint 3, Sprint 4 y esta app) y Gemini como analista del Paso 1.")
