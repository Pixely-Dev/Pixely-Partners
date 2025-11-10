import streamlit as st # type: ignore
import json
import os


def draw_dashboard(data: dict):
    """
    Organiza y renderiza el dashboard principal de redes sociales usando pestañas.

    Args:
        data (dict): El payload completo de insights cargado desde el JSON.
    """
    st.header("Dashboard de Análisis")

    # Crear pestañas para organizar los diferentes tipos de análisis
    quant_tab, qual_tab = st.tabs(["📊 Análisis Cuantitativo", "🧠 Análisis Cualitativo"])

    with quant_tab:
        st.subheader("Métricas de Rendimiento y Mercado")
        # --- Llamadas a módulos de vista cuantitativos (Q11-Q20) ---
        # Import and render each module individually so a missing view doesn't block the rest.
        try:
            from .view_components.quant.q11_view import display_q11_engagement
            try:
                display_q11_engagement()
            except Exception:
                st.info("Q11 no disponible o fallo al renderizar.")
        except Exception:
            st.info("Q11 view no encontrada.")

        # Explicitly import and render Quant views in the intended order
        # Use explicit local-relative imports with fallbacks to avoid misplacement
        quant_sequence = [
            ('Q12', 'view_components.quant.q12_view', 'display_q12_comunidad'),
            ('Q13', 'view_components.quant.q13_view', 'display_q13_frecuencia'),
            ('Q14', 'view_components.quant.q14_view', 'display_q14_formatos'),
            ('Q15', 'view_components.quant.q15_view', 'display_q15_hashtags'),
            # ('Q16', 'view_components.quant.q16_view', 'display_q16_benchmark'),  # DISABLED: Q16 commented out per single-client mode
            ('Q18', 'view_components.quant.q18_view', 'display_q18_anomalias'),
            ('Q19', 'view_components.quant.q19_view', 'display_q19_correlacion'),
            ('Q20', 'view_components.quant.q20_view', 'display_q20_kpi_global'),
        ]

        for name, rel_path, fn_name in quant_sequence:
            try:
                module = __import__(f'.{rel_path}', fromlist=['*'])
            except Exception:
                try:
                    # fallback to absolute-style import if package context differs
                    module = __import__(f'pipelines.social_media.{rel_path}', fromlist=['*'])
                except Exception:
                    st.info(f"{name} view no encontrada.")
                    continue

            display_fn = getattr(module, fn_name, None)
            if not display_fn:
                # autodetect any display_ function as a last resort
                for attr in dir(module):
                    if attr.startswith('display_'):
                        display_fn = getattr(module, attr)
                        break

            if display_fn:
                try:
                    display_fn()
                except Exception as e:
                    st.info(f"{name} fallo al renderizar: {e}")
            else:
                st.info(f"{name} no tiene función display_ reconocible.")

    with qual_tab:
        st.subheader("Insights de Contenido y Audiencia")
        try:
            # Render qualitative modules as labeled tabs including Q17 explicitly
            qual_tabs = st.tabs(["😢 Emociones (Q1)", "👤 Personalidad (Q2)", "💬 Tópicos (Q3)", "🙂 Sentimiento Agrupado (Q17)"])

            # Q1
            try:
                from .view_components.qual.q1_view import display_q1_emotions
                with qual_tabs[0]:
                    display_q1_emotions()
            except Exception:
                with qual_tabs[0]:
                    st.info("Q1 no disponible")

            # Q2
            try:
                from .view_components.qual.q2_view import display_q2_personalidad
                with qual_tabs[1]:
                    display_q2_personalidad()
            except Exception:
                with qual_tabs[1]:
                    st.info("Q2 no disponible")

            # Q3
            try:
                from .view_components.qual.q3_topicos_view import display_q3_topicos
                with qual_tabs[2]:
                    display_q3_topicos()
            except Exception:
                with qual_tabs[2]:
                    st.info("Q3 no disponible")

            # Q17
            try:
                from .view_components.quant.q17_view import display_q17_sentimiento_agrupado
                with qual_tabs[3]:
                    display_q17_sentimiento_agrupado()
            except Exception:
                with qual_tabs[3]:
                    st.info("Q17 no disponible")

        except Exception as e:
            st.warning(f"No se pudieron renderizar los módulos cualitativos: {e}")
