import os
import json
import streamlit as st
import pandas as pd
from .._outputs import get_outputs_dir


def display_q12_comunidad():
	script_dir = os.path.dirname(__file__)
	outputs_dir = get_outputs_dir()
	path = os.path.join(outputs_dir, 'q12_comunidad.json')

	st.header("🏘️ Q12 — Posicionamiento de Comunidad")
	if not os.path.exists(path):
		st.info("Resultados de Q12 no disponibles. Ejecuta el orquestador para generar 'q12_comunidad.json'.")
		return

	try:
		with open(path, 'r', encoding='utf-8') as f:
			data = json.load(f)

		total = data.get('total_seguidores_cliente')
		z = data.get('z_score_tamano_comunidad')
		ranking = data.get('ranking_por_red_social', [])

		col1, col2 = st.columns([2, 3])
		with col1:
			if total is not None:
				if z is not None:
					st.metric(label='Total seguidores (cliente)', value=f"{int(total):,}", delta=f"Z={z:.2f}")
				else:
					st.metric(label='Total seguidores (cliente)', value=f"{int(total):,}")
			else:
				st.write('Total de seguidores no disponible')

		with col2:
			if ranking:
				df = pd.DataFrame(ranking)
				df = df.rename(columns={'social_network': 'red', 'followers': 'followers'})
				df = df.set_index('red')
				st.bar_chart(df['followers'])
			else:
				st.write('No hay ranking por red disponible')

		# If actors present, show a single chart comparing actors' follower counts
		actors = data.get('actors')
		if actors and isinstance(actors, list):
			try:
				df_actors = pd.DataFrame(actors)
				# prefer aggregated followers (instagram) if provided as nested dict
				if 'followers' in df_actors.columns:
					# extract instagram followers where possible
					df_actors['instagram_followers'] = df_actors['followers'].apply(lambda x: x.get('instagram') if isinstance(x, dict) else x)
					st.subheader('Comparativa de tamaño de comunidad por actor (Instagram)')
					st.bar_chart(df_actors.set_index('actor')['instagram_followers'])
			except Exception as e:
				st.write('No fue posible renderizar comparativa por actor:', e)

		st.subheader('Benchmark (detalles)')
		bench = data.get('benchmark_metrics', {})
		if bench:
			col1, col2 = st.columns(2)
			with col1:
				st.metric('Benchmark mu', bench.get('mu'))
				st.metric('Benchmark sigma', bench.get('sigma'))
			with col2:
				# show ranking by social network if present
				if isinstance(bench.get('by_network'), dict):
					import pandas as _pd
					df = _pd.DataFrame([{'red': k, 'mu': v} for k, v in bench.get('by_network').items()])
					df = df.set_index('red')
					st.table(df)
				else:
					st.write('Detalles de benchmark limitados')
		else:
			st.write('No hay métricas de benchmark disponibles')

	except Exception as e:
		st.error(f"Error cargando Q12: {e}")

