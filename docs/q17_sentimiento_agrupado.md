Por supuesto. Procederemos con el análisis estructurado de **Q17: Sentimiento Agrupado (Polaridad Avanzada y NSS)**, siguiendo el formato riguroso de sus fuentes y centrándonos en el **Máximo Rendimiento** mediante la implementación del **Net Sentiment Score (NSS)**, el análisis de **series temporales** y la **contextualización competitiva (Z-Score)**.

El Q17 es un *framework* **cuantitativo** crucial que agrupa los resultados del análisis de sentimiento de los comentarios y debe integrarse fuertemente con **Q16 (Benchmark Competitivo)** para ser estratégico.

---

## Análisis Estructurado de Q17: Sentimiento Agrupado

##### Objetivo

El objetivo de Q17 (`q17_sentimiento_agrupado`) es proveer una visión consolidada de la polaridad del discurso del público (Positivo, Negativo, Neutro). Para alcanzar el **Máximo Rendimiento**, debemos evolucionar la métrica de una simple distribución porcentual estática a una **herramienta de Diagnóstico de Polaridad Temporal y Competitiva**.

1.  Implementar el **Net Sentiment Score (NSS)**: NSS = % Positivo - % Negativo.
2.  Generar una **serie temporal** del NSS (por día o semana) para rastrear tendencias.
3.  Integrar el análisis con **Q16 (Benchmark Competitivo)** para calcular el **Z-Score** de la polaridad del cliente frente al promedio del mercado.

##### Prompt Literal Completo

**Q17 no utiliza un *prompt* literal dirigido al modelo de IA (LLM)**. Es un análisis **cuantitativo** ejecutado por el *Orquestador* utilizando las librerías **Pandas/Python**.

La **Lógica de Cálculo (Python/Pandas)** se implementa en el módulo `q17_sentimiento_agrupado.py` (implícito), agrupando datos de sentimiento preclasificados:

| Lógica | Descripción | Fuente |
| :--- | :--- | :--- |
| **Cálculo del Net Sentiment Score (NSS)** | Implementar la fórmula NSS = Porcentaje Positivo - Porcentaje Negativo. | |
| **Serie Temporal NSS** | Generar una serie de tiempo del NSS (por día o semana) para visualizar la evolución de la polaridad a lo largo del tiempo. Esto complementa el análisis cualitativo de Q8. | |
| **Contexto Competitivo (Z-Score)** | Asumiendo que Q16 está implementado, comparar el NSS del cliente con la media ($\mu$) y desviación estándar ($\sigma$) del NSS de los competidores, calculando el **Z-Score** de la polaridad. | |

##### Crítica al Cálculo

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Punto Fuerte (Funcionalidad)** | El **Net Sentiment Score** (NSS) es un KPI ejecutivo simple. La integración del **Z-Score** (Q16) contextualiza inmediatamente la salud emocional de la marca frente a sus rivales. | |
| **Punto Débil (Metodología)** | La precisión del NSS depende enteramente de la precisión de la **clasificación inicial de sentimiento** (la cual puede fallar al detectar sarcasmo, humor, etc.). Si la clasificación es defectuosa, el NSS y su visualización asociada serán engañosos. | |
| **Dependencia Crítica** | El máximo rendimiento de Q17 requiere que **Q16 (Benchmark Competitivo)** haya sido ejecutado para proporcionar la media del NSS de los competidores. | |

##### Outputs

El *output* JSON debe ser una **estructura jerárquica** que cuantifique la polaridad y la tendencia, alineándose con el esquema Pydantic **`Q17SentimientoAgrupadoCompleto`**.

| Clave del JSON | Estructura Esperada | Requisito de Pydantic (Guardían) | Fuente |
| :--- | :--- | :--- | :--- |
| **`distribucion_polaridad`** | `Dict[str, float]` - Porcentajes de Positivo, Negativo, Neutro. | | |
| **`net_sentiment_score`** | `float` - El NSS del cliente. | | |
| **`serie_temporal_nss`** | `List[Dict]` - Serie de tiempo (NSS por semana). | **CRÍTICO:** `api/schemas.py` debe tener modelos que definan esta estructura de lista anidada. | |
| **`benchmark_comparativo`** | `Dict` - Objeto que incluye el **`z_score_nss`** del cliente. | | |

##### Modificación de la Arquitectura de la API (El Guardián)

| Acción Requerida | Razón | Fuente |
| :--- | :--- | :--- |
| **Actualizar `api/schemas.py`** | La API (Guardían Pydantic) debe ser modificada para aceptar la nueva estructura JSON de Q17, que incluye el `net_sentiment_score`, la `serie_temporal_nss` y el **Z-Score**. | |
| **Crear Modelos Pydantic** | Se necesitan nuevos esquemas Pydantic (`Q17SentimientoAgrupadoCompleto`) que definan esta estructura jerárquica para que el *payload* enriquecido del Orquestador pueda ser validado y almacenado. | |

##### La Forma en que Usa el Output para Visualizarse (Gráfico)

La visualización debe migrar de un *snapshot* estático a una herramienta de monitoreo estratégico de la salud emocional de la marca en el Frontend (Streamlit/Plotly).

| Gráfico | Tipo de Visualización | Propósito y Cómo se Construye (Plotly/Streamlit) | Fuente |
| :--- | :--- | :--- | :--- |
| **1. Card KPI de Polaridad (NSS)** | **Tarjeta Métrica con Indicador de Z-Score.** | Muestra el **NSS** del cliente. El color y el indicador deben basarse en el **Z-Score** para mostrar si la polaridad del cliente está por encima o por debajo de la media del mercado. | |
| **2. Tendencia Temporal Comparativa** | **Gráfico de Líneas Superpuesto.** | Utiliza la `serie_temporal_nss` del cliente. Este gráfico debe **superponer** la línea de la **media de NSS de los competidores** (obtenida de Q16). Esto visualiza si la estrategia está cerrando la brecha o si hay riesgo de caída. | |
| **3. Distribución (Contexto)** | **Gráfico Circular/Anillo.** | Mantiene la visualización de la distribución estática (Positivo, Negativo, Neutral) para que el ejecutivo entienda de dónde proviene el NSS (es decir, el volumen de positivos vs. negativos). | |

##### Puntos Débiles o Medidas de Contingencia

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Rendimiento Máximo** | Se logra al combinar la **Card NSS con Z-Score** y el **Gráfico de Líneas temporal comparativo**. Esto transforma la métrica en una herramienta de monitoreo estratégico de la salud emocional. | |
| **Dependencia del Guardián** | La modificación de los esquemas Pydantic en `api/schemas.py` es **obligatoria** para aceptar la nueva complejidad (NSS y serie temporal). | |
| **Metáfora** | La mejora de Q17 es como cambiar un **semáforo** (Gráfico Circular) por un **electrocardiograma conectado a un monitor de bolsa de valores**. Muestra el ritmo histórico del sentimiento y lo compara con el promedio del mercado (Z-Score). | |