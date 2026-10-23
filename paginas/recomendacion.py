import plotly.graph_objects as go
import streamlit as st

from core.datos import CANDIDATOS, FR_LBL, FRENTES, FUENTES
from core.llm import consultar_gemini, extraer_json, prompt_memo
from core.pipeline import PESOS_DECISION
from core.ui import config, encabezado, estilo, lista, puntos, resultados

encabezado("PASO 6 · DECISIÓN", "Recomendación del headhunter",
           "Juntamos tres evidencias: qué tan bien encaja el candidato con su mejor plan (paso 4), qué tan robusto es "
           "frente a la competencia (paso 5) y qué tan probable es que acepte el cargo.")

res = resultados()
if "ceo" not in res:
    st.error("No hay candidatos para recomendar. Revisa el filtro del paso 3.")
    st.stop()

cfg = config()
a = st.session_state["analisis"]
fin = res["finalistas"]
ceo = res["ceo"]
plan_b = fin[1] if len(fin) > 1 else None
descartados = [c["nombre"] for c in CANDIDATOS if c["id"] not in {p["id"] for p in res["pool"]}]

st.markdown(
    f"<div class='hero'><div class='k'>CEO recomendado para Intel</div><div class='name'>{ceo['nombre']}</div>"
    f"<div class='c'>{ceo['cargo']}</div></div>", unsafe_allow_html=True)
m = st.columns(5)
m[0].metric("Puntaje final", f"{ceo['puntaje']:.3f}")
m[1].metric("Ajuste al perfil", f"{ceo['ajuste']:.2f} / 10")
m[2].metric("Grado difuso", f"{ceo['grado']:.0%}")
m[3].metric("Valor Minimax", f"{ceo['minimax']['valor']:.2f}")
m[4].metric("Disponibilidad", f"{ceo['disponibilidad']*100:.0f}%")

izq, der = st.columns([1.1, 1])
with izq:
    st.markdown("**Por qué resuelve la problemática**")
    st.write(a.get("problematica_central", ""))
    st.write(f"Es el finalista con mejor equilibrio entre ajuste a la estrategia "
             f"(*{a.get('estrategia_reclutamiento', {}).get('nombre', '')}*), robustez frente a NVIDIA y AMD "
             f"(su mejor jugada es **{ceo['minimax']['jugada']}**) y probabilidad de aceptar el cargo.")
    riesgos = []
    if ceo["disponibilidad"] < 0.3:
        riesgos.append("Hoy dirige otra empresa: la negociación es el principal riesgo de ejecución.")
    if "conflicto" in ceo["alertas"]:
        riesgos.append("Dirige a un competidor o proveedor: hay que gestionar el conflicto de interés.")
    if ceo["grado"] < 1:
        riesgos.append(f"No cumple del todo los requisitos mínimos (grado {ceo['grado']:.0%}).")
    st.markdown("**Riesgos**")
    st.markdown(lista(riesgos) if riesgos else "Sin alertas del sistema experto.")
with der:
    st.markdown("**Mandato de 100 días**")
    st.dataframe([{"Frente": FR_LBL[f], "Intensidad": puntos(ceo["plan"][f]),
                   "Prioridad para Intel": f"{cfg['prioridades'][f]*100:.0f}%"} for f in FRENTES],
                 hide_index=True, use_container_width=True)

st.subheader("Cómo se decidió")
st.latex(rf"\text{{Puntaje}} = {PESOS_DECISION['ag']}\cdot \widehat{{F}}_{{AG}} + {PESOS_DECISION['minimax']}\cdot "
         rf"\widehat{{V}}_{{minimax}} + {PESOS_DECISION['disponibilidad']}\cdot \text{{disponibilidad}}")
fig = go.Figure()
for clave, nombre, color in (("ag", "Fitness del algoritmo genético", "#2563eb"),
                             ("minimax", "Valor Minimax", "#7c3aed"),
                             ("disponibilidad", "Disponibilidad", "#059669")):
    fig.add_bar(y=[c["nombre"] for c in fin], x=[c["aporte"][clave] for c in fin], name=nombre, orientation="h",
                marker_color=color)
