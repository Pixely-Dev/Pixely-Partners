> Nota (modo single-client): Documento adaptado al modo "single-client" — la evaluación de formatos y la validación estadística se realizan sobre datos del cliente y, cuando aplique, se contrastan con ventanas históricas del propio cliente en vez de con comparativas de competidores.

Continuando con la estructuración de los *frameworks* cuantitativos de Máximo Rendimiento, a continuación, se presenta el análisis detallado de **Q14: Efectividad de Formatos**, utilizando el formato riguroso de sus fuentes y centrándose en la **normalización** de la métrica y la validación por **prueba estadística ANOVA**.

El objetivo de Q14 es pasar de un simple ranking por conteo a una **recomendación de inversión de contenido respaldada por la ciencia de datos** (baseline interno o ventanas históricas del cliente).

---

## Análisis Estructurado de Q14: Efectividad de Formatos

##### Objetivo

El objetivo de Q14 (`q14_efectividad_formatos`) es identificar qué tipos de contenido (`content_type`) generan el mejor rendimiento en la audiencia. Para extraer el **Máximo Rendimiento**, debemos transformarla en un **Diagnóstico de Eficiencia de Contenido**:

1.  Corregir la base de cálculo, migrando de *engagement* bruto a **Engagement Rate (ER) normalizado** por alcance.
2.  Implementar el **Análisis de Varianza (ANOVA)** para validar la **significancia estadística** de la diferencia de rendimiento entre formatos.
3.  Generar el *ranking* de eficiencia segmentado **por cada red social** (`social_network`).

##### Prompt Literal Completo

**Q14 no utiliza un *prompt* literal dirigido al modelo de IA (LLM)**. Es un análisis **cuantitativo** ejecutado por el *Orquestador* utilizando las librerías **Pandas/Python** y librerías estadísticas (como `scipy.stats` o `statsmodels`).

La **Lógica de Cálculo (Python/Pandas)** se implementa en el módulo `q14_efectividad_formatos.py` (implícito):

1.  **Normalización de la Métrica (Eficiencia):** Calcular el Engagement Rate normalizado: $ER = \frac{Likes + Comentarios}{Vistas\ o\ Impresiones} \times 100$.
2.  **Prueba Estadística (ANOVA):** Aplicar el **Análisis de Varianza (ANOVA)** para comparar el ER entre los diferentes tipos de `content_type`. El *output* debe reportar un **valor P** (`p_value`) para confirmar si las diferencias de rendimiento son estadísticamente significativas.
3.  **Segmentación por Canal:** El *ranking* debe calcularse de manera segmentada para **cada** `social_network` (ej., Instagram, TikTok), ya que la efectividad de un formato varía por plataforma.

##### Crítica al Cálculo

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Punto Fuerte (Funcionalidad)** | La implementación del **ER normalizado** resuelve el problema de la métrica bruta. La **prueba ANOVA** proporciona **confianza estadística**, transformando una sugerencia en una recomendación de inversión respaldada por la ciencia de datos. | |
| **Punto Débil (Metodología)** | Requiere que los datos de entrada (`SocialMediaPost`) contengan el campo `views` o `impresiones` para que la normalización sea posible. | |
| **Modularidad** | La lógica de Q14 está aislada en su propio módulo (`q14_formatos.py`), lo que garantiza que si el cálculo estadístico falla, no detiene otros análisis (ej., Q15 o Q16). | |

##### Outputs

El *output* JSON debe ser una **estructura cuantificada, anidada y segmentada** para incluir la significancia estadística, alineándose con el esquema Pydantic **`Q14EfectividadFormatos`**.

| Clave del JSON | Estructura Esperada | Requisito de Pydantic (Guardían) | Fuente |
| :--- | :--- | :--- | :--- |
| **`ranking_global`** | `List[Dict]` - El *ranking* general de formatos con `er_promedio` y `p_value`. | | |
| **`ranking_por_red_social`** | `List[Dict]` - El *ranking* segmentado por `social_network`. | **CRÍTICO:** `api/schemas.py` debe tener modelos (`Q14RankingItem`, `Q14RankingPorRed`) para validar esta estructura anidada. | |
| **`p_value_general_anova`** | `float` - Valor P general para la prueba ANOVA sobre todos los formatos. | | |

##### Modificación de la Arquitectura de la API (El Guardián)

| Acción Requerida | Razón | Fuente |
| :--- | :--- | :--- |
| **Actualizar `api/schemas.py`** | La API (Guardían Pydantic) debe ser modificada para aceptar la nueva estructura JSON de Q14, incluyendo los campos anidados (`ranking_por_red_social`) y las métricas estadísticas (`p_value`, `significancia_vs_siguiente`). | |
| **Crear Modelos Pydantic** | Es **crucial** que los esquemas se actualicen (ej., `Q14EfectividadFormatos`, `Q14RankingItem`) porque si no se modifica la "forma" de los datos esperada, el *payload* enriquecido enviado por el Orquestador será **rechazado** por la API. | |

##### La Forma en que Usa el Output para Visualizarse (Gráfico)

La visualización debe destacar la jerarquía de eficiencia y la confianza estadística para el ejecutivo.

| Gráfico | Tipo de Visualización | Propósito y Cómo se Construye (Plotly/Streamlit) | Fuente |
| :--- | :--- | :--- | :--- |
| **1. Ranking de Eficiencia** | **Gráfico de Barras Horizontal.** | Muestra el `er_promedio` normalizado de cada formato. | |
| **2. Significancia Estadística** | **Anotaciones / Iconos de ANOVA.** | Se utilizan los `p_value` y la `significancia_vs_siguiente` para añadir marcadores visuales (ej., *badges* o colores) a las barras. Si la diferencia de rendimiento es estadísticamente significativa, se debe resaltar ("Líder Comprobado"). | |
| **3. Segmentación Dinámica** | **Selector de Red Social.** | Un *widget* de **Streamlit** (`st.selectbox`) permite al usuario filtrar el ranking de eficiencia por `social_network` (ej. "Instagram" vs. "TikTok") utilizando los datos de `ranking_por_red_social`. | |

##### Puntos Débiles o Medidas de Contingencia

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Rendimiento Máximo** | Se logra al validar la eficiencia (ER normalizado) con **pruebas estadísticas (ANOVA)**. Esto permite al equipo de marketing tomar decisiones de inversión con un respaldo de datos sólido. | |
| **Crítica de la Visualización** | La visualización de Q14 debe **evitar** mostrar solo el *ranking* de interacción bruta. El enfoque debe estar en el **ER normalizado** y la **Significancia Estadística**. | |
| **Dependencia** | El cálculo depende de la disponibilidad de los datos de `views` o `impresiones` en la tabla `SocialMediaPost`. | |