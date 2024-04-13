# nurai/interactions/interactions_router.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from nurai.database.database import get_db
from nurai.interactions.models.interaction import Interaction
from nurai.interactions.requests.interaction_create_request import InteractionCreate


router = APIRouter()


@router.post("/interactions/create_or_update/", response_model=InteractionCreate)
def create_interaction(interaction: InteractionCreate, db: Session = Depends(get_db)):
    """
    Create or update an interaction record based on the thread_ts.
    """
    interaction_data = interaction.dict()
    try:
        new_interaction = Interaction().create_or_update(db=db, **interaction_data)
        return new_interaction
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
