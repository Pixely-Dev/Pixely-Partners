
import datetime
from typing import Dict, Any
import pandas as pd
from .base_analyzer import BaseAnalyzer


class Q19Correlacion(BaseAnalyzer):
    """Q19: Correlaciones entre métricas clave (views, likes, comments).

    Devuelve la matriz de correlación (pearson) entre las métricas y una lista de
    los pares con mayor correlación absoluta.
    """

    def __init__(self, openai_client, config: Dict[str, Any]):
        super().__init__(openai_client, config)

    async def analyze(self) -> Dict[str, Any]:
        result = {"metadata": {"analysis": "Q19 Correlacion", "timestamp": datetime.datetime.utcnow().isoformat() + "Z"},
                  "correlation_matrix": {}, "top_pairs": [], "errors": []}

        try:
            data = self.load_ingested_data()
            posts = [p for p in data.get("posts", []) if not p.get("is_competitor")]
            if not posts:
                return result

            df = pd.DataFrame(posts)
            for col in ["viewsCount", "likesCount", "commentsCount"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

            metrics = [c for c in ["viewsCount", "likesCount", "commentsCount"] if c in df.columns]
            if not metrics:
                result["errors"].append("No hay métricas numéricas para correlacionar")
                return result

            corr = df[metrics].corr(method="pearson")
            result["correlation_matrix"] = corr.round(4).to_dict()

            # Flatten to pairs and sort by absolute correlation
            pairs = []
            for i in range(len(metrics)):
                for j in range(i + 1, len(metrics)):
                    a = metrics[i]
                    b = metrics[j]
                    val = corr.loc[a, b]
                    pairs.append({"pair": f"{a}__{b}", "corr": float(val)})

            pairs = sorted(pairs, key=lambda x: abs(x["corr"]), reverse=True)
            result["top_pairs"] = pairs

        except FileNotFoundError as fe:
            result["errors"].append(str(fe))
        except Exception as e:
            result["errors"].append(f"Unexpected error: {e}")

        return result
