from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# I. Authentication and Base Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    client_id: Optional[int] = None

    class Config:
        orm_mode = True

# II. Raw Data Models
class ClientBase(BaseModel):
    name: str

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    id: int
    seguidores_instagram: int = 0
    seguidores_tiktok: int = 0
    seguidores_facebook: int = 0

    class Config:
        orm_mode = True

class SocialMediaPostBase(BaseModel):
    post_url: str
    content_type: str
    likes: int
    comments: int
    is_sponsored: bool = False

class SocialMediaPostCreate(SocialMediaPostBase):
    pass

class SocialMediaPost(SocialMediaPostBase):
    id: int

    class Config:
        orm_mode = True

class CommentBase(BaseModel):
    post_url: str
    content: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int

    class Config:
        orm_mode = True

# III. High-Performance Models (Nested Structures)

# Q1, Q2, Q4, Q7, Q18 - Granular Analysis Item
class AnalisisPorPublicacionItem(BaseModel):
    post_url: str
    metrics: Dict[str, Any] = Field(..., description="Diccionario de métricas para la publicación específica")

# Q11, Q12, Q13, Q17 - Comparative Benchmark
class BenchmarkComparativo(BaseModel):
    media_competitiva: float
    desviacion_estandar_competitiva: float
    z_score_cliente: float

# Q1 Emociones
class Q1EmocionesAgregado(BaseModel):
    emocion_principal: str
    distribucion_emociones: Dict[str, float]
    polaridad_general: float # -1 to 1

class Q1EmocionesCompleto(BaseModel):
    analisis_agregado: Q1EmocionesAgregado
    analisis_por_publicacion: List[AnalisisPorPublicacionItem]

# Q2 Personalidad de Marca
class Q2PersonalidadAgregado(BaseModel):
    personalidad_principal: str
    distribucion_personalidades: Dict[str, float]

class Q2PersonalidadCompleta(BaseModel):
    analisis_agregado: Q2PersonalidadAgregado
    analisis_por_publicacion: List[AnalisisPorPublicacionItem]

# Q3 Temas
class Q3TemasItem(BaseModel):
    tema: str
    relevancia: float
    sentimiento_asociado: float

class Q3Temas(BaseModel):
    temas_principales: List[Q3TemasItem]

# Q4 Marcos Narrativos
class Q4MarcosNarrativosAgregado(BaseModel):
    marco_principal: str
    distribucion_marcos: Dict[str, float]

class Q4MarcosNarrativosCompleto(BaseModel):
    analisis_agregado: Q4MarcosNarrativosAgregado
    analisis_por_publicacion: List[AnalisisPorPublicacionItem]

# Q5 Influenciadores
class Q5InfluenciadorItem(BaseModel):
    nombre_usuario: str
    engagement_score: float
    alcance: int

class Q5Influenciadores(BaseModel):
    top_influenciadores: List[Q5InfluenciadorItem]

# Q6 Oportunidades
class Q6OportunidadItem(BaseModel):
    tipo: str
    descripcion: str
    impacto_estimado: str

class Q6Oportunidades(BaseModel):
    oportunidades_identificadas: List[Q6OportunidadItem]

# Q7 Sentimiento Detallado
class Q7SentimientoAgregado(BaseModel):
    polaridad_general: float
    distribucion_polaridad: Dict[str, float]

class Q7SentimientoDetallado(BaseModel):
    analisis_agregado: Q7SentimientoAgregado
    analisis_por_publicacion: List[AnalisisPorPublicacionItem]

# Q8 Temporal
class Q8TemporalItem(BaseModel):
    fecha: datetime
    metricas: Dict[str, Any]

class Q8Temporal(BaseModel):
    tendencia_general: str
    analisis_por_periodo: List[Q8TemporalItem]

# Q9 Recomendaciones
class Q9RecomendacionItem(BaseModel):
    area: str
    recomendacion: str
    prioridad: str

class Q9Recomendaciones(BaseModel):
    recomendaciones_clave: List[Q9RecomendacionItem]

# Q10 Resumen Ejecutivo
class Q10ResumenEjecutivo(BaseModel):
    alerta_prioritaria: str
    resumen_ejecutivo: str

# Q11 Engagement (estructura ampliada para coincidir con el analyzer y la documentación)
class Q11Benchmark(BaseModel):
    z_score_er: Optional[float] = None
    competitor_mean_er: Optional[float] = None
    competitor_mean_by_network: Optional[Dict[str, float]] = None


