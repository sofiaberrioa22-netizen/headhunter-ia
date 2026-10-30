import streamlit as st

from core import graficas
from core.datos import ANALISIS_REFERENCIA, CRIT_LBL, CRITERIOS, FR_LBL, FRENTES, REQ_LBL
from core.llm import construir_prompt, consultar_gemini, extraer_json
from core.ui import (ALERTA, MAL, MARCA, MARCA_2, OK, REQ_KEYS, VIOLETA, cargar_analisis, chip, config, encabezado,
                     grafica, kpis, lista_html, siguiente)

encabezado(1, "Analista de la industria", "Entender a Intel",
           "Antes de buscar candidatos, un asistente de IA (Gemini) analiza la empresa a partir de un dossier de hechos "
           "verificados y devuelve el perfil del CEO que necesita, ya traducido a números.")

a = st.session_state["analisis"]
d = a.get("diagnostico_empresa", {})
c = a.get("analisis_ceo_actual", {})
l = a.get("legado_ceo_anterior", {})
e = a.get("estrategia_reclutamiento", {})

kpis([
    ("Ingresos Q2 2026 · Intel", "US$16,1 B", "+25% interanual", MARCA),
    ("Ingresos trimestre · NVIDIA", "US$96,2 B", "+106% interanual · 6 veces Intel", "#64748b"),
    ("CPU de servidores · AMD", "46,2%", "de los ingresos x86", MAL),
    ("Clientes externos en 14A", "0", "con volumen firmado", ALERTA),
])
st.markdown(f"{chip('Crisis ' + a.get('tipo_crisis', 'MIXTA'), ALERTA)} &nbsp; "
            f"<span class='muted' style='font-size:0.85rem'>Fuente: {st.session_state['fuente']}</span>",
            unsafe_allow_html=True)
st.write("")

t1, t2, t3, t4 = st.tabs([":material/monitoring: Diagnóstico", ":material/person: CEO actual y anterior",
                          ":material/report: Problemática", ":material/target: Perfil que buscamos"])
with t1:
    izq, der = st.columns([1.1, 1], gap="large")
    with izq:
        st.markdown(f"<p style='font-size:1.02rem;line-height:1.65;color:#334155'>{d.get('resumen', '')}</p>",
                    unsafe_allow_html=True)
    with der.container(border=True):
        st.markdown("**La brecha con NVIDIA** · último trimestre reportado")
        grafica(graficas.brecha_intel_nvidia())
    f = st.columns(2) + st.columns(2)
    for col, titulo, clave, color in ((f[0], "Fortalezas", "fortalezas", OK), (f[1], "Debilidades", "debilidades", MAL),
                                      (f[2], "Oportunidades", "oportunidades", MARCA_2),
                                      (f[3], "Amenazas", "amenazas", ALERTA)):
        with col.container(border=True):
            st.markdown(f"<div class='sec' style='color:{color}'>{titulo}</div>" + lista_html(d.get(clave), color),
                        unsafe_allow_html=True)
with t2:
    x, y = st.columns(2)
    with x.container(border=True):
        st.markdown(f"### {c.get('nombre', '')}")
        st.caption("CEO actual")
        st.markdown(f"<div class='sec' style='color:{OK}'>Aciertos</div>" + lista_html(c.get("aciertos"), OK) +
                    f"<div class='sec' style='color:{MAL}'>Limitaciones</div>" + lista_html(c.get("limitaciones"), MAL),
                    unsafe_allow_html=True)
        st.info(c.get("por_que_se_requiere_un_cambio", ""), icon=":material/sync_alt:")
    with y.container(border=True):
        st.markdown(f"### {l.get('nombre', '')}")
        st.caption("CEO anterior · decisiones que dejaron atrás a Intel")
        st.markdown(lista_html(l.get("decisiones_que_dejaron_atras_a_intel"), MAL), unsafe_allow_html=True)
with t3:
    with st.container(border=True):
        st.markdown(f"<div class='sec' style='color:{MARCA}'>Problemática central</div>"
                    f"<p style='font-size:1.25rem;font-weight:600;line-height:1.5;color:#0f172a;margin:0'>"
                    f"{a.get('problematica_central', '')}</p>", unsafe_allow_html=True)
    st.markdown(f"<div class='sec' style='color:{MARCA_2}'>Hacia dónde va el mercado</div>"
                + lista_html(a.get("tendencias_mercado"), MARCA_2), unsafe_allow_html=True)
