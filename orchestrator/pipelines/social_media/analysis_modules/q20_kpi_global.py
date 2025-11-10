
import datetime
from typing import Dict, Any
import numpy as np
import pandas as pd
from .base_analyzer import BaseAnalyzer


class Q20KpiGlobal(BaseAnalyzer):
    """Q20: KPIs Globales de la cuenta.

    Calcula métricas agregadas simples: total de posts, vistas totales, promedio de ER,
    distribución de tipos de contenido y otras métricas útiles para el dashboard.
    """

    def __init__(self, openai_client, config: Dict[str, Any]):
        super().__init__(openai_client, config)

    async def analyze(self) -> Dict[str, Any]:
        result = {"metadata": {"analysis": "Q20 KPI Global", "timestamp": datetime.datetime.utcnow().isoformat() + "Z"},
                  "kpis": {}, "errors": []}

        try:
            data = self.load_ingested_data()
            posts = [p for p in data.get("posts", []) if not p.get("is_competitor")]
            if not posts:
                result["kpis"] = {}
                return result

            df = pd.DataFrame(posts)
            # Ensure numeric
            for col in ["viewsCount", "likesCount", "commentsCount"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

            total_posts = len(df)
            total_views = int(df["viewsCount"].sum()) if "viewsCount" in df.columns else 0
            avg_likes = float(df["likesCount"].mean()) if "likesCount" in df.columns else 0.0
            avg_comments = float(df["commentsCount"].mean()) if "commentsCount" in df.columns else 0.0

            # avg engagement rate per post using (likes + comments) / followers (sum of followers across networks)
            client_info = data.get("client_ficha", {})
            followers_total = sum([v for v in [client_info.get("seguidores_instagram"), client_info.get("seguidores_tiktok"), client_info.get("seguidores_otra_red_x")] if v])
            if followers_total and followers_total > 0:
                df["er_post"] = (df.get("likesCount", 0) + df.get("commentsCount", 0)) / float(followers_total)
                avg_er = float(df["er_post"].mean())
            else:
                avg_er = None

            content_type_counts = df["content_type"].value_counts().to_dict() if "content_type" in df.columns else {}

            result["kpis"] = {
                "total_posts": total_posts,
                "total_views": total_views,
                "avg_likes": avg_likes,
                "avg_comments": avg_comments,
                "avg_engagement_rate": avg_er,
                "content_type_counts": content_type_counts,
                "followers_total": int(followers_total) if followers_total else None
            }
            # Build actors list (client + competitors aggregated KPIs)
            actors = []
            # client entry
            actors.append({
                'actor': client_info.get('client_name') if isinstance(client_info, dict) else 'client',
                'username': client_info.get('client_name', 'client').lower() if isinstance(client_info, dict) else 'client',
                'followers': followers_total,
                'total_posts': total_posts,
                'total_views': total_views,
                'avg_engagement_rate': avg_er
            })

            # competitors: aggregate from posts marked as is_competitor
            all_posts = data.get('posts', [])
            try:
                import pandas as _pd
                df_all = _pd.DataFrame(all_posts)
                if 'is_competitor' in df_all.columns:
                    comp_df = df_all[df_all['is_competitor'] == True]
                    for owner, group in comp_df.groupby('ownerUsername'):
                        tp = int(group.shape[0])
                        views = int(group['viewsCount'].sum()) if 'viewsCount' in group else 0
                        likes = float(group['likesCount'].mean()) if 'likesCount' in group else 0.0
                        actors.append({'actor': owner, 'username': owner, 'total_posts': tp, 'total_views': views, 'avg_likes': likes})
            except Exception:
                pass

            result['actors'] = actors

        except FileNotFoundError as fe:
            result["errors"].append(str(fe))
        except Exception as e:
            result["errors"].append(f"Unexpected error: {e}")

        return result
