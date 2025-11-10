import os
import json
import numpy as np
import pandas as pd
import datetime
from typing import Dict, Any
from .base_analyzer import BaseAnalyzer


def run_q16_benchmark(mock_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates benchmark metrics (mean and std dev) for ER and followers.
    This helper is reused by the analyzer implementation below.
    """
    results = {}

    # --- Engagement Rate Calculation ---
    client_er = mock_data.get("client_er")
    competitor_ers = mock_data.get("competitor_ers", [])
    if client_er is not None:
        all_ers = [client_er] + competitor_ers
        if len(all_ers) >= 2:
            results["er_mean"] = float(np.mean(all_ers))
            results["er_std_dev"] = float(np.std(all_ers, ddof=1))
        else:
            results["er_mean"] = float(np.mean(all_ers)) if all_ers else 0.0
            results["er_std_dev"] = 0.0

    # --- Follower Count Calculation ---
    client_followers = mock_data.get("client_followers")
    competitor_followers = mock_data.get("competitor_followers", [])
    if client_followers is not None:
        all_followers = [client_followers] + competitor_followers
        if len(all_followers) >= 2:
            results["followers_mean"] = float(np.mean(all_followers))
            results["followers_std_dev"] = float(np.std(all_followers, ddof=1))
        else:
            results["followers_mean"] = float(np.mean(all_followers)) if all_followers else 0.0
            results["followers_std_dev"] = 0.0

    return results


class Q16Benchmark(BaseAnalyzer):
    """Q16: Benchmark del cliente vs competidores.

    Devuelve estadísticas básicas (media, desviación estándar) para ER y tamaño
    de comunidad. Implementación defensiva: si faltan datos, devuelve valores nulos
    y agrega items en 'errors'.
    """
    def __init__(self, openai_client, config: Dict[str, Any]):
        super().__init__(openai_client, config)

    async def analyze(self) -> Dict[str, Any]:
        result = {
            "metadata": {
                "analysis": "Q16 Benchmark",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
            },
            "benchmark": {},
            "errors": []
        }

        try:
            data = self.load_ingested_data()
            posts = data.get("posts", [])
            client_info = data.get("client_ficha", {})

            # Compute per-post engagement rate using followers from client_ficha according to social_network
            network_followers_map = {
                "Instagram": client_info.get("seguidores_instagram"),
                "TikTok": client_info.get("seguidores_tiktok"),
                "Otra": client_info.get("seguidores_otra_red_x")
            }

            client_posts = [p for p in posts if not p.get("is_competitor")]
            competitor_posts = [p for p in posts if p.get("is_competitor")]

            client_ers = []
            for p in client_posts:
                followers = network_followers_map.get(p.get("social_network"))
                likes = p.get("likesCount", 0) or 0
                comments = p.get("commentsCount", 0) or 0
                if followers and followers > 0:
                    er = (likes + comments) / float(followers)
                    client_ers.append(er)

            client_er_mean = float(np.mean(client_ers)) if client_ers else None

            # For competitors we don't have followers in ingested data; approximate competitor ERs
            # by using (likes+comments)/viewsCount as a proxy per competitor post, then aggregate per competitor.
            comp_ers_per_account = {}
            for p in competitor_posts:
                account = p.get("ownerUsername")
                likes = p.get("likesCount", 0) or 0
                comments = p.get("commentsCount", 0) or 0
                views = p.get("viewsCount") or 0
                if views and views > 0:
                    er_proxy = (likes + comments) / float(views)
                    comp_ers_per_account.setdefault(account, []).append(er_proxy)

            comp_ers = [float(np.mean(v)) for v in comp_ers_per_account.values() if v]
            comp_ers_list = [float(np.mean(v)) for v in comp_ers_per_account.values() if v]

            # Build richer competitor info (name, username, er_mean, followers if available)
            competitor_info = []
            # Attempt to read competitor landscape from client_info; it might be a JSON string or a list
            raw_comp_landscape = client_info.get('competitor_landscape')
            comp_landscape = []
            try:
                if isinstance(raw_comp_landscape, str):
                    comp_landscape = json.loads(raw_comp_landscape)
                elif isinstance(raw_comp_landscape, list):
                    comp_landscape = raw_comp_landscape
            except Exception:
                comp_landscape = []

            # Create a map from instagram handle -> landscape entry
            handle_map = {}
            for entry in comp_landscape:
                # entry instagram may be a URL like https://www.instagram.com/handle/
                insta = entry.get('instagram') or ''
                handle = insta.rstrip('/').split('/')[-1] if insta else entry.get('instagram_username') or entry.get('name')
                handle_map[handle] = entry

            for account, ers in comp_ers_per_account.items():
                er_mean = float(np.mean(ers)) if ers else None
                entry = handle_map.get(account, {})
                followers = None
                # try common keys
                if isinstance(entry, dict):
                    followers = entry.get('instagram_followers') or entry.get('seguidores_instagram')
                competitor_info.append({
                    'name': entry.get('name') if isinstance(entry, dict) else account,
                    'username': account,
                    'er': er_mean,
                    'followers': followers
                })

            mock_input = {
                "client_er": client_er_mean,
                "competitor_ers": [c['er'] for c in competitor_info if c.get('er') is not None],
                "client_followers": sum([v for v in network_followers_map.values() if v]) if network_followers_map else None,
                "competitor_followers": [c.get('followers') for c in competitor_info if c.get('followers') is not None]
            }

            benchmark_results = run_q16_benchmark(mock_input)

            result["benchmark"] = {
                "client_er_mean": client_er_mean,
                # return the richer competitor info for frontend rendering
                "competitor_ers": competitor_info,
                "results": benchmark_results
            }
            # also provide a normalized 'actors' list (client + competitors) for frontend
            client_entry = {
                'actor': client_info.get('client_name') if isinstance(client_info, dict) else 'client',
                'username': client_info.get('client_name', 'client').lower() if isinstance(client_info, dict) else 'client',
                'followers': mock_input.get('client_followers'),
                'er': client_er_mean
            }
            actors_list = [client_entry] + competitor_info
            result['actors'] = actors_list

        except FileNotFoundError as fe:
            result["errors"].append(str(fe))
        except Exception as e:
            result["errors"].append(f"Unexpected error: {e}")

        return result
