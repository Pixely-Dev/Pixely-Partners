import os
import json
import streamlit as st
import pandas as pd
from .._outputs import get_outputs_dir


def display_q15_hashtags():
    outputs_dir = get_outputs_dir()
    path = os.path.join(outputs_dir, 'q15_hashtags.json')

    st.header("#️⃣ Q15 — Hashtags Efectivos")
    if not os.path.exists(path):
        st.info("Resultados de Q15 no disponibles. Ejecuta el orquestador para generar 'q15_hashtags.json'.")
        return

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        ranking = data.get('ranking_hashtags_eficientes', [])
        if ranking:
            df = pd.DataFrame(ranking)
            # Defensive fill for missing columns
            for col in ['er_normalizado', 'uso', 'sentimiento_asociado', 'topico_dominante']:
                if col not in df.columns:
                    df[col] = None
            df['sentimiento_asociado'] = df['sentimiento_asociado'].fillna('N/A')
            df['topico_dominante'] = df['topico_dominante'].fillna('N/A')
            df = df.set_index('hashtag')
            st.bar_chart(df['er_normalizado'])
            st.table(df[['er_normalizado', 'uso', 'sentimiento_asociado', 'topico_dominante']].head(20))
        else:
            st.write('No hay hashtags suficientes (umbral mínimo no alcanzado)')

    except Exception as e:
        st.error(f"Error cargando Q15: {e}")
