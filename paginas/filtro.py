import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.datos import CANDIDATOS, REQ_ATRIB, REQ_LBL
from core.difuso import tolerancia_de
from core.experto import construir_reglas
from core.ui import MODO_CLASICO, MODO_DIFUSO, chip, config, encabezado, estilo, resultados, siguiente

encabezado("PASO 3 · DESCARTE", "Filtro de requisitos",
           "Descartamos a quienes no cumplen lo mínimo que Intel necesita. Desde el Sprint 4 el filtro usa lógica "
           "difusa: ya no pregunta si el candidato cumple, sino qué tanto cumple.")

antes, ahora = st.columns(2)
with antes.container(border=True):
    st.markdown("**Antes · filtro clásico (Sprint 3)**")
    st.markdown("Funciona como un portero con una regla estricta: *si tienes 8 o más en tecnología, entras; si no, te "
                "quedas afuera*. Trata igual a quien tiene 7,9 y a quien tiene 2. Cuando nadie pasaba, había que usar "
                "una **regla de relajación** que bajaba la exigencia.")
with ahora.container(border=True):
    st.markdown("**Ahora · lógica difusa (Sprint 4)**")
    st.markdown("Cada requisito se cumple en un **grado** entre 0 y 1: 100 %, 70 %, 30 % o nada. Como un headhunter real: "
                "*le falta algo de experiencia, pero en lo demás está muy bien*. El grado total es el del requisito "
                "**menos cumplido**: una cadena es tan fuerte como su eslabón más débil.")

st.segmented_control("Filtro que usa el resto del sistema", [MODO_DIFUSO, MODO_CLASICO], key="modo")

cfg = config()
res = resultados()
por_id = {c["id"]: c for c in CANDIDATOS}
clasico = {r["id"]: r for r in res["clasico"]["resultados"]}
req = cfg["requisitos"]

if cfg["modo"] == "difuso":
    c1, c2, c3 = st.columns(3)
    c1.slider("Tolerancia en puntajes", 0.5, 4.0, step=0.5, key="tol_puntos",
              help="Cuántos puntos por debajo del mínimo empieza a contar el grado. Con 2: el mínimo de tecnología es "
                   "8, así que 6 vale 0 %, 7 vale 50 % y 8 vale 100 %.")
    c2.slider("Tolerancia en años como CEO", 1.0, 4.0, step=1.0, key="tol_anos")
    c3.slider("Grado mínimo para seguir en el proceso", 0.1, 1.0, step=0.05, key="corte",
              help="Corte α: solo los candidatos con un grado igual o mayor pasan a la comparación (paso 4).")
    cfg = config()
    res = resultados()

difuso = {r["id"]: r for r in res["difuso"]}

# ---------------------------------------------------------------- tabla de resultados
st.subheader("Resultado del filtro")
filas = []
for c in CANDIDATOS:
    d, k = difuso[c["id"]], clasico[c["id"]]
    filas.append({
        "Candidato": c["nombre"],
        **{REQ_LBL[r]: d["grados"][r] for r in req},
        "Grado total": d["grado"],
        "Lógica difusa": d["etiqueta"],
        "Lo frena": d["limitante"] or "—",
        "Filtro clásico": "Apto" if k["apto"] else "No apto",
        "Sigue en el proceso": d["grado"] >= cfg["corte"] if cfg["modo"] == "difuso" else k["apto"],
    })
df = pd.DataFrame(filas).sort_values("Grado total", ascending=False)
col_cfg = {REQ_LBL[r]: st.column_config.NumberColumn(REQ_LBL[r], format="percent", width="small") for r in req}
col_cfg["Grado total"] = st.column_config.ProgressColumn("Grado total", min_value=0, max_value=1, format="percent")
col_cfg["Sigue en el proceso"] = st.column_config.CheckboxColumn("Sigue")
st.dataframe(df, hide_index=True, use_container_width=True, column_config=col_cfg)

n_clas = sum(k["apto"] for k in clasico.values())
if cfg["modo"] == "difuso":
    pasan = [por_id[i]["nombre"] for i, d in difuso.items() if d["grado"] >= cfg["corte"]]
    recuperados = [por_id[i]["nombre"] for i, d in difuso.items() if d["grado"] >= cfg["corte"] and not clasico[i]["apto"]]
    m1, m2, m3 = st.columns(3)
    m1.metric("Aptos con el filtro clásico", f"{n_clas} de 7")
    m2.metric("Siguen con lógica difusa", f"{len(pasan)} de 7")
    m3.metric("Regla de relajación", "No se necesita",
              help="El filtro clásico bajaba los umbrales cuando quedaban menos de 2 aptos. Con grados, nadie queda "
                   f"afuera por décimas. Con los requisitos actuales, el clásico la aplicó {res['clasico']['relajaciones']} veces.")
    if recuperados:
        st.success("**Candidatos que el filtro clásico habría perdido:** " + ", ".join(recuperados) +
                   ". Estaban cerca del mínimo; ahora siguen en el proceso, pero con una penalización proporcional a lo "
                   "que les falta (paso 4).", icon=":material/person_add:")
