import os
import json
import streamlit as st
import pandas as pd
from .._outputs import get_outputs_dir


def display_q13_frecuencia():
    outputs_dir = get_outputs_dir()
    path = os.path.join(outputs_dir, 'q13_frecuencia.json')

    st.header("⏱️ Q13 — Frecuencia de Publicación")
    if not os.path.exists(path):
        st.info("Resultados de Q13 no disponibles. Ejecuta el orquestador para generar 'q13_frecuencia.json'.")
        return

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        global_freq = data.get('posts_por_dia_promedio_global')
        consistency = data.get('consistencia_desviacion')
        freq_by_red = data.get('frecuencia_por_red', [])

        col1, col2 = st.columns([2, 3])
        with col1:
            st.metric('Posts por día (promedio global)', f"{global_freq:.2f}" if global_freq is not None else "N/A")
            st.caption('Consistencia (desviación estándar de posts por día)')
            st.write(consistency)

        with col2:
            if freq_by_red:
                df = pd.DataFrame(freq_by_red).set_index('social_network')
                st.bar_chart(df['posts_per_day'])
            else:
                st.write('No hay datos de frecuencia por red')

        st.subheader('Benchmark (detalles)')
        bench = data.get('benchmark_comparativo', {})
        if bench:
            import pandas as _pd
            # try to show as table if structure is mapping
            if isinstance(bench, dict):
                rows = []
                for k, v in bench.items():
                    rows.append({'metric': k, 'value': v})
                st.table(_pd.DataFrame(rows).set_index('metric'))
            else:
                st.write(bench)
        else:
            st.write('No hay benchmark comparativo disponible')

    except Exception as e:
        st.error(f"Error cargando Q13: {e}")
