import pandas as pd
import streamlit as st

from core import graficas
from core.datos import CANDIDATOS, CRIT_LBL, CRITERIOS
from core.genetico import ajuste_estrategico
from core.ui import ALERTA, MAL, MARCA, OK, chip, config, encabezado, grafica, kpis, lista_html, siguiente

encabezado(2, "Búsqueda", "Candidatos",
           "Siete ejecutivos reales y reconocidos de la industria de semiconductores. Para cada uno revisamos qué logró y "
           "qué no logró en las empresas que ha dirigido.")

cfg = config()
ajustes = {c["id"]: ajuste_estrategico(c, cfg["pesos"]) for c in CANDIDATOS}

st.info("Los puntajes de 0 a 10 son **estimaciones del equipo** a partir de información pública (uso académico). "
        "Pat Gelsinger, el CEO anterior de Intel, se incluye como **candidato de control**: el sistema debería detectar "
        "que su perfil no resuelve los problemas actuales.", icon=":material/info:")

nombres = [c["nombre"] for c in CANDIDATOS]
sel = st.pills("Elige un candidato", nombres, default=nombres[0]) or nombres[0]
c = next(x for x in CANDIDATOS if x["nombre"] == sel)

izq, der = st.columns([1.05, 1], gap="large")
with izq:
    with st.container(border=True):
        st.markdown(f"<div style='display:flex;align-items:center;gap:12px'>"
                    f"<div style='width:46px;height:46px;border-radius:14px;background:{c['color']};color:white;"
                    f"display:flex;align-items:center;justify-content:center;font-weight:800;font-size:1.1rem'>"
                    f"{''.join(p[0] for p in c['nombre'].replace('.', ' ').split()[:2])}</div>"
                    f"<div><div style='font-size:1.45rem;font-weight:800;color:#0f172a;line-height:1.1'>{c['nombre']}</div>"
                    f"<div class='muted' style='font-size:0.9rem'>{c['cargo']}</div></div></div>", unsafe_allow_html=True)
        st.write("")
        kpis([
            ("Ajuste al perfil", f"{ajustes[c['id']]:.2f}", "de 10 puntos", MARCA),
            ("Años como CEO", str(c["exp_ceo"]), "experiencia al mando", "#64748b"),
            ("Disponibilidad", f"{c['disponibilidad'] * 100:.0f}%", "probabilidad de aceptar", OK if c["disponibilidad"] >= 0.3 else ALERTA),
        ])
        if c["conflicto"]:
            st.markdown(chip("Dirige hoy a un competidor o proveedor", MAL), unsafe_allow_html=True)
        st.markdown(f"<div class='sec' style='color:{OK}'>Lo que logró</div>" + lista_html(c["logros"], OK) +
                    f"<div class='sec' style='color:{MAL}'>Lo que no logró</div>" + lista_html(c["no_logros"], MAL),
                    unsafe_allow_html=True)
with der:
    with st.container(border=True):
        comparar = st.multiselect("Comparar con", [n for n in nombres if n != sel], placeholder="Agrega candidatos al radar")
        sel_c = [c] + [x for x in CANDIDATOS if x["nombre"] in comparar]
        st.markdown("**Su perfil frente a lo que Intel necesita**")
        grafica(graficas.radar(sel_c, cfg["pesos"]))
        st.caption("Pasa el mouse por cada punta para ver el puntaje. Haz clic en la leyenda para ocultar o mostrar un perfil.")

st.write("")
st.markdown("## Todos los candidatos de un vistazo")
izq, der = st.columns([1.25, 1], gap="large")
with izq:
    with st.container(border=True):
        st.markdown("**Ajuste al perfil vs. probabilidad de aceptar** · el tamaño indica los años como CEO")
        grafica(graficas.mapa_candidatos(CANDIDATOS, ajustes))
with der:
    tabla = pd.DataFrame([{"Candidato": x["nombre"], "Ajuste": round(ajustes[x["id"]], 2),
                           "Años CEO": x["exp_ceo"], "Disponibilidad": x["disponibilidad"]}
                          for x in CANDIDATOS]).sort_values("Ajuste", ascending=False)
    st.dataframe(tabla, hide_index=True, width="stretch", height=300, column_config={
        "Ajuste": st.column_config.ProgressColumn("Ajuste", min_value=0, max_value=10, format="%.2f"),
        "Disponibilidad": st.column_config.NumberColumn(format="percent"),
    })
    with st.expander("Ver los 8 puntajes de cada candidato"):
        st.dataframe(pd.DataFrame([{"Candidato": x["nombre"], **{CRIT_LBL[k]: x[k] for k in CRITERIOS}}
                                   for x in CANDIDATOS]), hide_index=True, width="stretch")

siguiente("paginas/filtro.py", "Siguiente: descartar a quien no cumple lo mínimo", "Filtro con lógica difusa.")
