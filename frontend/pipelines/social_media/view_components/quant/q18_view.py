import os
import json
import streamlit as st
import pandas as pd
from .._outputs import get_outputs_dir


def display_q18_anomalias():
    outputs_dir = get_outputs_dir()
    path = os.path.join(outputs_dir, 'q18_anomalias.json')

    st.header("⚠️ Q18 — Anomalías")
    if not os.path.exists(path):
        st.info("Resultados de Q18 no disponibles. Ejecuta el orquestador para generar 'q18_anomalias.json'.")
        return

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        summary = data.get('summary', {})
        anomalies = data.get('anomalies', [])

        st.subheader('Resumen estadístico')
        # Render summary as metric cards when possible
        try:
            mean_val = summary.get('mean') or summary.get('avg')
            std_val = summary.get('std') or summary.get('std_dev')
            count_val = summary.get('count') or summary.get('n')
            cols = st.columns(3)
            with cols[0]:
                if count_val is not None:
                    st.metric('Posts analizados', str(count_val))
            with cols[1]:
                if mean_val is not None:
                    st.metric('Media (valor)', f"{mean_val}")
            with cols[2]:
                if std_val is not None:
                    st.metric('Desviación estándar', f"{std_val}")
        except Exception:
            st.write(summary)

        # Show anomalies as a table and an interactive scatter if numeric values exist
        if anomalies:
            df = pd.DataFrame(anomalies)
            if 'post_id' in df.columns:
                df = df.set_index('post_id')
            st.subheader('Anomalías detectadas')
            st.table(df)

            # Try to plot: find a numeric column to visualize (value, metric, z_score)
            numeric_cols = df.select_dtypes(include='number').columns.tolist()
            if numeric_cols:
                val_col = None
                for candidate in ['value', 'metric', 'z_score', 'zscore', 'views', 'engagement_rate']:
                    if candidate in numeric_cols:
                        val_col = candidate
                        break
                if val_col is None:
                    val_col = numeric_cols[0]

                try:
                    import plotly.express as px
                    fig = px.scatter(df.reset_index(), x=df.reset_index().columns[0], y=val_col,
                                     color=val_col, size=val_col, title='Anomalías: Valor vs Post')
                    st.plotly_chart(fig, use_container_width=True)
                except Exception:
                    st.info('No fue posible generar el gráfico interactivo de anomalías.')
            # description
            st.markdown("""
**Qué muestra:** El panel lista las publicaciones cuyo rendimiento es atípico respecto a la distribución histórica. El gráfico de dispersión resalta qué publicaciones difieren significativamente.

**Cómo se mide:** Las anomalías se detectan sobre métricas normalizadas (p.ej. ER normalizado) usando criterios estadísticos como Z-Score. Se recomienda priorizar anomalías con Z-Score > 3 o < -2.

**Uso y tips:** Use este panel para identificar 'viralidad' positiva vs. riesgos. Combine con Q3 (tópicos) y Q7 (sentimiento) para entender la causa de la anomalía.
""")
        else:
            st.write('No se detectaron anomalías')

    except Exception as e:
        st.error(f"Error cargando Q18: {e}")
