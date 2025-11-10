import os
import json
import streamlit as st
import pandas as pd
from .._outputs import get_outputs_dir


def display_q16_benchmark():
    outputs_dir = get_outputs_dir()
    path = os.path.join(outputs_dir, 'q16_benchmark.json')

    st.header("📊 Q16 — Benchmark")
    if not os.path.exists(path):
        st.info("Resultados de Q16 no disponibles. Ejecuta el orquestador para generar 'q16_benchmark.json'.")
        return

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        bench = data.get('benchmark', {})

        # Single-client system: show only client benchmark metrics and suppress competitor charts
        client_er = bench.get('client_er_mean')
        results = bench.get('results', {})
        col1, col2 = st.columns(2)
        with col1:
            if client_er is not None:
                st.metric('Client ER mean', f"{client_er:.4f}")
            else:
                st.write('No hay métricas de cliente disponibles en el benchmark.')
        with col2:
            if results:
                st.metric('ER std dev', f"{results.get('er_std_dev'):.4f}" if results.get('er_std_dev') is not None else 'N/A')
        st.info('El sistema está configurado para análisis de un solo cliente; las comparativas con competidores se omiten por diseño.')

        st.subheader('Resumen')
        results = bench.get('results', {})
        if results:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric('ER mean', f"{results.get('er_mean'):.4f}" if results.get('er_mean') is not None else 'N/A')
            with col2:
                st.metric('ER std dev', f"{results.get('er_std_dev'):.4f}" if results.get('er_std_dev') is not None else 'N/A')
            with col3:
                st.metric('Followers mean', f"{int(results.get('followers_mean')):,}" if results.get('followers_mean') is not None else 'N/A')

        st.subheader('Detalles de entradas')
        client_er = bench.get('client_er_mean')
        competitor_ers = bench.get('competitor_ers', [])
        # show bar chart comparing client vs competitors. Support two formats:
        # - legacy: competitor_ers is list of floats
        # - enhanced: competitor_ers is list of dicts {name, username, er, followers}
        try:
            import pandas as _pd
            rows = []
            if client_er is not None:
                rows.append({'actor': 'client', 'er': client_er})

            if competitor_ers:
                # enhanced format: list of dicts
                if isinstance(competitor_ers[0], dict):
                    for c in competitor_ers:
                        name = c.get('name') or c.get('username') or f"competitor_{len(rows)+1}"
                        er = None
                        if c.get('er') is not None:
                            er = c.get('er')
                        elif c.get('er_mean') is not None:
                            er = c.get('er_mean')
                        rows.append({'actor': name, 'er': er})
                else:
                    # legacy list of floats
                    for i, c in enumerate(competitor_ers):
                        rows.append({'actor': f'competitor_{i+1}', 'er': c})

            if rows:
                dfc = _pd.DataFrame(rows).set_index('actor')
                st.bar_chart(dfc['er'])
        except Exception:
            st.write({'client_er_mean': client_er, 'competitor_ers': competitor_ers})

    except Exception as e:
        st.error(f"Error cargando Q16: {e}")
