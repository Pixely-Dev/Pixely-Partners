
import datetime
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from .base_analyzer import BaseAnalyzer


class Q18Anomalias(BaseAnalyzer):
    """Q18: Detección de anomalías simples en series de vistas/engagement.

    Método: detecta posts con `viewsCount` fuera de mean +/- 3*std y reporta.
    """

    def __init__(self, openai_client, config: Dict[str, Any]):
        super().__init__(openai_client, config)

    async def analyze(self) -> Dict[str, Any]:
        result = {"metadata": {"analysis": "Q18 Anomalias", "timestamp": datetime.datetime.utcnow().isoformat() + "Z"},
                  "anomalies": [], "errors": []}
        try:
            data = self.load_ingested_data()
            posts = [p for p in data.get("posts", []) if not p.get("is_competitor")]

            if not posts:
                return result

            df = pd.DataFrame(posts)
            if "viewsCount" not in df.columns:
                result["errors"].append("viewsCount no disponible en posts")
                return result

            df["viewsCount"] = pd.to_numeric(df["viewsCount"], errors="coerce").fillna(0)
            mu = df["viewsCount"].mean()
            sigma = df["viewsCount"].std()

            if pd.isna(sigma) or sigma == 0:
                return result

            upper = mu + 3 * sigma
            lower = max(0, mu - 3 * sigma)

            anomalous = df[(df["viewsCount"] > upper) | (df["viewsCount"] < lower)]

            for _, row in anomalous.iterrows():
                result["anomalies"].append({
                    "post_id": row.get("post_id"),
                    "viewsCount": int(row.get("viewsCount", 0)),
                    "reason": "high" if row.get("viewsCount") > upper else "low",
                    "z_score": float((row.get("viewsCount") - mu) / sigma)
                })

            result["summary"] = {"mean_views": float(mu), "std_views": float(sigma), "upper_threshold": float(upper), "lower_threshold": float(lower)}

        except FileNotFoundError as fe:
            result["errors"].append(str(fe))
        except Exception as e:
            result["errors"].append(f"Unexpected error: {e}")

        return result
