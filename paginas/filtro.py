import pandas as pd
import streamlit as st

from core import graficas
from core.datos import CANDIDATOS, REQ_ATRIB, REQ_LBL
from core.difuso import tolerancia_de
from core.experto import construir_reglas
from core.ui import (MAL, MARCA, MODO_CLASICO, MODO_DIFUSO, OK, chip, config, encabezado, galeria, grafica, kpis,
                     resultados, siguiente)

encabezado(3, "Descarte · Sprint 4", "Filtro de requisitos",
           "Ya no preguntamos <b>¿cumple o no?</b> sino <b>¿qué tanto cumple?</b> El grado total es el del requisito "
           "menos cumplido: el eslabón más débil.")

st.segmented_control("Filtro", [MODO_DIFUSO, MODO_CLASICO], key="modo", label_visibility="collapsed")
cfg = config()
if cfg["modo"] == "difuso":
    with st.expander("Ajustar el filtro difuso", icon=":material/tune:"):
        c1, c2, c3 = st.columns(3, gap="large")
        c1.slider("Tolerancia en puntajes", 0.5, 4.0, step=0.5, key="tol_puntos",
                  help="Con 2: si el mínimo es 8, un 6 vale 0 %, un 7 vale 50 % y un 8 vale 100 %.")
        c2.slider("Tolerancia en años como CEO", 1.0, 4.0, step=1.0, key="tol_anos")
        c3.slider("Grado mínimo para seguir", 0.1, 1.0, step=0.05, key="corte")

cfg = config()
res = resultados()
por_id = {c["id"]: c for c in CANDIDATOS}
clasico = {r["id"]: r for r in res["clasico"]["resultados"]}
difuso = {r["id"]: r for r in res["difuso"]}
req = cfg["requisitos"]
pasan = {c["id"] for c in res["pool"]}

n_clas = sum(k["apto"] for k in clasico.values())
recuperados = [por_id[i]["nombre"] for i in pasan if not clasico[i]["apto"]]
kpis([
    ("Filtro clásico", f"{n_clas} de 7", "pasan (todo o nada)", "#64748b"),
    ("Lógica difusa", f"{len(pasan)} de 7", f"siguen (grado ≥ {cfg['corte']:.0%})", OK),
    ("Recuperados", str(len(recuperados)), ", ".join(recuperados) or "ninguno", MARCA),
    ("Regla de relajación", "Ya no hace falta", f"antes: {res['clasico']['relajaciones']} veces", "#8b5cf6"),
] if cfg["modo"] == "difuso" else [
    ("Filtro clásico", f"{n_clas} de 7", "pasan (todo o nada)", "#64748b"),
    ("Reglas de relajación", str(res["clasico"]["relajaciones"]), "bajan la exigencia", MAL),
])

orden = sorted(CANDIDATOS, key=lambda c: -difuso[c["id"]]["grado"])
galeria(orden, pie=(lambda c: f"{difuso[c['id']]['etiqueta']} · {difuso[c['id']]['grado']:.0%}") if cfg["modo"] == "difuso"
        else (lambda c: "Apto" if clasico[c["id"]]["apto"] else "No apto"),
        apagados={c["id"] for c in CANDIDATOS if c["id"] not in pasan})

with st.container(border=True):
    st.markdown("### Qué tanto cumple cada candidato")
    filas = [{"nombre": c["nombre"], "grados": difuso[c["id"]]["grados"], "grado": difuso[c["id"]]["grado"]} for c in orden]
    grafica(graficas.mapa_grados(filas, {r: REQ_LBL[r] for r in req}))

with st.container(border=True):
    st.markdown("### Del todo o nada al grado de cumplimiento")
    req_sel = st.radio("Requisito", list(req), format_func=lambda r: REQ_LBL[r], horizontal=True,
                       label_visibility="collapsed")
    u, t = req[req_sel], tolerancia_de(req_sel, cfg["tol_puntos"], cfg["tol_anos"])
    grados = {c["id"]: difuso[c["id"]]["grados"][req_sel] for c in CANDIDATOS}
    grafica(graficas.pertenencia(CANDIDATOS, REQ_ATRIB[req_sel], grados, u, t, REQ_LBL[req_sel]))
    haas, gels = difuso["C6"], difuso["C7"]
    st.markdown(f"{chip(haas['etiqueta'], haas['color'])} **Rene Haas** queda en {haas['grado']:.0%}: le frena "
                f"{haas['limitante'].lower() if haas['limitante'] else 'nada'}. &nbsp; "
                f"{chip(gels['etiqueta'], gels['color'])} **Pat Gelsinger** queda en {gels['grado']:.0%}: el sistema "
                f"sigue descartando a quien debe.", unsafe_allow_html=True)

with st.expander("Reglas del sistema experto", icon=":material/rule:"):
    for r in construir_reglas(res["clasico"]["req"]):
        st.markdown(f"`{r.id_regla}` {r.descripcion}")
    st.markdown("`D1` SI todos los requisitos SON suficientes ENTONCES candidato ES apto · Y difuso = mínimo")
    st.dataframe(pd.DataFrame([{"Candidato": por_id[i]["nombre"], "Reglas disparadas": " → ".join(k["traza"]) or "—",
                                "Dictamen clásico": "APTO" if k["apto"] else "NO APTO"} for i, k in clasico.items()]),
                 hide_index=True, width="stretch")

siguiente("paginas/seleccion.py", "Siguiente: elegir candidato y plan")
