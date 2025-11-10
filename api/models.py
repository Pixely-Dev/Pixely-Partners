from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    client_id = Column(Integer, ForeignKey("clients.id"))

    client = relationship("Client", back_populates="users")

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    seguidores_instagram = Column(Integer, default=0)
    seguidores_tiktok = Column(Integer, default=0)
    seguidores_facebook = Column(Integer, default=0)

    users = relationship("User", back_populates="client")
    social_media_insights = relationship("SocialMediaInsight", back_populates="client")

class SocialMediaPost(Base):
    __tablename__ = "social_media_posts"

    id = Column(Integer, primary_key=True, index=True)
    post_url = Column(String, unique=True, index=True)
    content_type = Column(String)
    likes = Column(Integer)
    comments = Column(Integer)
    is_sponsored = Column(Boolean, default=False)

    comments_rel = relationship("Comment", back_populates="post")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_url = Column(String, ForeignKey("social_media_posts.post_url"))
    content = Column(String)

    post = relationship("SocialMediaPost", back_populates="comments_rel")

class SocialMediaInsight(Base):
    __tablename__ = "social_media_insights"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    q1_emociones_usuario = Column(JSON)
    q2_personalidad_marca = Column(JSON)
    q3_temas = Column(JSON)
    q4_marcos_narrativos = Column(JSON)
    q5_influenciadores = Column(JSON)
    q6_oportunidades = Column(JSON)
    q7_sentimiento_detallado = Column(JSON)
    q8_temporal = Column(JSON)
    q9_recomendaciones = Column(JSON)
    q10_resumen_ejecutivo = Column(JSON)
    q11_engagement = Column(JSON)
    q12_comunidad = Column(JSON)
    q13_frecuencia = Column(JSON)
    q14_formatos = Column(JSON)
    q15_hashtags = Column(JSON)
    q16_benchmark = Column(JSON)
    q17_sentimiento_agrupado = Column(JSON)
    q18_anomalias = Column(JSON)
    q19_correlacion = Column(JSON)
    q20_kpi_global = Column(JSON)

    client = relationship("Client", back_populates="social_media_insights")