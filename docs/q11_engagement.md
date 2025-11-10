> Nota (modo single-client): Este documento está adaptado al modo "single-client" — los cálculos de benchmarking y Z-Scores se realizan respecto a baselines internos (histórico del cliente o targets) y no contra competidores externos.

Por supuesto. Procederemos con el análisis estructurado de **Q11: Engagement General**, siguiendo el formato riguroso de sus fuentes y centrándose en la **cuantificación contextual** mediante el **Z-Score** y la segmentación por red social.

El Q11 es un *framework* **cuantitativo** crucial que, en modo single-client, se integra con **Q16 (Benchmark Interno)** para proporcionar Máximo Rendimiento a partir del histórico del cliente.

---

## Análisis Estructurado de Q11: Engagement General

##### Objetivo

El objetivo de Q11 (`q11_engagement_general`) es determinar la tasa de interacción de la audiencia con el contenido de la marca. Para extraer el **Máximo Rendimiento**, debemos transformar esta métrica de un KPI aislado a un **contexto comparativo y segmentado**.

1.  Calcular el Engagement Rate (ER) promedio segmentado **por cada red social** presente en los datos.
2.  Generar una **serie temporal** del ER para rastrear su evolución.
3.  Integrar el análisis con **Q16 (Benchmark Competitivo)** para reportar el **Z-Score** del cliente, contextualizando su rendimiento frente al promedio del mercado.

##### Prompt Literal Completo

**Q11 no utiliza un *prompt* literal dirigido al modelo de IA (LLM)**. Es un análisis **cuantitativo** ejecutado por el *Orquestador* utilizando las librerías **Pandas/Python**.

La **Lógica de Cálculo (Python/Pandas)** se implementa en el módulo `q11_engagement_general.py` (dentro de la lógica del Orquestador):
1.  Utilizar Pandas para calcular el Engagement Rate (ER) promedio para cada `social_network` presente en el *DataFrame* de publicaciones.
2.  Generar una serie temporal de ER (por semana).
3.  Asumiendo que los datos de la media ($\mu$) y la desviación estándar ($\sigma$) de los competidores ya fueron calculados por **Q16**, calcular el **Z-Score de Engagement** para el cliente.

##### Crítica al Cálculo

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Punto Fuerte (Funcionalidad)** | La **segmentación por red social** permite la asignación de recursos. El **Z-Score** proporciona contexto inmediato, resolviendo el problema del KPI aislado. | |
| **Punto Débil (Metodología)** | El máximo rendimiento de Q11 **depende enteramente** de la implementación funcional de **Q16 (Benchmark Competitivo)**. Sin la media y desviación estándar de los competidores, el Z-Score no se puede calcular. | |
| **Mitigación de Errores** | Al ser un cálculo nativo de Python/Pandas, Q11 no está sujeto a fallos de formato JSON de la IA o a errores de autenticación de OpenAI. | |

##### Outputs

El *output* JSON debe ser una **estructura cuantificada y anidada** que permita la visualización segmentada y contextual, alineándose con el esquema Pydantic **`Q11EngagementGeneral`**.

| Clave del JSON | Estructura Esperada | Requisito de Pydantic (Guardían) |
| :--- | :--- | :--- |
| **`engagement_global_promedio`** | `float` - El ER general del cliente. | |
| **`engagement_segmentado_red`** | `List[Dict]` - Lista de objetos que contiene `social_network` y el ER asociado. | |
| **`serie_temporal_er`** | `List[Dict]` - Serie temporal semanal del ER. | |
| **`benchmark_comparativo`** | `Dict` - Objeto que incluye el **`z_score_er`** y la media competitiva (asumiendo datos de Q16). | |

##### Modificación de la Arquitectura de la API (El Guardián)

| Acción Requerida | Razón | Fuente |
| :--- | :--- | :--- |
| **Actualizar `api/schemas.py`** | La API (Guardían Pydantic) debe ser modificada para aceptar la nueva estructura anidada de Q11, incluyendo los campos `engagement_segmentado_red`, `serie_temporal_er` y `benchmark_comparativo`. | |
| **Crear Modelos Pydantic** | Se deben crear y/o modificar los modelos para validar estos nuevos campos cuantificables. Si los esquemas no se actualizan, el *payload* enviado por el Orquestador será rechazado. | |

##### La Forma en que Usa el Output para Visualizarse (Gráfico)

La visualización debe pasar de una métrica aislada a un contexto competitivo y de diagnóstico en el Frontend (Streamlit).

| Gráfico | Tipo de Visualización | Propósito y Cómo se Construye (Plotly/Streamlit) |
| :--- | :--- | :--- |
| **1. KPI Global Contextual** | **Card Métrica con Indicador de Z-Score.** | Muestra el `engagement_global_promedio`. Incluye un icono (flecha verde/roja) y el valor del `z_score_er` para dar contexto inmediato sobre el rendimiento frente a la competencia (Q16). |
| **2. Comparativa Segmentada** | **Gráfico de Barras Agrupadas.** | Utiliza `engagement_segmentado_red` para mostrar el ER del cliente en cada red social. Se superpone una barra que muestre el **promedio de la competencia** para esa red, lo que es vital para la asignación de recursos. |
| **3. Evolución del ER** | **Gráfico de Líneas Temporal.** | Trazar el `serie_temporal_er`. Es crucial superponer la línea del **promedio de la competencia** para ver si la brecha está aumentando o disminuyendo. |
| **4. Mapa de Posicionamiento Competitivo (Sintético)** | **Gráfico de Radar (Gráfico de Araña).** | Aunque la estructura del *output* de Q11 es lineal, el *frontend* debe usar el *insight* de **Q16 (Benchmark)** para trazar el ER del cliente y los competidores en un gráfico de radar junto con otras métricas clave (Q12, Q13), proporcionando un mapa de posicionamiento holístico. |

##### Puntos Débiles o Medidas de Contingencia

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Rendimiento Máximo** | Se logra únicamente al integrar Q11 con la información de **Q16 (Benchmark Competitivo)**. Sin la comparación de competidores, Q11 pierde su valor estratégico. | |
| **Crítica a la Visualización** | El uso de **Z-Scores** y **Barras Agrupadas por Red Social/Competidor** convierte la métrica en una herramienta diagnóstica que indica *dónde* está ganando o perdiendo el cliente contra su mercado. | |
| **Metáfora** | La mejora del Q11 es como transformar un **termómetro** (que solo mide tu temperatura) en una **tabla de crecimiento pediátrica** (que te dice si esa temperatura es normal, comparada con el promedio del mercado y la tendencia histórica). | |