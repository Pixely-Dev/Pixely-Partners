Continuando con la refactorización de los *frameworks* cuantitativos, a continuación, se presenta el análisis estructurado de **Q16: Benchmark Competitivo**, siguiendo el formato riguroso de las fuentes.

Q16 es un componente **crítico y estratégico** para el proyecto Pixely, ya que su implementación desbloquea el **Máximo Rendimiento** para múltiples Qs cuantitativas (Q11, Q12, Q13, Q17, Q20), las cuales dependen de la contextualización que proporciona el *benchmark*.

---

## Análisis Estructurado de Q16: Benchmark Competitivo

##### Objetivo

El objetivo de Q16 (`q16_benchmark_competitivo`), actualmente marcado como **"No Implementado"**, es transformar los KPIs absolutos del cliente en inteligencia de mercado contextual. Para extraer el **Máximo Rendimiento**, se debe:

1.  Asegurar la **ingesta de datos** de las publicaciones y métricas de los 4 competidores listados en la **Ficha Cliente**.
2.  Implementar el cálculo de la **posición relativa** del cliente utilizando el **Z-Score** para los KPIs clave (Engagement Rate, Frecuencia, Comunidad).
3.  Generar una **matriz de comparación** que el *frontend* pueda consumir para crear un **Mapa de Posicionamiento**.

##### Prompt Literal Completo

**Q16 no utiliza un *prompt* literal dirigido al modelo de IA (LLM)**. Es un análisis **cuantitativo** ejecutado por el *Orquestador* utilizando las librerías **Pandas/Python**.

La **Lógica de Cálculo (Python/Pandas)** se implementa en el módulo `q16_benchmark_competitivo.py` (implícito):

| Lógica | Descripción | Fuente |
| :--- | :--- | :--- |
| **Implementación de Datos** | El Orquestador debe asegurar el acceso a los datos de publicaciones y comentarios de los 4 competidores listados en la Ficha Cliente. | |
| **Cálculo de la Media Competitiva** | Determinar la media ($\mu$) y la desviación estándar ($\sigma$) de los KPIs clave (Q11 ER, Q12 Comunidad, Q13 Frecuencia, Q17 NSS) utilizando los datos de **todos** los perfiles (cliente + competidores). | |
| **Cálculo del Z-Score** | Aplicar la fórmula $Z = \frac{X - \mu}{\sigma}$ al rendimiento del cliente ($X$) para cada KPI. Esto proporciona el contexto competitivo para Q11, Q12, Q13, Q17 y Q20. | |
| **Benchmark Cualitativo** | (Óptimo) Integrar la comparación de **Q3 (Tópicos)** y **Q2 (Personalidad de Marca)** del cliente con la media de los competidores, explicando *por qué* el rendimiento numérico es diferente. | |

##### Crítica al Cálculo

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Punto Fuerte (Funcionalidad)** | Q16 es la **clave estratégica**. El **Z-Score** transforma el ER (Q11), el tamaño de la comunidad (Q12) y la frecuencia (Q13) en métricas de posicionamiento. | |
| **Punto Débil (Pre-requisito)** | El máximo rendimiento de Q16 requiere que las demás Qs (Q11, Q12, Q13, Q17) se hayan ejecutado previamente para obtener los valores absolutos del cliente que se utilizarán en la fórmula del Z-Score. | |
| **Dependencia Crítica** | El análisis Q12 se **desbloquea** utilizando los datos de seguidores de los competidores que deben estar definidos en el JSON `competitors_details` de la **Ficha Cliente**. | |

##### Outputs

El *output* JSON debe ser una **matriz de comparación anidada** que el **Guardían** pueda consumir fácilmente. El esquema Pydantic asociado es **`Q16BenchmarkCompetitivo`** (implícito).

| Clave del JSON | Estructura Esperada | Requisito de Pydantic (Guardían) | Fuente |
| :--- | :--- | :--- | :--- |
| **`kpi_scores_cliente`** | `Dict` - Los Z-Scores y valores absolutos del cliente para Q11, Q12, Q13 y Q17 (NSS). | | |
| **`perfiles_competitivos`** | `List[Dict]` - Una lista que contiene el rendimiento de cada competidor en las métricas clave. | **CRÍTICO:** `api/schemas.py` debe tener modelos para validar esta matriz de comparación y los Z-Scores. | |
| **`ranking_global`** | `List[Dict]` - El *ranking* de los 5 perfiles (cliente + 4 competidores) en métricas clave (ej. ER). | | |

##### Modificación de la Arquitectura de la API (El Guardián)

| Acción Requerida | Razón | Fuente |
| :--- | :--- | :--- |
| **Actualizar `api/schemas.py`** | El *output* JSON de Q16 es una matriz compleja y anidada. Los esquemas Pydantic (`Q16BenchmarkCompetitivo`) deben ser actualizados para aceptar esta estructura compleja y los múltiples Z-Scores. | |
| **Validación de la Ficha Cliente** | Los modelos Pydantic de `FichaCliente` deben haber sido modificados previamente para incluir y validar los datos de `seguidores_instagram`, `seguidores_tiktok`, etc., del cliente y los competidores. | |

##### La Forma en que Usa el Output para Visualizarse (Gráfico)

La visualización debe sintetizar la complejidad del *benchmark* en una vista ejecutiva, utilizando el Frontend (Streamlit/Plotly).

| Gráfico | Tipo de Visualización | Propósito y Cómo se Construye (Plotly/Streamlit) | Fuente |
| :--- | :--- | :--- | :--- |
| **1. Mapa de Posicionamiento Holístico** | **Gráfico de Radar (*Radar Chart*)** | **Propósito:** Mostrar el posicionamiento completo del cliente. Cada eje representa un KPI clave (Q11 ER, Q12 Comunidad, Q13 Frecuencia, etc.). | |
| **2. Diagnóstico de Alerta Rápida** | **KPI Cards con Z-Score** | Para cada KPI (Q11, Q13, Q17), se muestra el valor del cliente y su **Z-Score** asociado. El color de la tarjeta (verde/rojo) debe estar condicionado por el signo del Z-Score, indicando el desempeño frente al promedio del mercado. | |
| **3. Desglose de Ranking** | **Gráficos de Barras Comparativas** | Muestra el *ranking* de los 5 perfiles (cliente + 4 competidores) en una métrica específica (ej. Tasa de Engagement en Instagram). | |

##### Puntos Débiles o Medidas de Contingencia

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Rendimiento Máximo** | Se logra al utilizar el **Gráfico de Radar** (Gráfico 1) que integra todas las métricas clave (Q11, Q12, Q13, etc.) y las normaliza (Z-Score o 0-100), permitiendo al ejecutivo ver el perfil estratégico completo de la marca. | |
| **Crítica de la Visualización** | La visualización de Q16 es esencial para dar contexto a Q11, Q12 y Q13. Sin la comparación, estas métricas son simplemente números absolutos sin contexto de mercado. | |
| **Metáfora** | Q16 es la herramienta que te dice si estás ganando o perdiendo la carrera. Transforma los datos de la marca de un **cronómetro interno** (Q11) a una **tabla de tiempos de vuelta** que compara el rendimiento con los líderes del mercado. | |