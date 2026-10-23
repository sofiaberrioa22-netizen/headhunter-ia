"""Paso 1 (Sprints 2 y 3): sistema experto con reglas SI-ENTONCES y encadenamiento hacia adelante."""
from dataclasses import dataclass
from typing import Callable

OBLIGATORIOS = {"experiencia_ceo_ok", "tecnologia_ok", "gobernanza_ok", "transformacion_ok"}


@dataclass
class Regla:
    id_regla: str
    descripcion: str
    condicion: Callable
    consecuente: str


def construir_reglas(req):
    return [
        Regla("R1", f"SI años como CEO ≥ {req['exp_min_ceo_anos']:g} ENTONCES experiencia_ceo_ok",
              lambda c, h: c["exp_ceo"] >= req["exp_min_ceo_anos"], "experiencia_ceo_ok"),
        Regla("R2", f"SI tecnología ≥ {req['min_tecnologia']:g} ENTONCES tecnologia_ok",
              lambda c, h: c["tecnologia"] >= req["min_tecnologia"], "tecnologia_ok"),
        Regla("R3", f"SI gobernanza ≥ {req['min_gobernanza']:g} ENTONCES gobernanza_ok",
              lambda c, h: c["gobernanza"] >= req["min_gobernanza"], "gobernanza_ok"),
        Regla("R4", f"SI transformación ≥ {req['min_transformacion']:g} ENTONCES transformacion_ok",
              lambda c, h: c["transformacion"] >= req["min_transformacion"], "transformacion_ok"),
        Regla("R5", "SI disponibilidad < 30% ENTONCES riesgo_disponibilidad (alerta, no descarta)",
              lambda c, h: c["disponibilidad"] < 0.30, "riesgo_disponibilidad"),
        Regla("R6", "SI dirige hoy a un competidor o proveedor ENTONCES riesgo_conflicto (alerta, no descarta)",
              lambda c, h: c["conflicto"], "riesgo_conflicto"),
        Regla("R7", "SI R1 ∧ R2 ∧ R3 ∧ R4 ENTONCES cumple_requisitos",
              lambda c, h: OBLIGATORIOS.issubset(h), "cumple_requisitos"),
        Regla("R8", "SI cumple_requisitos ENTONCES dictamen = APTO",
              lambda c, h: "cumple_requisitos" in h, "APTO"),
    ]


def encadenamiento_adelante(candidato, reglas):
    """Dispara reglas hasta que no aparece ningún hecho nuevo. Devuelve (hechos, traza)."""
    hechos, traza, nuevo = set(), [], True
    while nuevo:
        nuevo = False
        for r in reglas:
            if r.consecuente not in hechos and r.condicion(candidato, hechos):
                hechos.add(r.consecuente)
                traza.append(r.id_regla)
                nuevo = True
    return hechos, traza


def alertas(hechos):
    return sorted(h.replace("riesgo_", "") for h in hechos if h.startswith("riesgo"))


def filtro_clasico(candidatos, req_inicial, minimo_aptos=2):
    """Filtro todo-o-nada del Sprint 3. Si quedan menos de `minimo_aptos`, aplica la regla de relajación."""
    req = dict(req_inicial)
    for intento in range(10):
        reglas = construir_reglas(req)
        resultados = []
        for c in candidatos:
            hechos, traza = encadenamiento_adelante(c, reglas)
            resultados.append({"id": c["id"], "hechos": hechos, "traza": traza, "apto": "APTO" in hechos})
        if sum(r["apto"] for r in resultados) >= minimo_aptos or intento == 9:
            return {"resultados": resultados, "req": req, "relajaciones": intento}
        req = {k: (max(0, v - 1) if k == "exp_min_ceo_anos" else max(0, v - 0.5)) for k, v in req.items()}
