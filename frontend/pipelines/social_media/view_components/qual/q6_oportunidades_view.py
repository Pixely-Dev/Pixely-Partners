import streamlit as st # pyright: ignore[reportMissingImports]
import pandas as pd
import plotly.express as px
import json
import os
from .._outputs import get_outputs_dir

def load_q6_data():
    """Carga los datos del análisis Q6 desde el archivo JSON."""
    outputs_dir = get_outputs_dir()
    json_path = os.path.join(outputs_dir, 'q6_oportunidades.json')

    if not os.path.exists(json_path):
        st.warning(f"Aún no se ha generado el análisis de oportunidades (Q6). Ejecuta el pipeline correspondiente. Path: {json_path}")
        return None

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Eliminar cualquier carácter BOM si existe
            if content.startswith('\ufeff'):
                content = content[1:]
            # Intentar decodificar el JSON
            data = json.loads(content)
            
            # Verificar la estructura esperada
            if "lista_oportunidades" not in data:
                st.error("El archivo JSON no tiene la estructura esperada (falta 'lista_oportunidades')")
                return None
                
            return data
    except json.JSONDecodeError as e:
        st.error(f"Error al decodificar el JSON de Q6: {str(e)}\nPath: {json_path}")
        with st.expander("Contenido del archivo con error"):
            st.code(content[:500] + "..." if len(content) > 500 else content)
        return None
    except Exception as e:
        st.error(f"Error al cargar Q6: {str(e)}")
        return None

def display_q6_oportunidades():
    """
    Muestra los resultados del análisis de oportunidades (Q6) usando una matriz de priorización estratégica.
    """
    st.header("Q6: Análisis de Oportunidades de Mercado")

    data = load_q6_data()
    if data is None:
        return

    oportunidades = data.get("lista_oportunidades", [])
    metadata = data.get("metadata", {})

    if not oportunidades:
        st.info("No se encontraron oportunidades para mostrar.")
        return

    # Crear DataFrame para la visualización
    df = pd.DataFrame(oportunidades)
    
    # Convertir actividad_competitiva a valores numéricos para el eje X
    actividad_map = {"Baja": 1, "Media": 2, "Alta": 3}
    df["actividad_valor"] = df["actividad_competitiva"].map(actividad_map)

    # Crear gráfico de dispersión (Matriz de Priorización)
    fig = px.scatter(
        df,
        x="actividad_valor",
        y="gap_score",
        text="tema",
        title="Matriz de Priorización Estratégica",
        labels={
            "actividad_valor": "Barrera de Entrada (Actividad Competitiva)",
            "gap_score": "Urgencia Estratégica (Gap Score)",
            "tema": "Oportunidad"
        },
        height=600
    )

    # Personalizar el gráfico
    fig.update_traces(
        marker=dict(size=12),
        textposition="top center"
    )
    fig.update_xaxes(
        ticktext=["Baja", "Media", "Alta"],
        tickvals=[1, 2, 3],
        range=[0.5, 3.5]
    )
    fig.update_yaxes(range=[0, 100])

    # Agregar zonas de prioridad
    fig.add_shape(
        type="rect",
        x0=0.5, y0=70,
        x1=1.5, y1=100,
        fillcolor="rgba(0,255,0,0.1)",
        line_width=0,
        name="Alta Prioridad"
    )
    fig.add_shape(
        type="rect",
        x0=2.5, y0=0,
        x1=3.5, y1=30,
        fillcolor="rgba(255,0,0,0.1)",
        line_width=0,
        name="Baja Prioridad"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Mostrar métricas agregadas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Promedio Gap Score", f"{metadata.get('promedio_gap', 0):.1f}")
    with col2:
        dist = metadata.get("distribucion_actividad", {})
        st.metric("Oportunidades Alta Prioridad", 
                 sum(1 for op in oportunidades if op["gap_score"] >= 70 and op["actividad_competitiva"] == "Baja"))
    with col3:
        st.metric("Total Oportunidades", metadata.get("total_oportunidades", 0))

    # Detalles de las oportunidades
    st.subheader("Detalles de Oportunidades")
    for oportunidad in sorted(oportunidades, key=lambda x: x["gap_score"], reverse=True):
        with st.expander(f"{oportunidad['tema']} (Gap Score: {oportunidad['gap_score']})"):
            col1, col2 = st.columns([2,1])
            with col1:
                st.markdown(f"**Justificación:** {oportunidad['justificacion']}")
                st.markdown(f"**Recomendación:** {oportunidad['recomendacion_accion']}")
            with col2:
                st.metric("Gap Score", oportunidad["gap_score"])
                st.markdown(f"**Actividad Competitiva:** {oportunidad['actividad_competitiva']}")