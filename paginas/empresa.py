import plotly.graph_objects as go
import streamlit as st

from core.datos import ANALISIS_REFERENCIA, CRIT_LBL, CRITERIOS, FR_LBL, FRENTES, REQ_LBL
from core.llm import construir_prompt, consultar_gemini, extraer_json
from core.ui import REQ_KEYS, cargar_analisis, config, encabezado, estilo, lista, siguiente

encabezado("PASO 1 · ANALISTA DE LA INDUSTRIA", "Entender a Intel",
           "Antes de buscar candidatos, un asistente de IA (Gemini) analiza la empresa a partir de un dossier de "
           "hechos verificados y devuelve el perfil del CEO que necesita, ya traducido a números.")

a = st.session_state["analisis"]
d = a.get("diagnostico_empresa", {})
c = a.get("analisis_ceo_actual", {})
l = a.get("legado_ceo_anterior", {})
e = a.get("estrategia_reclutamiento", {})

k1, k2, k3, k4 = st.columns(4)
k1.metric("Ingresos Q2 2026 · Intel", "US$16,1 B", "+25% interanual")
k2.metric("Ingresos trimestre · NVIDIA", "US$96,2 B", "+106% interanual")
k3.metric("CPU de servidores · AMD", "46,2%", "de los ingresos x86", delta_color="off")
k4.metric("Clientes externos en 14A", "0", "con volumen firmado", delta_color="off")

st.caption(f"Fuente del análisis: {st.session_state['fuente']} · Tipo de crisis: **{a.get('tipo_crisis', 'MIXTA')}**")

t1, t2, t3, t4 = st.tabs(["Diagnóstico", "CEO actual y anterior", "Problemática", "Perfil que buscamos"])
with t1:
    st.write(d.get("resumen", ""))
    f1, f2, f3, f4 = st.columns(4)
    for col, titulo, clave in ((f1, "Fortalezas", "fortalezas"), (f2, "Debilidades", "debilidades"),
                               (f3, "Oportunidades", "oportunidades"), (f4, "Amenazas", "amenazas")):
        with col.container(border=True):
            st.markdown(f"**{titulo}**")
            st.markdown(lista(d.get(clave)))
    fig = go.Figure()
    fig.add_bar(name="Intel", x=["Ingresos del trimestre (US$ B)", "Margen bruto (%)"], y=[16.1, 40.4], marker_color="#2563eb")
    fig.add_bar(name="NVIDIA", x=["Ingresos del trimestre (US$ B)", "Margen bruto (%)"], y=[96.2, 75.0], marker_color="#94a3b8")
    st.markdown("**La brecha con NVIDIA** (último trimestre reportado)")
    st.plotly_chart(estilo(fig, 280), use_container_width=True)
with t2:
    x, y = st.columns(2)
    with x.container(border=True):
        st.markdown(f"**CEO actual: {c.get('nombre', '')}**")
        st.markdown("Aciertos\n" + lista(c.get("aciertos")))
        st.markdown("Limitaciones\n" + lista(c.get("limitaciones")))
        st.info(c.get("por_que_se_requiere_un_cambio", ""), icon=":material/sync_alt:")
    with y.container(border=True):
        st.markdown(f"**Legado del CEO anterior: {l.get('nombre', '')}**")
        st.markdown(lista(l.get("decisiones_que_dejaron_atras_a_intel")))
with t3:
    st.markdown(f"#### {a.get('problematica_central', '')}")
    st.markdown("**Hacia dónde va el mercado**")
    st.markdown(lista(a.get("tendencias_mercado")))
with t4:
    st.markdown(f"#### Estrategia: {e.get('nombre', '')}")
    st.write(e.get("perfil_ideal", ""))
    p1, p2, p3 = st.columns(3)
    with p1.container(border=True):
        st.markdown("**Pilares**\n" + lista(e.get("pilares")))
    with p2.container(border=True):
        st.markdown("**Preguntas para la entrevista**\n" + lista(e.get("preguntas_clave_entrevista")))
    with p3.container(border=True):
        st.markdown("**Señales de alerta**\n" + lista(e.get("senales_de_alerta")))

# ---------------------------------------------------------------- del perfil a los números
st.subheader("Del perfil a los números")
st.write("El asistente traduce el perfil en tres cosas que usa el resto del sistema. Puedes ajustarlas y todo se "
         "recalcula.")
cfg = config()
n1, n2, n3 = st.columns([1, 1.3, 1.3])
with n1.container(border=True):
    st.markdown("**Requisitos mínimos** → paso 3")
    for k, v in cfg["requisitos"].items():
        st.markdown(f"{REQ_LBL[k]} ≥ **{v:g}**{' años' if k == 'exp_min_ceo_anos' else ''}")
with n2.container(border=True):
    st.markdown("**Importancia de cada cualidad** → paso 4")
    fig = go.Figure(go.Bar(y=[CRIT_LBL[k] for k in CRITERIOS], x=[cfg["pesos"][k] * 100 for k in CRITERIOS],
                           orientation="h", marker_color="#2563eb", text=[f"{cfg['pesos'][k]*100:.0f}%" for k in CRITERIOS]))
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(estilo(fig, 250, leyenda=False), use_container_width=True)
with n3.container(border=True):
    st.markdown("**Prioridad de cada frente** → paso 4")
    fig = go.Figure(go.Bar(y=[FR_LBL[f] for f in FRENTES], x=[cfg["prioridades"][f] * 100 for f in FRENTES],
                           orientation="h", marker_color="#059669", text=[f"{cfg['prioridades'][f]*100:.0f}%" for f in FRENTES]))
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(estilo(fig, 250, leyenda=False), use_container_width=True)
st.caption(a.get("justificacion_cuantitativa", ""))

with st.expander("Ajustar los números manualmente"):
    r1, r2, r3 = st.columns(3)
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
    st.button("Restaurar los valores del análisis", on_click=cargar_analisis,
              args=(st.session_state["analisis"], st.session_state["fuente"]))

# ---------------------------------------------------------------- fuente del análisis
with st.expander("Repetir el análisis con Gemini en vivo"):
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
    if b1.button("Consultar a Gemini", type="primary", disabled=not (clave or clave_servidor)):
        registro = []
        with st.spinner("Consultando a Gemini… puede tardar hasta un minuto"):
            try:
                texto, modelo = consultar_gemini(construir_prompt(extra.strip()), clave or clave_servidor, registro=registro)
                cargar_analisis(extraer_json(texto), f"Gemini en vivo ({modelo})")
                st.rerun()
            except Exception as ex:
                st.error(f"{ex}  \n" + " · ".join(registro))
    if b2.button("Volver al análisis de referencia"):
        cargar_analisis(ANALISIS_REFERENCIA, "Análisis de referencia (respuesta guardada de Gemini)")
        st.rerun()

siguiente("paginas/candidatos.py", "Siguiente: candidatos")
