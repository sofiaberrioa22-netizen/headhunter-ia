"""Estado compartido entre páginas y piezas visuales reutilizables."""
import pandas  # noqa: F401  se importa una vez aquí para que plotly no lo importe a medias desde dos sesiones
import plotly.graph_objects as go
import plotly.io as pio
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

# Paleta de la app
TINTA, SUAVE, LINEA = "#0f172a", "#64748b", "#e5e9f2"
MARCA, MARCA_2 = "#4f46e5", "#0ea5e9"
OK, ALERTA, MAL, VIOLETA = "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"

PASOS = [
    ("paginas/empresa.py", "Entender a Intel"),
    ("paginas/candidatos.py", "Candidatos"),
    ("paginas/filtro.py", "Filtro"),
    ("paginas/seleccion.py", "Selección"),
    ("paginas/competencia.py", "Competencia"),
    ("paginas/recomendacion.py", "Recomendación"),
]


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


# ---------------------------------------------------------------- encabezados y navegación
def encabezado(paso, etiqueta, titulo, descripcion):
    """Encabezado de página con la barra de progreso de los 6 pasos del headhunter."""
    barra = ""
    if paso:
        barra = "<div class='stepper'>" + "".join(
            f"<div class='seg {'done' if i < paso else 'now' if i == paso else ''}' title='{n}'>"
            f"<span>{i}</span><em>{n}</em></div>" for i, (_, n) in enumerate(PASOS, start=1)) + "</div>"
    st.markdown(
        f"<div class='ph'>{barra}<div class='eyebrow'>{('Paso ' + str(paso) + ' de 6 · ') if paso else ''}{etiqueta}</div>"
        f"<h1>{titulo}</h1><p class='lead'>{descripcion}</p></div>", unsafe_allow_html=True)


def siguiente(pagina, texto, detalle=""):
    st.write("")
    with st.container(border=True, key="cta_siguiente"):
        a, b = st.columns([3, 1.2], vertical_alignment="center")
        a.markdown(f"**{texto}**" + (f"  \n<span class='muted'>{detalle}</span>" if detalle else ""), unsafe_allow_html=True)
        if b.button("Continuar", type="primary", icon=":material/arrow_forward:", icon_position="right",
                    width="stretch", key=f"ir_{pagina}"):
            st.switch_page(pagina)


# ---------------------------------------------------------------- piezas de HTML
def kpis(items):
    """items: lista de (etiqueta, valor, detalle, color). Se muestran como tarjetas en una grilla adaptable."""
    celdas = "".join(
        f"<div class='kpi' style='--c:{color}'><div class='l'>{l}</div><div class='v'>{v}</div>"
        f"<div class='s'>{s}</div></div>" for l, v, s, color in items)
    st.markdown(f"<div class='kpis'>{celdas}</div>", unsafe_allow_html=True)


def chip(texto, color):
    return f"<span class='chip' style='--c:{color}'>{texto}</span>"


def puntos(n, total=3):
    return "●" * n + "○" * (total - n)


def barra_intensidad(n, color=MARCA):
    celdas = "".join(f"<i style='background:{color if k < n else '#e2e8f0'}'></i>" for k in range(3))
    return f"<span class='bars'>{celdas}</span>"


def lista(items):
    return "\n".join(f"- {x}" for x in (items or []))


def lista_html(items, color):
    return "<ul class='lst' style='--c:" + color + "'>" + "".join(f"<li>{x}</li>" for x in (items or [])) + "</ul>"


# ---------------------------------------------------------------- gráficas
pio.templates["headhunter"] = go.layout.Template(
    layout=dict(
        font=dict(family='"Source Sans", "Source Sans Pro", sans-serif', size=13, color="#334155"),
        colorway=[MARCA, OK, ALERTA, VIOLETA, MARCA_2, "#ec4899", MAL],
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(bgcolor="white", bordercolor=LINEA, font=dict(color=TINTA, size=12)),
        xaxis=dict(gridcolor="#eef1f6", zeroline=False, linecolor=LINEA, ticks=""),
        yaxis=dict(gridcolor="#eef1f6", zeroline=False, linecolor=LINEA, ticks=""),
        polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(gridcolor=LINEA), angularaxis=dict(gridcolor=LINEA)),
    )
)


def estilo(fig, alto=320, leyenda=True):
    fig.update_layout(
        template="headhunter", height=alto, margin=dict(l=8, r=8, t=36, b=8), showlegend=leyenda,
        # Streamlit reemplaza los fondos transparentes por el gris del tema; las gráficas van sobre tarjetas blancas
        paper_bgcolor="white", plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0, font=dict(size=11)) if leyenda else None,
    )
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)
    return fig


