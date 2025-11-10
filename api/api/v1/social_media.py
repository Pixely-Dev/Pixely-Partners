from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import SocialMediaPost, SocialMediaPostCreate, Comment, CommentCreate, SocialMediaInsight, SocialMediaInsightCreate
from crud import create_social_media_post, create_comment, create_social_media_insight, get_latest_social_media_insight_by_client
from auth import get_current_user

router = APIRouter()

@router.post("/social-media/posts", response_model=SocialMediaPost)
def create_post_endpoint(post: SocialMediaPostCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return create_social_media_post(db=db, post=post)

@router.post("/social-media/comments", response_model=Comment)
def create_comment_endpoint(comment: CommentCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return create_comment(db=db, comment=comment)

@router.post("/social-media/insights", response_model=SocialMediaInsight)
def create_insight_endpoint(insight: SocialMediaInsightCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return create_social_media_insight(db=db, insight=insight)

@router.get("/social-media/insights/client/{client_id}", response_model=SocialMediaInsight)
def get_latest_insight_for_client(client_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    insight = get_latest_social_media_insight_by_client(db, client_id)
    if insight is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No insights found for this client")
    return insight
