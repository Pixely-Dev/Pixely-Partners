> Nota (modo single-client): Documento adaptado al modo "single-client" — Q12 calcula posicionamiento respecto a baselines internos o valores objetivo, en lugar de comparativas con competidores externos.

El análisis de **Q12: Crecimiento/Posicionamiento de Seguidores** es fundamental porque resuelve el estado previo de **"No Implementado"** y transforma la métrica en inteligencia de posicionamiento basada en el historial/objetivos del cliente.

Debido a que los datos de seguidores disponibles ahora se cargan en la **Ficha Cliente** (ej., `seguidores_instagram`, `seguidores_tiktok`, etc.), que es un *snapshot* (conteo actual) y no una serie temporal histórica, el foco del análisis cambia de la *tasa de crecimiento en el tiempo* al **Análisis de Posicionamiento de Comunidad** (baseline interno o target).

A continuación, se presenta el análisis estructurado de Q12, detallando las modificaciones necesarias en las tres capas de la arquitectura para el **Máximo Rendimiento**.

---

## Análisis Estructurado de Q12: Crecimiento/Posicionamiento de Seguidores

##### Objetivo

El objetivo de Q12 (`q12_crecimiento_seguidores`) es determinar el **posicionamiento de la marca** dentro de su mercado en términos de tamaño de comunidad.

1.  **Resolver el estado "No Implementado"** utilizando los nuevos datos de `seguidores_instagram`, `seguidores_tiktok`, etc., de la **Ficha Cliente**.
2.  Evaluar el **tamaño absoluto de la comunidad** del cliente en comparación con sus competidores (integrando **Q16**).
3.  Cuantificar si el tamaño de la comunidad del cliente es un *outlier* positivo o negativo, utilizando el **Z-Score**.

##### Prompt Literal Completo

**Q12 no utiliza un *prompt* literal dirigido al modelo de IA (LLM)**. Es un análisis **cuantitativo** ejecutado por el *Orquestador* utilizando las librerías **Pandas** y la lógica de Python.

La **Lógica de Cálculo (Python/Pandas)** se implementa en el módulo `q12_comunidad.py` (implícito) o dentro del Orquestador:

1.  **Obtener Datos:** El Orquestador debe consumir los conteos de seguidores del cliente y de los competidores (definidos en `competitor_landscape` de la Ficha Cliente).
2.  **Cálculo de Benchmark:** Determinar la media ($\mu$) y la desviación estándar ($\sigma$) del total de seguidores del grupo (cliente + competidores).
3.  **Cálculo de Z-Score de Comunidad:** Aplicar la fórmula $Z = \frac{X - \mu}{\sigma}$, donde $X$ es el número de seguidores del cliente.
4.  **Generación de Ranking:** Producir un *ranking* de tamaño de comunidad por red social.

##### Crítica al Cálculo

| Punto | Descripción | Fuentes |
| :--- | :--- | :--- |
| **Punto Fuerte (Funcionalidad)** | El nuevo *input* en la Ficha Cliente **desbloquea** el análisis, resolviendo el estado de "No Implementado". La implementación del **Z-Score** proporciona contexto competitivo inmediato. | |
| **Punto Débil (Metodología)** | Se pierde la capacidad de evaluar la **evolución en el tiempo** o la **tasa de crecimiento orgánico** (análisis original) al usar solo un dato *snapshot* (conteo actual). | |
| **Dependencia Crítica** | El rendimiento de Q12 depende enteramente de la capacidad del Orquestador para acceder y procesar los datos de seguidores de los competidores, lo que implica una integración funcional con **Q16 (Benchmark Competitivo)**. | |

##### Outputs

El *output* JSON debe ser una **estructura cuantificada** enfocada en el posicionamiento, alineándose con el esquema Pydantic **`Q12PosicionamientoComunidad`**.

| Clave del JSON | Estructura Esperada | Requisito de Pydantic (Guardían) | Fuentes |
| :--- | :--- | :--- | :--- |
| **`total_seguidores_cliente`** | `float` - Conteo total de seguidores. | | |
| **`z_score_tamano_comunidad`** | `float` - La posición del cliente en desviaciones estándar respecto a la media de competidores. | **CRÍTICO:** El esquema `Q12PosicionamientoComunidad` debe validar este campo. | |
| **`ranking_por_red_social`** | `List[Dict]` - Posición del cliente por cada red social. | | |
| **`benchmark_metrics`** | `Dict` - Media ($\mu$) y desviación estándar ($\sigma$) del grupo competitivo. | | |

##### Modificación de la Arquitectura de la API (El Guardián)

| Acción Requerida | Razón | Fuentes |
| :--- | :--- | :--- |
| **Modificación de Modelos ORM** | Los campos `seguidores_instagram`, `seguidores_tiktok` y `seguidores_facebook` fueron añadidos a la tabla **`FichaCliente`** en `models.py` para desbloquear Q12. | |
| **Actualizar `api/schemas.py`** | Los esquemas Pydantic que definen la `FichaCliente` deben actualizarse para incluir y validar los nuevos campos de seguidores. | |
| **Crear Esquema `Q12PosicionamientoComunidad`** | La API (Guardían Pydantic) debe ser modificada para aceptar la estructura cuantificada y anidada de Q12, incluyendo el **Z-Score** y el *ranking*. | |

##### La Forma en que Usa el Output para Visualizarse (Gráfico)

La visualización debe destacar la posición relativa del cliente frente a sus competidores en el Frontend. El módulo de vista (ej. `q12_view.py`) consume el *payload* enriquecido.

| Gráfico | Tipo de Visualización | Propósito y Cómo se Construye (Plotly/Streamlit) | Fuentes |
| :--- | :--- | :--- | :--- |
| **1. KPI Card Contextual** | **Card Métrica con Indicador de Z-Score.** | Muestra la **Posición de Ranking** y el **Z-Score**. El color de la tarjeta (verde/rojo) debe cambiar según el Z-Score (verde si Z-Score > 0, rojo si < 0) para un diagnóstico instantáneo. | |
| **2. Comparativa Segmentada** | **Gráfico de Barras Comparativas.** | Muestra el conteo de seguidores del cliente frente a cada competidor, segmentado por red social, para visualizar inmediatamente la cuota de comunidad. | |
| **3. Mapa de Posicionamiento (Sintético)** | **Gráfico de Radar (*Radar Chart*)** | El máximo rendimiento visual se logra integrando Q12 con otras métricas competitivas (Q11 Engagement, Q13 Frecuencia) para trazar el perfil completo del cliente y sus competidores en una sola visualización. | |

##### Puntos Débiles o Medidas de Contingencia

| Punto | Descripción | Fuentes |
| :--- | :--- | :--- |
| **Punto Débil (Dependencia de Q16)** | El Máximo Rendimiento de Q12 es una métrica de **posicionamiento** y depende de la capacidad del Orquestador para obtener y procesar los datos de los competidores (Q16). | |
| **Garantía de la Visualización** | Es crucial que la visualización **siempre** incluya la tasa de Engagement (Q11), ya que una comunidad pequeña (Q12 bajo) pero de alta calidad (Q11 alto) puede ser malinterpretada si se observa aisladamente. | |
| **Mitigación de Errores** | Al ser un cálculo de **Python/Pandas**, Q12 no está sujeto a fallos de formato JSON de la IA o a errores de autenticación de OpenAI. | |

La mejora transforma a Q12 en un **mapa de cuota de mercado comunitaria**, permitiendo la toma de decisiones estratégicas sobre qué red social priorizar para el crecimiento.