class Q11Engagement(BaseModel):
    # Retener campo legado por compatibilidad pero añadir la estructura esperada por el analyzer
    engagement_rate_cliente: Optional[float] = None

    # Campos alineados con `docs/q11_engagement.md` y con el output de
    # `orchestrator/pipelines/social_media/analysis_modules/q11_engagement.py`.
    engagement_global_promedio: Optional[float] = None
    engagement_segmentado_red: Optional[List[Dict[str, Any]]] = []
    serie_temporal_er: Optional[List[Dict[str, Any]]] = []
    benchmark_comparativo: Optional[Q11Benchmark] = None
    actors: Optional[List[Dict[str, Any]]] = None

# Q12 Comunidad
class Q12PosicionamientoComunidad(BaseModel):
    z_score_tamano_comunidad: float
    benchmark_comparativo: BenchmarkComparativo

# Q13 Frecuencia
class Q13Frecuencia(BaseModel):
    frecuencia_publicacion_cliente: float
    benchmark_comparativo: BenchmarkComparativo

# Q14 Formatos
class Q14FormatoRankingItem(BaseModel):
    formato: str
    engagement_rate_normalizado: float
    p_value: Optional[float] = None
    significancia_vs_siguiente: Optional[bool] = None

class Q14Formatos(BaseModel):
    ranking_formatos: List[Q14FormatoRankingItem]

# Q15 Hashtags
class Q15HashtagItem(BaseModel):
    hashtag: str
    engagement_promedio: float
    alcance_promedio: int

class Q15Hashtags(BaseModel):
    top_hashtags: List[Q15HashtagItem]

# Q16 Benchmark
# Q16Benchmark removed/commented out as Q16 is disabled in orchestrator/frontend
# class Q16Benchmark(BaseModel):
#     media_competitiva_general: Dict[str, float]
#     desviacion_estandar_competitiva_general: Dict[str, float]

# Q17 Sentimiento Agrupado
class Q17SentimientoAgrupado(BaseModel):
    sentimiento_general_cliente: float
    benchmark_comparativo: BenchmarkComparativo

# Q18 Anomalias
class Q18AnomaliaItem(BaseModel):
    post_url: str
    tipo_anomalia: str
    descripcion: str
    severidad: str

class Q18Anomalias(BaseModel):
    anomalias_detectadas: List[Q18AnomaliaItem]
    analisis_por_publicacion: List[AnalisisPorPublicacionItem] # For detailed anomaly metrics per post

# Q19 Correlacion
class Q19Correlacion(BaseModel):
    r_squared: float
    p_value: float
    variables_correlacionadas: Dict[str, float]

# Q20 KPI Global
class ContribucionPorKpi(BaseModel):
    kpi: str
    contribucion: float # Percentage or weighted value

class Q20KpiGlobal(BaseModel):
    z_score_kpi_global: float
    contribucion_por_kpi: List[ContribucionPorKpi]

# IV. The Final Guardian (SocialMediaInsightCreate)
class SocialMediaInsightCreate(BaseModel):
    client_id: int
    q1_emociones_usuario: Optional[Q1EmocionesCompleto] = None
    q2_personalidad_marca: Optional[Q2PersonalidadCompleta] = None
    q3_temas: Optional[Q3Temas] = None
    q4_marcos_narrativos: Optional[Q4MarcosNarrativosCompleto] = None
    q5_influenciadores: Optional[Q5Influenciadores] = None
    q6_oportunidades: Optional[Q6Oportunidades] = None
    q7_sentimiento_detallado: Optional[Q7SentimientoDetallado] = None
    q8_temporal: Optional[Q8Temporal] = None
    q9_recomendaciones: Optional[Q9Recomendaciones] = None
    q10_resumen_ejecutivo: Optional[Q10ResumenEjecutivo] = None
    q11_engagement: Optional[Q11Engagement] = None
    q12_comunidad: Optional[Q12PosicionamientoComunidad] = None
    q13_frecuencia: Optional[Q13Frecuencia] = None
    q14_formatos: Optional[Q14Formatos] = None
    q15_hashtags: Optional[Q15Hashtags] = None
    # q16_benchmark: Optional[Q16Benchmark] = None  # DISABLED: Q16 commented out
    q17_sentimiento_agrupado: Optional[Q17SentimientoAgrupado] = None
    q18_anomalias: Optional[Q18Anomalias] = None
    q19_correlacion: Optional[Q19Correlacion] = None
    q20_kpi_global: Optional[Q20KpiGlobal] = None

class SocialMediaInsight(SocialMediaInsightCreate):
    id: int

    class Config:
        orm_mode = True