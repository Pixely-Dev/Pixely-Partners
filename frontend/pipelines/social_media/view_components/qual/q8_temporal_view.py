import streamlit as st # pyright: ignore[reportMissingImports]
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime
from .._outputs import get_outputs_dir

def load_q8_data():
    """Carga los datos del análisis Q8 desde el archivo JSON."""
    outputs_dir = get_outputs_dir()

    json_path = os.path.join(outputs_dir, 'q8_temporal.json')
    if not os.path.exists(json_path):
        st.warning(f"Aún no se ha generado el análisis temporal (Q8). Path: {json_path}")
        return None

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        st.error(f"Error al cargar Q8: {str(e)}")
        return None

def display_q8_temporal():
    """
    Muestra los resultados del análisis temporal (Q8).
    """
    st.header("Q8: Análisis Temporal")
    
    data = load_q8_data()
    if data is None:
        return
    # 1. Tendencia General de Interacciones
    st.subheader("Tendencia General de Interacciones")
    tendencia = data.get("tendencia_general", [])

    if not tendencia:
        st.warning("No hay datos en 'tendencia_general' para mostrar. Ejecuta el pipeline Q8 para generar resultados.")
    else:
        # Convertir fechas con defensiva sobre posibles formatos/keys
        df_tendencia = pd.DataFrame(tendencia)
        if 'fecha' in df_tendencia.columns:
            df_tendencia['fecha'] = pd.to_datetime(df_tendencia['fecha'], errors='coerce')
        elif 'date' in df_tendencia.columns:
            df_tendencia['fecha'] = pd.to_datetime(df_tendencia['date'], errors='coerce')
        else:
            # Intentar inferir columnas si son positional
            if df_tendencia.shape[1] >= 2:
                # Renombrar las primeras dos columnas a fecha/interacciones
                cols = list(df_tendencia.columns)
                df_tendencia = df_tendencia.rename(columns={cols[0]: 'fecha', cols[1]: 'interacciones'})
                df_tendencia['fecha'] = pd.to_datetime(df_tendencia['fecha'], errors='coerce')
            else:
                st.warning("Los datos de 'tendencia_general' no contienen una columna de fecha reconocible.")
                df_tendencia = None

        if df_tendencia is not None and not df_tendencia.empty and 'interacciones' in df_tendencia.columns:
            fig_tendencia = px.line(
                df_tendencia,
                x='fecha',
                y='interacciones',
                title="Evolución de Interacciones en el Tiempo"
            )
            fig_tendencia.update_layout(
                xaxis_title="Fecha",
                yaxis_title="Número de Interacciones"
            )
            st.plotly_chart(fig_tendencia, use_container_width=True)
        else:
            st.info("No hay suficientes datos válidos para graficar la tendencia de interacciones.")

    # 2. Patrones por Día de la Semana
    st.subheader("Patrones por Día de la Semana")
    
    patrones = data.get("patrones_dia_semana", [])
    if not patrones:
        st.info("No hay datos de 'patrones_dia_semana' disponibles.")
    else:
        df_patrones = pd.DataFrame(patrones)
        if 'dia' in df_patrones.columns and 'promedio_interacciones' in df_patrones.columns:
            fig_patrones = px.bar(
                df_patrones,
                x='dia',
                y='promedio_interacciones',
                title="Promedio de Interacciones por Día de la Semana",
                color='promedio_interacciones'
            )
            st.plotly_chart(fig_patrones, use_container_width=True)
        else:
            st.info("Los datos de patrones por día no tienen las columnas esperadas ('dia','promedio_interacciones').")

    # 3. Horas Pico
    st.subheader("Horas Pico de Actividad")
    
    horas = data.get("horas_pico", [])
    if not horas:
        st.info("No hay datos de 'horas_pico' disponibles.")
    else:
        df_horas = pd.DataFrame(horas)
        if 'hora' in df_horas.columns and 'promedio_actividad' in df_horas.columns:
            fig_horas = px.line(
                df_horas,
                x='hora',
                y='promedio_actividad',
                title="Actividad Promedio por Hora del Día"
            )
            fig_horas.update_layout(
                xaxis_title="Hora del Día",
                yaxis_title="Nivel de Actividad Promedio"
            )
            st.plotly_chart(fig_horas, use_container_width=True)
        else:
            st.info("Los datos de horas pico no tienen las columnas esperadas ('hora','promedio_actividad').")

    # 4. Momentos Destacados
    st.subheader("Momentos Destacados")
    
    momentos = data.get("momentos_destacados", [])
    if not momentos:
        st.info("No hay 'momentos_destacados' para mostrar.")
    else:
        for momento in momentos:
            fecha = momento.get('fecha', 'sin fecha')
            titulo = momento.get('titulo', 'Sin título')
            with st.expander(f"📅 {fecha} - {titulo}", expanded=False):
                inter = momento.get('interacciones')
                try:
                    inter_display = f"{int(inter):,}" if inter is not None else "N/A"
                except Exception:
                    inter_display = str(inter)
                st.write(f"**Interacciones:** {inter_display}")
                st.write(f"**Descripción:** {momento.get('descripcion', '')}")
                if 'tendencia' in momento:
                    st.write(f"**Tendencia:** {momento['tendencia']}")