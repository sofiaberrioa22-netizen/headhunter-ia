"""Estado compartido entre páginas y piezas visuales reutilizables."""
import pandas  # noqa: F401  se importa una vez aquí para que plotly no lo importe a medias desde dos sesiones
import streamlit as st

from core.datos import ANALISIS_REFERENCIA, CRITERIOS, FRENTES
from core.llm import validar_configuracion
from core.pipeline import ejecutar

MODO_DIFUSO = "Lógica difusa · Sprint 4"
MODO_CLASICO = "Filtro clásico · Sprint 3"

DEFAULTS = {
    "modo": MODO_DIFUSO, "tol_puntos": 2.0, "tol_anos": 2.0, "corte": 0.5,
    "ga_pob": 40, "ga_gen": 60, "ga_mut": 0.15, "ga_seed": 42,
}
REQ_KEYS = {"exp_min_ceo_anos": "req_exp", "min_tecnologia": "req_tec",
            "min_gobernanza": "req_gob", "min_transformacion": "req_tra"}


def _claves_persistentes():
    return list(DEFAULTS) + list(REQ_KEYS.values()) + [f"peso_{k}" for k in CRITERIOS] + [f"prio_{f}" for f in FRENTES]


def cargar_analisis(analisis, fuente):
    """Guarda el análisis del Paso 0 y lleva sus números a los controles de la app."""
    cfg = validar_configuracion(analisis)
    st.session_state["analisis"] = analisis
    st.session_state["fuente"] = fuente
    for k, wk in REQ_KEYS.items():
        st.session_state[wk] = float(cfg["requisitos"][k])
    for k in CRITERIOS:
        st.session_state[f"peso_{k}"] = round(cfg["pesos"][k], 2)
    for f in FRENTES:
        st.session_state[f"prio_{f}"] = round(cfg["prioridades"][f], 2)


def iniciar_estado():
    if "analisis" not in st.session_state:
        for k, v in DEFAULTS.items():
            st.session_state[k] = v
        cargar_analisis(ANALISIS_REFERENCIA, "Análisis de referencia (respuesta guardada de Gemini)")
    # Streamlit borra el estado de un widget cuando su página no se muestra; reasignarlo lo conserva.
    for k in _claves_persistentes():
        if k in st.session_state:
            st.session_state[k] = st.session_state[k]


def _normalizar(d):
    s = sum(max(0.0, v) for v in d.values())
    return {k: max(0.0, v) / s for k, v in d.items()} if s > 0 else {k: 1 / len(d) for k in d}


def config():
    ss = st.session_state
    return {
        "requisitos": {k: (int(ss[wk]) if k == "exp_min_ceo_anos" else float(ss[wk])) for k, wk in REQ_KEYS.items()},
        "pesos": _normalizar({k: ss[f"peso_{k}"] for k in CRITERIOS}),
        "prioridades": _normalizar({f: ss[f"prio_{f}"] for f in FRENTES}),
        "modo": "clasico" if ss.get("modo") == MODO_CLASICO else "difuso",
        "tol_puntos": float(ss["tol_puntos"]), "tol_anos": float(ss["tol_anos"]), "corte": float(ss["corte"]),
        "ga": {"tam_pob": int(ss["ga_pob"]), "generaciones": int(ss["ga_gen"]),
               "p_mut": float(ss["ga_mut"]), "semilla": int(ss["ga_seed"])},
    }


@st.cache_data(show_spinner=False)
def _ejecutar_cache(cfg_items):
    import json
    return ejecutar(json.loads(cfg_items))


def resultados():
    import json
    return _ejecutar_cache(json.dumps(config(), sort_keys=True))


# ---------------------------------------------------------------- visuales
def encabezado(paso, titulo, descripcion):
    if paso:
        st.caption(paso)
    st.title(titulo)
    st.markdown(f"<p class='lead'>{descripcion}</p>", unsafe_allow_html=True)


def siguiente(pagina, texto):
    st.divider()
    _, c = st.columns([3, 1])
    c.page_link(pagina, label=texto, icon=":material/arrow_forward:", use_container_width=True)


def estilo(fig, alto=320, leyenda=True):
    fig.update_layout(
        template="simple_white", height=alto, margin=dict(l=10, r=10, t=30, b=10),
        font=dict(family="Inter, Segoe UI, sans-serif", size=12, color="#334155"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, x=0) if leyenda else None,
        showlegend=leyenda, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(gridcolor="#eef2f7", zeroline=False)
    fig.update_yaxes(gridcolor="#eef2f7", zeroline=False)
    return fig


def puntos(n, total=3):
    return "●" * n + "○" * (total - n)


def lista(items):
    return "\n".join(f"- {x}" for x in (items or []))


def chip(texto, color):
    return (f"<span style='display:inline-block;padding:2px 10px;border-radius:999px;font-size:0.8rem;"
            f"font-weight:600;color:{color};background:{color}14;border:1px solid {color}40'>{texto}</span>")


CSS = """
<style>
.block-container {max-width: 1150px; padding-top: 2.2rem; padding-bottom: 3rem;}
h1 {font-weight: 700; letter-spacing: -0.02em;}
h2, h3 {font-weight: 650; letter-spacing: -0.01em;}
p.lead {color: #475569; font-size: 1.05rem; margin-top: -0.4rem; margin-bottom: 1.4rem;}
[data-testid="stMetricValue"] {font-size: 1.6rem;}
[data-testid="stCaptionContainer"] p {letter-spacing: 0.02em;}
.paso {border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px 16px; height: 100%; background: #ffffff;}
.paso .n {font-size: 0.75rem; font-weight: 700; color: #2563eb; text-transform: uppercase; letter-spacing: 0.06em;}
.paso .t {font-weight: 650; margin: 4px 0 4px;}
.paso .d {font-size: 0.88rem; color: #475569;}
.hero {border: 1px solid #bbf7d0; background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 70%);
       border-radius: 16px; padding: 22px 24px; margin-bottom: 1rem;}
.hero .k {font-size: 0.78rem; font-weight: 700; color: #059669; text-transform: uppercase; letter-spacing: 0.06em;}
.hero .name {font-size: 2rem; font-weight: 750; letter-spacing: -0.02em; margin: 2px 0;}
.hero .c {color: #475569;}
</style>
"""
