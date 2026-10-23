# Headhunter IA: el próximo CEO de Intel

Proyecto del curso **Fundamentos de Inteligencia Artificial**. La app hace el trabajo de un *headhunter*: entiende a la
empresa, evalúa candidatos reales y recomienda al líder que mejor puede sacarla adelante. El caso es **Intel**, que se
quedó atrás frente a NVIDIA.

**Integrantes:** María Adelaida Restrepo, Juanita Arenas, Michelle Ruiz, Sofía Berrío y Jerónimo Morales.

## Flujo de la app

| Paso | Rol | Técnica | Sprint |
|---|---|---|---|
| 1 · Entender a Intel | Analista de la industria | LLM externo (Gemini) + dossier de hechos → JSON | 3 |
| 2 · Candidatos | Búsqueda | Base de conocimiento de 7 ejecutivos reales | 3 |
| 3 · Filtro de requisitos | Descarte | Sistema experto (encadenamiento hacia adelante) + **lógica difusa** | 2, 3, **4** |
| 4 · Selección y mandato | Comparación | Algoritmo genético verificado con búsqueda exhaustiva | 3 |
| 5 · Reacción de la competencia | Prueba de estrés | Equilibrio de Nash + Minimax con poda Alfa-Beta | 3 |
| 6 · Recomendación | Decisión | Puntaje ponderado + memo del LLM | 3 |
| Bitácora | — | A* (Sprint 1), sistema experto (Sprint 2), pipeline (Sprint 3), lógica difusa (Sprint 4) | 1–4 |

### Sprint 4: lógica difusa

El filtro deja de preguntar "¿cumple o no cumple?" y pregunta "¿qué tanto cumple?". Cada requisito tiene una función
de pertenencia en rampa (0 % por debajo de *mínimo − tolerancia*, 100 % desde el mínimo). El grado del candidato es el
**mínimo** de sus grados: vale lo que vale su requisito menos cumplido. Pasan a la comparación quienes superan un corte
α (50 % por defecto) y el algoritmo genético penaliza la brecha con `−0.10 · (1 − grado)`. Ya no hace falta la regla de
relajación.

## Ejecutar en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

La app trae guardada una respuesta de Gemini, así que funciona sin API key. Para pedir un análisis nuevo, escribe tu
clave en la página 1 o créala como secreto `GEMINI_API_KEY` (en local, en `.streamlit/secrets.toml`; en Streamlit
Community Cloud, en *Settings → Secrets*). Nunca subas la clave al repositorio.

## Uso académico

Los puntajes de los candidatos son estimaciones del equipo hechas con información pública; no son evaluaciones reales
de esas personas. Los pagos de los juegos son pedagógicos.

Herramientas de IA que apoyaron el desarrollo: ChatGPT y Gemini (Sprints 1 y 2) y Claude (Sprints 3 y 4 y esta app).
