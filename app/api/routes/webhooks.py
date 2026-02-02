from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from twilio.request_validator import RequestValidator

from app.database.database import get_db
from app.core.config import Config
from app.services.message_service import handle_inbound_sms

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])

@router.post("/twilio/sms")
async def twilio_sms_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Receives incoming SMS from Twilio.
    Validates signature to ensure security.
    """
    
    # 1. Get the Data (Twilio sends Form Data, NOT JSON)
    form_data = await request.form()
    data = dict(form_data)
    
    # 2. Security Check (Signature Validation)
    # Twilio sends the signature in the header
    signature = request.headers.get("X-Twilio-Signature", "")
    
    # We need the exact URL Twilio thinks it hit.
    # Twilio usually forwards 'X-Forwarded-Proto'.
    url = str(request.url)
    
    # FIX for ngrok: If your API sees 'http' but ngrok is 'https', validation fails.
    if "ngrok" in url and url.startswith("http://"):
        url = url.replace("http://", "https://")

    # Use the Auth Token from your Config
    validator = RequestValidator(Config.TWILIO_TOKEN)
    
    # Validate
    if not validator.validate(url, data, signature):
        # We raise 403 Forbidden if the signature doesn't match
        # print(f"DEBUG: Sig Failed! URL: {url} | Sig: {signature}") # Uncomment to debug
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Twilio Signature")

    # 3. Process Logic
    handle_inbound_sms(data, db)
    
    # 4. Return TwiML
    # Return empty XML so Twilio doesn't auto-reply to the user
    return Response(content="<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response></Response>", media_type="application/xml")