Absolutamente. A continuación, se presenta el análisis estructurado de **Q20: KPI Global (Índice Compuesto de Rendimiento)**, siguiendo el formato riguroso de las fuentes y centrándose en el **Máximo Rendimiento** mediante la **Ponderación Estratégica** y el **Diagnóstico de Contribución**.

El Q20 es el índice sintético que resume el rendimiento general de la marca y debe ser reestructurado para reflejar los objetivos de negocio del cliente y proporcionar contexto competitivo.

---

## Análisis Estructurado de Q20: KPI Global (Índice Compuesto de Rendimiento)

##### Objetivo

El objetivo de Q20 (`q20_kpi_global`) es calcular un puntaje único y compuesto que refleje el rendimiento general de la estrategia digital del cliente. El **Máximo Rendimiento** se logra al transformar la fórmula básica inicial ("ejemplo muy básico") en un **Índice Ponderado Estratégico**, dotado de transparencia y contexto:

1.  **Expansión de Variables:** Incluir los pilares de Social Media: **Engagement (Q11)**, **Comunidad (Q12)**, **Frecuencia (Q13/Q14)**, y **Sentimiento (Q17)**.
2.  **Ponderación Dinámica:** Asignar pesos (ponderación) a las métricas constituyentes basándose en el **objetivo de negocio principal** (`primary_business_goal`) del cliente, obtenido de la **Ficha Cliente**.
3.  **Benchmarking:** Integrar el análisis con **Q16 (Benchmark Competitivo)** para calcular el **Z-Score del KPI Global** del cliente frente a la media de su mercado.

##### Prompt Literal Completo

**Q20 no utiliza un *prompt* literal dirigido al modelo de IA (LLM)**. Es un análisis **cuantitativo** ejecutado por el *Orquestador* utilizando las librerías **Pandas/Python**.

La **Lógica de Cálculo (Python/Pandas)** se implementa en el módulo `q20_kpi_global.py` (implícito):

| Lógica | Descripción | Fuente |
| :--- | :--- | :--- |
| **Expansión de Variables** | El índice debe incluir variables clave (Q11, Q12, Q13, Q17). | |
| **Ponderación Estratégica** | Asignar el mayor peso (ponderación) a la métrica que se alinee con el `primary_business_goal` de la Ficha Cliente. Por ejemplo, si el objetivo es "Aumentar Crecimiento de Comunidad", Q12 recibe el peso más alto. | |
| **Cálculo de Benchmarking** | Calcular el índice compuesto para el cliente y para los competidores (usando Q16), y aplicar la fórmula del **Z-Score al KPI Global**. | |
| **Transparencia** | Desglosar la **contribución_por_kpi** para que el *frontend* pueda mostrar *por qué* el puntaje es el que es. | |

##### Crítica al Cálculo

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Punto Fuerte (Funcionalidad)** | El índice ponderado y benchmarkeado (Z-Score) es un indicador de **reporting estratégico de primer nivel**. La inclusión del desglose de contribución resuelve la crítica de la "caja negra" del cálculo. | |
| **Punto Débil (Metodología)** | La fiabilidad del cálculo depende de la correcta **ejecución y ponderación** de los *frameworks* subyacentes (Q11, Q12, Q17). Si la ponderación dinámica (basada en el objetivo del cliente) es incorrecta, el índice dirigirá la estrategia hacia el camino equivocado. | |
| **Dependencia Crítica** | Q20 depende de que **Q16 (Benchmark Competitivo)** haya sido implementado para proporcionar los datos necesarios para el cálculo del Z-Score. | |

##### Outputs

El *output* JSON debe ser una **estructura jerárquica y cuantificada** para el índice compuesto, alineándose con el esquema Pydantic **`Q20KpiGlobal`** (implícito).

| Clave del JSON | Estructura Esperada | Requisito de Pydantic (Guardían) | Fuente |
| :--- | :--- | :--- | :--- |
| **`puntaje_final_escalado`** | `float` - El puntaje final del índice (escala 0-100). | | |
| **`z_score_kpi_global`** | `float` - La posición del cliente en desviaciones estándar respecto a la media competitiva. | **CRÍTICO:** El esquema debe validar este campo. | |
| **`contribucion_por_kpi`** | `List[Dict]` - Desglose de cómo contribuyó cada métrica constituyente (Q11, Q12, Q17) al puntaje final. | | |
| **`metrica_mas_ponderada`** | `str` - La métrica que recibió el mayor peso estratégico. | | |

##### Modificación de la Arquitectura de la API (El Guardián)

| Acción Requerida | Razón | Fuente |
| :--- | :--- | :--- |
| **Actualizar `api/schemas.py`** | La API (Guardían Pydantic) debe ser actualizada para aceptar la nueva complejidad anidada de Q20, que incluye el `z_score_kpi_global` y la lista `contribucion_por_kpi`. | |
| **Crear Modelos Pydantic** | Es **fundamental** definir los esquemas Pydantic para `Q20KpiGlobal` para que el *payload* enriquecido del Orquestador pueda ser validado y almacenado. | |

##### La Forma en que Usa el Output para Visualizarse (Gráfico)

La visualización debe presentar el KPI Global como una herramienta de monitoreo de impacto estratégico en el Frontend (Streamlit/Plotly).

| Gráfico | Tipo de Visualización | Propósito y Cómo se Construye (Plotly/Streamlit) | Fuente |
| :--- | :--- | :--- | :--- |
| **1. KPI Card de Impacto Inmediato** | **Tarjeta Métrica con Z-Score.** | Muestra el `puntaje_final_escalado` y, crucialmente, el **Z-Score del KPI Global**. El color de la tarjeta debe ser condicional (ej. verde si Z-Score es positivo) para una alerta ejecutiva inmediata. | |
| **2. Medidor de Rendimiento** | **Medidor de Aguja (*Gauge Chart*)** | Muestra el `puntaje_final_escalado` en una escala 0-100, con la media del mercado (Q16) marcada como referencia. Esta es la visualización canónica para el KPI Global. | |
| **3. Transparencia del Cálculo** | **Gráfico de Barras de Contribución** | Utiliza la `contribucion_por_kpi` para mostrar visualmente qué *frameworks* (Q11, Q12, Q17) están impulsando o frenando el rendimiento global. Esto resuelve la crítica de la "caja negra". | |
| **4. Panel de Estrategia** | Texto Destacado | Muestra la `metrica_mas_ponderada` (ej. "Crecimiento de Comunidad") para reforzar la alineación con el `primary_business_goal` del cliente. | |

##### Puntos Débiles o Medidas de Contingencia

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Rendimiento Máximo** | Se logra al combinar la **Aguda del Indicador** (magnitud) con el **Gráfico de Contribución** (transparencia) y la **Alerta Z-Score** (contexto competitivo). | |
| **Crítica al Cálculo** | La fiabilidad de la visualización depende de la correcta ponderación de los *frameworks* subyacentes (Q11, Q12, Q17, etc.). | |
| **Metáfora** | La mejora de Q20 lo transforma de un termómetro a un **tablero de control de un coche de Fórmula 1**. Muestra la velocidad general (KPI Global) y detalla el rendimiento del motor (Q11), el combustible (Q13) y la aerodinámica (Q12), permitiendo la optimización componente a componente para ganar la carrera (el *benchmark*). | |