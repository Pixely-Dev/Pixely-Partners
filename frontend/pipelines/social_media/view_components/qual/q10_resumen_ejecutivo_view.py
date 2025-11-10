import streamlit as st # pyright: ignore[reportMissingImports]
import json
import os
from datetime import datetime


def load_q10_data():
    from .._outputs import get_outputs_dir
    outputs_dir = get_outputs_dir()
    json_path = os.path.join(outputs_dir, 'q10_resumen_ejecutivo.json')

    if not os.path.exists(json_path):
        st.warning(f"Aún no se ha generado Q10 (Resumen Ejecutivo). Path: {json_path}")
        return None

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error al cargar Q10: {e}")
        return None


def display_q10_resumen_ejecutivo():
    st.header("Q10: Resumen Ejecutivo")

    data = load_q10_data()
    if data is None:
        return

    # legacy: fecha may be at top-level or inside metadata
    fecha = data.get('fecha_analisis') or data.get('metadata', {}).get('fecha_analisis') or data.get('metadata', {}).get('date')
    if fecha:
        st.markdown(f"**Fecha de Análisis:** {fecha}")

    resumen = data.get('resumen')
    # historic key for action items
    prioridades = data.get('prioridades') or data.get('puntos_clave') or []

    st.subheader("Resumen (viñetas)")
    if not resumen:
        st.info("No hay resumen generado. Ejecuta el módulo Q10 desde el orquestador.")
    else:
        # resumen can be a string or a list. If string, split into sentences for bullets
        if isinstance(resumen, str):
            # try to split into reasonable sentences
            parts = [s.strip() for s in resumen.replace('\n', ' ').split('. ') if s.strip()]
            for p in parts:
                st.markdown(f"- {p.strip().rstrip('.')}")
        elif isinstance(resumen, (list, tuple)):
            for r in resumen:
                st.markdown(f"- {r}")
        else:
            st.markdown(f"- {str(resumen)}")

    st.subheader("Prioridades y Acciones")
    if not prioridades:
        st.info("No hay prioridades generadas.")
    else:
        for p in prioridades:
            if isinstance(p, dict):
                st.markdown(f"**Acción:** {p.get('accion') or p.get('title') or p.get('name')}  \
                             **Impacto:** {p.get('impacto_score', p.get('impact', 'N/A'))}  \
                             **Frameworks:** {p.get('frameworks_relevantes', p.get('frameworks', 'N/A'))}")
            else:
                st.markdown(f"- {p}")
