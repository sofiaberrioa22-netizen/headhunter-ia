"""Paso 0: el LLM externo (Gemini) analiza a Intel y traduce el perfil del CEO a números."""
import json
import time

import numpy as np
import requests

from core.datos import CRITERIOS, DOSSIER, EMPRESA, FECHA_ANALISIS, FRENTES

MODELOS_GEMINI = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.5-flash-lite",
                  "gemini-flash-lite-latest", "gemini-2.0-flash"]

INSTRUCCION_SISTEMA = (
    "Eres un analista senior del contexto de la industria tecnológica y de semiconductores y un experto en "
    "gobierno corporativo y búsqueda de ejecutivos (executive search). Respondes en español, con rigor, "
    "basándote en los hechos que se te entregan. Respondes ÚNICAMENTE con un objeto JSON válido."
)

ESQUEMA_RESPUESTA = {
    "empresa": "string",
    "diagnostico_empresa": {"resumen": "string (5-7 líneas)", "fortalezas": ["string"], "debilidades": ["string"],
                            "oportunidades": ["string"], "amenazas": ["string"]},
    "analisis_ceo_actual": {"nombre": "string", "aciertos": ["string"], "limitaciones": ["string"],
                            "por_que_se_requiere_un_cambio": "string"},
    "legado_ceo_anterior": {"nombre": "string", "decisiones_que_dejaron_atras_a_intel": ["string"]},
    "problematica_central": "string",
    "tipo_crisis": "TECNOLOGICA | FINANCIERA | GOBERNANZA | MIXTA",
    "tendencias_mercado": ["string"],
    "estrategia_reclutamiento": {"nombre": "string", "pilares": ["string"], "perfil_ideal": "string",
                                 "preguntas_clave_entrevista": ["string"], "senales_de_alerta": ["string"]},
    "requisitos_rigidos": {"exp_min_ceo_anos": "entero 3-15", "min_tecnologia": "0-10",
                           "min_gobernanza": "0-10", "min_transformacion": "0-10"},
    "pesos_criterios": {k: "peso" for k in CRITERIOS},
    "prioridades_frentes": {k: "peso" for k in FRENTES},
    "justificacion_cuantitativa": "string",
}


def construir_prompt(extra=""):
    contexto = f"\nCONTEXTO ADICIONAL DEL USUARIO: {extra}\n" if extra else ""
    return f"""Contexto: un software académico de reclutamiento busca al mejor CEO para {EMPRESA}. La empresa se quedó atrás
por decisiones de sus CEO anteriores y fue superada por NVIDIA. Se necesita un CEO que la desestanque y la impulse
en la industria tecnológica mundial. Fecha del análisis: {FECHA_ANALISIS}.

DOSSIER DE HECHOS VERIFICADOS (no inventes cifras que no estén aquí):
{json.dumps(DOSSIER, ensure_ascii=False, indent=1)}
{contexto}
TAREA:
1. Analiza la empresa, a su CEO actual y el legado del CEO anterior.
2. Explica la problemática central y por qué se requiere un nuevo tipo de liderazgo.
3. Diseña una estrategia de reclutamiento y el perfil del nuevo CEO.
4. Traduce el perfil a números: requisitos_rigidos (realistas; umbrales demasiado altos dejan sin candidatos),
   pesos_criterios (8 pesos que sumen 1) y prioridades_frentes (6 pesos que sumen 1).

Responde SOLO con un JSON que siga exactamente este esquema:
{json.dumps(ESQUEMA_RESPUESTA, ensure_ascii=False, indent=1)}"""


def consultar_gemini(prompt, api_key, reintentos=2, registro=None):
    """Prueba cada modelo en orden; si está saturado (429/500/503) espera y reintenta. Devuelve (texto, modelo)."""
    log = registro if registro is not None else []
    cuerpo = {
        "systemInstruction": {"parts": [{"text": INSTRUCCION_SISTEMA}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"},
    }
    for modelo in MODELOS_GEMINI:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
        for intento in range(1, reintentos + 1):
            try:
                r = requests.post(url, headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
                                  json=cuerpo, timeout=120)
            except requests.exceptions.RequestException as ex:
                log.append(f"{modelo}: error de red ({ex.__class__.__name__})")
                time.sleep(3 * intento)
                continue
            if r.status_code == 200:
                partes = r.json()["candidates"][0]["content"]["parts"]
                log.append(f"{modelo}: respuesta recibida")
                return "".join(p.get("text", "") for p in partes), modelo
            log.append(f"{modelo}: HTTP {r.status_code}")
            if r.status_code in (401, 403):
                raise RuntimeError("La API key fue rechazada. Revísala.")
            if r.status_code in (429, 500, 503):
                time.sleep(6 * intento)
                continue
            break  # 400/404: modelo no disponible, se pasa al siguiente
    raise RuntimeError("Todos los modelos fallaron. Espera unos minutos o usa el análisis de referencia.")


def extraer_json(texto):
    """Convierte la respuesta en dict aunque el LLM la envuelva en ```json ... ```."""
    texto = texto.strip()
    inicio, fin = texto.find("{"), texto.rfind("}")
    return json.loads(texto[inicio:fin + 1])


def _a_numero(valor, defecto):
    try:
        return float(valor)
    except (TypeError, ValueError):
        return defecto


def normalizar_pesos(diccionario, claves):
    """Lleva los pesos a [0, ∞), completa los faltantes y hace que sumen 1."""
    v = np.array([max(0.0, _a_numero((diccionario or {}).get(k), 0.0)) for k in claves])
    if v.sum() == 0:
        v = np.ones(len(claves))
    return {k: float(x) for k, x in zip(claves, v / v.sum())}


def validar_configuracion(a):
    """El LLM es una fuente externa: se valida y se acota todo lo que llega antes de usarlo."""
    req = a.get("requisitos_rigidos", {}) or {}
    return {
        "tipo_crisis": a.get("tipo_crisis", "MIXTA"),
        "requisitos": {
            "exp_min_ceo_anos": int(np.clip(_a_numero(req.get("exp_min_ceo_anos"), 5), 3, 15)),
            "min_tecnologia": float(np.clip(_a_numero(req.get("min_tecnologia"), 7), 0, 9.5)),
            "min_gobernanza": float(np.clip(_a_numero(req.get("min_gobernanza"), 7), 0, 9.5)),
            "min_transformacion": float(np.clip(_a_numero(req.get("min_transformacion"), 6), 0, 9.5)),
        },
        "pesos": normalizar_pesos(a.get("pesos_criterios"), CRITERIOS),
        "prioridades": normalizar_pesos(a.get("prioridades_frentes"), FRENTES),
    }


def prompt_memo(resumen):
    return ("Con base EXCLUSIVAMENTE en estos resultados de un sistema de reclutamiento, redacta en español un memo de "
            "recomendación (máximo 300 palabras) para la junta directiva. Explica por qué el candidato recomendado "
            "resuelve la problemática, qué riesgos tiene (incluida su disponibilidad) y cuál es el plan B. Devuelve un "
            "JSON con la clave 'memo' (texto en Markdown).\n\n" + json.dumps(resumen, ensure_ascii=False, indent=1))