fig.update_layout(barmode="stack")
fig.update_yaxes(autorange="reversed")
fig.update_xaxes(title="Puntaje final")
st.plotly_chart(estilo(fig, 240), use_container_width=True)
st.caption("Los términos con sombrero se normalizan entre los finalistas (el mejor vale 1 y el peor 0), así que las "
           "diferencias pequeñas en fitness pueden verse grandes.")

st.subheader("Finalistas")
cols = st.columns(len(fin))
for i, (col, c) in enumerate(zip(cols, fin)):
    with col.container(border=True):
        st.markdown(f"**#{i + 1} · {c['nombre']}**" + ("  · recomendado" if i == 0 else "  · plan B" if i == 1 else ""))
        st.caption(f"Puntaje {c['puntaje']:.3f} · grado {c['grado']:.0%} · {c['etiqueta']}")
        st.markdown("Lo que logró\n" + lista(c["logros"]))
        st.markdown("Lo que no logró\n" + lista(c["no_logros"]))

st.info(f"**Plan B:** {plan_b['nombre'] if plan_b else '—'}. **Descartados en el filtro:** "
        f"{', '.join(descartados) or 'ninguno'}.", icon=":material/alt_route:")

# ---------------------------------------------------------------- memo
st.subheader("Memo para la junta directiva")
resumen = {
    "empresa": "Intel Corporation", "problematica": a.get("problematica_central"),
    "ceo_recomendado": ceo["nombre"], "mandato": ceo["plan"], "estrategia_minimax": ceo["minimax"]["jugada"],
    "finalistas": [{"nombre": c["nombre"], "logros": c["logros"], "no_logros": c["no_logros"],
                    "disponibilidad": c["disponibilidad"], "puntaje_final": round(c["puntaje"], 3)} for c in fin],
}
try:
    clave_servidor = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    clave_servidor = ""

memo = st.session_state.get("memo")
if memo and memo["ceo"] == ceo["nombre"]:
    st.markdown(memo["texto"])
    st.caption("Redactado por Gemini a partir de los resultados calculados: el asistente redacta, pero no decide.")
else:
    foco = ", ".join(FR_LBL[f] for f in FRENTES if ceo["plan"][f] == 3)
    st.markdown(
        f"Recomendamos a **{ceo['nombre']}** como CEO de Intel. {a.get('problematica_central', '')} "
        f"Su perfil combina un ajuste de {ceo['ajuste']:.2f}/10 con la estrategia buscada y su mandato de 100 días "
        f"concentra el esfuerzo en {foco or 'los frentes prioritarios'}. Frente a la competencia, su estrategia más "
        f"robusta es *{ceo['minimax']['jugada']}*, con un valor garantizado de {ceo['minimax']['valor']:.2f}.\n\n"
        f"El principal riesgo es la disponibilidad ({ceo['disponibilidad']*100:.0f}%). Si la negociación no prospera, "
        f"el plan B es **{plan_b['nombre'] if plan_b else '—'}**."
    )
    with st.expander("Pedir a Gemini que redacte el memo"):
        clave = st.text_input("API key de Gemini", type="password", key="clave_memo",
                              placeholder="Configurada en el servidor" if clave_servidor else "AIza...")
        if st.button("Redactar memo", disabled=not (clave or clave_servidor)):
            with st.spinner("Redactando…"):
                try:
                    texto, _ = consultar_gemini(prompt_memo(resumen), clave or clave_servidor)
                    st.session_state["memo"] = {"ceo": ceo["nombre"], "texto": extraer_json(texto).get("memo", "")}
                    st.rerun()
                except Exception as ex:
                    st.error(str(ex))

st.divider()
st.caption("Fuentes: " + " · ".join(FUENTES) + ". Uso académico: los puntajes de los candidatos son estimaciones del "
           "equipo, no evaluaciones reales de esas personas.")
