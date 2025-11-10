Silencio. A continuación, se presenta el análisis estructurado de **Q18: Detección de Anomalías**, siguiendo el formato riguroso de las fuentes y centrándose en el **Máximo Rendimiento** mediante el **Diagnóstico de Causalidad de Contenido** y la integración semántica.

El objetivo principal es transformar la detección de *outliers* de un evento estadístico a un diagnóstico de crisis o replicación de éxito, vinculando la anomalía con la causa cualitativa (tópico y sentimiento).

---

## Análisis Estructurado de Q18: Detección de Anomalías

##### Objetivo

El objetivo de Q18 (`q18_deteccion_anomalias`) es identificar publicaciones con un rendimiento excepcionalmente alto o bajo (es decir, *outliers* o anomalías). Para alcanzar el **Máximo Rendimiento**, la métrica debe ser enriquecida con el **contexto de causalidad**:

1.  Basar la detección en la **Eficiencia** (Engagement Rate normalizado) en lugar de conteos brutos.
2.  Para cada anomalía detectada, adjuntar el **Tópico Dominante (Q3)** y el **Sentimiento Detallado (Q7)** de los comentarios asociados.
3.  Clasificar la anomalía automáticamente como **"Viral Positivo"** o **"Crisis/Riesgo"**.

##### Prompt Literal Completo

**Q18 no utiliza un *prompt* literal dirigido al modelo de IA (LLM)**. Es un análisis **cuantitativo** ejecutado por el *Orquestador* utilizando las librerías **Pandas/Python** y lógica estadística (ej., Z-Score).

La **Lógica de Cálculo (Python/Pandas)** se implementa en el módulo `q18_deteccion_anomalias.py` (implícito):

| Lógica | Descripción | Fuente |
| :--- | :--- | :--- |
| **Detección Basada en Eficiencia** | El *outlier* se detecta sobre el **Engagement Rate normalizado** (interacción / alcance o vistas), en lugar de conteos brutos, para asegurar que la "viralidad" sea genuinamente eficiente y no solo el resultado de inversión publicitaria (`is_sponsored`). | |
| **Cálculo de Causalidad** | Para los *outliers* detectados (ej., Z-Score > 3 o < -2), el módulo debe buscar los *insights* cualitativos de esa publicación (Q3 y Q7) y adjuntar el **Tópico Dominante (Q3)** y el **Sentimiento Detallado (Q7)** asociado a los comentarios. | |
| **Clasificación Automática** | Clasificar la anomalía como **"Viral Positivo"** (si Z-Score alto + Sentimiento Positivo/Neutro) o **"Crisis/Riesgo"** (si Z-Score alto o bajo + Sentimiento Negativo/Mixto). | |

##### Crítica al Cálculo

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Punto Fuerte (Funcionalidad)** | La integración de la detección estadística con el **contexto semántico (Q3 y Q7)** proporciona el diagnóstico de causalidad, esencial para la replicación de contenido exitoso. | |
| **Punto Débil (Metodología)** | La efectividad del análisis de causalidad depende directamente de la precisión del análisis semántico (Q3/Q7). Si la clasificación de tópicos o sentimientos falla, la explicación de la anomalía será errónea. | |
| **Modularidad** | La lógica de Q18 debe ser capaz de consumir los *outputs* de Q3 (Tópicos) y Q7 (Sentimiento Detallado). | |

##### Outputs

El *output* JSON debe ser una **estructura anidada** que contenga la explicación semántica, alineándose con el esquema Pydantic **`Q18DeteccionAnomaliasCompleto`**.

| Clave del JSON | Estructura Esperada | Requisito de Pydantic (Guardían) | Fuente |
| :--- | :--- | :--- | :--- |
| **`anomalias_detectadas`** | `List[Dict]` - Lista de los *outliers* identificados. | | |
| **`contexto_semantico`** | `Dict` - Anidado dentro de cada anomalía. Incluye `topico_dominante` (Q3) y `sentimiento_agregado` (Q7). | **CRÍTICO:** `api/schemas.py` debe validar esta estructura anidada. | |
| **`clasificacion_anomalia`** | `str` - Clasificación automática (ej. "Viral Positivo", "Crisis/Riesgo"). | | |

##### Modificación de la Arquitectura de la API (El Guardián)

| Acción Requerida | Razón | Fuente |
| :--- | :--- | :--- |
| **Actualizar `api/schemas.py`** | El *payload* JSON de Q18 incluye un **objeto anidado** (`contexto_semantico`) y campos como `clasificacion_anomalia` que son nuevos. Los esquemas Pydantic deben ser modificados (ej., `Q18DeteccionAnomaliasCompleto`) para aceptar esta complejidad. | |
| **Validación** | La API actúa como **Guardían**. Si los esquemas no se modifican, el Orquestador fallará al intentar almacenar el *insight* en la base de datos. | |

##### La Forma en que Usa el Output para Visualizarse (Gráfico)

La visualización debe pasar de un análisis de puntos estático a un **panel de diagnóstico interactivo** en el Frontend (Streamlit/Plotly).

| Gráfico | Tipo de Visualización | Propósito y Cómo se Construye (Plotly/Streamlit) | Fuente |
| :--- | :--- | :--- | :--- |
| **1. Mapa de Rendimiento** | **Gráfico de Dispersión (*Scatter Plot*)** | Muestra la distribución del rendimiento (ej. ER normalizado en Eje Y) para identificar visualmente los *outliers*. | |
| **2. Alerta Visual Reforzada** | **Highlighting Dinámico (Puntos Condicionales)** | Los *outliers* se trazan con puntos de mayor tamaño y **colores condicionales**: **Verde** (Viralidad Positiva) o **Rojo/Naranja** (Crisis/Riesgo). | |
| **3. Diagnóstico de Causalidad** | **Tooltip Integrado** | Al pasar el cursor sobre un punto anómalo, el *tooltip* (función de Plotly) debe mostrar la **clasificación de la anomalía**, el **Tópico Dominante (Q3)** y el **Sentimiento Agregado (Q7)**. Esto integra análisis cuantitativo y cualitativo en un punto de interacción. | |
| **4. Panel Ejecutivo de Alertas** | **Lista de Alertas Prioritarias** | Un panel de Streamlit que enumere los Top 3 *outliers*, mostrando la URL y la clasificación inmediata ("Viralidad Positiva por Tópico de Sostenibilidad"). | |

##### Puntos Débiles o Medidas de Contingencia

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Rendimiento Máximo** | Se logra mediante la integración semántica (Gráfico 3), la cual proporciona al ejecutivo la **narrativa detrás del pico**. | |
| **Dependencia** | El cálculo depende de la detección previa de tópicos y sentimiento (Q3 y Q7) para el enriquecimiento del contexto. | |
| **Metáfora** | La mejora convierte al Q18 en un **detector de oro inteligente** que no solo identifica el metal (interacción inusual) sino que inmediatamente te dice qué tipo de metal es (oro o chatarra) y cuál fue la **veta de contenido** que lo produjo (Tópico Dominante). | |