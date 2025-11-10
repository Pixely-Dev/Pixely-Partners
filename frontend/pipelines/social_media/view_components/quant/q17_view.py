import os
import json
import streamlit as st
import pandas as pd
from .._outputs import get_outputs_dir


def display_q17_sentimiento_agrupado():
    outputs_dir = get_outputs_dir()
    path = os.path.join(outputs_dir, 'q17_sentimiento_agrupado.json')

    st.header("🙂 Q17 — Sentimiento Agrupado")
    if not os.path.exists(path):
        st.info("Resultados de Q17 no disponibles. Ejecuta el orquestador para generar 'q17_sentimiento_agrupado.json'.")
        return

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        groups = data.get('groups', {})
        if groups:
            rows = []
            for k, v in groups.items():
                rows.append({
                    'grupo': k,
                    'count': v.get('count'),
                    'pct_positive': v.get('pct_positive'),
                    'pct_neutral': v.get('pct_neutral'),
                    'pct_negative': v.get('pct_negative')
                })
            df = pd.DataFrame(rows).set_index('grupo')
            st.table(df)
            # Description: what this chart/table represents
            st.markdown("""
**Qué muestra:** El cuadro anterior resume la distribución de polaridad por grupo (Positivo / Neutro / Negativo) y las proporciones asociadas.

**Cómo se mide:** Se calcula el porcentaje de comentarios o menciones clasificadas en cada categoría. Se puede derivar el Net Sentiment Score (NSS) como NSS = %Positivo − %Negativo.

**Uso y tips:** Use la métrica NSS para comparar la salud emocional del público a lo largo del tiempo y contra benchmarks competitivos (Q16). Una caída súbita en NSS puede indicar riesgo reputacional.
""")
        else:
            st.write('No hay datos de sentimiento agrupado')

    except Exception as e:
        st.error(f"Error cargando Q17: {e}")
