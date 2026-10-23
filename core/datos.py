"""Base de conocimiento del proyecto: candidatos, dossier de Intel y análisis de referencia del LLM.

Los datos vienen del notebook del Sprint 3 (versión 2) y de su prototipo HTML.
Los puntajes 0-10 son estimaciones del equipo hechas con evidencia pública (uso académico).
"""

EMPRESA = "Intel Corporation"
FECHA_ANALISIS = "2026-10-15"

CRITERIOS = ["tecnologia", "manufactura", "ia", "finanzas", "transformacion", "liderazgo", "ecosistema", "gobernanza"]
CRIT_LBL = {
    "tecnologia": "Tecnología", "manufactura": "Manufactura", "ia": "IA", "finanzas": "Finanzas",
    "transformacion": "Transformación", "liderazgo": "Liderazgo", "ecosistema": "Ecosistema", "gobernanza": "Gobernanza",
}
FRENTES = ["foundry", "aceleradores_ia", "cpu_data_center", "pc_ia", "eficiencia_costos", "alianzas"]
FR_LBL = {
    "foundry": "Foundry", "aceleradores_ia": "Aceleradores de IA", "cpu_data_center": "CPU para data center",
    "pc_ia": "PC con IA", "eficiencia_costos": "Eficiencia de costos", "alianzas": "Alianzas",
}
REQ_LBL = {
    "exp_min_ceo_anos": "Años como CEO", "min_tecnologia": "Tecnología",
    "min_gobernanza": "Gobernanza", "min_transformacion": "Transformación",
}
# requisito -> atributo del candidato que se compara
REQ_ATRIB = {
    "exp_min_ceo_anos": "exp_ceo", "min_tecnologia": "tecnologia",
    "min_gobernanza": "gobernanza", "min_transformacion": "transformacion",
}

COLORES = ["#2563eb", "#059669", "#d97706", "#7c3aed", "#ea580c", "#db2777", "#dc2626"]

