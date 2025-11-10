import streamlit as st
import json
import os
from .._outputs import get_outputs_dir

def load_q4_data():
    """Carga los datos del análisis Q4 desde el archivo JSON."""
    outputs_dir = get_outputs_dir()
    json_path = os.path.join(outputs_dir, 'q4_marcos_narrativos.json')

    if not os.path.exists(json_path):
        st.error(f"No se encontró el archivo de resultados en la ruta: {json_path}")
        return None

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError:
        st.error(f"Error al decodificar el archivo JSON: {json_path}")
        return None
    except Exception as e:
        st.error(f"Ocurrió un error inesperado al cargar Q4: {e}")
        return None

def display_q4_marcos_narrativos():
    st.title("📜 Marcos Narrativos")
    st.write("Este análisis identifica los marcos narrativos utilizados en la comunicación de la marca. Ayuda a comprender cómo se cuenta la historia de la marca y qué arquetipos se están empleando.")
    st.header("Q4: Marcos Narrativos")

    data = load_q4_data()
    if data is None:
        return

    if "marcos_narrativos" in data and data["marcos_narrativos"]:
        st.subheader("Marcos Narrativos Identificados")

        for marco in data["marcos_narrativos"]:
            st.markdown(f"**Marco:** {marco.get('marco', 'N/A')}")
            st.markdown(f"**Descripción:** {marco.get('descripcion', 'N/A')}")

            if "ejemplos" in marco and marco["ejemplos"]:
                with st.expander("Ver ejemplos"):
                    for ejemplo in marco["ejemplos"]:
                        st.write(f"- {ejemplo}")
            st.divider()
    else:
        st.warning("No se encontraron datos de marcos narrativos.")