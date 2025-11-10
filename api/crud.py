from sqlalchemy.orm import Session
from models import User, Client, SocialMediaPost, Comment, SocialMediaInsight
from schemas import UserCreate, ClientCreate, SocialMediaPostCreate, CommentCreate, SocialMediaInsightCreate
from auth import get_password_hash

# User CRUD
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate, client_id: int = None):
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password, client_id=client_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

def update_user_email(db: Session, user_id: int, new_email: str):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db_user.email = new_email
        db.commit()
        db.refresh(db_user)
    return db_user

def update_user_password(db: Session, user_id: int, new_password: str):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db_user.hashed_password = get_password_hash(new_password)
        db.commit()
        db.refresh(db_user)
    return db_user

# Client CRUD
def get_client(db: Session, client_id: int):
    return db.query(Client).filter(Client.id == client_id).first()

def get_clients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Client).offset(skip).limit(limit).all()

def create_client(db: Session, client: ClientCreate):
    db_client = Client(name=client.name)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

# SocialMediaPost CRUD
def create_social_media_post(db: Session, post: SocialMediaPostCreate):
    db_post = SocialMediaPost(**post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

# Comment CRUD
def create_comment(db: Session, comment: CommentCreate):
    db_comment = Comment(**comment.dict())
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

# SocialMediaInsight CRUD
def create_social_media_insight(db: Session, insight: SocialMediaInsightCreate):
    db_insight = SocialMediaInsight(**insight.dict())
    db.add(db_insight)
    db.commit()
    db.refresh(db_insight)
    return db_insight

def get_social_media_insights_by_client(db: Session, client_id: int, skip: int = 0, limit: int = 100):
    return db.query(SocialMediaInsight).filter(SocialMediaInsight.client_id == client_id).offset(skip).limit(limit).all()

def get_latest_social_media_insight_by_client(db: Session, client_id: int):
    return db.query(SocialMediaInsight).filter(SocialMediaInsight.client_id == client_id).order_by(SocialMediaInsight.id.desc()).first()
