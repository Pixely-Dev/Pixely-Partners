import streamlit as st # pyright: ignore[reportMissingImports]
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from .._outputs import get_outputs_dir

def load_q7_data():
    """Carga los datos del análisis Q7 desde el archivo JSON."""
    # Resolve outputs dir (try env, container default, repo-relative)
    outputs_dir = get_outputs_dir()

    json_path = os.path.join(outputs_dir, 'q7_sentimiento_detallado.json')
    if not os.path.exists(json_path):
        st.warning(f"Aún no se ha generado el análisis de sentimiento detallado (Q7). Path: {json_path}")
        return None

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        st.error(f"Error al cargar Q7: {str(e)}")
        return None

def display_q7_sentimiento_detallado():
    """
    Muestra los resultados del análisis de sentimiento detallado (Q7).
    """
    st.header("Q7: Análisis de Sentimiento Detallado")
    
    data = load_q7_data()
    if data is None:
        return

    # 1. Gráfico de Anillo para Sentimiento Global + Tarjeta de Subjetividad
    analisis_agregado = data["analisis_agregado"]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Preparar datos para el gráfico de anillo
        sentimientos = ["Positivo", "Negativo", "Neutro", "Mixto"]
        valores = [
            analisis_agregado["positivo"],
            analisis_agregado["negativo"],
            analisis_agregado["neutro"],
            analisis_agregado["mixto"]
        ]
        
        fig = go.Figure(data=[go.Pie(
            labels=sentimientos,
            values=valores,
            hole=.4,
            marker_colors=['#2ecc71', '#e74c3c', '#95a5a6', '#f1c40f']
        )])
        
        fig.update_layout(
            title="Distribución Global de Sentimientos",
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Mostrar Score de Subjetividad Global
        st.metric(
            "Score de Subjetividad Global",
            f"{analisis_agregado['subjetividad_promedio_global']*100:.1f}%",
            help="0% = Completamente objetivo, 100% = Completamente subjetivo"
        )

    # 2. Top 5 Publicaciones con Mayor Ambivalencia
    st.subheader("Top 5 Publicaciones con Mayor Ambivalencia")
    
    df_posts = pd.DataFrame(data["analisis_por_publicacion"])
    df_posts["porcentaje_mixto"] = df_posts["distribucion"].apply(lambda x: x["mixto"] * 100)
    top_5_posts = df_posts.nlargest(5, "porcentaje_mixto")
    
    fig_bars = px.bar(
        top_5_posts,
        x="post_url",
        y="porcentaje_mixto",
        title="Publicaciones con Mayor Sentimiento Mixto",
        labels={
            "post_url": "URL de la Publicación",
            "porcentaje_mixto": "% de Comentarios Mixtos"
        }
    )
    
    st.plotly_chart(fig_bars, use_container_width=True)

    # 3. Selector de Publicaciones y Panel de Evidencia
    st.subheader("Análisis Detallado por Publicación")
    
    selected_post = st.selectbox(
        "Selecciona una publicación para ver detalles:",
        options=df_posts["post_url"].tolist(),
        format_func=lambda x: f"Post: ...{x[-30:]}" if len(x) > 30 else x
    )
    
    if selected_post:
        post_data = df_posts[df_posts["post_url"] == selected_post].iloc[0]
        
        # Mostrar distribución de sentimientos para esta publicación
        col1, col2 = st.columns([2, 1])
        
        with col1:
            dist = post_data["distribucion"]
            fig_post = go.Figure(data=[go.Bar(
                x=["Positivo", "Negativo", "Neutro", "Mixto"],
                y=[dist["positivo"], dist["negativo"], dist["neutro"], dist["mixto"]],
                marker_color=['#2ecc71', '#e74c3c', '#95a5a6', '#f1c40f']
            )])
            
            fig_post.update_layout(
                title=f"Distribución de Sentimientos - {selected_post[-30:]}",
                yaxis_title="Proporción",
                showlegend=False
            )
            
            st.plotly_chart(fig_post, use_container_width=True)
        
        with col2:
            st.metric(
                "Score de Subjetividad",
                f"{post_data['subjetividad_promedio']*100:.1f}%"
            )
            st.metric(
                "Total Comentarios",
                post_data["total_comentarios"]
            )
        
        # Mostrar ejemplo de comentario mixto
        if post_data["ejemplo_mixto"]["texto"]:
            st.info("Ejemplo de Comentario con Sentimiento Mixto:")
            st.markdown(f"""
            > {post_data["ejemplo_mixto"]["texto"]}
            
            *- Usuario: {post_data["ejemplo_mixto"]["username"]}*
            """)