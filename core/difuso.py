"""Paso 1 con lógica difusa (Sprint 4): en lugar de "¿cumple o no?", "¿qué tanto cumple?".

Cada requisito tiene una función de pertenencia en rampa:
    μ(x) = 0                     si x ≤ umbral − tolerancia
    μ(x) = (x − (umbral − tol)) / tol   en la zona intermedia
    μ(x) = 1                     si x ≥ umbral
El grado de aptitud del candidato es el mínimo de sus grados (Y difuso = mínimo):
vale lo que vale su requisito menos cumplido, como una cadena y su eslabón más débil.
"""
from core.datos import REQ_ATRIB, REQ_LBL
from core.experto import construir_reglas, encadenamiento_adelante

ETIQUETAS = [  # (grado mínimo, etiqueta lingüística, color)
    (1.0, "Apto", "#059669"),
    (0.5, "Parcialmente apto", "#2563eb"),
    (1e-9, "Poco apto", "#d97706"),
    (0.0, "No apto", "#dc2626"),
]


def pertenencia(x, umbral, tolerancia):
    if tolerancia <= 0:
        return 1.0 if x >= umbral else 0.0
    return float(min(1.0, max(0.0, (x - (umbral - tolerancia)) / tolerancia)))


def etiqueta(grado):
    for minimo, nombre, color in ETIQUETAS:
        if grado >= minimo - 1e-12:
            return nombre, color
    return ETIQUETAS[-1][1], ETIQUETAS[-1][2]


def tolerancia_de(req_key, tol_puntos, tol_anos):
    return tol_anos if req_key == "exp_min_ceo_anos" else tol_puntos


def filtro_difuso(candidatos, req, tol_puntos=2.0, tol_anos=2.0):
    """Devuelve, por candidato, el grado de cada requisito, el grado global (mínimo) y las alertas R5/R6."""
    reglas_alerta = [r for r in construir_reglas(req) if r.id_regla in ("R5", "R6")]
    resultados = []
    for c in candidatos:
        grados = {k: pertenencia(c[REQ_ATRIB[k]], u, tolerancia_de(k, tol_puntos, tol_anos)) for k, u in req.items()}
        global_ = min(grados.values())
        limitante = min(grados, key=grados.get)
        hechos, _ = encadenamiento_adelante(c, reglas_alerta)
        nombre, color = etiqueta(global_)
        resultados.append({
            "id": c["id"], "grados": grados, "grado": global_, "etiqueta": nombre, "color": color,
            "limitante": REQ_LBL[limitante] if global_ < 1 else None, "hechos": hechos,
        })
    return resultados