CONFIG_GRAFICA = {"displaylogo": False, "responsive": True,
                  "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
                  "toImageButtonOptions": {"format": "png", "scale": 2}}


def grafica(fig, **kw):
    """Todas las gráficas pasan por aquí: interactivas (zoom, hover, leyenda clicable) y descargables como PNG."""
    return st.plotly_chart(fig, width="stretch", config=CONFIG_GRAFICA, theme=None, **kw)


CSS = """
<style>
.block-container {max-width: 1180px; padding-top: 3.2rem; padding-bottom: 4rem;}
h1, h2, h3 {letter-spacing: -0.02em; color: #0f172a;}
h2 {font-weight: 750 !important;} h3 {font-weight: 700 !important;}
.muted {color: #64748b;}

/* ---------- encabezado de página ---------- */
.ph h1 {font-size: 2.3rem; font-weight: 800; margin: 0.15rem 0 0.35rem; padding: 0; line-height: 1.15;}
.ph .eyebrow {font-size: 0.74rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #4f46e5;}
.ph p.lead {color: #475569; font-size: 1.05rem; line-height: 1.6; max-width: 820px; margin: 0 0 1.4rem;}
.stepper {display: flex; gap: 6px; margin-bottom: 1.1rem;}
.stepper .seg {flex: 1; min-width: 0;}
.stepper .seg::before {content: ""; display: block; height: 5px; border-radius: 99px; background: #e2e8f0; margin-bottom: 6px;}
.stepper .seg.done::before {background: #a5b4fc;}
.stepper .seg.now::before {background: linear-gradient(90deg, #4f46e5, #0ea5e9);}
.stepper .seg span {display: none;}
.stepper .seg em {font-style: normal; font-size: 0.72rem; color: #94a3b8; font-weight: 600; white-space: nowrap;
                  overflow: hidden; text-overflow: ellipsis; display: block;}
.stepper .seg.now em {color: #4f46e5;}
@media (max-width: 640px) {.stepper .seg em {display: none;} .ph h1 {font-size: 1.8rem;}}

/* ---------- tarjetas ---------- */
[data-testid="stVerticalBlockBorderWrapper"], [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] {
  background: #ffffff; border-radius: 16px !important; border-color: #e5e9f2 !important;
  box-shadow: 0 1px 2px rgba(15,23,42,0.04), 0 6px 20px -12px rgba(15,23,42,0.18);}
.st-key-cta_siguiente {background: linear-gradient(120deg, #eef2ff 0%, #f0f9ff 100%) !important;
  border-color: #c7d2fe !important;}

/* ---------- KPIs ---------- */
.kpis {display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin: 0.2rem 0 1.2rem;}
.kpi {background: #fff; border: 1px solid #e5e9f2; border-radius: 16px; padding: 14px 16px; position: relative;
      overflow: hidden; box-shadow: 0 6px 20px -14px rgba(15,23,42,0.25);}
.kpi::before {content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: var(--c);}
.kpi .l {font-size: 0.72rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;}
.kpi .v {font-size: 1.6rem; font-weight: 800; color: #0f172a; letter-spacing: -0.02em; margin: 2px 0; line-height: 1.2;}
.kpi .s {font-size: 0.82rem; color: var(--c); font-weight: 600;}

/* ---------- chips, listas, barras ---------- */
.chip {display: inline-block; white-space: nowrap; padding: 2px 10px; border-radius: 999px; font-size: 0.78rem; font-weight: 700;
       color: var(--c); background: color-mix(in srgb, var(--c) 10%, white);
       border: 1px solid color-mix(in srgb, var(--c) 30%, white);}
ul.lst {list-style: none; padding: 0; margin: 0.2rem 0 0.6rem;}
ul.lst li {position: relative; padding: 5px 0 5px 20px; color: #334155; font-size: 0.93rem; line-height: 1.45;}
ul.lst li::before {content: ""; position: absolute; left: 2px; top: 12px; width: 8px; height: 8px; border-radius: 3px;
                   background: var(--c);}
.bars {display: inline-flex; gap: 3px; vertical-align: middle;}
.bars i {display: inline-block; width: 18px; height: 7px; border-radius: 3px;}
.sec {font-size: 0.74rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; margin: 0.3rem 0 0.2rem;}

/* ---------- portada ---------- */
.hero {position: relative; overflow: hidden; border-radius: 22px; padding: 38px 36px 34px; margin-bottom: 1.4rem;
       background: radial-gradient(1200px 400px at 85% -20%, rgba(14,165,233,0.45), transparent 60%),
                   radial-gradient(800px 380px at -10% 120%, rgba(139,92,246,0.45), transparent 60%),
                   linear-gradient(135deg, #0b1437 0%, #1e1b4b 55%, #0c2a4d 100%); color: #e2e8f0;}
.hero .tag {display: inline-block; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
            color: #c7d2fe; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.16);
            padding: 4px 10px; border-radius: 999px;}
.hero h1 {color: #ffffff !important; font-size: 2.8rem; font-weight: 800; line-height: 1.08; margin: 14px 0 10px; padding: 0;}
.hero h1 span {background: linear-gradient(90deg, #a5b4fc, #67e8f9); -webkit-background-clip: text; background-clip: text;
               color: transparent;}
.hero p {color: #cbd5e1; font-size: 1.08rem; line-height: 1.6; max-width: 720px; margin: 0;}
.hero .res {display: flex; gap: 12px; flex-wrap: wrap; margin-top: 22px;}
.hero .res div {background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.14); border-radius: 14px;
                padding: 10px 16px; min-width: 170px;}
.hero .res small {display: block; font-size: 0.7rem; letter-spacing: 0.06em; text-transform: uppercase; color: #a5b4fc;
                  font-weight: 700;}
.hero .res b {font-size: 1.2rem; color: #fff;}
@media (max-width: 640px) {.hero {padding: 26px 20px;} .hero h1 {font-size: 2rem;}}

.paso {background: #fff; border: 1px solid #e5e9f2; border-radius: 16px; padding: 16px 18px; height: 100%;
       transition: transform .15s ease, box-shadow .15s ease; box-shadow: 0 6px 20px -16px rgba(15,23,42,0.3);}
.paso:hover {transform: translateY(-2px); box-shadow: 0 14px 30px -18px rgba(79,70,229,0.45);}
.paso .ic {width: 34px; height: 34px; border-radius: 10px; display: flex; align-items: center; justify-content: center;
           font-weight: 800; color: #fff; background: linear-gradient(135deg, #4f46e5, #0ea5e9); margin-bottom: 10px;}
.paso .t {font-weight: 700; color: #0f172a; margin-bottom: 4px;}
.paso .d {font-size: 0.88rem; color: #64748b; line-height: 1.45;}

/* ---------- ganador ---------- */
.win {border-radius: 22px; padding: 28px 30px; margin-bottom: 1rem; color: #ecfdf5; position: relative; overflow: hidden;
      background: radial-gradient(700px 300px at 100% 0%, rgba(16,185,129,0.55), transparent 60%),
                  linear-gradient(135deg, #064e3b 0%, #0f3d3e 60%, #0b2a3a 100%);}
.win .k {font-size: 0.74rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #6ee7b7;}
.win .n {font-size: 2.5rem; font-weight: 800; color: #fff; letter-spacing: -0.02em; line-height: 1.1; margin: 6px 0 4px;}
.win .c {color: #a7f3d0;}
.win .pb {margin-top: 16px; display: inline-block; font-size: 0.85rem; background: rgba(255,255,255,0.1);
          border: 1px solid rgba(255,255,255,0.18); padding: 6px 12px; border-radius: 10px; color: #d1fae5;}

/* ---------- widgets ---------- */
[data-testid="stTabs"] button[role="tab"] {font-weight: 600;}
[data-testid="stMetric"] {background: #fff; border: 1px solid #e5e9f2; border-radius: 14px; padding: 10px 14px;}
[data-testid="stSidebar"] {border-right: 1px solid #e5e9f2; background: #ffffff;}
.sb-brand {display: flex; gap: 10px; align-items: center; margin: 0 0 0.4rem;}
.sb-brand .logo {width: 34px; height: 34px; border-radius: 10px; background: linear-gradient(135deg, #4f46e5, #0ea5e9);
                 display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 800;}
.sb-brand b {display: block; color: #0f172a;} .sb-brand small {color: #64748b;}
.sb-card {background: #f8fafc; border: 1px solid #e5e9f2; border-radius: 14px; padding: 12px 14px; font-size: 0.88rem;}
.sb-card .r {display: flex; justify-content: space-between; gap: 8px; padding: 3px 0;}
.sb-card .r span {color: #64748b;} .sb-card .r b {color: #0f172a; text-align: right;}
</style>
"""
