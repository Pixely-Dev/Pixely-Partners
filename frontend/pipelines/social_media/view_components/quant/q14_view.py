import os
import json
import streamlit as st
import pandas as pd
from .._outputs import get_outputs_dir


def display_q14_formatos():
    outputs_dir = get_outputs_dir()
    path = os.path.join(outputs_dir, 'q14_formatos.json')

    st.header("🖼️ Q14 — Efectividad de Formatos")
    if not os.path.exists(path):
        st.info("Resultados de Q14 no disponibles. Ejecuta el orquestador para generar 'q14_formatos.json'.")
        return

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        ranking = data.get('ranking_global', [])
        p_value = data.get('p_value_general_anova')
        ranking_por_red = data.get('ranking_por_red_social', [])

        if ranking:
            df = pd.DataFrame(ranking).set_index('content_type')
            st.bar_chart(df['er_promedio'])
        else:
            st.write('No hay ranking global disponible')

        st.write(f"p-value ANOVA: {p_value}")

        st.subheader('Ranking por red social')
        if ranking_por_red:
            import pandas as _pd
            for item in ranking_por_red:
                st.write(f"Red: {item.get('social_network')}")
                ranking = item.get('ranking', {})
                if isinstance(ranking, dict):
                    df = _pd.Series(ranking).reset_index()
                    df.columns = ['content_type', 'er_promedio']
                    df = df.set_index('content_type')
                    st.bar_chart(df['er_promedio'])
                    st.table(df)
                else:
                    st.write(ranking)
        else:
            st.write('No hay ranking por red disponible')

    except Exception as e:
        st.error(f"Error cargando Q14: {e}")
