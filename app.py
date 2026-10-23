"""Headhunter IA: el próximo CEO de Intel. Fundamentos de IA, Sprints 1 a 4."""
import streamlit as st

from core.datos import INTEGRANTES
from core.ui import CSS, MODO_CLASICO, iniciar_estado, resultados

st.set_page_config(page_title="Headhunter IA", page_icon=":material/person_search:", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)
iniciar_estado()

paginas = {
    "": [st.Page("paginas/inicio.py", title="Inicio", icon=":material/home:", default=True)],
    "El trabajo del headhunter": [
        st.Page("paginas/empresa.py", title="1 · Entender a Intel", icon=":material/apartment:"),
        st.Page("paginas/candidatos.py", title="2 · Candidatos", icon=":material/groups:"),
        st.Page("paginas/filtro.py", title="3 · Filtro de requisitos", icon=":material/filter_alt:"),
        st.Page("paginas/seleccion.py", title="4 · Selección y mandato", icon=":material/genetics:"),
        st.Page("paginas/competencia.py", title="5 · Reacción de la competencia", icon=":material/swords:"),
        st.Page("paginas/recomendacion.py", title="6 · Recomendación", icon=":material/workspace_premium:"),
    ],
    "Bitácora": [st.Page("paginas/evolucion.py", title="Cómo lo construimos", icon=":material/timeline:")],
}
nav = st.navigation(paginas)

with st.sidebar:
    res = resultados()
    st.caption("ESTADO DEL ANÁLISIS")
    st.markdown(f"**Filtro:** {'Clásico' if st.session_state.get('modo') == MODO_CLASICO else 'Lógica difusa'}  \n"
                f"**Pasan el filtro:** {len(res['pool'])} de 7  \n"
                f"**Recomendado:** {res['ceo']['nombre'] if 'ceo' in res else '—'}")
    st.divider()
    st.caption("Fundamentos de IA · " + ", ".join(INTEGRANTES))

nav.run()
