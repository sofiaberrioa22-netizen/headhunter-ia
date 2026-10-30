import streamlit as st

from core.datos import CANDIDATOS, INTEGRANTES
from core.edificios import edificios_img
from core.portada import CSS_CARRERA
from core.ui import galeria, resultados

res = resultados()
ceo = res.get("ceo")
plan_b = res["finalistas"][1] if ceo and len(res["finalistas"]) > 1 else None

st.html(
    CSS_CARRERA +
    "<div class='hero'><span class='tag'>Fundamentos de IA · Proyecto del semestre</span>"
    "<h1>Buscamos al próximo <span>CEO de Intel</span></h1>"
    "<p>NVIDIA tomó la delantera. Un headhunter con inteligencia artificial elige al líder que puede devolver a Intel "
    "a la pelea.</p>"
    + edificios_img() +
    "<div class='res'>"
    f"<div><small>CEO recomendado</small><b>{ceo['nombre'] if ceo else '—'}</b></div>"
    f"<div><small>Plan B</small><b>{plan_b['nombre'] if plan_b else '—'}</b></div>"
    "<div><small>Candidatos evaluados</small><b>7 ejecutivos reales</b></div>"
    "</div></div>")

a, b, _ = st.columns([1.2, 1.2, 2.4])
if a.button("Empezar el recorrido", type="primary", icon=":material/play_arrow:", width="stretch"):
    st.switch_page("paginas/empresa.py")
if b.button("Ver la recomendación", icon=":material/workspace_premium:", width="stretch"):
    st.switch_page("paginas/recomendacion.py")

st.markdown("## Los candidatos")
galeria(CANDIDATOS, pie=lambda c: c["cargo"].split(" (")[0].split(";")[0])

st.markdown("## El método en seis pasos")
PASOS = [
    ("Entender a Intel", "Análisis con IA", "paginas/empresa.py"),
    ("Candidatos", "7 ejecutivos reales", "paginas/candidatos.py"),
    ("Filtro", "Lógica difusa", "paginas/filtro.py"),
    ("Selección", "Algoritmo genético", "paginas/seleccion.py"),
    ("Competencia", "Teoría de juegos", "paginas/competencia.py"),
    ("Recomendación", "CEO + plan B", "paginas/recomendacion.py"),
]
cols = st.columns(6)
for n, (col, (t, d, pag)) in enumerate(zip(cols, PASOS), start=1):
    with col:
        st.markdown(f"<div class='paso'><div class='ic'>{n}</div><div class='t'>{t}</div><div class='d'>{d}</div></div>",
                    unsafe_allow_html=True)
        st.page_link(pag, label="Abrir", icon=":material/arrow_forward:")

st.divider()
st.caption("Integrantes: " + ", ".join(INTEGRANTES) + " · Uso académico: los puntajes son estimaciones del equipo.")