with t4:
    st.markdown(f"### Estrategia: {e.get('nombre', '')}")
    st.markdown(f"<p class='muted' style='font-size:1.02rem'>{e.get('perfil_ideal', '')}</p>", unsafe_allow_html=True)
    p = st.columns(3)
    for col, titulo, clave, color in ((p[0], "Pilares", "pilares", MARCA),
                                      (p[1], "Preguntas para la entrevista", "preguntas_clave_entrevista", VIOLETA),
                                      (p[2], "Señales de alerta", "senales_de_alerta", MAL)):
        with col.container(border=True):
            st.markdown(f"<div class='sec' style='color:{color}'>{titulo}</div>" + lista_html(e.get(clave), color),
                        unsafe_allow_html=True)

# ---------------------------------------------------------------- del perfil a los números
st.write("")
st.markdown("## Del perfil a los números")
st.markdown("<p class='muted'>El asistente traduce el perfil en tres cosas que usa el resto del sistema. Puedes "
            "ajustarlas abajo y todo se recalcula.</p>", unsafe_allow_html=True)
cfg = config()
n1, n2, n3 = st.columns([0.9, 1.25, 1.25])
with n1.container(border=True):
    st.markdown(f"<div class='sec' style='color:{MARCA}'>Requisitos mínimos → paso 3</div>", unsafe_allow_html=True)
    for k, v in cfg["requisitos"].items():
        st.markdown(f"<div style='display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid "
                    f"#eef1f6'><span>{REQ_LBL[k]}</span><b>≥ {v:g}{' años' if k == 'exp_min_ceo_anos' else ''}</b></div>",
                    unsafe_allow_html=True)
with n2.container(border=True):
    st.markdown(f"<div class='sec' style='color:{MARCA}'>Importancia de cada cualidad → paso 4</div>",
                unsafe_allow_html=True)
    grafica(graficas.barras_pesos([CRIT_LBL[k] for k in CRITERIOS], [cfg["pesos"][k] for k in CRITERIOS], MARCA))
with n3.container(border=True):
    st.markdown(f"<div class='sec' style='color:{OK}'>Prioridad de cada frente → paso 4</div>", unsafe_allow_html=True)
    grafica(graficas.barras_pesos([FR_LBL[f] for f in FRENTES], [cfg["prioridades"][f] for f in FRENTES], OK))
st.caption(a.get("justificacion_cuantitativa", ""))

with st.expander("Ajustar los números manualmente", icon=":material/tune:"):
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
        for f in FRENTES:
            st.slider(FR_LBL[f], 0.0, 0.5, step=0.01, key=f"prio_{f}")
    st.caption("Los pesos y prioridades se normalizan para sumar 100%.")
    st.button("Restaurar los valores del análisis", icon=":material/restart_alt:", on_click=cargar_analisis,
              args=(st.session_state["analisis"], st.session_state["fuente"]))

# ---------------------------------------------------------------- fuente del análisis
with st.expander("Repetir el análisis con Gemini en vivo", icon=":material/auto_awesome:"):
    st.write("La app trae guardada una respuesta de Gemini con el mismo formato JSON del notebook, para que funcione "
             "sin conexión. Si tienes una API key de Gemini (gratis en aistudio.google.com/apikey), puedes pedir un "
             "análisis nuevo. La clave no se guarda.")
    try:
        clave_servidor = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        clave_servidor = ""
    clave = st.text_input("API key de Gemini", type="password",
                          placeholder="Configurada en el servidor" if clave_servidor else "AIza...")
    extra = st.text_area("Contexto adicional para el asistente (opcional)",
                         placeholder="Ej.: la junta prioriza que el nuevo CEO no tenga conflictos de interés")
    b1, b2 = st.columns(2)
    if b1.button("Consultar a Gemini", type="primary", icon=":material/send:", disabled=not (clave or clave_servidor)):
        registro = []
        with st.spinner("Consultando a Gemini… puede tardar hasta un minuto"):
            try:
                texto, modelo = consultar_gemini(construir_prompt(extra.strip()), clave or clave_servidor, registro=registro)
                cargar_analisis(extraer_json(texto), f"Gemini en vivo ({modelo})")
                st.rerun()
            except Exception as ex:
                st.error(f"{ex}  \n" + " · ".join(registro))
    if b2.button("Volver al análisis de referencia", icon=":material/history:"):
        cargar_analisis(ANALISIS_REFERENCIA, "Análisis de referencia (respuesta guardada de Gemini)")
        st.rerun()

siguiente("paginas/candidatos.py", "Siguiente: conocer a los candidatos", "Siete ejecutivos reales de la industria.")
