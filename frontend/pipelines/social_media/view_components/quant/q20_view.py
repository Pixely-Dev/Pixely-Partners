import os
import json
import streamlit as st
import pandas as pd
from .._outputs import get_outputs_dir


def display_q20_kpi_global():
    outputs_dir = get_outputs_dir()
    path = os.path.join(outputs_dir, 'q20_kpi_global.json')

    st.header("📈 Q20 — KPI Global")
    if not os.path.exists(path):
        st.info("Resultados de Q20 no disponibles. Ejecuta el orquestador para generar 'q20_kpi_global.json'.")
        return

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        kpis = data.get('kpis', {})
        if kpis:
            st.subheader('KPIs principales')
            # Present main KPIs as metric cards
            total_posts = kpis.get('total_posts') or kpis.get('posts_total')
            total_views = kpis.get('total_views') or kpis.get('views_total')
            avg_er = kpis.get('avg_engagement_rate') or kpis.get('avg_er')
            followers = kpis.get('followers_total') or kpis.get('followers')

            cols = st.columns(4)
            with cols[0]:
                if total_posts is not None:
                    st.metric('Total posts', str(total_posts))
            with cols[1]:
                if total_views is not None:
                    st.metric('Total views', f"{total_views}")
            with cols[2]:
                if avg_er is not None:
                    try:
                        st.metric('Avg. Engagement Rate', f"{float(avg_er):.4f}")
                    except Exception:
                        st.metric('Avg. Engagement Rate', str(avg_er))
            with cols[3]:
                if followers is not None:
                    st.metric('Followers (total)', f"{followers}")

            # Distribución por tipo de contenido
            if kpis.get('content_type_counts'):
                st.subheader('Distribución por tipo de contenido')
                df = pd.DataFrame.from_dict(kpis.get('content_type_counts'), orient='index', columns=['count'])
                st.bar_chart(df['count'])

            # Description
            st.markdown("""
**Qué muestra:** Panel ejecutivo de KPIs agregados (posts, vistas, engagement rate y seguidores). La distribución por tipo de contenido permite identificar formatos que aportan más alcance o interacción.

**Cómo se mide:** KPIs calculados a partir de los posts analizados en el periodo. El Avg. Engagement Rate normalmente es interacciones/vistas o interacciones/alcance.

**Uso y tips:** Use estas métricas como control de salud y para priorizar formatos que maximicen ER y alcance. Combine con Q16 (benchmark) para entender desempeño relativo.
""")
        else:
            st.write('No hay KPIs calculados')

    except Exception as e:
        st.error(f"Error cargando Q20: {e}")
