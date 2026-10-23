"""Código de los Sprints 1 y 2, conservado para la bitácora."""
import heapq
import math
from dataclasses import dataclass
from typing import List

# ============================================================== SPRINT 1 · A* (Valle de Aburrá)
UBICACIONES = {
    "Base_Norte": (0.5, 3.0), "Base_Centro": (1.0, -1.5), "Base_Sur": (2.0, -4.5),
    "E01_Copacabana": (3.0, 14.0), "E02_Bello": (1.0, 8.5), "E03_Aranjuez": (2.0, 4.5), "E04_Robledo": (-3.0, 4.0),
    "E05_Laureles": (-2.0, 1.0), "E06_BuenosAires": (2.5, 0.5), "E07_Belen": (-2.5, -2.0), "E08_Poblado": (1.5, -3.0),
    "E09_Envigado": (2.5, -6.5), "E10_Itagui": (-1.5, -6.5), "E11_Sabaneta": (1.5, -9.0), "E12_LaEstrella": (-2.0, -10.0),
}
EMPLEADOS_INFO = {
    "E01_Copacabana": {"ventana": (8.0, 12.0), "duracion": 0.75, "hora_historia": 8.5},
    "E02_Bello": {"ventana": (8.5, 12.5), "duracion": 1.00, "hora_historia": 9.0},
    "E03_Aranjuez": {"ventana": (9.0, 14.0), "duracion": 0.50, "hora_historia": 11.5},
    "E04_Robledo": {"ventana": (8.0, 13.0), "duracion": 0.75, "hora_historia": 8.5},
    "E05_Laureles": {"ventana": (10.0, 15.0), "duracion": 0.50, "hora_historia": 14.0},
    "E06_BuenosAires": {"ventana": (8.5, 12.0), "duracion": 0.75, "hora_historia": 10.0},
    "E07_Belen": {"ventana": (9.0, 14.0), "duracion": 1.00, "hora_historia": 13.0},
    "E08_Poblado": {"ventana": (8.0, 12.0), "duracion": 0.50, "hora_historia": 8.5},
    "E09_Envigado": {"ventana": (10.0, 16.0), "duracion": 0.75, "hora_historia": 11.5},
    "E10_Itagui": {"ventana": (8.0, 12.0), "duracion": 0.50, "hora_historia": 10.0},
    "E11_Sabaneta": {"ventana": (11.0, 16.0), "duracion": 0.75, "hora_historia": 15.0},
    "E12_LaEstrella": {"ventana": (8.5, 13.0), "duracion": 1.00, "hora_historia": 9.0},
}
VELOCIDAD_KMH, PESO_SORPRESA, MARGEN_MINIMO, HORA_SALIDA, MAX_JORNADA = 24.0, 3.5, 1.5, 8.0, 8.0
BASES = ["Base_Norte", "Base_Centro", "Base_Sur"]


def distancia(a, b):
    (x1, y1), (x2, y2) = UBICACIONES[a], UBICACIONES[b]
    return math.hypot(x2 - x1, y2 - y1) * 1.3  # 1.3: se va por calles, no en línea recta


def formatear_hora(h):
    horas, minutos = int(h), int(round((h - int(h)) * 60))
    if minutos == 60:
        horas, minutos = horas + 1, 0
    return f"{horas:02d}:{minutos:02d}"


class Estado:
    def __init__(self, nodo, pendientes, reloj, g, base, padre=None):
        self.nodo, self.pendientes, self.reloj, self.g, self.padre = nodo, pendientes, reloj, g, padre
        self.h = distancia(nodo, base) if not pendientes else min(distancia(nodo, p) for p in pendientes)
        self.f = self.g + self.h

    def __lt__(self, otro):
        return self.f < otro.f


