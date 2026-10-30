import streamlit as st

from core import graficas
from core.datos import ANALISIS_REFERENCIA, CRIT_LBL, CRITERIOS, FR_LBL, FRENTES, REQ_LBL
from core.llm import construir_prompt, consultar_gemini, extraer_json
from core.ui import (ALERTA, MAL, MARCA, MARCA_2, OK, REQ_KEYS, cargar_analisis, config, encabezado, grafica, kpis,
                     lista_html, siguiente)

encabezado(1, "Analista de la industria", "Entender a Intel",
           "Un asistente de IA (Gemini) analiza la empresa y define el perfil del CEO que necesita.")

a = st.session_state["analisis"]
d = a.get("diagnostico_empresa", {})
e = a.get("estrategia_reclutamiento", {})

kpis([
    ("Ingresos Q2 2026 · Intel", "US$16,1 B", "+25% interanual", MARCA),
    ("Ingresos trimestre · NVIDIA", "US$96,2 B", "6 veces Intel", "#64748b"),
    ("CPU de servidores · AMD", "46,2%", "de los ingresos x86", MAL),
    ("Clientes externos en 14A", "0", "con volumen firmado", ALERTA),
])

izq, der = st.columns([1.5, 1], gap="large")
with izq.container(border=True):
    st.markdown("### La brecha con NVIDIA")
    grafica(graficas.brecha_intel_nvidia())
with der:
    with st.container(border=True):
        st.markdown(f"<div class='sec' style='color:{MARCA}'>El problema</div>"
                    f"<p style='font-size:1.15rem;font-weight:600;line-height:1.5;color:#0f172a;margin:0'>"
                    f"{a.get('problematica_central', '')}</p>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(f"<div class='sec' style='color:{OK}'>El CEO que buscamos</div>"
                    f"<p style='font-size:1.05rem;font-weight:700;margin:0 0 4px'>{e.get('nombre', '')}</p>"
                    + lista_html(e.get("pilares", [])[:3], OK), unsafe_allow_html=True)

with st.expander("Diagnóstico completo (FODA, CEO actual y anterior)", icon=":material/monitoring:"):
    f = st.columns(4)
    for col, titulo, clave, color in ((f[0], "Fortalezas", "fortalezas", OK), (f[1], "Debilidades", "debilidades", MAL),
                                      (f[2], "Oportunidades", "oportunidades", MARCA_2), (f[3], "Amenazas", "amenazas", ALERTA)):
        col.markdown(f"<div class='sec' style='color:{color}'>{titulo}</div>" + lista_html(d.get(clave), color),
                     unsafe_allow_html=True)
    c, l = a.get("analisis_ceo_actual", {}), a.get("legado_ceo_anterior", {})
    x, y = st.columns(2)
    x.markdown(f"<div class='sec' style='color:{MARCA}'>CEO actual · {c.get('nombre', '')}</div>"
               + lista_html(c.get("limitaciones"), MAL), unsafe_allow_html=True)
    y.markdown(f"<div class='sec' style='color:{MAL}'>Legado de {l.get('nombre', '')}</div>"
               + lista_html(l.get("decisiones_que_dejaron_atras_a_intel"), MAL), unsafe_allow_html=True)

# ---------------------------------------------------------------- del perfil a los números
st.markdown("## Lo que más pesa en el nuevo CEO")
cfg = config()
izq, der = st.columns([1.6, 1], gap="large")
with izq.container(border=True):
    grafica(graficas.barras_pesos([CRIT_LBL[k] for k in CRITERIOS], [cfg["pesos"][k] for k in CRITERIOS], MARCA))
with der.container(border=True):
    st.markdown(f"<div class='sec' style='color:{MARCA}'>Requisitos mínimos</div>", unsafe_allow_html=True)
    for k, v in cfg["requisitos"].items():
        st.markdown(f"<div style='display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid "
                    f"#eef1f6;font-size:1.05rem'><span>{REQ_LBL[k]}</span><b>≥ {v:g}"
                    f"{' años' if k == 'exp_min_ceo_anos' else ''}</b></div>", unsafe_allow_html=True)

with st.expander("Ajustar los números", icon=":material/tune:"):
    r1, r2, r3 = st.columns(3, gap="large")
    with r1:
        st.markdown("**Requisitos mínimos**")
        st.slider("Años como CEO", 3.0, 15.0, step=1.0, key=REQ_KEYS["exp_min_ceo_anos"])
        st.slider("Tecnología", 0.0, 9.5, step=0.5, key=REQ_KEYS["min_tecnologia"])
        st.slider("Gobernanza", 0.0, 9.5, step=0.5, key=REQ_KEYS["min_gobernanza"])
        st.slider("Transformación", 0.0, 9.5, step=0.5, key=REQ_KEYS["min_transformacion"])
    with r2:
        st.markdown("**Importancia de cada cualidad**")
        for k in CRITERIOS:
            st.slider(CRIT_LBL[k], 0.0, 0.5, step=0.01, key=f"peso_{k}")
    with r3:
        st.markdown("**Prioridad de cada frente**")
        for f_ in FRENTES:
            st.slider(FR_LBL[f_], 0.0, 0.5, step=0.01, key=f"prio_{f_}")
    st.button("Restaurar valores", icon=":material/restart_alt:", on_click=cargar_analisis,
              args=(st.session_state["analisis"], st.session_state["fuente"]))

with st.expander("Repetir el análisis con Gemini en vivo", icon=":material/auto_awesome:"):
    st.caption(f"Fuente actual: {st.session_state['fuente']}. La clave no se guarda.")
    try:
        clave_servidor = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        clave_servidor = ""
    clave = st.text_input("API key de Gemini", type="password",
                          placeholder="Configurada en el servidor" if clave_servidor else "AIza...")
    extra = st.text_area("Contexto adicional (opcional)")
    b1, b2 = st.columns(2)
    if b1.button("Consultar a Gemini", type="primary", icon=":material/send:", disabled=not (clave or clave_servidor)):
        registro = []
        with st.spinner("Consultando a Gemini…"):
            try:
                texto, modelo = consultar_gemini(construir_prompt(extra.strip()), clave or clave_servidor, registro=registro)
                cargar_analisis(extraer_json(texto), f"Gemini en vivo ({modelo})")
                st.rerun()
            except Exception as ex:
                st.error(f"{ex}  \n" + " · ".join(registro))
    if b2.button("Volver al análisis de referencia", icon=":material/history:"):
        cargar_analisis(ANALISIS_REFERENCIA, "Análisis de referencia (respuesta guardada de Gemini)")
        st.rerun()

siguiente("paginas/candidatos.py", "Siguiente: los candidatos")