CANDIDATOS = [
    {"id": "C1", "nombre": "Lisa Su", "cargo": "Presidenta y CEO de AMD (desde 2014)",
     "exp_ceo": 12, "tecnologia": 9.5, "manufactura": 6.5, "ia": 8.5, "finanzas": 8.5, "transformacion": 9.5,
     "liderazgo": 9.5, "ecosistema": 9.0, "gobernanza": 9.5, "disponibilidad": 0.10, "conflicto": True,
     "logros": [
         "Rescató a AMD de una situación cercana a la quiebra (2014) con la arquitectura Zen y el diseño por chiplets.",
         "Llevó a AMD al 46% de los ingresos de CPU x86 para servidores (Q1 2026), casi todo ganado a Intel.",
         "Compró Xilinx (~US$49.000 M, 2022) y construyó la línea Instinct (MI300/MI400) de aceleradores de IA.",
         "Firmó acuerdos de varios gigavatios con OpenAI (2025) y Meta (2026) para la serie MI450.",
     ],
     "no_logros": [
         "La participación de AMD en aceleradores de IA sigue siendo pequeña frente a NVIDIA.",
         "Su ecosistema de software (ROCm) va detrás de CUDA.",
         "Nunca ha dirigido fábricas propias: AMD es fabless y depende de TSMC.",
     ]},
    {"id": "C2", "nombre": "C.C. Wei", "cargo": "Presidente de la junta y CEO de TSMC",
     "exp_ceo": 8, "tecnologia": 8.5, "manufactura": 10.0, "ia": 7.5, "finanzas": 8.5, "transformacion": 6.5,
     "liderazgo": 8.5, "ecosistema": 9.5, "gobernanza": 9.0, "disponibilidad": 0.05, "conflicto": True,
     "logros": [
         "Como CEO (2018) y presidente (2024) consolidó a TSMC como líder mundial en N5, N3 y N2.",
         "Es el fabricante de los chips de IA de NVIDIA, AMD, Apple y los hiperescaladores; amplió el empaquetado CoWoS.",
         "Lideró la expansión en Arizona, con un compromiso total de US$165.000 M.",
     ],
     "no_logros": [
         "La primera fábrica de Arizona se retrasó de 2024 a 2025 por falta de mano de obra y choques culturales.",
         "No tiene experiencia dirigiendo una empresa en crisis ni el diseño de productos propios (TSMC es foundry pura).",
     ]},
    {"id": "C3", "nombre": "Hock Tan", "cargo": "Presidente y CEO de Broadcom (desde 2006)",
     "exp_ceo": 20, "tecnologia": 6.5, "manufactura": 5.0, "ia": 9.0, "finanzas": 10.0, "transformacion": 9.0,
     "liderazgo": 6.5, "ecosistema": 8.5, "gobernanza": 7.0, "disponibilidad": 0.10, "conflicto": True,
     "logros": [
         "Convirtió a Avago en Broadcom con adquisiciones: Broadcom (2016), CA (2018), Symantec Enterprise (2019) y VMware (US$69.000 M, 2023).",
         "Construyó el negocio de chips de IA a medida (XPU) para Google, OpenAI y Anthropic. Q3 FY2026: ingresos de US$29.600 M (+86%).",
         "Es reconocido por su disciplina de costos y márgenes muy altos.",
     ],
     "no_logros": [
         "Su oferta hostil por Qualcomm (2018) fue bloqueada por el Gobierno de EE. UU.",
         "Los cambios de licenciamiento de VMware provocaron rechazo de clientes, demandas y quejas regulatorias en Europa.",
         "Su estilo de recortes agresivos choca con una cultura de I+D como la de Intel.",
     ]},
    {"id": "C4", "nombre": "Sanjay Mehrotra", "cargo": "Presidente de la junta y CEO de Micron (desde 2017)",
     "exp_ceo": 14, "tecnologia": 9.0, "manufactura": 9.0, "ia": 8.0, "finanzas": 8.0, "transformacion": 8.0,
     "liderazgo": 8.0, "ecosistema": 8.0, "gobernanza": 9.0, "disponibilidad": 0.15, "conflicto": False,
     "logros": [
         "Cofundó SanDisk (1988) y, como CEO, la vendió a Western Digital por ~US$19.000 M (2016).",
         "Llevó a Micron al liderazgo en memoria HBM para IA. FY2026: ingresos récord de US$133.200 M (+256%).",
         "Dirige fábricas propias en EE. UU. y Asia; obtuvo ~US$6.100 M del CHIPS Act.",
     ],
     "no_logros": [
         "Micron llegó tarde a HBM3 frente a SK hynix.",
         "Registró una pérdida de ~US$5.800 M en el ciclo bajo de FY2023.",
         "China prohibió el uso de chips de Micron en infraestructura crítica (2023).",
     ]},
    {"id": "C5", "nombre": "Cristiano Amon", "cargo": "Presidente y CEO de Qualcomm (desde 2021)",
     "exp_ceo": 5, "tecnologia": 8.5, "manufactura": 5.0, "ia": 7.0, "finanzas": 7.0, "transformacion": 7.5,
     "liderazgo": 8.0, "ecosistema": 8.5, "gobernanza": 8.5, "disponibilidad": 0.25, "conflicto": True,
     "logros": [
         "Diversificó Qualcomm hacia automoción: +61% interanual en Q3 FY2026 (US$1.590 M).",
         "Entró al mercado de PC con Snapdragon X (Arm), en competencia directa con Intel.",
         "Ganó el juicio contra Arm por licencias (jurado, diciembre de 2024).",
     ],
     "no_logros": [
         "Perdió el negocio de módems de Apple; el segmento de celulares cayó 20% interanual en Q3 FY2026.",
         "Su entrada a centros de datos aún no genera ingresos relevantes.",
         "La participación de Snapdragon en PC sigue siendo pequeña.",
     ]},
    {"id": "C6", "nombre": "Rene Haas", "cargo": "CEO de Arm (desde 2022) y líder de SoftBank Group International",
     "exp_ceo": 4, "tecnologia": 8.0, "manufactura": 4.0, "ia": 8.0, "finanzas": 8.0, "transformacion": 7.5,
     "liderazgo": 7.5, "ecosistema": 8.0, "gobernanza": 7.5, "disponibilidad": 0.20, "conflicto": True,
     "logros": [
         "Llevó a Arm a la salida a bolsa más grande de 2023 (Nasdaq).",
         "Aumentó las regalías con Armv9 e impulsó la adopción de Arm en centros de datos.",
         "Trabajó 7 años en NVIDIA; en 2026 SoftBank amplió su rol para coordinar sus empresas de chips e IA.",
     ],
     "no_logros": [
         "Perdió el juicio contra Qualcomm (diciembre de 2024).",
         "Su giro hacia chips propios genera conflicto con los clientes de Arm.",
         "No tiene experiencia en manufactura ni en dirigir una empresa de más de 100.000 empleados.",
     ]},
    {"id": "C7", "nombre": "Pat Gelsinger", "cargo": "Socio general de Playground Global; presidente ejecutivo de Gloo",
     "exp_ceo": 13, "tecnologia": 9.5, "manufactura": 7.0, "ia": 4.0, "finanzas": 3.5, "transformacion": 5.0,
     "liderazgo": 7.0, "ecosistema": 7.5, "gobernanza": 7.0, "disponibilidad": 0.90, "conflicto": False,
     "logros": [
         "Fue arquitecto del 80486 y CTO de Intel (2001–2009).",
         "Como CEO de VMware (2012–2021) más que duplicó los ingresos.",
         "Impulsó el CHIPS Act y la estrategia IDM 2.0 (Intel Foundry).",
     ],
     "no_logros": [
         "Como CEO de Intel (2021–2024): pérdida de ~US$18.700 M en 2024, suspensión del dividendo y recorte de ~15% de la plantilla.",
         "Llegó tarde a la IA: Gaudi no cumplió su meta de ventas.",
         "Invirtió en fábricas sin clientes de foundry comprometidos; fue removido por la junta.",
     ]},
]
for _i, _c in enumerate(CANDIDATOS):
    _c["color"] = COLORES[_i]

