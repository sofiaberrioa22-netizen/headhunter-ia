import streamlit as st

from core import graficas
from core.datos import CANDIDATOS, FR_LBL, FRENTES, FUENTES
from core.llm import consultar_gemini, extraer_json, prompt_memo
from core.pipeline import PESOS_DECISION
from core.ui import (ALERTA, MAL, MARCA, OK, VIOLETA, avatar, config, creditos_fotos, encabezado, galeria,
                     kpis, lista_html, resultados)

encabezado(6, "Decisión", "Recomendación del headhunter")

res = resultados()
if "ceo" not in res:
    st.error("No hay candidatos para recomendar. Revisa el filtro del paso 3.")
    st.stop()

cfg = config()
a = st.session_state["analisis"]
fin = res["finalistas"]
ceo = res["ceo"]
plan_b = fin[1] if len(fin) > 1 else None
descartados = [c for c in CANDIDATOS if c["id"] not in {p["id"] for p in res["pool"]}]

st.markdown(
    f"<div class='win' style='display:flex;gap:28px;align-items:center;flex-wrap:wrap'>{avatar(ceo, 150, 5)}<div>"
    f"<div class='k'>CEO recomendado para Intel</div><div class='n'>{ceo['nombre']}</div><div class='c'>{ceo['cargo']}</div>"
    f"<div class='pb'>Plan B: <b>{plan_b['nombre'] if plan_b else '—'}</b></div></div></div>", unsafe_allow_html=True)
kpis([
    ("Puntaje final", f"{ceo['puntaje']:.3f}", "el más alto", OK),
    ("Ajuste al perfil", f"{ceo['ajuste']:.2f}", "de 10", MARCA),
    ("Grado difuso", f"{ceo['grado']:.0%}", ceo["etiqueta"], OK if ceo["grado"] >= 1 else ALERTA),
    ("Valor Minimax", f"{ceo['minimax']['valor']:.2f}", ceo["minimax"]["jugada"], VIOLETA),
    ("Aceptaría", f"{ceo['disponibilidad'] * 100:.0f}%", "principal riesgo" if ceo["disponibilidad"] < 0.3 else "probable",
     ALERTA if ceo["disponibilidad"] < 0.3 else OK),
])

graficas.decision(fin, PESOS_DECISION, "Cómo se decidió",
                  f"Puntaje = {PESOS_DECISION['ag']:.0%} algoritmo genético + {PESOS_DECISION['minimax']:.0%} Minimax + "
                  f"{PESOS_DECISION['disponibilidad']:.0%} disponibilidad (normalizados entre finalistas)")

izq, der = st.columns([1.3, 1], gap="large")
with izq:
    graficas.radar(fin, cfg["pesos"], "Los finalistas frente a lo que Intel necesita")
with der:
    tabs = st.tabs([c["nombre"] for c in fin])
    for i, (tab, c) in enumerate(zip(tabs, fin)):
        with tab:
            rol = "Recomendado" if i == 0 else "Plan B" if i == 1 else "Tercer finalista"
            st.markdown(f"<div class='persona'>{avatar(c, 70)}<div><div class='pn'>{rol}</div>"
                        f"<div class='pc'>puntaje {c['puntaje']:.3f} · grado {c['grado']:.0%}</div></div></div>",
                        unsafe_allow_html=True)
            st.markdown(f"<div class='sec' style='color:{OK}'>Logró</div>" + lista_html(c["logros"][:3], OK) +
                        f"<div class='sec' style='color:{MAL}'>No logró</div>" + lista_html(c["no_logros"][:2], MAL),
                        unsafe_allow_html=True)

st.markdown("## Descartados en el filtro")
galeria(descartados, pie=lambda c: "no cumple lo mínimo", apagados={c["id"] for c in descartados})

with st.expander("Memo para la junta directiva", icon=":material/description:"):
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
            f"Recomendamos a **{ceo['nombre']}** como CEO de Intel. Su mandato de 100 días se concentra en "
            f"{foco or 'los frentes prioritarios'} y su estrategia más robusta frente a la competencia es "
            f"*{ceo['minimax']['jugada']}*. El principal riesgo es su disponibilidad "
            f"({ceo['disponibilidad'] * 100:.0f}%); si no acepta, el plan B es **{plan_b['nombre'] if plan_b else '—'}**.")
        clave = st.text_input("API key de Gemini para redactar el memo", type="password", key="clave_memo",
                              placeholder="Configurada en el servidor" if clave_servidor else "AIza...")
        if st.button("Redactar con Gemini", icon=":material/edit_note:", disabled=not (clave or clave_servidor)):
            resumen = {
                "empresa": "Intel Corporation", "problematica": a.get("problematica_central"),
                "ceo_recomendado": ceo["nombre"], "mandato": ceo["plan"], "estrategia_minimax": ceo["minimax"]["jugada"],
                "finalistas": [{"nombre": c["nombre"], "logros": c["logros"], "no_logros": c["no_logros"],
                                "disponibilidad": c["disponibilidad"], "puntaje_final": round(c["puntaje"], 3)} for c in fin],
            }
            with st.spinner("Redactando…"):
                try:
                    texto, _ = consultar_gemini(prompt_memo(resumen), clave or clave_servidor)
                    st.session_state["memo"] = {"ceo": ceo["nombre"], "texto": extraer_json(texto).get("memo", "")}
                    st.rerun()
                except Exception as ex:
                    st.error(str(ex))

st.divider()
cred = creditos_fotos()
st.caption("Fotos: Wikimedia Commons · " + " · ".join(
    f"{c['nombre']}: {cred[c['id']]['autor']} ({cred[c['id']]['licencia']})" for c in CANDIDATOS))
st.caption("Fuentes: " + " · ".join(FUENTES) + ". Uso académico: los puntajes son estimaciones del equipo.")
