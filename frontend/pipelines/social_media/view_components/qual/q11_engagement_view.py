import os
import json
from typing import Any

import streamlit as st
import pandas as pd
from .._outputs import get_outputs_dir


def display_q11_engagement():
    """Vista Streamlit mejorada para Q11 - Engagement.

    Muestra:
    - KPI global (engagement_global_promedio) con indicador de z-score si está disponible.
    - Gráfico de barras comparando ER por red social con la media de competidores (si existe).
    - Serie temporal del ER (gráfico de líneas).

    Si el archivo `q11_engagement.json` no existe, muestra un mensaje instructivo.
    """
    outputs_dir = get_outputs_dir()
    output_path = os.path.join(outputs_dir, 'q11_engagement.json')

    st.header("🤝 Q11 — Engagement General")

    if not os.path.exists(output_path):
        st.info("Resultados de Q11 no disponibles. Ejecuta el orquestador para generar 'q11_engagement.json' en orchestrator/outputs.")
        return

    try:
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

    # System is single-client by design; frontend treats outputs as client-only.

        # --- KPI global y Z-score ---
        eg = data.get('engagement_global_promedio')
        bench = data.get('benchmark_comparativo', {}) or {}
        z = bench.get('z_score_er')

        col1, col2 = st.columns([2, 3])
        with col1:
            if eg is not None:
                # Mostrar con 6 decimales por defecto
                if z is not None:
                    # Mostrar valor y z como delta (ejemplo simple)
                    delta_str = f"Z={z:.2f}"
                    st.metric(label="Engagement global promedio", value=f"{eg:.6f}", delta=delta_str)
                else:
                    st.metric(label="Engagement global promedio", value=f"{eg:.6f}")
            else:
                st.write("Engagement global no disponible")

            # Texto explicativo breve
            st.caption("ER calculado como (likes + comments) / followers (o fallback a interactions/views). Z-score compara contra competidores (Q16).")

        # --- Barras comparativas por red ---
        st.subheader("Comparativa por red social")
        seg = data.get('engagement_segmentado_red', []) or []
        comp_by_net = bench.get('competitor_mean_by_network', {}) or {}

        if seg:
            df_seg = pd.DataFrame(seg)
            df_seg = df_seg.rename(columns={"social_network": "red", "engagement_rate": "cliente_er"})

            # Añadir columna con competitor mean si existe
            df_seg["competitor_er"] = df_seg["red"].map(comp_by_net)

            # Preparar chart: DataFrame con columnas cliente_er y competitor_er (rellenar NaN con None)
            plot_df = df_seg.set_index("red")[ ["cliente_er", "competitor_er"] ]
            # st.bar_chart puede consumir DataFrame
            st.bar_chart(plot_df)
        else:
            st.write("No hay datos segmentados disponibles")

    # --- Serie temporal del ER ---
        st.subheader("Evolución semanal del ER")
        serie = data.get('serie_temporal_er', []) or []
        if serie:
            df_time = pd.DataFrame(serie)
            # column names expected: week_start, engagement_rate
            df_time = df_time.sort_values('week_start')
            df_time = df_time.set_index(pd.to_datetime(df_time['week_start']))
            st.line_chart(df_time['engagement_rate'])
        else:
            st.write("No hay serie temporal disponible")

    # --- Benchmark detallado (presentación amigable) ---
        # Benchmark (detalles) — show only client metrics; competitor comparatives are omitted
        st.subheader("Benchmark (detalles)")
        try:
            z = bench.get('z_score_er')
            comp_mean = bench.get('competitor_mean_er') or bench.get('competitor_mean_by_network') and next(iter(bench.get('competitor_mean_by_network').values()))
            col1, col2 = st.columns(2)
            with col1:
                if z is not None:
                    st.metric(label='Z-score ER', value=f"{z:.3f}")
                    # Show client mean ER if present; competitor aggregates intentionally omitted
                    client_mean = bench.get('client_er_mean')
                    if client_mean is not None:
                        st.metric(label='Client mean ER', value=f"{client_mean:.6f}")
            with col2:
                comp_by_net = bench.get('competitor_mean_by_network', {})
                # competitor table suppressed (single-client architecture)
        except Exception as e:
            st.write('Detalles de benchmark no disponibles en formato amigable:', e)
        # --- Actors: single-client system: show only client actor metrics if present ---
        actors = data.get('actors')
        if actors and isinstance(actors, list):
            try:
                df_actors = pd.DataFrame(actors)
                # If there's only one actor record, show it as client metrics
                if len(df_actors) == 1:
                    if 'er_mean' in df_actors.columns:
                        df_plot = df_actors.set_index('actor')['er_mean']
                        st.subheader('Métricas por actor (cliente)')
                        st.bar_chart(df_plot)
                else:
                    # If multiple actors appear, avoid competitor comparisons and pick best-effort first row
                    st.info('Sistema configurado para análisis de un solo cliente. Se muestran únicamente métricas atribuidas al cliente cuando están disponibles.')
                    if 'er_mean' in df_actors.columns:
                        df_client = df_actors.head(1).set_index('actor')['er_mean']
                        st.bar_chart(df_client)
            except Exception as e:
                st.write('No fue posible renderizar métricas de actor:', e)

    except Exception as e:
        st.error(f"Error cargando resultados de Q11: {e}")