DOSSIER = {
    "fecha_corte": FECHA_ANALISIS,
    "ceo_actual": {
        "nombre": "Lip-Bu Tan", "desde": "marzo de 2025",
        "trayectoria": "CEO de Cadence Design Systems (2009–2021); fundador de Walden International; miembro de la junta "
                       "de Intel hasta agosto de 2024, cuando renunció por desacuerdos con la estrategia.",
        "decisiones": [
            "Reducción fuerte de plantilla y recorte de gastos operativos durante 2025.",
            "Cancelación o retraso de fábricas (Alemania y Polonia canceladas; Ohio desacelerada).",
            "Venta del 51% de Altera a Silver Lake.",
            "Entrada del Gobierno de EE. UU. como mayor accionista (~10%, agosto de 2025), inversión de NVIDIA por "
            "US$5.000 M (sept. 2025) y de SoftBank por US$2.000 M.",
            "Lanzamiento de Panther Lake en el nodo 18A; kit de diseño (PDK) 0.9 del nodo 14A para clientes externos en octubre de 2026.",
        ],
        "resultados_recientes": "Q2 2026: ingresos US$16.100 M (+25% interanual); Data Center e IA US$6.300 M (+59%); "
                                "Foundry US$5.800 M (+31%); margen bruto GAAP 40,4%. Pérdida neta GAAP de US$11.000 M por "
                                "un ajuste contable ligado al acuerdo CHIPS. La demanda de CPU para servidores supera la capacidad.",
        "controversias": "En agosto de 2025 el presidente de EE. UU. pidió públicamente su renuncia por sus inversiones "
                         "ligadas a China; luego se reunieron y el Gobierno terminó tomando una participación en Intel.",
    },
    "ceo_anterior": {
        "nombre": "Pat Gelsinger",
        "periodo": "febrero de 2021 – diciembre de 2024 (salida forzada por la junta)",
        "decisiones": [
            "Estrategia IDM 2.0: ser fabricante propio y foundry para terceros; plan de '5 nodos en 4 años'.",
            "Inversiones masivas en fábricas sin clientes externos de foundry comprometidos.",
            "Apuesta tardía y débil por aceleradores de IA (Gaudi no alcanzó la meta de US$500 M en 2024).",
            "2024: pérdida neta de ~US$18.700 M, suspensión del dividendo y recorte de ~15% de la plantilla.",
        ],
    },
    "mercado": {
        "nvidia": "Q2 FY2027: ingresos de US$96.200 M (+106%), Data Center US$89.000 M, margen bruto del 75%.",
        "amd": "Q1 2026: 33,2% de las unidades y 46,2% de los ingresos de CPU x86 para servidores. Intel conserva cerca del 70% del mercado de PC.",
        "tsmc": "N2 en producción desde finales de 2025; inversión anunciada de US$165.000 M en Arizona.",
        "foundry_intel": "Ningún cliente externo ha firmado un compromiso formal de volumen en 14A. Se reporta que Apple "
                         "evalúa 14A y que Intel se unió al proyecto Terafab. Producción de volumen de 14A en 2029.",
        "tendencias": [
            "Demanda explosiva de cómputo para IA.",
            "Chips a medida (ASIC/XPU) de los hiperescaladores.",
            "Soberanía tecnológica y relocalización de la manufactura (CHIPS Act).",
            "Avance de Arm en PC y centros de datos.",
            "Escasez de capacidad en nodos avanzados y empaquetado.",
        ],
    },
}

