from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import Client, ClientCreate
from crud import get_clients, create_client, get_client
from auth import get_current_user

router = APIRouter()

@router.get("/clients", response_model=List[Client])
def read_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    clients = get_clients(db, skip=skip, limit=limit)
    return clients

@router.post("/clients/", response_model=Client)
def create_client_endpoint(client: ClientCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return create_client(db=db, client=client)

@router.get("/clients/me/fiche", response_model=Client) # Using Client schema for FichaCliente as it contains the required fields
def read_client_fiche(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    client_id = current_user.client_id
    if client_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not associated with user")
    client = get_client(db, client_id=client_id)
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return client