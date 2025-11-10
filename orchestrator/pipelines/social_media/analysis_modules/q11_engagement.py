from typing import Any, Dict, List
import os
import json

import pandas as pd

from .base_analyzer import BaseAnalyzer


class Q11Engagement(BaseAnalyzer):
	"""
	Cálculo cuantitativo de Engagement (Q11).
	Implementa la interfaz del BaseAnalyzer y devuelve un dict con la estructura esperada:
	{
		"engagement_global_promedio": float,
		"engagement_segmentado_red": List[Dict],
		"serie_temporal_er": List[Dict],
		"benchmark_comparativo": Dict
	}
	"""

	def __init__(self, openai_client: Any, config: Dict[str, Any]):
		super().__init__(openai_client, config)

	async def analyze(self) -> Dict[str, Any]:
		"""
		Carga datos ingeridos y calcula métricas de engagement.
		Nota: método pensado como cálculo cuantitativo (no llamadas a LLM).
		"""
		ingested = self.load_ingested_data()

		posts = ingested.get("posts", [])
		if not posts:
			return {
				"engagement_global_promedio": None,
				"engagement_segmentado_red": [],
				"serie_temporal_er": [],
				"benchmark_comparativo": {"z_score_er": None, "competitor_mean_er": None}
			}

		# Crear DataFrame y normalizar columnas
		df = pd.DataFrame(posts)

		# Normalizar columnas numéricas y valores vacíos
		for col in ["likesCount", "commentsCount", "viewsCount"]:
			if col in df.columns:
				df[col] = pd.to_numeric(df[col], errors="coerce")
			else:
				df[col] = pd.NA

		# Interacciones (definición simple: likes + comments)
		df["interactions"] = df["likesCount"].fillna(0) + df["commentsCount"].fillna(0)

		# Obtener seguidores por red desde client_ficha si está disponible
		client_ficha = ingested.get("client_ficha", {}) or {}
		followers_map = {
			"instagram": client_ficha.get("seguidores_instagram"),
			"tiktok": client_ficha.get("seguidores_tiktok"),
			# fallback genérico
			"otra_red_x": client_ficha.get("seguidores_otra_red_x")
		}

		def compute_er(row):
			# Primero intentar usar seguidores por red
			sn = str(row.get("social_network", "")).lower()
			followers = None
			if sn and sn in followers_map and followers_map.get(sn):
				followers = followers_map.get(sn)

			interactions = row.get("interactions", 0) or 0
			views = row.get("viewsCount")

			# Preferir tasa sobre seguidores; si no disponible, usar interacciones/views
			try:
				if followers and followers > 0:
					return float(interactions) / float(followers)
				if views and float(views) > 0:
					return float(interactions) / float(views)
			except Exception:
				return None
			return None

		df["er_interaction"] = df.apply(compute_er, axis=1)

		# Engagement global promedio (media de ER por post)
		engagement_global_promedio = None
		try:
			engagement_global_promedio = float(df["er_interaction"].dropna().mean())
		except Exception:
			engagement_global_promedio = None

		# Segmentación por red social
		engagement_segmentado = []
		try:
			grouped = df.groupby("social_network")["er_interaction"].mean()
			for sn, val in grouped.items():
				engagement_segmentado.append({"social_network": sn, "engagement_rate": None if pd.isna(val) else float(val)})
		except Exception:
			engagement_segmentado = []

		# Serie temporal semanal del ER
		serie_temporal = []
		if "timestamp" in df.columns:
			try:
				df["_ts"] = pd.to_datetime(df["timestamp"], errors="coerce")
				weekly = df.set_index("_ts")["er_interaction"].resample("W").mean()
				for ts, val in weekly.items():
					serie_temporal.append({"week_start": ts.strftime("%Y-%m-%d"), "engagement_rate": None if pd.isna(val) else float(val)})
			except Exception:
				serie_temporal = []

		# Intentar cargar benchmark competitivo (Q16) si existe, además calcular medias por red
		benchmark = {"z_score_er": None, "competitor_mean_er": None, "competitor_mean_by_network": {}}
		try:
			# 1) calcular media y std de competidores a partir de posts marcados como is_competitor
			if "is_competitor" in df.columns:
				comp_df = df[df["is_competitor"].astype(str).str.upper() == "TRUE"]
				if not comp_df.empty:
					comp_mean = comp_df["er_interaction"].dropna().mean()
					comp_std = comp_df["er_interaction"].dropna().std()
					benchmark["competitor_mean_er"] = None if pd.isna(comp_mean) else float(comp_mean)

					# medias por red
					try:
						comp_by_net = comp_df.groupby("social_network")["er_interaction"].mean().to_dict()
						# convertir numpy floats a float nativos y omitir NaN
						comp_by_net_clean = {k: (None if pd.isna(v) else float(v)) for k, v in comp_by_net.items()}
						benchmark["competitor_mean_by_network"] = comp_by_net_clean
					except Exception:
						benchmark["competitor_mean_by_network"] = {}

					# z-score comparando engagement_global_promedio con comp_mean si sigma válida
					if benchmark["competitor_mean_er"] is not None and comp_std and not pd.isna(comp_std):
						if engagement_global_promedio is not None:
							z = (engagement_global_promedio - float(benchmark["competitor_mean_er"])) / float(comp_std)
							benchmark["z_score_er"] = float(z)

			# 2) además, si existe archivo q16_benchmark.json (precalculated), usarlo para complementar
			q16_path = os.path.join(self.outputs_dir, "q16_benchmark.json")
			if os.path.exists(q16_path):
				with open(q16_path, "r", encoding="utf-8") as f:
					q16 = json.load(f)
				mu = q16.get("engagement_mean")
				sigma = q16.get("engagement_std")
				if mu is not None and sigma:
					benchmark["competitor_mean_er"] = float(mu)
					if engagement_global_promedio is not None:
						z = (engagement_global_promedio - float(mu)) / float(sigma)
						benchmark["z_score_er"] = float(z)
		except Exception:
			# en caso de cualquier fallo, dejar los valores por defecto (None/empty)
			benchmark = {"z_score_er": None, "competitor_mean_er": None, "competitor_mean_by_network": {}}

		result = {
			"engagement_global_promedio": engagement_global_promedio,
			"engagement_segmentado_red": engagement_segmentado,
			"serie_temporal_er": serie_temporal,
			"benchmark_comparativo": benchmark,
			# Nuevo campo: actors -> lista con métricas por actor (client + competitors)
			"actors": []
		}

		# Build actors list: client aggregated + competitors
		actors: List[Dict[str, Any]] = []

		# Client metrics
		client_posts = df[~df.get("is_competitor", False).astype(bool)] if "is_competitor" in df.columns else df
		client_er = None
		try:
			client_er = float(client_posts["er_interaction"].dropna().mean())
		except Exception:
			client_er = None

		client_entry = {
			"actor": client_ficha.get("client_name") or "client",
			"username": client_ficha.get("client_name", "client").lower() if client_ficha.get("client_name") else "client",
			"followers": {
				"instagram": client_ficha.get("seguidores_instagram"),
				"tiktok": client_ficha.get("seguidores_tiktok"),
				"other": client_ficha.get("seguidores_otra_red_x")
			},
			"er_mean": client_er
		}
		actors.append(client_entry)

		# Competitor metrics: aggregate per ownerUsername
		comp_df = df[df.get("is_competitor") == True] if "is_competitor" in df.columns else df[df.get("is_competitor")]
		comp_by_account = {}
		if not comp_df.empty:
			for _, row in comp_df.iterrows():
				acc = row.get("ownerUsername")
				if not acc:
					continue
				comp_by_account.setdefault(acc, []).append(row.get("er_interaction"))

		# Try to extract competitor follower info from client_ficha competitor_landscape
		raw_comp_landscape = client_ficha.get("competitor_landscape")
		comp_landscape = []
		try:
			if isinstance(raw_comp_landscape, str):
				comp_landscape = json.loads(raw_comp_landscape)
			elif isinstance(raw_comp_landscape, list):
				comp_landscape = raw_comp_landscape
		except Exception:
			comp_landscape = []

		# map handle -> entry
		handle_map = {}
		for entry in comp_landscape:
			insta = entry.get("instagram") or ""
			handle = insta.rstrip('/').split('/')[-1] if insta else entry.get('instagram_username') or entry.get('name')
			handle_map[handle] = entry

		for acc, ers in comp_by_account.items():
			clean_ers = [e for e in ers if e is not None]
			er_mean = float(pd.Series(clean_ers).mean()) if clean_ers else None
			entry = handle_map.get(acc, {})
			followers = None
			if isinstance(entry, dict):
				followers = entry.get('instagram_followers') or entry.get('seguidores_instagram')
			actors.append({
				"actor": entry.get('name') if isinstance(entry, dict) else acc,
				"username": acc,
				"followers": followers,
				"er_mean": er_mean
			})

		result["actors"] = actors

		return result

