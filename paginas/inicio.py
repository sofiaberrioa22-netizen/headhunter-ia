import streamlit as st

from core.datos import INTEGRANTES
from core.ui import resultados

res = resultados()
ceo = res.get("ceo")
plan_b = res["finalistas"][1] if ceo and len(res["finalistas"]) > 1 else None

st.markdown(
    "<div class='hero'><span class='tag'>Fundamentos de Inteligencia Artificial · Proyecto del semestre</span>"
    "<h1>Buscamos al próximo<br><span>CEO de Intel</span></h1>"
    "<p>Hacemos el trabajo de un <b>headhunter</b>: la persona que una empresa contrata para encontrar a su próximo "
    "líder. Intel se quedó atrás frente a NVIDIA y necesita a alguien que la vuelva a poner en la pelea.</p>"
    "<div class='res'>"
    f"<div><small>CEO recomendado</small><b>{ceo['nombre'] if ceo else '—'}</b></div>"
    f"<div><small>Plan B</small><b>{plan_b['nombre'] if plan_b else '—'}</b></div>"
    f"<div><small>Candidatos evaluados</small><b>7 ejecutivos reales</b></div>"
    "</div></div>", unsafe_allow_html=True)

a, b, _ = st.columns([1.2, 1.2, 2])
if a.button("Empezar el recorrido", type="primary", icon=":material/play_arrow:", width="stretch"):
    st.switch_page("paginas/empresa.py")
if b.button("Ver la recomendación", icon=":material/workspace_premium:", width="stretch"):
    st.switch_page("paginas/recomendacion.py")

st.write("")
st.markdown("## Primero entender a la empresa, después buscar")
st.markdown(
    "<p class='muted' style='font-size:1.02rem;max-width:820px'>Un buen headhunter no empieza buscando candidatos. "
    "Empieza por entender <b>a quién necesita la empresa</b>: qué problemas tiene, qué errores cometieron sus líderes "
    "anteriores y hacia dónde va el mercado. Con eso define qué tipo de CEO hace falta. Después hace su trabajo de "
    "siempre, en seis pasos:</p>", unsafe_allow_html=True)

PASOS = [
    ("Entender a Intel", "Un asistente de IA analiza la empresa y define el perfil del CEO.", "paginas/empresa.py"),
    ("Buscar candidatos", "Siete ejecutivos reales: qué lograron y qué no lograron.", "paginas/candidatos.py"),
    ("Descartar", "Quién cumple lo mínimo y qué tan cerca está quien no cumple.", "paginas/filtro.py"),
    ("Comparar", "Quién encaja mejor con los problemas de Intel, y con qué plan.", "paginas/seleccion.py"),
    ("Anticipar a la competencia", "Cómo reaccionarían NVIDIA y AMD con cada finalista.", "paginas/competencia.py"),
    ("Recomendar", "El candidato ideal, un plan B y la razón de la elección.", "paginas/recomendacion.py"),
]
for fila in (PASOS[:3], PASOS[3:]):
    cols = st.columns(3)
    for col, (t, d, pag) in zip(cols, fila):
        n = PASOS.index((t, d, pag)) + 1
        with col:
            st.markdown(f"<div class='paso'><div class='ic'>{n}</div><div class='t'>{t}</div>"
                        f"<div class='d'>{d}</div></div>", unsafe_allow_html=True)
            st.page_link(pag, label="Abrir", icon=":material/arrow_forward:")

st.write("")
st.markdown("## Cómo lo desarrollamos")
c1, c2 = st.columns([1.15, 1], gap="large")
with c1:
    for titulo, texto, color in (
        ("La base", "Un sistema que revisa si un candidato cumple los requisitos de un cargo, como un reclutador con su "
                    "lista de chequeo.", "#4f46e5"),
        ("Más inteligente", "El sistema aprendió a comparar muchas opciones y escoger la mejor, y a pensar cómo "
                            "reaccionaría la competencia ante las decisiones del nuevo CEO.", "#0ea5e9"),
        ("Un analista de IA", "Un asistente hace el análisis inicial de la empresa, para que el perfil del CEO se base "
                              "en la situación real y no en suposiciones.", "#8b5cf6"),
    ):
        st.markdown(f"<div style='border-left:4px solid {color};padding:4px 0 4px 14px;margin-bottom:14px'>"
                    f"<b>{titulo}</b><br><span class='muted'>{texto}</span></div>", unsafe_allow_html=True)
    st.page_link("paginas/evolucion.py", label="Bitácora de los cuatro sprints", icon=":material/timeline:")
with c2:
    with st.container(border=True):
        st.markdown("<span class='chip' style='--c:#10b981'>Nuevo · Sprint 4</span>", unsafe_allow_html=True)
        st.markdown("### Lógica difusa")
        st.markdown(
            "El filtro ya no pregunta *¿cumple o no cumple?* sino **¿qué tanto cumple?**. Quien está a una décima del "
            "mínimo ya no vale lo mismo que quien está muy lejos, y ya no hace falta bajar la exigencia cuando nadie pasa.")
        st.page_link("paginas/filtro.py", label="Ver el filtro difuso", icon=":material/arrow_forward:")

st.divider()
st.caption(
    "Integrantes: " + ", ".join(INTEGRANTES) + ". Uso académico: los puntajes de los candidatos son estimaciones del "
    "equipo hechas con información pública; no son evaluaciones reales de esas personas."
)
