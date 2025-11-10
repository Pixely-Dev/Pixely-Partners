import streamlit as st # type: ignore
import pandas as pd
import json
import os
import importlib


# Helper: attempt to load a display function from multiple possible module paths
def _load_display_func(module_path_candidates, func_name):
    for mp in module_path_candidates:
        try:
            mod = importlib.import_module(mp)
            fn = getattr(mod, func_name, None)
            if fn:
                return fn
        except Exception:
            continue
    return None


def main():
    st.set_page_config(layout="wide", page_title="Pixely Dashboard")

    # Sidebar for navigation
    st.sidebar.title("Menú Principal")
    page = st.sidebar.radio("Selecciona una página", [
        "🏠 Pixely Partners",
        "📚 Wiki",
        "📊 Dashboard",
        "🧠 Análisis Cualitativo",
        "📈 Análisis Cuantitativo",
        "🛠️ Hilos de Trabajo"
    ])

    # Main content area
    if page == "🏠 Pixely Partners":
        st.title("Bob el constructor está trabajando 👷")
        st.write("Pronto habrá novedades aquí.")
    elif page == "📊 Dashboard":
        st.title("Dashboard de Pixely")
        # Show where the frontend expects outputs to be (helps debugging mounts)
        try:
            from pipelines.social_media.view_components._outputs import get_outputs_dir
            od = get_outputs_dir()
            st.caption(f"Orchestrator outputs dir (resolved): {od}")
            # list q*.json files present
            try:
                files = sorted([f for f in os.listdir(od) if f.startswith('q') and f.endswith('.json')])
                st.write('Resultados detectados:', files)
            except Exception:
                st.write('No se pudo listar archivos en el directorio de outputs (posible permisos o rutas montadas).')

        except Exception:
            st.caption('No se pudo resolver outputs_dir (get_outputs_dir)')

        # Render the main dashboard which internally calls the individual modules
        try:
            draw_fn = _load_display_func([
                'pipelines.social_media.view',
                'frontend.pipelines.social_media.view',
                'pipelines.social_media.view',
                'view'
            ], 'draw_dashboard')
            if draw_fn:
                draw_fn({})
            else:
                st.error('No se encontró la función draw_dashboard para renderizar el dashboard')
        except Exception as e:
            st.error(f"No se pudo renderizar el dashboard: {e}")

    elif page == "📚 Wiki":
        st.title("Bob el constructor está trabajando 👷")
        st.write("Pronto habrá novedades aquí.")
    elif page == "🧠 Análisis Cualitativo":
        st.title("Análisis Cualitativo")
        # Tabs for Q1-Q10
        qual_tabs = st.tabs([
            "😢 Emociones", 
            "👤 Personalidad", 
            "💬 Tópicos", 
            "📜 Marcos Narrativos", 
            "🌟 Influenciadores", 
            "🚀 Oportunidades", 
            "🔍 Sentimiento Detallado", 
            "⏰ Temporal", 
            "📝 Recomendaciones", 
            "📝 Resumen Ejecutivo"
        ])
        
        with qual_tabs[0]: # Q1 Emociones

            # Load Q1 data and display (lazy-import to avoid module path issues)
            st.header("🎭 Análisis dimensional de Plutchik")
            fn = _load_display_func([
                'pipelines.social_media.view_components.qual.q1_view',
                'frontend.pipelines.social_media.view_components.qual.q1_view',
                'view_components.qual.q1_view'
            ], 'display_q1_emotions')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q1 fallo al renderizar: {e}")
            else:
                st.info('Q1 no disponible')

        with qual_tabs[1]: # Q2 Personalidad
            fn = _load_display_func([
                'pipelines.social_media.view_components.qual.q2_view',
                'frontend.pipelines.social_media.view_components.qual.q2_view',
                'view_components.qual.q2_view'
            ], 'display_q2_personality')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q2 fallo al renderizar: {e}")
            else:
                st.info('Q2 no disponible')
        
        with qual_tabs[2]: # Q3 Temas
            st.header("💬 Análisis de Tópicos Principales")
            fn = _load_display_func([
                'pipelines.social_media.view_components.qual.q3_topicos_view',
                'frontend.pipelines.social_media.view_components.qual.q3_topicos_view',
                'view_components.qual.q3_topicos_view'
            ], 'display_q3_topicos')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q3 fallo al renderizar: {e}")
            else:
                st.info('Q3 no disponible')

        with qual_tabs[3]: # Q4 Marcos Narrativos
            fn = _load_display_func([
                'pipelines.social_media.view_components.qual.q4_marcos_narrativos_view',
                'frontend.pipelines.social_media.view_components.qual.q4_marcos_narrativos_view',
                'view_components.qual.q4_marcos_narrativos_view'
            ], 'display_q4_marcos_narrativos')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q4 fallo al renderizar: {e}")
            else:
                st.info('Q4 no disponible')

        with qual_tabs[4]: # Q5 Influenciadores
            fn = _load_display_func([
                'pipelines.social_media.view_components.qual.q5_influenciadores_view',
                'frontend.pipelines.social_media.view_components.qual.q5_influenciadores_view',
                'view_components.qual.q5_influenciadores_view'
            ], 'display_q5_influenciadores')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q5 fallo al renderizar: {e}")
            else:
                st.info('Q5 no disponible')

        with qual_tabs[5]: # Q6 Oportunidades
            fn = _load_display_func([
                'pipelines.social_media.view_components.qual.q6_oportunidades_view',
                'frontend.pipelines.social_media.view_components.qual.q6_oportunidades_view',
                'view_components.qual.q6_oportunidades_view'
            ], 'display_q6_oportunidades')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q6 fallo al renderizar: {e}")
            else:
                st.info('Q6 no disponible')
        with qual_tabs[6]: # Q7 Sentimiento Detallado
            fn = _load_display_func([
                'pipelines.social_media.view_components.qual.q7_sentimiento_detallado_view',
                'frontend.pipelines.social_media.view_components.qual.q7_sentimiento_detallado_view',
                'view_components.qual.q7_sentimiento_detallado_view'
            ], 'display_q7_sentimiento_detallado')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q7 fallo al renderizar: {e}")
            else:
                st.info('Q7 no disponible')
        with qual_tabs[7]: # Q8 Temporal
            st.header("⏰ Análisis Temporal")
            fn = _load_display_func([
                'pipelines.social_media.view_components.qual.q8_temporal_view',
                'frontend.pipelines.social_media.view_components.qual.q8_temporal_view',
                'view_components.qual.q8_temporal_view'
            ], 'display_q8_temporal')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q8 fallo al renderizar: {e}")
            else:
                st.info('Q8 no disponible')
        with qual_tabs[8]: # Q9 Recomendaciones
            st.header("📝 Recomendaciones Creativas")
            fn = _load_display_func([
                'pipelines.social_media.view_components.qual.q9_recomendaciones_view',
                'frontend.pipelines.social_media.view_components.qual.q9_recomendaciones_view',
                'view_components.qual.q9_recomendaciones_view'
            ], 'display_q9_recomendaciones')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q9 fallo al renderizar: {e}")
            else:
                st.info('Q9 no disponible')
        with qual_tabs[9]: # Q10 Resumen Ejecutivo
            st.header("📝 Resumen Ejecutivo")
            fn = _load_display_func([
                'pipelines.social_media.view_components.qual.q10_resumen_ejecutivo_view',
                'frontend.pipelines.social_media.view_components.qual.q10_resumen_ejecutivo_view',
                'view_components.qual.q10_resumen_ejecutivo_view'
            ], 'display_q10_resumen_ejecutivo')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q10 fallo al renderizar: {e}")
            else:
                st.info('Q10 no disponible')
        # Q17 Sentimiento Agrupado (muestra en la sección cualitativa)
        st.markdown("---")
        st.header("📊 Sentimiento Agrupado (Q17)")
        try:
            fn = _load_display_func([
                'pipelines.social_media.view_components.qual.q17_view',
                'frontend.pipelines.social_media.view_components.qual.q17_view',
                'view_components.qual.q17_view'
            ], 'display_q17_sentimiento_agrupado')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q17 fallo al renderizar: {e}")
            else:
                st.info('Q17 no disponible')
        except Exception as e:
            st.info(f"Q17 no disponible: {e}")
        # ... and so on for Q4-Q10
    elif page == "📈 Análisis Cuantitativo":
        st.title("Análisis Cuantitativo")
        # Tabs for Q11-Q20
        quant_tabs = st.tabs([
            "🤝 Engagement", 
            "🏘️ Comunidad", 
            "⏱️ Frecuencia", 
            "🖼️ Formatos", 
            "#️⃣ Hashtags", 
            "🏆 Benchmark", 
            "📊 Sentimiento Agrupado", 
            "📉 Anomalías", 
            "🔗 Correlación", 
            "🎯 KPI Global"
        ])
        with quant_tabs[0]: # Q11 Engagement
            st.header("Q11: Engagement")
            fn = _load_display_func([
                'pipelines.social_media.view_components.quant.q11_view',
                'frontend.pipelines.social_media.view_components.quant.q11_view',
                'view_components.quant.q11_view',
                'pipelines.social_media.view_components.qual.q11_engagement_view'
            ], 'display_q11_engagement')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q11 fallo al renderizar: {e}")
            else:
                st.info('Q11 no disponible')
        with quant_tabs[1]: # Q12 Comunidad
            fn = _load_display_func([
                'pipelines.social_media.view_components.quant.q12_view',
                'frontend.pipelines.social_media.view_components.quant.q12_view',
                'view_components.quant.q12_view'
            ], 'display_q12_comunidad')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q12 fallo al renderizar: {e}")
            else:
                st.info('Q12 no disponible')
        with quant_tabs[2]: # Q13 Frecuencia
            fn = _load_display_func([
                'pipelines.social_media.view_components.quant.q13_view',
                'frontend.pipelines.social_media.view_components.quant.q13_view',
                'view_components.quant.q13_view'
            ], 'display_q13_frecuencia')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q13 fallo al renderizar: {e}")
            else:
                st.info('Q13 no disponible')
        with quant_tabs[3]: # Q14 Formatos
            fn = _load_display_func([
                'pipelines.social_media.view_components.quant.q14_view',
                'frontend.pipelines.social_media.view_components.quant.q14_view',
                'view_components.quant.q14_view'
            ], 'display_q14_formatos')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q14 fallo al renderizar: {e}")
            else:
                st.info('Q14 no disponible')
        with quant_tabs[4]: # Q15 Hashtags
            fn = _load_display_func([
                'pipelines.social_media.view_components.quant.q15_view',
                'frontend.pipelines.social_media.view_components.quant.q15_view',
                'view_components.quant.q15_view'
            ], 'display_q15_hashtags')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q15 fallo al renderizar: {e}")
            else:
                st.info('Q15 no disponible')
        # Q16 Benchmark tab is disabled (commented out) to operate in single-client mode
        # with quant_tabs[5]: # Q16 Benchmark
        #     st.header("🏆 Benchmark")
        #     fn = _load_display_func([
        #         'pipelines.social_media.view_components.quant.q16_view',
        #         'frontend.pipelines.social_media.view_components.quant.q16_view',
        #         'view_components.quant.q16_view'
        #     ], 'display_q16_benchmark')
        #     if fn:
        #         try:
        #             fn()
        #         except Exception as e:
        #             st.info(f"Q16 fallo al renderizar: {e}")
        #     else:
        #         st.info('Q16 no disponible')
        with quant_tabs[6]: # Q17 Sentimiento Agrupado
            st.header("📊 Sentimiento Agrupado")
            fn = _load_display_func([
                'pipelines.social_media.view_components.quant.q17_view',
                'frontend.pipelines.social_media.view_components.quant.q17_view',
                'view_components.quant.q17_view',
                'pipelines.social_media.view_components.qual.q17_view'
            ], 'display_q17_sentimiento_agrupado')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q17 fallo al renderizar: {e}")
            else:
                st.info('Q17 no disponible')
        with quant_tabs[7]: # Q18 Anomalías
            st.header("📉 Anomalías")
            fn = _load_display_func([
                'pipelines.social_media.view_components.quant.q18_view',
                'frontend.pipelines.social_media.view_components.quant.q18_view',
                'view_components.quant.q18_view'
            ], 'display_q18_anomalias')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q18 fallo al renderizar: {e}")
            else:
                st.info('Q18 no disponible')
        with quant_tabs[8]: # Q19 Correlación
            st.header("🔗 Correlación")
            fn = _load_display_func([
                'pipelines.social_media.view_components.quant.q19_view',
                'frontend.pipelines.social_media.view_components.quant.q19_view',
                'view_components.quant.q19_view'
            ], 'display_q19_correlacion')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q19 fallo al renderizar: {e}")
            else:
                st.info('Q19 no disponible')
        with quant_tabs[9]: # Q20 KPI Global
            st.header("🎯 KPI Global")
            fn = _load_display_func([
                'pipelines.social_media.view_components.quant.q20_view',
                'frontend.pipelines.social_media.view_components.quant.q20_view',
                'view_components.quant.q20_view'
            ], 'display_q20_kpi_global')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q20 fallo al renderizar: {e}")
            else:
                st.info('Q20 no disponible')
        # ... and so on for Q12-Q20
    elif page == "🛠️ Hilos de Trabajo":
        st.title("Bob el constructor está trabajando 👷")
        st.write("Pronto habrá novedades aquí.")

if __name__ == "__main__":
    main()
