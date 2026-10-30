import streamlit as st

from core import graficas
from core.datos import CANDIDATOS, FR_LBL, FRENTES, FUENTES
from core.llm import consultar_gemini, extraer_json, prompt_memo
from core.pipeline import PESOS_DECISION
from core.ui import (ALERTA, MAL, MARCA, OK, VIOLETA, barra_intensidad, config, encabezado, grafica, kpis, lista_html,
                     resultados)

encabezado(6, "Decisión", "Recomendación del headhunter",
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
    f"<div class='win'><div class='k'>CEO recomendado para Intel</div><div class='n'>{ceo['nombre']}</div>"
    f"<div class='c'>{ceo['cargo']}</div>"
    f"<div class='pb'>Plan B: <b>{plan_b['nombre'] if plan_b else '—'}</b></div></div>", unsafe_allow_html=True)
kpis([
    ("Puntaje final", f"{ceo['puntaje']:.3f}", "el más alto de los finalistas", OK),
    ("Ajuste al perfil", f"{ceo['ajuste']:.2f}", "de 10 puntos", MARCA),
    ("Grado difuso", f"{ceo['grado']:.0%}", ceo["etiqueta"], OK if ceo["grado"] >= 1 else ALERTA),
    ("Valor Minimax", f"{ceo['minimax']['valor']:.2f}", ceo["minimax"]["jugada"], VIOLETA),
    ("Disponibilidad", f"{ceo['disponibilidad'] * 100:.0f}%", "probabilidad de aceptar",
     ALERTA if ceo["disponibilidad"] < 0.3 else OK),
])

izq, der = st.columns([1.1, 1], gap="large")
with izq:
    with st.container(border=True):
        st.markdown(f"<div class='sec' style='color:{MARCA}'>Por qué resuelve la problemática</div>", unsafe_allow_html=True)
        st.write(a.get("problematica_central", ""))
        st.write(f"Es el finalista con mejor equilibrio entre ajuste a la estrategia "
                 f"(*{a.get('estrategia_reclutamiento', {}).get('nombre', '')}*), robustez frente a NVIDIA y AMD (su mejor "
                 f"jugada es **{ceo['minimax']['jugada']}**) y probabilidad de aceptar el cargo.")
        riesgos = []
        if ceo["disponibilidad"] < 0.3:
            riesgos.append("Hoy dirige otra empresa: la negociación es el principal riesgo de ejecución.")
        if "conflicto" in ceo["alertas"]:
            riesgos.append("Dirige a un competidor o proveedor: hay que gestionar el conflicto de interés.")
        if ceo["grado"] < 1:
            riesgos.append(f"No cumple del todo los requisitos mínimos (grado {ceo['grado']:.0%}).")
        st.markdown(f"<div class='sec' style='color:{MAL}'>Riesgos</div>" +
                    lista_html(riesgos or ["Sin alertas del sistema experto."], MAL), unsafe_allow_html=True)
with der:
    with st.container(border=True):
        st.markdown(f"<div class='sec' style='color:{MARCA}'>Mandato de 100 días</div>", unsafe_allow_html=True)
        for f in FRENTES:
            v = ceo["plan"][f]
            st.markdown(f"<div style='display:flex;justify-content:space-between;align-items:center;padding:7px 0;"
                        f"border-bottom:1px solid #eef1f6'><span>{FR_LBL[f]} <span class='muted' style='font-size:0.78rem'>"
                        f"· prioridad {cfg['prioridades'][f] * 100:.0f}%</span></span>"
                        f"<span>{barra_intensidad(v, MARCA)}</span></div>", unsafe_allow_html=True)

st.markdown("## Cómo se decidió")
with st.container(border=True):
    st.latex(rf"\text{{Puntaje}} = {PESOS_DECISION['ag']}\cdot \widehat{{F}}_{{AG}} + {PESOS_DECISION['minimax']}\cdot "
             rf"\widehat{{V}}_{{minimax}} + {PESOS_DECISION['disponibilidad']}\cdot \text{{disponibilidad}}")
    grafica(graficas.decision(fin, PESOS_DECISION))
    st.caption("Pasa el mouse por cada tramo para ver cuánto aporta. Los términos con sombrero se normalizan entre los "
               "finalistas (el mejor vale 1 y el peor 0), así que diferencias pequeñas pueden verse grandes.")

st.markdown("## Finalistas")
izq, der = st.columns([1, 1.2], gap="large")
with izq.container(border=True):
    st.markdown("**Perfiles comparados**")
    grafica(graficas.radar(fin, cfg["pesos"]))
with der:
    tabs = st.tabs([f"#{i + 1} {c['nombre']}" for i, c in enumerate(fin)])
    for i, (tab, c) in enumerate(zip(tabs, fin)):
        with tab:
            rol = "Recomendado" if i == 0 else "Plan B" if i == 1 else "Tercer finalista"
            st.markdown(f"**{rol}** · puntaje {c['puntaje']:.3f} · grado {c['grado']:.0%} ({c['etiqueta'].lower()})")
            st.markdown(f"<div class='sec' style='color:{OK}'>Lo que logró</div>" + lista_html(c["logros"], OK) +
                        f"<div class='sec' style='color:{MAL}'>Lo que no logró</div>" + lista_html(c["no_logros"], MAL),
                        unsafe_allow_html=True)

st.info(f"**Plan B:** {plan_b['nombre'] if plan_b else '—'}. **Descartados en el filtro:** "
        f"{', '.join(descartados) or 'ninguno'}.", icon=":material/alt_route:")

# ---------------------------------------------------------------- memo
st.markdown("## Memo para la junta directiva")
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

with st.container(border=True):
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
            f"El principal riesgo es la disponibilidad ({ceo['disponibilidad'] * 100:.0f}%). Si la negociación no "
            f"prospera, el plan B es **{plan_b['nombre'] if plan_b else '—'}**.")
        with st.expander("Pedir a Gemini que redacte el memo", icon=":material/auto_awesome:"):
            clave = st.text_input("API key de Gemini", type="password", key="clave_memo",
                                  placeholder="Configurada en el servidor" if clave_servidor else "AIza...")
            if st.button("Redactar memo", icon=":material/edit_note:", disabled=not (clave or clave_servidor)):
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
