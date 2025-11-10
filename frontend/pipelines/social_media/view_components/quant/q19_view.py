import os
import json
import streamlit as st
import pandas as pd
from .._outputs import get_outputs_dir


def display_q19_correlacion():
    outputs_dir = get_outputs_dir()
    path = os.path.join(outputs_dir, 'q19_correlacion.json')

    st.header("🔗 Q19 — Correlación")
    if not os.path.exists(path):
        st.info("Resultados de Q19 no disponibles. Ejecuta el orquestador para generar 'q19_correlacion.json'.")
        return

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        matrix = data.get('correlation_matrix', {})
        top_pairs = data.get('top_pairs', [])

        if matrix:
            st.subheader('Matriz de correlación')
            df = pd.DataFrame(matrix)
            st.table(df)
            st.markdown("""
**Qué muestra:** La matriz representa la correlación (Pearson) entre las variables analizadas (por ejemplo: vistas, likes, comentarios). Los valores cercanos a 1 o -1 indican fuerte correlación positiva o negativa respectivamente.

**Cómo se mide:** Se calcula la correlación Pearson entre pares de métricas. Un valor alto sugiere que una variable puede explicar parte de la variación de la otra, pero no implica causalidad.

**Uso y tips:** Use la matriz para escoger pares a modelar (Q19) y como entrada para regresiones predictivas. Combine con pruebas de significancia y modelos multivariables antes de recomendar cambios.
""")
        else:
            st.write('Matriz no disponible')

        st.subheader('Pares con mayor correlación')
        if top_pairs:
            st.table(pd.DataFrame(top_pairs))
            st.markdown("""
**Qué muestra:** Lista los pares de variables con mayor correlación detectada. Útil para priorizar análisis adicionales o pruebas A/B.

**Tips:** Priorice pares con alto coeficiente y suficiente tamaño de muestra. Verifique luego la significancia estadística (p-value) y, si es posible, modele la relación con regresión.
""")
        else:
            st.write('No hay pares calculados')

    except Exception as e:
        st.error(f"Error cargando Q19: {e}")
