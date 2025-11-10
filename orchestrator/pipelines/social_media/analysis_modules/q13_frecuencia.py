from typing import Any, Dict
import pandas as pd
import os
import json

from .base_analyzer import BaseAnalyzer


class Q13Frecuencia(BaseAnalyzer):
	"""Análisis Q13: Frecuencia de Publicación."""

	def __init__(self, openai_client: Any, config: Dict[str, Any]):
		super().__init__(openai_client, config)

	async def analyze(self) -> Dict[str, Any]:
		ingested = self.load_ingested_data()
		posts = ingested.get("posts", [])
		df = pd.DataFrame(posts)

		if df.empty:
			return {"posts_por_dia_promedio_global": None, "frecuencia_por_red": [], "consistencia_desviacion": None, "benchmark_comparativo": {}}

		# Normalizar timestamp
		if "timestamp" in df.columns:
			df["_ts"] = pd.to_datetime(df["timestamp"], errors="coerce")
		else:
			df["_ts"] = pd.NaT

		# Calcular posts por día por red
		freq_list = []
		try:
			for sn, group in df.groupby("social_network"):
				# contar posts por dia
				series = group.set_index("_ts").resample("D").size()
				mean_per_day = float(series.mean()) if not series.empty else 0.0
				std_per_day = float(series.std()) if not series.empty else 0.0
				freq_list.append({"social_network": sn, "posts_per_day": mean_per_day, "std_per_day": std_per_day})
		except Exception:
			freq_list = []

		# Posts por día promedio global
		try:
			all_series = df.set_index("_ts").resample("D").size()
			posts_por_dia_prom = float(all_series.mean()) if not all_series.empty else 0.0
			consistencia = float(all_series.std()) if not all_series.empty else 0.0
		except Exception:
			posts_por_dia_prom = None
			consistencia = None

		# Benchmark: intentar leer q16_benchmark.json para frecuencia
		benchmark = {"competitor_mean_freq": None, "z_score_frecuencia": None}
		try:
			q16_path = os.path.join(self.outputs_dir, "q16_benchmark.json")
			if os.path.exists(q16_path):
				with open(q16_path, "r", encoding="utf-8") as f:
					q16 = json.load(f)
				comp_mean = q16.get("frequency_mean")
				comp_std = q16.get("frequency_std")
				if comp_mean is not None:
					benchmark["competitor_mean_freq"] = float(comp_mean)
				if comp_mean is not None and comp_std:
					if posts_por_dia_prom is not None:
						benchmark["z_score_frecuencia"] = float((posts_por_dia_prom - float(comp_mean)) / float(comp_std))
		except Exception:
			pass

		# Añadir actors: calcular frecuencia por actor (ownerUsername)
		actors = []
		try:
			if "ownerUsername" in df.columns:
				for owner, group in df.groupby("ownerUsername"):
					series = group.set_index("_ts").resample("D").size()
					mean_per_day = float(series.mean()) if not series.empty else 0.0
					actors.append({"actor": owner, "posts_per_day": mean_per_day})
		except Exception:
			actors = []

		result = {
			"posts_por_dia_promedio_global": posts_por_dia_prom,
			"frecuencia_por_red": freq_list,
			"consistencia_desviacion": consistencia,
			"benchmark_comparativo": benchmark,
			"actors": actors
		}

		return result