def a_estrella(base, empleados):
    cola = [Estado(base, empleados, HORA_SALIDA, 0.0, base)]
    while cola:
        actual = heapq.heappop(cola)
        if not actual.pendientes:
            if actual.nodo == base:
                camino = []
                while actual:
                    camino.append(actual.nodo)
                    actual = actual.padre
                return camino[::-1]
            h_llegada = actual.reloj + distancia(actual.nodo, base) / VELOCIDAD_KMH
            if h_llegada - HORA_SALIDA <= MAX_JORNADA:
                heapq.heappush(cola, Estado(base, [], h_llegada, actual.g + distancia(actual.nodo, base), base, actual))
            continue
        for sig in actual.pendientes:
            d = distancia(actual.nodo, sig)
            h_llegada = actual.reloj + d / VELOCIDAD_KMH
            info = EMPLEADOS_INFO[sig]
            if h_llegada > info["ventana"][1]:
                continue
            h_inicio = max(h_llegada, info["ventana"][0])
            if h_inicio + info["duracion"] - HORA_SALIDA > MAX_JORNADA:
                continue
            dif = abs(h_inicio - info["hora_historia"])  # penaliza visitas predecibles (factor sorpresa)
            penalidad = (MARGEN_MINIMO - dif) * PESO_SORPRESA if dif < MARGEN_MINIMO else 0
            heapq.heappush(cola, Estado(sig, [p for p in actual.pendientes if p != sig], h_inicio + info["duracion"],
                                        actual.g + d + penalidad, base, actual))
    return None


def resolver_sprint1():
    zonas = {b: [] for b in BASES}
    for emp in EMPLEADOS_INFO:
        zonas[min(BASES, key=lambda b: distancia(emp, b))].append(emp)
    salida = {}
    for base, emps in zonas.items():
        ruta = a_estrella(base, emps)
        pasos, reloj = [], HORA_SALIDA
        for o, d in zip(ruta, ruta[1:]):
            reloj += distancia(o, d) / VELOCIDAD_KMH
            if d == base:
                pasos.append({"hora": formatear_hora(reloj), "lugar": "Regreso a la base", "espera_min": 0, "sorpresa": ""})
                continue
            info = EMPLEADOS_INFO[d]
            inicio = max(reloj, info["ventana"][0])
            espera = int((inicio - reloj) * 60)
            reloj = inicio + info["duracion"]
            sorpresa = abs(inicio - info["hora_historia"]) >= MARGEN_MINIMO
            pasos.append({"hora": formatear_hora(inicio), "lugar": d.split("_", 1)[1], "espera_min": espera,
                          "sorpresa": "Lograda" if sorpresa else "Predecible",
                          "historial": formatear_hora(info["hora_historia"])})
        salida[base] = {"ruta": ruta, "pasos": pasos}
    return salida


# ============================================================== SPRINT 2 · Sistema experto de reclutamiento
NIVELES_ESTUDIO = {"Bachiller": 1, "Técnico": 2, "Profesional": 3, "Posgrado": 4}
NIVELES_INGLES = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}


@dataclass
class Candidato:
    nombre: str
    experiencia_anos: float
    estudios: str
    nivel_ingles: str
    hab_tecnicas: List[str]
    hab_blandas: List[str]
    disponibilidad: str
    modalidad: str


@dataclass
class Vacante:
    cargo: str
    nivel_cargo: str
    exp_minima: float
    estudios_minimos: str
    ingles_minimo: str
    hab_tecnicas_req: List[str]
    hab_blandas_req: List[str]
    disponibilidad_req: str
    modalidad_req: str


VACANTES = [
    Vacante("Auxiliar de Bodega", "Operativo", 0.5, "Bachiller", "A1", ["Manejo de Inventario"],
            ["Puntualidad", "Trabajo en Equipo"], "Tiempo Completo", "Presencial"),
    Vacante("Desarrollador de Software", "Profesional", 3.0, "Profesional", "B2", ["Python", "SQL", "Git"],
            ["Comunicación Asertiva", "Resolución de Problemas"], "Tiempo Completo", "Híbrido"),
    Vacante("Director de Tecnología (CTO)", "Gerente", 8.0, "Posgrado", "C1", ["Arquitectura de Software", "Presupuestos"],
            ["Liderazgo", "Negociación"], "Tiempo Completo", "Presencial"),
]
CANDIDATOS_S2 = [
    [Candidato("Pedro Gómez", 1.0, "Bachiller", "A1", ["Manejo de Inventario"], ["Puntualidad", "Trabajo en Equipo"], "Tiempo Completo", "Presencial"),
     Candidato("Juan Ruiz", 0.2, "Bachiller", "A1", ["Manejo de Inventario"], ["Puntualidad", "Trabajo en Equipo"], "Tiempo Completo", "Presencial"),
     Candidato("Luisa Cano", 2.0, "Bachiller", "A1", ["Manejo de Inventario"], ["Trabajo en Equipo"], "Medio Tiempo", "Presencial")],
    [Candidato("Ana Martínez", 4.0, "Profesional", "B2", ["Python", "SQL", "Git"], ["Comunicación Asertiva", "Resolución de Problemas"], "Tiempo Completo", "Híbrido"),
     Candidato("Carlos López", 5.0, "Profesional", "A2", ["Python", "SQL", "Git"], ["Comunicación Asertiva", "Resolución de Problemas"], "Tiempo Completo", "Híbrido"),
     Candidato("Sofía Torres", 1.5, "Técnico", "B2", ["Python"], ["Comunicación Asertiva", "Resolución de Problemas"], "Tiempo Completo", "Híbrido")],
    [Candidato("Roberto Silva", 10.0, "Posgrado", "C1", ["Arquitectura de Software", "Presupuestos"], ["Liderazgo", "Negociación"], "Tiempo Completo", "Presencial"),
     Candidato("Elena Vargas", 9.0, "Profesional", "C1", ["Arquitectura de Software", "Presupuestos"], ["Liderazgo", "Negociación"], "Tiempo Completo", "Presencial"),
     Candidato("Mario Ríos", 6.0, "Posgrado", "B2", ["Presupuestos"], ["Liderazgo"], "Tiempo Completo", "Remoto")],
]

