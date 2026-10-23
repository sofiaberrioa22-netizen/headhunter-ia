import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.sprints import BASES, CANDIDATOS_S2, REGLAS_S2, UBICACIONES, VACANTES, evaluar_sprint2, resolver_sprint1
from core.ui import encabezado, estilo

encabezado("BITÁCORA", "Cómo lo construimos",
           "El proyecto creció por entregas durante el semestre. Cada sprint agregó una técnica de inteligencia "
           "artificial y todas terminan trabajando juntas en esta app.")

linea = [
    ("Sprint 1", "Búsqueda informada (A*)", "Agentes que buscan la mejor opción con una función de costo."),
    ("Sprint 2", "Sistema experto", "La base: revisar requisitos como un reclutador con su lista de chequeo."),
    ("Sprint 3", "LLM + algoritmo genético + teoría de juegos", "Analizar a Intel, comparar opciones y anticipar a la competencia."),
    ("Sprint 4", "Lógica difusa", "Pasar de «¿cumple o no?» a «¿qué tanto cumple?»."),
]
cols = st.columns(4)
for col, (s, t, d) in zip(cols, linea):
    col.markdown(f"<div class='paso'><div class='n'>{s}</div><div class='t'>{t}</div><div class='d'>{d}</div></div>",
                 unsafe_allow_html=True)
st.write("")

t1, t2, t3, t4 = st.tabs(["Sprint 1 · A*", "Sprint 2 · Sistema experto", "Sprint 3 · Pipeline del headhunter",
                          "Sprint 4 · Lógica difusa"])

with t1:
    st.markdown("#### Rutas de supervisión de teletrabajadores en el Valle de Aburrá")
    st.write("Tres supervisores visitan a doce teletrabajadores. Cada empleado se asigna a la base más cercana y A* "
             "busca, para cada base, la ruta de menor costo f = g + h. Se respetan las ventanas horarias y la jornada "
             "de 8 horas, y se penalizan las visitas **predecibles**: si el supervisor llega a menos de 1,5 horas de la "
             "hora de la visita anterior, el empleado no se sorprende.")
    st.write("Aquí aprendimos la idea que reaparece en todo el proyecto: un agente que **evalúa alternativas con una "
             "función de costo** y escoge la mejor.")
    sol = resolver_sprint1()
    colores = {"Base_Norte": "#2563eb", "Base_Centro": "#059669", "Base_Sur": "#d97706"}
    izq, der = st.columns([1, 1.1])
    with izq:
        fig = go.Figure()
        for base, s in sol.items():
            xs = [UBICACIONES[n][0] for n in s["ruta"]]
            ys = [UBICACIONES[n][1] for n in s["ruta"]]
            fig.add_scatter(x=xs, y=ys, mode="lines+markers", name=base.replace("_", " "),
                            line=dict(color=colores[base], width=2), marker=dict(size=8))
        for n, (x, y) in UBICACIONES.items():
            fig.add_annotation(x=x, y=y, text=n.split("_", 1)[1], showarrow=False, yshift=12, font=dict(size=10))
        fig.update_xaxes(title="km (Oeste ← → Este)")
        fig.update_yaxes(title="km (Sur ← → Norte)", scaleanchor="x")
        st.plotly_chart(estilo(fig, 520), use_container_width=True)
    with der:
        base = st.radio("Base", BASES, horizontal=True, format_func=lambda b: b.replace("_", " "))
        st.dataframe(pd.DataFrame(sol[base]["pasos"]).rename(columns={
            "hora": "Hora", "lugar": "Visita", "espera_min": "Espera (min)", "sorpresa": "Sorpresa",
            "historial": "Hora anterior"}), hide_index=True, use_container_width=True)
        st.caption("Distancias en línea recta × 1,3 para simular calles reales; velocidad promedio de 24 km/h.")

