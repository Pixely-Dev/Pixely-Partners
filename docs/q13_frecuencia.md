> Nota (modo single-client): Documento adaptado al modo "single-client" — las comparativas de frecuencia se realizan contra baselines internos o valores objetivo del cliente y no contra datos de competidores externos.

Por supuesto. Procederemos con el análisis estructurado de **Q13: Frecuencia de Publicación**, siguiendo el formato riguroso de sus fuentes y centrándonos en el **Máximo Rendimiento** mediante el **Diagnóstico de Eficiencia** y la **Contextualización (baseline interno)**.

El Q13 es un *framework* **cuantitativo** crucial que migra de un simple promedio descriptivo a una herramienta de diagnóstico de optimización de calendario.

---

## Análisis Estructurado de Q13: Frecuencia de Publicación

##### Objetivo

El objetivo de Q13 (`q13_frecuencia_publicacion`) es determinar el ritmo y la cadencia con la que la marca publica contenido. Para extraer el **Máximo Rendimiento**, debemos transformarla en una **herramienta de diagnóstico de eficiencia y contexto competitivo**:

1.  Calcular la frecuencia promedio segmentada **por cada red social** (publicaciones por día o semana).
2.  Cuantificar la **Consistencia** del ritmo de publicación (usando la desviación estándar).
3.  Integrar el análisis con **Q16 (Benchmark Competitivo)** para reportar el **Z-Score** de la frecuencia del cliente, contextualizando su ritmo frente al promedio del mercado.

##### Prompt Literal Completo

**Q13 no utiliza un *prompt* literal dirigido al modelo de IA (LLM)**. Es un análisis **cuantitativo** ejecutado por el *Orquestador* utilizando las librerías **Pandas/Python**.

La **Lógica de Cálculo (Python/Pandas)** se implementa en el módulo `q13_frecuencia_publicacion.py` (implícito):
1.  **Segmentación por Red Social:** Utilizar Pandas para agrupar las publicaciones (`posts_df`) por la columna `social_network` y calcular la frecuencia promedio (publicaciones/día) para cada red (Instagram, TikTok, etc.).
2.  **Cálculo de Consistencia:** Calcular la **desviación estándar de la frecuencia diaria**. Una desviación estándar alta indica inconsistencia en el ritmo de publicación.
3.  **Preparación para Benchmark (Q16):** Asumiendo que los datos de la media ($\mu$) y la desviación estándar ($\sigma$) de los competidores ya fueron calculados por **Q16**, calcular el **Z-Score de Frecuencia** para el cliente.

##### Crítica al Cálculo

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Punto Fuerte (Funcionalidad)** | La **segmentación por red social** permite optimizar la planificación de recursos. El **Z-Score** proporciona contexto inmediato, permitiendo saber si el cliente es lento o agresivo en su ritmo frente al mercado. | |
| **Punto Débil (Metodología)** | La **Consistencia** (desviación estándar) es una métrica crucial añadida. Un alto promedio de publicación, pero una alta desviación, indica ineficiencia operativa o picos de trabajo erráticos. | |
| **Dependencia Crítica** | El máximo rendimiento de Q13 **depende enteramente** de la implementación funcional de **Q16 (Benchmark Competitivo)** para obtener la media y desviación estándar de los competidores. | |

##### Outputs

El *output* JSON debe ser una **estructura cuantificada y anidada** que refleje la segmentación y el contexto competitivo, alineándose con el esquema Pydantic **`Q13FrecuenciaPublicacion`**.

| Clave del JSON | Estructura Esperada | Requisito de Pydantic (Guardían) | Fuente |
| :--- | :--- | :--- | :--- |
| **`posts_por_dia_promedio_global`** | `float` - La frecuencia general del cliente. | | |
| **`frecuencia_por_red`** | `List[Dict]` - Lista que contiene `social_network` y la frecuencia (posts/día) asociada. | **CRÍTICO:** `api/schemas.py` debe tener modelos para esta estructura. | |
| **`consistencia_desviacion`** | `float` - Desviación estándar de la frecuencia diaria. | | |
| **`benchmark_comparativo`** | `Dict` - Objeto que incluye el **`z_score_frecuencia`** y la media competitiva (asumiendo datos de Q16). | | |

##### Modificación de la Arquitectura de la API (El Guardián)

| Acción Requerida | Razón | Fuente |
| :--- | :--- | :--- |
| **Actualizar `api/schemas.py`** | La API (Guardían Pydantic) debe ser modificada para aceptar la nueva estructura anidada y cuantificada de Q13, incluyendo los campos `frecuencia_por_red`, `consistencia_desviacion` y `z_score_frecuencia`. | |
| **Crear Modelos Pydantic** | Es necesario crear y/o modificar los modelos Pydantic (`Q13FrecuenciaPublicacion`) para validar estos nuevos campos cuantificables. Si los esquemas no se actualizan, el *payload* enviado por el Orquestador será rechazado. | |

##### La Forma en que Usa el Output para Visualizarse (Gráfico)

La visualización debe convertir los datos numéricos en una herramienta de optimización de calendario de contenido.

| Gráfico | Tipo de Visualización | Propósito y Cómo se Construye (Plotly/Streamlit) | Fuente |
| :--- | :--- | :--- | :--- |
| **1. Diagnóstico KPI** | **Card Métrica con Z-Score.** | Muestra `posts_por_dia_promedio_global` y el **Z-Score de Frecuencia** asociado. El color del *card* indica si el cliente está por encima o por debajo del ritmo promedio del mercado. | |
| **2. Desempeño Competitivo** | **Gráfico de Barras Agrupadas.** | Compara la frecuencia promedio del cliente con la **frecuencia media de los competidores**, segmentado por `social_network`. Esto es vital para identificar brechas de ritmo específicas. | |
| **3. Consistencia y Distribución** | **Histograma de Frecuencia Semanal/Diaria.** | Muestra el recuento de publicaciones por día de la semana o por hora, permitiendo visualizar si la publicación es errática o consistente (respaldado por la métrica `consistencia_desviacion`). | |
| **4. Correlación de Eficiencia (Q11 & Q13)** | **Scatter Plot (Correlación).** | Trazar la **Frecuencia (Eje X)** contra el **Engagement Rate (Q11) (Eje Y)**. Esto ayuda a diagnosticar si la alta frecuencia genera *engagement* o si el público se satura. | |

##### Puntos Débiles o Medidas de Contingencia

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Rendimiento Máximo** | Se logra al integrar Q13 con Q11 y Q16. Sin el **Benchmark Competitivo (Q16)**, la métrica de frecuencia carece de contexto estratégico. | |
| **Crítica a la Visualización** | La visualización mediante el *Scatter Plot* (Gráfico 4) es esencial para validar si la frecuencia es eficiente o si solo estamos "generando más trabajo sin impacto". | |
| **Metáfora** | La mejora de Q13 es como usar un **temporizador de cocina con una alarma de eficiencia**. Compara la velocidad del cliente con la receta estándar (Benchmark Competitivo) y avisa si está siendo demasiado rápido o inconsistente (desviación), lo cual puede arruinar el producto final (Engagement Rate). | |