import streamlit as st

from core import graficas
from core.datos import CANDIDATOS
from core.genetico import ajuste_estrategico
from core.ui import (ALERTA, MAL, MARCA, OK, avatar, chip, config, encabezado, grafica, kpis, lista_html, siguiente)

encabezado(2, "Búsqueda", "Los candidatos", "Siete ejecutivos reales de la industria de semiconductores.")

cfg = config()
ajustes = {c["id"]: ajuste_estrategico(c, cfg["pesos"]) for c in CANDIDATOS}

with st.container(border=True):
    st.markdown("### ¿Quién encaja mejor con lo que Intel necesita?")
    grafica(graficas.ranking_candidatos(CANDIDATOS, ajustes))
    st.caption("Pasa el mouse por cada barra para ver el detalle. Puntajes estimados por el equipo con información pública.")

st.markdown("## Perfil de cada candidato")
nombres = [c["nombre"] for c in CANDIDATOS]
sel = st.pills("Candidato", nombres, default=nombres[0], label_visibility="collapsed") or nombres[0]
c = next(x for x in CANDIDATOS if x["nombre"] == sel)

izq, der = st.columns([1, 1.2], gap="large")
with izq.container(border=True):
    st.markdown(f"<div style='text-align:center'>{avatar(c, 150, 5)}"
                f"<div style='font-size:1.7rem;font-weight:800;margin-top:10px;color:#0f172a'>{c['nombre']}</div>"
                f"<div class='muted'>{c['cargo']}</div></div>", unsafe_allow_html=True)
    st.write("")
    kpis([
        ("Ajuste", f"{ajustes[c['id']]:.2f}", "de 10", MARCA),
        ("Años CEO", str(c["exp_ceo"]), "al mando", "#64748b"),
        ("Aceptaría", f"{c['disponibilidad'] * 100:.0f}%", "probabilidad", OK if c["disponibilidad"] >= 0.3 else ALERTA),
    ])
    if c["conflicto"]:
        st.markdown(chip("Dirige hoy a un competidor o proveedor", MAL), unsafe_allow_html=True)
    st.markdown(f"<div class='sec' style='color:{OK}'>Logró</div>" + lista_html(c["logros"][:3], OK) +
                f"<div class='sec' style='color:{MAL}'>No logró</div>" + lista_html(c["no_logros"][:2], MAL),
                unsafe_allow_html=True)
with der.container(border=True):
    comparar = st.multiselect("Comparar con", [n for n in nombres if n != sel], placeholder="Agrega candidatos al radar")
    grafica(graficas.radar([c] + [x for x in CANDIDATOS if x["nombre"] in comparar], cfg["pesos"]))
    st.caption("Línea punteada: lo que Intel necesita. Clic en la leyenda para ocultar un perfil.")

siguiente("paginas/filtro.py", "Siguiente: el filtro de requisitos")