with t2:
    st.markdown("#### El sistema experto de reclutamiento")
    st.write("Reglas SI → ENTONCES y un motor de **encadenamiento hacia adelante**: dispara reglas mientras aparezcan "
             "hechos nuevos. Si se cumplen los siete requisitos, el candidato es APTO. Es la base del filtro que hoy "
             "evalúa a los candidatos a CEO de Intel.")
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
    st.dataframe(pd.DataFrame([{"Vacante": VACANTES[i].cargo, "Candidato": cc.nombre,
                                "Resultado": "APTO" if evaluar_sprint2(cc, VACANTES[i])["apto"] else "NO APTO",
                                "Fallos": ", ".join(evaluar_sprint2(cc, VACANTES[i])["fallos"]) or "—"}
                               for i in range(3) for cc in CANDIDATOS_S2[i]]), hide_index=True, use_container_width=True)

with t3:
    st.markdown("#### El headhunter completo")
    st.write("Aplicamos lo anterior a un caso real: elegir al próximo CEO de Intel. El sprint tuvo dos versiones.")
    a, b = st.columns(2)
    with a.container(border=True):
        st.markdown("**Versión 1**")
        st.markdown("- El tipo de crisis se detectaba con palabras clave.\n"
                    "- El «algoritmo genético» solo subía el fitness con el número de generación: no tenía población, "
                    "cruce ni mutación, y el ganador estaba decidido desde el principio.")
    with b.container(border=True):
        st.markdown("**Versión 2 (la que usa esta app)**")
        st.markdown("- Un **LLM externo** (Gemini) analiza a Intel y devuelve un JSON con el perfil y los pesos.\n"
                    "- **Algoritmo genético real**: población, torneo, cruce, mutación y elitismo, verificado contra "
                    "la búsqueda exhaustiva.\n"
                    "- **Teoría de juegos** (clase 07): equilibrio de Nash y Minimax con poda Alfa-Beta.")
    st.markdown("| Paso de la app | Rol | Técnica |\n|---|---|---|\n"
                "| 1 · Entender a Intel | Analista de la industria | LLM externo + dossier de hechos |\n"
                "| 3 · Filtro | Headhunter: descarte | Sistema experto (Sprint 2) + lógica difusa (Sprint 4) |\n"
                "| 4 · Selección | Headhunter: comparación | Algoritmo genético |\n"
                "| 5 · Competencia | Prueba de estrés | Nash + Minimax con poda Alfa-Beta |\n"
                "| 6 · Recomendación | Decisión | Puntaje ponderado + memo del LLM |")

with t4:
    st.markdown("#### Del portero estricto al headhunter que matiza")
    st.write("El filtro del Sprint 3 funcionaba como un portero: si tienes 8 o más en tecnología entras; si no, te "
             "quedas afuera. Trataba igual a quien tenía 7,9 que a quien tenía 2, y cuando nadie pasaba había que "
             "inventar una regla de relajación que bajaba la exigencia.")
    st.write("La lógica difusa cambia la pregunta: en lugar de *¿cumple o no cumple?*, pregunta *¿qué tanto cumple?*. "
             "Cada requisito tiene una función de pertenencia en rampa, y el grado del candidato es el de su requisito "
             "**menos cumplido** (Y difuso = mínimo).")
    st.markdown("**Qué cambió en el sistema**\n"
                "- El filtro devuelve un grado de 0 a 100 % y una etiqueta: apto, parcialmente apto, poco apto o no apto.\n"
                "- Pasan a la comparación quienes superan un grado mínimo (corte α, por defecto 50 %).\n"
                "- El algoritmo genético penaliza la brecha: `−0.10 · (1 − grado)`.\n"
                "- La regla de relajación ya no hace falta.")
    st.page_link("paginas/filtro.py", label="Ver el filtro difuso en acción", icon=":material/arrow_forward:")

st.divider()
st.caption("Herramientas de IA que apoyaron el desarrollo: ChatGPT y Gemini (figuras y código de los Sprints 1 y 2), "
           "Claude (Sprint 3, Sprint 4 y esta app) y Gemini como analista del Paso 1.")
