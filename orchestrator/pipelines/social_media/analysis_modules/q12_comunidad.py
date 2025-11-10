from typing import Any, Dict
import os
import json

import pandas as pd

from .base_analyzer import BaseAnalyzer


class Q12Comunidad(BaseAnalyzer):
	"""Análisis Q12: Crecimiento / Posicionamiento de Seguidores."""

	def __init__(self, openai_client: Any, config: Dict[str, Any]):
		super().__init__(openai_client, config)

	async def analyze(self) -> Dict[str, Any]:
		ingested = self.load_ingested_data()
		client_ficha = ingested.get("client_ficha", {}) or {}

		# Extraer seguidores por red desde ficha
		seguidores_instagram = client_ficha.get("seguidores_instagram")
		seguidores_tiktok = client_ficha.get("seguidores_tiktok")
		seguidores_otra = client_ficha.get("seguidores_otra_red_x")

		# Total seguidores (sumar los que existan)
		total = 0
		for v in (seguidores_instagram, seguidores_tiktok, seguidores_otra):
			try:
				if v is not None:
					total += float(v)
			except Exception:
				continue

		# Ranking por red social
		ranking_por_red = []
		if seguidores_instagram is not None:
			ranking_por_red.append({"social_network": "Instagram", "followers": float(seguidores_instagram)})
		if seguidores_tiktok is not None:
			ranking_por_red.append({"social_network": "TikTok", "followers": float(seguidores_tiktok)})
		if seguidores_otra is not None:
			ranking_por_red.append({"social_network": "Otra", "followers": float(seguidores_otra)})

		# Intentar obtener benchmark de Q16 (precalculated)
		benchmark = {"mu": None, "sigma": None}
		z_score = None
		try:
			q16_path = os.path.join(self.outputs_dir, "q16_benchmark.json")
			if os.path.exists(q16_path):
				with open(q16_path, "r", encoding="utf-8") as f:
					q16 = json.load(f)
				mu = q16.get("followers_mean") or q16.get("engagement_mean")
				sigma = q16.get("followers_std") or q16.get("engagement_std")
				if mu is not None:
					benchmark["mu"] = float(mu)
				if sigma is not None:
					benchmark["sigma"] = float(sigma)
				# calcular z
				if benchmark.get("mu") is not None and benchmark.get("sigma"):
					z_score = (total - benchmark["mu"]) / benchmark["sigma"]
		except Exception:
			pass

		result = {
			"total_seguidores_cliente": total,
			"z_score_tamano_comunidad": None if z_score is None else float(z_score),
			"ranking_por_red_social": ranking_por_red,
			"benchmark_metrics": benchmark,
		}

		# Nuevo campo: actors con cliente + competidores (si hay landscape)
		actors = []
		actors.append({
			"actor": client_ficha.get("client_name") or "client",
			"username": client_ficha.get("client_name", "client").lower() if client_ficha.get("client_name") else "client",
			"followers": {
				"instagram": seguidores_instagram,
				"tiktok": seguidores_tiktok,
				"other": seguidores_otra
			}
		})

		# parse competitor_landscape if present
		raw_comp_landscape = client_ficha.get("competitor_landscape")
		comp_landscape = []
		try:
			if isinstance(raw_comp_landscape, str):
				comp_landscape = json.loads(raw_comp_landscape)
			elif isinstance(raw_comp_landscape, list):
				comp_landscape = raw_comp_landscape
		except Exception:
			comp_landscape = []

		for entry in comp_landscape:
			actors.append({
				"actor": entry.get("name") or entry.get("instagram") or "competitor",
				"username": (entry.get("instagram") or "").rstrip('/').split('/')[-1] if entry.get("instagram") else None,
				"followers": {
					"instagram": entry.get("instagram_followers") or entry.get("seguidores_instagram"),
					"tiktok": entry.get("tiktok_followers") or entry.get("seguidores_tiktok"),
					"other": entry.get("other_followers") or entry.get("seguidores_otra_red_x")
				}
			})

		result["actors"] = actors

		return result

