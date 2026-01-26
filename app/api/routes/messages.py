from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.api.dependencies import get_current_user
from app.api.schemas import MessageCreate, MessageResponse
from app.services.message_service import send_one_off_message

router = APIRouter(prefix="/api/messages", tags=["Messages"])

@router.post("/send", response_model=MessageResponse)
def send_message(
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Sends a manual message to a specific lead.
    Used for 1-on-1 replies in the chat interface.
    """
    try:
        # We pass logic to the service layer to keep routes clean
        return send_one_off_message(payload, db)
    except ValueError as e:
        # Catch known errors (missing phone, bad lead ID)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Catch unexpected server errors
        print(f"[ERROR] Manual Send Failed: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