else:
    st.warning(f"Con el filtro clásico pasan **{n_clas} de 7**. Se aplicaron **{res['clasico']['relajaciones']}** "
               "reglas de relajación.", icon=":material/rule:")

# ---------------------------------------------------------------- ejemplos y funciones de pertenencia
st.subheader("Cómo se calcula el grado")
izq, der = st.columns([1, 1.3])
with izq:
    req_sel = st.selectbox("Requisito", list(req), format_func=lambda r: REQ_LBL[r])
    u = req[req_sel]
    t = tolerancia_de(req_sel, cfg["tol_puntos"], cfg["tol_anos"])
    st.markdown(f"Mínimo pedido: **{u:g}**. Tolerancia: **{t:g}**.")
    st.markdown(f"- Con {u - t:g} o menos, el grado es **0 %**.\n"
                f"- Entre {u - t:g} y {u:g}, el grado sube en línea recta.\n"
                f"- Con {u:g} o más, el grado es **100 %**.")
    st.markdown("**Dos casos del proyecto**")

    def debilidades(d):
        return ", ".join(f"{REQ_LBL[r].lower()} ({g:.0%})" for r, g in sorted(d["grados"].items(), key=lambda x: x[1])
                         if g < 1) or "ninguna"

    for cid, nota in (("C6", "El filtro clásico lo descartaba por completo aunque estaba cerca."),
                      ("C7", "Es el candidato de control: el sistema debe seguir descartando a quien debe descartar.")):
        d = difuso[cid]
        st.markdown(f"{chip(d['etiqueta'], d['color'])} **{por_id[cid]['nombre']}** · grado total {d['grado']:.0%}. "
                    f"Requisitos que no cumple del todo: {debilidades(d)}. {nota}", unsafe_allow_html=True)
with der:
    atrib = REQ_ATRIB[req_sel]
    xs = [c[atrib] for c in CANDIDATOS]
    lo, hi = min(min(xs), u - t) - 1, max(max(xs), u) + 1
    xx = np.linspace(lo, hi, 200)
    yy = np.clip((xx - (u - t)) / t, 0, 1)
    fig = go.Figure()
    fig.add_scatter(x=xx, y=yy, mode="lines", line=dict(color="#2563eb", width=3), name="Grado de cumplimiento")
    fig.add_scatter(x=[u, u], y=[0, 1], mode="lines", line=dict(color="#94a3b8", dash="dot"), name="Mínimo (filtro clásico)")
    for c in CANDIDATOS:
        g = difuso[c["id"]]["grados"][req_sel]
        fig.add_scatter(x=[c[atrib]], y=[g], mode="markers", marker=dict(size=11, color=c["color"], line=dict(color="white", width=1)),
                        showlegend=False, hovertemplate=f"{c['nombre']}: {c[atrib]} → {g:.0%}<extra></extra>")
    grupos = {}  # candidatos con el mismo valor comparten una sola etiqueta
    for c in CANDIDATOS:
        grupos.setdefault(c[atrib], []).append(c["nombre"].split()[-1])
    for i, (x, nombres_x) in enumerate(sorted(grupos.items())):
        fig.add_annotation(x=x, y=float(np.clip((x - (u - t)) / t, 0, 1)), text="<br>".join(nombres_x), showarrow=False,
                           yshift=14 + 8 * (len(nombres_x) - 1) if i % 2 == 0 else -14 - 8 * (len(nombres_x) - 1),
                           font=dict(size=10, color="#334155"))
    fig.update_yaxes(range=[-0.08, 1.18], tickformat=".0%", title="Grado")
    fig.update_xaxes(title=REQ_LBL[req_sel])
    st.plotly_chart(estilo(fig, 360), use_container_width=True)

with st.expander("Base de reglas del sistema experto (Sprints 2 y 3)"):
    st.write("El sistema experto se conserva. Sus reglas de alerta (R5 y R6) siguen activas en los dos modos: no "
             "descartan, pero penalizan en el paso 4.")
    for r in construir_reglas(res["clasico"]["req"]):
        st.markdown(f"`{r.id_regla}` {r.descripcion}")
    st.markdown("**Reglas difusas (Sprint 4)**")
    st.markdown("`D1` SI experiencia ES suficiente Y tecnología ES suficiente Y gobernanza ES suficiente Y "
                "transformación ES suficiente ENTONCES candidato ES apto  \n"
                "Y difuso = mínimo de los grados. Etiquetas: **Apto** (100 %), **Parcialmente apto** (50 % o más), "
                "**Poco apto** (más de 0 %), **No apto** (0 %).")
    st.markdown("**Traza del encadenamiento hacia adelante (filtro clásico)**")
    st.dataframe(pd.DataFrame([{"Candidato": por_id[i]["nombre"], "Reglas disparadas": " → ".join(k["traza"]) or "—",
                                "Dictamen": "APTO" if k["apto"] else "NO APTO"} for i, k in clasico.items()]),
                 hide_index=True, use_container_width=True)

siguiente("paginas/seleccion.py", "Siguiente: selección y mandato")
