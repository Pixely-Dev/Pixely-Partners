import json
import pandas as pd
from typing import List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_fixed
from openai import AsyncOpenAI
import asyncio
import os

import logging

from .base_analyzer import BaseAnalyzer

class Q3Topicos(BaseAnalyzer):
    def __init__(self, openai_client: AsyncOpenAI, config: Dict[str, Any]):
        super().__init__(openai_client, config)
        self.output_file = os.path.join(self.outputs_dir, "q3_topicos.json")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(15))
    async def _get_topics_from_openai(self, text: str) -> Dict[str, Any]:
        prompt = f"""
        Analiza el siguiente texto de comentarios de redes sociales. Identifica los 3 tópicos principales y el sentimiento general (positivo, negativo, neutral, mixto) asociado a cada tópico.
        Devuelve un JSON con la siguiente estructura:
        {{
            "topicos_principales": [
                {{"topico": "nombre_topico_1", "sentimiento": "positivo/negativo/neutral/mixto", "porcentaje_relevancia": 0.X}},
                {{"topico": "nombre_topico_2", "sentimiento": "positivo/negativo/neutral/mixto", "porcentaje_relevancia": 0.X}},
                {{"topico": "nombre_topico_3", "sentimiento": "positivo/negativo/neutral/mixto", "porcentaje_relevancia": 0.X}}
            ]
        }}
        Texto: {text}
        """
        logging.info(f"Making OpenAI call for topic analysis for text: {text[:100]}...") # Log the call
        response = await self.openai_client.chat.completions.create(
            model=self.config["openai_model"],
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        return json.loads(response.choices[0].message.content)

    async def analyze(self) -> Dict[str, Any]:
        ingested_data = self.load_ingested_data()
        
        if not ingested_data:
            print("No ingested data found for Q3.")
            return {}

        all_posts_analysis = []
        global_topics_summary: Dict[str, float] = {}

        for post in ingested_data.get("posts", []):
            post_url = post.get("post_url", "unknown_url")
            comments = [c for c in ingested_data.get("comments", []) if c.get("post_url") == post_url]
            
            if not comments:
                continue

            consolidated_comments = " ".join([comment.get("comment_text", "") for comment in comments])
            
            if not consolidated_comments.strip():
                continue

            try:
                topics_analysis = await self._get_topics_from_openai(consolidated_comments)
                
                post_topics = {
                    "post_url": post_url,
                    "topicos": topics_analysis.get("topicos_principales", [])
                }
                all_posts_analysis.append(post_topics)

                # Aggregate for global summary
                for topic_info in topics_analysis.get("topicos_principales", []):
                    topic_name = topic_info.get("topico")
                    relevance = topic_info.get("porcentaje_relevancia", 0.0)
                    if topic_name:
                        global_topics_summary[topic_name] = global_topics_summary.get(topic_name, 0.0) + relevance

            except Exception as e:
                print(f"Error analyzing topics for post {post_url}: {e}")
                continue
        
        # Normalize global topic relevance
        total_relevance = sum(global_topics_summary.values())
        if total_relevance > 0:
            for topic in global_topics_summary:
                global_topics_summary[topic] /= total_relevance

        # Sort global topics by relevance and take top 5
        sorted_global_topics = sorted(global_topics_summary.items(), key=lambda item: item[1], reverse=True)[:5]
        final_global_summary = [{"topico": k, "porcentaje_relevancia": v} for k, v in sorted_global_topics]

        output_data = {
            "resumen_global_topicos": final_global_summary,
            "analisis_por_publicacion": all_posts_analysis
        }
        return output_data

if __name__ == "__main__":
    # This part is for testing the Q3 module independently
    # In a real scenario, this would be called by analyze.py
    async def main():
        from dotenv import load_dotenv
        load_dotenv()
        
        # Mock config and OpenAI client for testing
        mock_config = {
            "openai_model": "gpt-4o-mini", # Or your preferred model
            "outputs_dir": "../../outputs"
        }
        mock_openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        q3_analyzer = Q3Topicos(mock_openai_client, mock_config)
        await q3_analyzer.analyze()

    asyncio.run(main())