REGLAS_S2 = [  # (id, descripción, condición(c, v, hechos), hecho, mensaje si falla)
    ("R1_EXP", "SI experiencia ≥ requerida ENTONCES experiencia_ok",
     lambda c, v, h: c.experiencia_anos >= v.exp_minima, "experiencia_ok", "Experiencia laboral insuficiente"),
    ("R2_ESTUDIOS", "SI estudios ≥ requeridos ENTONCES estudios_ok",
     lambda c, v, h: NIVELES_ESTUDIO[c.estudios] >= NIVELES_ESTUDIO[v.estudios_minimos], "estudios_ok",
     "Nivel de estudios inferior al requerido"),
    ("R3_INGLES", "SI inglés ≥ requerido ENTONCES ingles_ok",
     lambda c, v, h: NIVELES_INGLES[c.nivel_ingles] >= NIVELES_INGLES[v.ingles_minimo], "ingles_ok",
     "Nivel de inglés insuficiente"),
    ("R4_TECH", "SI posee todas las habilidades técnicas ENTONCES tecnicas_ok",
     lambda c, v, h: set(v.hab_tecnicas_req) <= set(c.hab_tecnicas), "tecnicas_ok", "Faltan habilidades técnicas"),
    ("R5_BLANDAS", "SI posee todas las habilidades blandas ENTONCES blandas_ok",
     lambda c, v, h: set(v.hab_blandas_req) <= set(c.hab_blandas), "blandas_ok", "Faltan habilidades blandas"),
    ("R6_DISP", "SI la disponibilidad coincide ENTONCES disponibilidad_ok",
     lambda c, v, h: c.disponibilidad == v.disponibilidad_req, "disponibilidad_ok", "Disponibilidad incompatible"),
    ("R7_MODALIDAD", "SI la modalidad coincide ENTONCES modalidad_ok",
     lambda c, v, h: c.modalidad == v.modalidad_req, "modalidad_ok", "Modalidad incompatible"),
    ("R8_INTEGRACION", "SI se cumplen los 7 requisitos ENTONCES cumple_todos_los_requisitos",
     lambda c, v, h: {"experiencia_ok", "estudios_ok", "ingles_ok", "tecnicas_ok", "blandas_ok", "disponibilidad_ok",
                      "modalidad_ok"} <= h, "cumple_todos_los_requisitos", None),
    ("R9_APROBACION", "SI cumple_todos_los_requisitos ENTONCES CONCLUSIÓN: APTO",
     lambda c, v, h: "cumple_todos_los_requisitos" in h, "APTO", None),
]


def evaluar_sprint2(c, v):
    hechos, traza, nuevo = set(), [], True
    while nuevo:
        nuevo = False
        for rid, _, cond, hecho, _ in REGLAS_S2:
            if hecho not in hechos and cond(c, v, hechos):
                hechos.add(hecho)
                traza.append((rid, hecho))
                nuevo = True
    fallos = [msg for _, _, _, hecho, msg in REGLAS_S2 if msg and hecho not in hechos]
    return {"apto": "APTO" in hechos, "traza": traza, "fallos": fallos}
