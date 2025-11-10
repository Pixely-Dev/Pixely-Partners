Continuando con la estructuración de los *frameworks* cuantitativos de Máximo Rendimiento, a continuación, se presenta el análisis detallado de **Q15: Hashtags Efectivos**, utilizando el formato riguroso de sus fuentes y centrándose en la **normalización** de la métrica y la **contextualización semántica**.

El objetivo de Q15 es migrar de un simple conteo a un **Análisis de Rentabilidad Semántica**.

---

## Análisis Estructurado de Q15: Hashtags Efectivos

##### Objetivo

El objetivo de Q15 (`q15_hashtags_efectivos`) es identificar los *hashtags* que generan la interacción más valiosa. Para extraer el **Máximo Rendimiento**, debemos transformarla en una métrica de **Rentabilidad Semántica**:

1.  **Normalización de Eficiencia:** El *ranking* debe basarse en el **Engagement Rate (ER) normalizado** (interacción / alcance), no en el *engagement* bruto, para clasificar *hashtags* que son genuinamente eficientes.
2.  **Contextualización Semántica:** Correlacionar cada *hashtag* con el **Sentimiento Agregado (Q17)** y el **Tópico Principal (Q3)** asociado. Esto justifica *por qué* son efectivos (si impulsan conversación positiva o controversia negativa).
3.  **Filtrado de Ruido:** Implementar un **umbral mínimo de uso** (ej., debe aparecer en al menos 5 publicaciones) para evitar que *hashtags* usados una sola vez inflen falsamente el promedio.

##### Prompt Literal Completo

**Q15 no utiliza un *prompt* literal dirigido al modelo de IA (LLM)**. Es un análisis **cuantitativo** ejecutado por el *Orquestador* utilizando las librerías **Pandas/Python**.

La **Lógica de Cálculo (Python/Pandas)** se implementa en el módulo `q15_hashtags_efectivos.py` (implícito):
1.  **Cálculo Normalizado:** Utilizar Pandas para calcular el ER normalizado para cada *hashtag* (interacción dividida por `views` o `impresiones`).
2.  **Filtrado:** Aplicar un umbral mínimo de uso (ej., 5 publicaciones).
3.  **Correlación Semántica:** Para los *hashtags* clasificados como eficientes, se debe agregar el **Sentimiento Agregado (Q17)** y el **Tópico Principal (Q3)** asociado a las publicaciones donde aparece. Esto requiere la integración con los *insights* cualitativos previamente calculados.

##### Crítica al Cálculo

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Punto Fuerte (Funcionalidad)** | La **normalización por alcance** resuelve el problema de la métrica bruta. La **contextualización semántica** (Tópico y Sentimiento) justifica la rentabilidad del *hashtag*. | |
| **Punto Débil (Metodología)** | Requiere que la tabla `SocialMediaPost` contenga el campo `views` o `impresiones` para la normalización. Además, requiere que Q3 y Q17 hayan sido calculados previamente para la correlación semántica. | |
| **Mitigación de Errores** | El filtrado de ruido por umbral mínimo es clave para evitar *outliers* falsos que podrían dominar el *ranking*. | |

##### Outputs

El *output* JSON debe ser una **estructura cuantificada, anidada y semánticamente enriquecida**, alineándose con el esquema Pydantic **`Q15HashtagsEfectivos`**.

| Clave del JSON | Estructura Esperada | Requisito de Pydantic (Guardían) | Fuente |
| :--- | :--- | :--- | :--- |
| **`ranking_hashtags_eficientes`** | `List[Dict]` - Lista de *hashtags* rankeados. Cada objeto incluye `hashtag`, **`er_normalizado`**, **`sentimiento_asociado`** (Q17) y **`topico_dominante`** (Q3). | **CRÍTICO:** `api/schemas.py` debe tener modelos (`Q15HashtagRankingItem`) que definan esta estructura anidada y compleja. | |

##### Modificación de la Arquitectura de la API (El Guardián)

| Acción Requerida | Razón | Fuente |
| :--- | :--- | :--- |
| **Actualizar `api/schemas.py`** | La API (Guardían Pydantic) debe ser modificada para aceptar la estructura anidada de Q15, incluyendo la métrica normalizada y los campos de texto (`sentimiento_asociado`, `topico_dominante`). | |
| **Crear Modelos Pydantic** | Se necesita el modelo `Q15HashtagsEfectivos` (implícito) y `Q15HashtagRankingItem` para validar la lista anidada. Sin esta modificación, el *payload* enriquecido será rechazado. | |

##### La Forma en que Usa el Output para Visualizarse (Gráfico)

La visualización debe destacar la **rentabilidad** y la **naturaleza semántica** de la interacción en el Frontend (Streamlit).

| Gráfico | Tipo de Visualización | Propósito y Cómo se Construye (Plotly/Streamlit) | Fuente |
| :--- | :--- | :--- | :--- |
| **1. Ranking de Eficiencia** | **Gráfico de Barras** | Muestra el **ER normalizado** (Eje Y) para los Top 10 *hashtags*, resolviendo el punto débil de la métrica bruta. | |
| **2. Contexto Semántico** | **Coloración Condicional de Barras** | Las barras se deben **colorear** según el `sentimiento_asociado` (Q17). Por ejemplo, verde si el *hashtag* impulsa interacción positiva, y rojo si está asociado a quejas o controversia (Negativo/Mixto). | |
| **3. Nube de Palabras Semántica** | **Word Cloud (Optimizado)** | La nube de palabras se construye donde el **tamaño** del *hashtag* se basa en su **ER promedio (eficiencia)**, en lugar de solo su frecuencia de uso. | |
| **4. Detalle de Tópico** | **Tooltip Interactivo** | Al pasar el cursor sobre una barra, un *tooltip* debe mostrar el **`topico_dominante`** (Q3) y el porcentaje exacto de polaridad (Q17), integrando la inteligencia cualitativa con el *ranking* cuantitativo. | |

##### Puntos Débiles o Medidas de Contingencia

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Rendimiento Máximo** | Se obtiene al obligar al Orquestador a la **normalización** por alcance y a la **integración semántica** (Q3/Q17), lo que permite al ejecutivo tomar decisiones basadas en el ROI de la palabra clave. | |
| **Crítica de la Visualización** | La visualización de barras coloreadas por sentimiento (Gráfico 2) es esencial para que el ejecutivo vea rápidamente **qué tipo de conversación** se está impulsando. | |
| **Analogía** | La mejora convierte al Q15 de un simple contador de votos a un **Cálculo de Rentabilidad de Inversión (ROI)**: no solo dice qué *hashtag* se usó mucho, sino cuál generó la interacción más valiosa por impresión, y si esa interacción fue la que la marca realmente quería. | |