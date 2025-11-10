from typing import Any, Dict, List
import os
import json
import re

import pandas as pd

from .base_analyzer import BaseAnalyzer


class Q15Hashtags(BaseAnalyzer):
	"""Análisis Q15: Hashtags Efectivos."""

	def __init__(self, openai_client: Any, config: Dict[str, Any]):
		super().__init__(openai_client, config)

	async def analyze(self) -> Dict[str, Any]:
		ingested = self.load_ingested_data()
		posts = ingested.get("posts", [])
		df = pd.DataFrame(posts)

		if df.empty:
			return {"ranking_hashtags_eficientes": []}

		# preparar campos
		for col in ["likesCount", "commentsCount", "viewsCount"]:
			if col in df.columns:
				df[col] = pd.to_numeric(df[col], errors="coerce")
			else:
				df[col] = pd.NA

		df["interactions"] = df["likesCount"].fillna(0) + df["commentsCount"].fillna(0)

		# extraer hashtags
		def extract_hashtags(text: str) -> List[str]:
			if not text:
				return []
			return re.findall(r"#\w+", text)

		df["hashtags"] = df.get("caption", "").apply(extract_hashtags)
		df_expl = df.explode("hashtags")
		df_expl = df_expl.dropna(subset=["hashtags"])

		if df_expl.empty:
			return {"ranking_hashtags_eficientes": []}

		# calcular er normalizado por hashtag (interactions / views)
		def safe_div(i, v):
			try:
				if v and float(v) > 0:
					return float(i) / float(v)
			except Exception:
				return None
			return None

		df_expl["er_normalizado"] = df_expl.apply(lambda r: safe_div(r.get("interactions", 0), r.get("viewsCount")), axis=1)

		# agrupar por hashtag
		grouped = df_expl.groupby("hashtags").agg(count_posts=("hashtags", "size"), er_mean=("er_normalizado", lambda s: float(s.dropna().mean()) if not s.dropna().empty else None)).reset_index()

		# aplicar umbral minimo de uso
		MIN_USE = 5
		grouped = grouped[grouped["count_posts"] >= MIN_USE]

		# preparar ranking
		ranking = []
		for _, row in grouped.sort_values("er_mean", ascending=False).iterrows():
			ranking.append({
				"hashtag": row["hashtags"],
				"er_normalizado": None if pd.isna(row["er_mean"]) else float(row["er_mean"]),
				"uso": int(row["count_posts"]),
				"sentimiento_asociado": None,
				"topico_dominante": None,
			})

		# Intentar enriquecer con Q17 y Q3 si existen (placeholder)
		# Si existen archivos q17_sentimiento_agrupado.json y q3_topicos.json, podríamos mapear, pero dejamos placeholders por ahora.

		return {"ranking_hashtags_eficientes": ranking}