# Respuesta del LLM guardada (mismo esquema JSON del notebook). Permite usar la app sin API key.
ANALISIS_REFERENCIA = {
    "empresa": "Intel Corporation",
    "diagnostico_empresa": {
        "resumen": "Intel vive una recuperación operativa real en 2026: sus ingresos crecieron 25% en Q2 y su margen bruto "
                   "subió a 40,4%, impulsados por la demanda de CPU para servidores de IA. Pero la brecha estructural con "
                   "NVIDIA es enorme: NVIDIA factura unas seis veces más por trimestre, con márgenes del 75%. Intel no tiene "
                   "una franquicia relevante en aceleradores de IA y su foundry aún no tiene un cliente externo comprometido "
                   "en volumen. Además, AMD ya captura el 46% de los ingresos de CPU para servidores. La empresa depende de "
                   "capital externo y necesita convertir la recuperación táctica en una estrategia ganadora de largo plazo.",
        "fortalezas": [
            "Cerca del 70% del mercado de CPU para PC y una enorme base instalada x86",
            "Fabricación avanzada propia en EE. UU. (18A en producción, 14A en camino), clave para la soberanía tecnológica",
            "Respaldo de capital del Gobierno de EE. UU., NVIDIA y SoftBank",
            "Demanda de CPU para servidores de IA mayor que la capacidad, con 10 contratos de largo plazo",
        ],
        "debilidades": [
            "Sin producto competitivo en aceleradores de IA (Gaudi no alcanzó sus metas)",
            "Intel Foundry sin clientes externos comprometidos en volumen",
            "Pérdida de cuota en servidores frente a AMD",
            "Historial de retrasos de nodos que dañó su credibilidad de ejecución",
        ],
        "oportunidades": [
            "Ser la alternativa occidental a TSMC para Apple, Terafab y los hiperescaladores",
            "Empaquetado avanzado (Foveros/EMIB) ante la escasez de CoWoS",
            "Alianza con NVIDIA: CPU x86 con NVLink y SoC para PC con GPU RTX",
            "AI PC y CPU para inferencia en centros de datos",
        ],
        "amenazas": [
            "NVIDIA, AMD y los ASIC de los hiperescaladores capturan el gasto en IA",
            "Avance de Arm en PC y servidores",
            "TSMC con N2, A14 y US$165.000 M en Arizona",
            "Intensidad de capital: si 14A no consigue clientes, la foundry vuelve a destruir valor",
        ],
    },
    "analisis_ceo_actual": {
        "nombre": "Lip-Bu Tan",
        "aciertos": [
            "Estabilizó las finanzas: recortó costos, vendió el 51% de Altera y atrajo capital estratégico",
            "Disciplina de inversión: canceló fábricas sin demanda (Alemania, Polonia)",
            "Recuperó la confianza del mercado con resultados por encima de lo esperado durante 2026",
        ],
        "limitaciones": [
            "Su perfil es de inversionista y de software EDA, no de operación de fábricas a gran escala",
            "La estrategia de IA en centros de datos sigue sin un producto líder",
            "Tuvo una polémica pública por sus inversiones ligadas a China (agosto de 2025)",
            "La recuperación se basa en CPU y no cierra la brecha con NVIDIA",
        ],
        "por_que_se_requiere_un_cambio": "La fase de estabilización ya se logró. La siguiente fase exige un líder que "
            "convierta a Intel en un actor central de la infraestructura de IA, que llene las fábricas con clientes externos "
            "y construya una oferta de IA competitiva. Es pasar de un CEO de rescate financiero a un CEO de crecimiento "
            "tecnológico y de manufactura.",
    },
    "legado_ceo_anterior": {
        "nombre": "Pat Gelsinger",
        "decisiones_que_dejaron_atras_a_intel": [
            "Construyó capacidad de foundry (IDM 2.0) sin clientes externos comprometidos",
            "Llegó tarde y con poca fuerza a los aceleradores de IA, mientras NVIDIA capturaba el mercado",
            "Hizo promesas agresivas de nodos ('5 en 4 años') que presionaron las finanzas",
            "Terminó con pérdidas récord en 2024, suspensión del dividendo y despidos masivos",
        ],
    },
    "problematica_central": "Intel recuperó estabilidad financiera, pero sigue fuera del centro del gasto mundial en IA. "
        "No tiene un acelerador competitivo, su foundry no ha llenado sus fábricas con clientes externos y pierde terreno "
        "en servidores. Necesita un CEO que combine excelencia en manufactura de semiconductores, visión de IA y capacidad "
        "de construir alianzas con clientes.",
    "tipo_crisis": "MIXTA",
    "tendencias_mercado": [
        "Cómputo para IA como motor del gasto en semiconductores",
        "Chips a medida de los hiperescaladores",
        "Relocalización de la manufactura y soberanía tecnológica",
        "Arm en PC y servidores",
        "Cuellos de botella en empaquetado avanzado y memoria HBM",
    ],
    "estrategia_reclutamiento": {
        "nombre": "Constructor de plataforma: IA + manufactura",
        "pilares": [
            "Experiencia comprobada operando manufactura de semiconductores a gran escala",
            "Historial transformando una empresa rezagada en líder de su categoría",
            "Credibilidad con clientes de IA (hiperescaladores, NVIDIA, Apple) y con el Gobierno",
            "Disciplina de capital: invertir solo con demanda comprometida",
            "Gobernanza impecable y sin conflictos de interés",
        ],
        "perfil_ideal": "Ejecutivo con al menos 5 años como CEO de una empresa de semiconductores, profundo dominio técnico "
                        "y de manufactura, experiencia llevando productos al mercado de IA, historial de transformación y "
                        "relaciones sólidas con clientes estratégicos.",
        "preguntas_clave_entrevista": [
            "¿Qué tres clientes externos firmaría para 14A en sus primeros 12 meses y cómo?",
            "¿Cómo competiría Intel en IA sin enfrentarse de frente a NVIDIA?",
            "¿Qué invertiría y qué cerraría en sus primeros 100 días?",
        ],
        "senales_de_alerta": [
            "Promesas de nodos sin clientes ni fechas verificables",
            "Conflictos de interés con competidores o proveedores",
            "Recortes de I+D como única palanca de mejora",
        ],
    },
    "requisitos_rigidos": {"exp_min_ceo_anos": 5, "min_tecnologia": 8, "min_gobernanza": 7.5, "min_transformacion": 7},
    "pesos_criterios": {"tecnologia": 0.16, "manufactura": 0.18, "ia": 0.18, "finanzas": 0.10, "transformacion": 0.14,
                        "liderazgo": 0.10, "ecosistema": 0.08, "gobernanza": 0.06},
    "prioridades_frentes": {"foundry": 0.28, "aceleradores_ia": 0.24, "cpu_data_center": 0.18, "pc_ia": 0.08,
                            "eficiencia_costos": 0.10, "alianzas": 0.12},
    "justificacion_cuantitativa": "Manufactura e IA pesan más porque son las dos brechas centrales. La transformación pesa "
        "por la necesidad de un giro. Foundry e IA lideran las prioridades porque definen el valor de largo plazo; las "
        "alianzas son el puente hacia los clientes de la foundry.",
}

FUENTES = [
    "Intel Q2 2026 (Yahoo Finance, 23-jul-2026)",
    "NVIDIA 8-K Q2 FY2027 (SEC, 26-ago-2026)",
    "Mercury Research vía Tom's Hardware (14-may-2026)",
    "AI Weekly, PDK 14A (27-jun-2026)",
    "CNN/CNBC, inversión de NVIDIA en Intel (18-sep-2025)",
    "Micron Q4 FY2026 (Blocks & Files, 01-oct-2026)",
    "Broadcom Q3 FY2026 (DatacenterDynamics, 04-sep-2026)",
    "Qualcomm Q3 FY2026 (Futurum, 03-ago-2026)",
    "Bloomberg Law, Rene Haas (21-abr-2026)",
    "Wikipedia: Pat Gelsinger, Lisa Su, C.C. Wei, Hock Tan",
]

INTEGRANTES = ["María Adelaida Restrepo", "Juanita Arenas", "Michelle Ruiz", "Sofía Berrío", "Jerónimo Morales"]
