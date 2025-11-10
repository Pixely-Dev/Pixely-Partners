
import datetime
from typing import Dict, Any
from .base_analyzer import BaseAnalyzer


class Q17SentimientoAgrupado(BaseAnalyzer):
    """Q17: Agrega sentimiento por segmento (ej. tipo de contenido y red).

    Heurística ligera: si no existen campos de sentimiento en los posts, aplica una
    regla basada en palabras positivas/negativas sobre el `caption`.
    """
    POSITIVE_WORDS = ["bueno", "excelente", "genial", "gracias", "gran", "mejor", "amor", "éxito", "feliz"]
    NEGATIVE_WORDS = ["mal", "malo", "problema", "pobre", "odio", "queja", "triste", "peor"]

    def __init__(self, openai_client, config: Dict[str, Any]):
        super().__init__(openai_client, config)

    def _score_caption(self, caption: str) -> int:
        if not caption:
            return 0
        text = caption.lower()
        score = 0
        for w in self.POSITIVE_WORDS:
            if w in text:
                score += 1
        for w in self.NEGATIVE_WORDS:
            if w in text:
                score -= 1
        return score

    async def analyze(self) -> Dict[str, Any]:
        result = {
            "metadata": {"analysis": "Q17 Sentimiento Agrupado", "timestamp": datetime.datetime.utcnow().isoformat() + "Z"},
            "groups": {},
            "errors": []
        }

        try:
            data = self.load_ingested_data()
            posts = data.get("posts", [])

            # Determine sentiment for each post
            for p in posts:
                # prefer explicit sentiment if present
                sentiment = p.get("sentiment")
                if sentiment is None:
                    score = self._score_caption(p.get("caption", ""))
                    if score > 0:
                        sentiment = "positive"
                    elif score < 0:
                        sentiment = "negative"
                    else:
                        sentiment = "neutral"

                key = f"{p.get('social_network','Unknown')}|{p.get('content_type','Unknown')}"
                grp = result["groups"].setdefault(key, {"count": 0, "positive": 0, "neutral": 0, "negative": 0})
                grp["count"] += 1
                grp[sentiment] += 1

            # Convert counts to percentages for convenience
            for k, v in result["groups"].items():
                cnt = v["count"] or 1
                v["pct_positive"] = v["positive"] / cnt
                v["pct_neutral"] = v["neutral"] / cnt
                v["pct_negative"] = v["negative"] / cnt

            # Build actors sentiment summary (per ownerUsername)
            try:
                owners = {}
                for p in posts:
                    owner = p.get('ownerUsername') or p.get('username') or 'unknown'
                    sent = p.get('sentiment')
                    if sent is None:
                        score = self._score_caption(p.get('caption', ''))
                        if score > 0:
                            sent = 'positive'
                        elif score < 0:
                            sent = 'negative'
                        else:
                            sent = 'neutral'
                    owners.setdefault(owner, {'count': 0, 'positive': 0, 'neutral': 0, 'negative': 0})
                    owners[owner]['count'] += 1
                    owners[owner][sent] += 1

                actors = []
                for owner, stats in owners.items():
                    cnt = stats['count'] or 1
                    actors.append({
                        'actor': owner,
                        'count': cnt,
                        'pct_positive': stats['positive'] / cnt,
                        'pct_neutral': stats['neutral'] / cnt,
                        'pct_negative': stats['negative'] / cnt
                    })
                result['actors'] = actors
            except Exception:
                # ignore actor building errors
                pass

        except FileNotFoundError as fe:
            result["errors"].append(str(fe))
        except Exception as e:
            result["errors"].append(f"Unexpected error: {e}")

        return result
