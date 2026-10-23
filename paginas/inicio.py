import streamlit as st

from core.datos import INTEGRANTES
from core.ui import resultados

st.caption("FUNDAMENTOS DE INTELIGENCIA ARTIFICIAL · PROYECTO DEL SEMESTRE")
st.title("Headhunter IA: el próximo CEO de Intel")
st.markdown(
    "<p class='lead'>Hacemos el trabajo de un <b>headhunter</b>, la persona que una empresa contrata para encontrar "
    "a su próximo líder. Esta vez buscamos al nuevo CEO de una empresa que pasa por un mal momento: "
    "<b>Intel</b>, que se quedó atrás frente a NVIDIA y necesita a alguien que la vuelva a poner en la pelea.</p>",
    unsafe_allow_html=True,
)

res = resultados()
if "ceo" in res:
    ceo, plan_b = res["ceo"], (res["finalistas"][1] if len(res["finalistas"]) > 1 else None)
    with st.container(border=True):
        a, b, c = st.columns([2, 2, 1.2], vertical_alignment="center")
        a.caption("CEO recomendado")  # texto en vez de st.metric para que el nombre no se corte en pantallas angostas
        a.markdown(f"### {ceo['nombre']}")
        b.caption("Plan B")
        b.markdown(f"### {plan_b['nombre'] if plan_b else '—'}")
        c.page_link("paginas/recomendacion.py", label="Ver el informe", icon=":material/arrow_forward:")

st.subheader("Primero entender a la empresa, después buscar")
st.markdown(
    "Un buen headhunter no empieza buscando candidatos. Empieza por entender **a quién necesita la empresa**: qué "
    "problemas tiene, qué errores cometieron sus líderes anteriores y hacia dónde va el mercado. Con eso define qué "
    "tipo de CEO hace falta y qué cualidades son indispensables. Después hace su trabajo de siempre:"
)

PASOS = [
    ("1", "Entender a Intel", "Un asistente de IA analiza la empresa y define el perfil del CEO.", "paginas/empresa.py"),
    ("2", "Buscar candidatos", "Siete ejecutivos reales: qué lograron y qué no lograron.", "paginas/candidatos.py"),
    ("3", "Descartar", "Quién cumple lo mínimo, y qué tan cerca está quien no cumple.", "paginas/filtro.py"),
    ("4", "Comparar", "Quién encaja mejor con los problemas de Intel y con qué plan.", "paginas/seleccion.py"),
    ("5", "Anticipar a la competencia", "Cómo reaccionarían NVIDIA y AMD con cada finalista.", "paginas/competencia.py"),
    ("6", "Recomendar", "El candidato ideal, un plan B y la razón de la elección.", "paginas/recomendacion.py"),
]
for fila in (PASOS[:3], PASOS[3:]):
    cols = st.columns(3)
    for col, (n, t, d, pag) in zip(cols, fila):
        with col:
            st.markdown(f"<div class='paso'><div class='n'>Paso {n}</div><div class='t'>{t}</div>"
                        f"<div class='d'>{d}</div></div>", unsafe_allow_html=True)
            st.page_link(pag, label="Abrir", icon=":material/arrow_forward:")

st.subheader("Cómo lo desarrollamos")
c1, c2 = st.columns(2)
with c1:
    st.markdown(
        "Lo construimos poco a poco durante el semestre, por entregas:\n"
        "- **La base:** un sistema que revisa si un candidato cumple los requisitos de un cargo, como un reclutador "
        "con su lista de chequeo.\n"
        "- **Más inteligente:** el sistema aprendió a comparar muchas opciones y escoger la mejor, y a pensar cómo "
        "reaccionaría la competencia ante las decisiones del nuevo CEO.\n"
        "- **Un analista de IA:** un asistente hace el análisis inicial de la empresa, para que el perfil del CEO se "
        "base en la situación real y no en suposiciones."
    )
with c2:
    with st.container(border=True):
        st.markdown("**Nuevo en el Sprint 4 · Lógica difusa**")
        st.markdown(
            "El filtro ya no pregunta *¿cumple o no cumple?* sino *¿qué tanto cumple?*. Quien está a una décima del "
            "mínimo ya no vale lo mismo que quien está muy lejos, y ya no hace falta bajar la exigencia cuando nadie pasa."
        )
        st.page_link("paginas/filtro.py", label="Ver el filtro difuso", icon=":material/arrow_forward:")
    st.page_link("paginas/evolucion.py", label="Bitácora de los cuatro sprints", icon=":material/timeline:")

st.divider()
st.caption(
    "Integrantes: " + ", ".join(INTEGRANTES) + ". Uso académico: los puntajes de los candidatos son estimaciones del "
    "equipo hechas con información pública; no son evaluaciones reales de esas personas."
)
