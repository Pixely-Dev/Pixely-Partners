from typing import Dict, Any
import logging
import json
import pandas as pd
from .base_analyzer import BaseAnalyzer


class Q8Temporal(BaseAnalyzer):
    """Q8 — Análisis temporal (UTF-8 copy)."""

    def __init__(self, openai_client: Any, config: Dict[str, Any]):
        super().__init__(openai_client, config)

    async def analyze(self) -> Dict[str, Any]:
        ingested = self.load_ingested_data()
        posts = ingested.get("posts", [])
        if not posts:
            logging.warning("Q8: no posts")
            return {}

        df = pd.DataFrame(posts)
        if "fecha_publicacion" in df.columns:
            df["fecha"] = pd.to_datetime(df["fecha_publicacion"], errors="coerce")
        else:
            df["fecha"] = pd.to_datetime(df.get("created_at", pd.Series([None] * len(df))), errors="coerce")

        # Normalizar interacciones
        if "engagement_total" in df.columns:
            df["interacciones"] = pd.to_numeric(df["engagement_total"], errors="coerce").fillna(0)
        elif "interactions" in df.columns:
            df["interacciones"] = pd.to_numeric(df["interactions"], errors="coerce").fillna(0)
        else:
            df["interacciones"] = 0

        # Construir prompt conciso para la llamada a OpenAI (se espera JSON)
        total_posts = len(df)
        date_min = str(df["fecha"].min()) if not df["fecha"].isnull().all() else "N/A"
        date_max = str(df["fecha"].max()) if not df["fecha"].isnull().all() else "N/A"

        prompt = (
            f"Analiza los patrones temporales de actividad entre {date_min} y {date_max}. "
            f"Total publicaciones: {total_posts}. Devuelve un JSON con claves: tendencia_general, patrones_dia_semana, horas_pico, momentos_destacados."
        )

        # Intentar llamada real a la API de OpenAI a través del cliente proporcionado
        try:
            if hasattr(self.openai_client, "chat"):
                logging.info("Q8: llamando a OpenAI (intento real)")
                response = await self.openai_client.chat.completions.create(
                    model=self.config.get("openai_model", "gpt-4"),
                    messages=[
                        {"role": "system", "content": "Eres un analista que responde con JSON estructurado."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                )

                # Extraer texto de la respuesta de forma segura
                try:
                    analysis_text = response.choices[0].message.content
                except Exception:
                    analysis_text = None

                if analysis_text:
                    try:
                        analysis_json = json.loads(analysis_text)
                        return analysis_json
                    except json.JSONDecodeError:
                        logging.warning("Q8: respuesta OpenAI no es JSON, se usará fallback")

        except Exception as e:
            # Registrar la excepción (p. ej. errores de facturación/credenciales)
            logging.error(f"Q8: error llamando a OpenAI: {e}")

        # Fallback estadístico si la llamada falla o no devuelve JSON
        tendencia = df.groupby(df["fecha"].dt.date)["interacciones"].sum().reset_index()
        tendencia_records = [{"fecha": str(r["fecha"]), "interacciones": int(r["interacciones"])} for _, r in tendencia.tail(7).iterrows()]

        return {"tendencia_general": tendencia_records}

        # Return simple aggregated result as placeholder
        tendencia = df.groupby(df["fecha"].dt.date)["interacciones"].sum().reset_index()
        tendencia_records = [{"fecha": str(r["fecha"]), "interacciones": int(r["interacciones"])} for _, r in tendencia.tail(7).iterrows()]

        return {"tendencia_general": tendencia_records}
