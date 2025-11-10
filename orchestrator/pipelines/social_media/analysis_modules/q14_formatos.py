from typing import Any, Dict
import os
import json

import pandas as pd

from .base_analyzer import BaseAnalyzer

try:
	from scipy.stats import f_oneway
except Exception:
	f_oneway = None


class Q14Formatos(BaseAnalyzer):
	"""Análisis Q14: Efectividad de Formatos (ANOVA)."""

	def __init__(self, openai_client: Any, config: Dict[str, Any]):
		super().__init__(openai_client, config)

	async def analyze(self) -> Dict[str, Any]:
		ingested = self.load_ingested_data()
		posts = ingested.get("posts", [])
		df = pd.DataFrame(posts)

		if df.empty:
			return {"ranking_global": [], "ranking_por_red_social": [], "p_value_general_anova": None}

		# Preparar interacciones y vistas
		for col in ["likesCount", "commentsCount", "viewsCount"]:
			if col in df.columns:
				df[col] = pd.to_numeric(df[col], errors="coerce")
			else:
				df[col] = pd.NA

		df["interactions"] = df["likesCount"].fillna(0) + df["commentsCount"].fillna(0)
		# ER normalizado (interactions / views)
		def safe_div(i, v):
			try:
				if v and float(v) > 0:
					return float(i) / float(v)
			except Exception:
				return None
			return None

		df["er_norm"] = df.apply(lambda r: safe_div(r.get("interactions", 0), r.get("viewsCount")), axis=1)

		# Ranking global por content_type
		ranking_global = []
		try:
			grouped = df.groupby("content_type")["er_norm"].mean()
			for ct, val in grouped.items():
				ranking_global.append({"content_type": ct, "er_promedio": None if pd.isna(val) else float(val)})
		except Exception:
			ranking_global = []

		# Ranking por red social
		ranking_por_red = []
		try:
			for sn, group in df.groupby("social_network"):
				grp = group.groupby("content_type")["er_norm"].mean().to_dict()
				clean = {k: (None if pd.isna(v) else float(v)) for k, v in grp.items()}
				ranking_por_red.append({"social_network": sn, "ranking": clean})
		except Exception:
			ranking_por_red = []

		p_value = None
		# ANOVA: necesita al menos 2 grupos con datos
		try:
			if f_oneway is not None:
				groups = [g.dropna().values for _, g in df.groupby("content_type")["er_norm"]]
				groups = [g for g in groups if len(g) > 0]
				if len(groups) >= 2:
					stat, p = f_oneway(*groups)
					p_value = float(p)
		except Exception:
			p_value = None

		return {"ranking_global": ranking_global, "ranking_por_red_social": ranking_por_red, "p_value_general_anova": p_value}

