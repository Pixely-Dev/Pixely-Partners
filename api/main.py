from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from database import get_db
from schemas import Token, UserCreate, User, ClientCreate, Client, SocialMediaInsight
from crud import create_user, get_user_by_email, create_client, get_client, get_latest_social_media_insight_by_client
from auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user, verify_password

from api.v1 import clients, social_media

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Pixely User API", version="1.0")

# Middleware for logging exceptions
@app.middleware("http")
async def exception_logging_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/users/", response_model=User)
async def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db=db, user=user)

@app.post("/clients/", response_model=Client)
async def create_new_client(client: ClientCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # In a real application, you might want to associate the client with the user creating it
    # For simplicity, we'll just create the client for now.
    return create_client(db=db, client=client)

# Include routers
app.include_router(clients.router, prefix="/api/v1", tags=["clients"])
app.include_router(social_media.router, prefix="/api/v1", tags=["social_media"])
