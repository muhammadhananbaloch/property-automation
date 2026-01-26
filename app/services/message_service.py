import json
from sqlalchemy.orm import Session
from twilio.rest import Client

from app.database.models import Message, Lead, CampaignLead
from app.core.config import Config
from app.api.schemas import MessageCreate

def send_one_off_message(payload: MessageCreate, db: Session):
    """
    Sends a single, immediate SMS to a lead.
    Handles phone number extraction, error logging, and cost capture.
    """
    
    # 1. Fetch Lead
    lead = db.query(Lead).filter(Lead.radar_id == payload.lead_id).first()
    if not lead:
        raise ValueError(f"Lead {payload.lead_id} not found.")

    # 2. Phone Number Logic (The Safety Net)
    target_phone = None
    
    if lead.phone_numbers:
        # DB might store as JSON string or Python list
        phones = lead.phone_numbers
        if isinstance(phones, str):
            try:
                phones = json.loads(phones)
            except json.JSONDecodeError:
                phones = []
        
        # We default to the FIRST number.
        if isinstance(phones, list) and len(phones) > 0:
            target_phone = phones[0]

    if not target_phone:
        raise ValueError("This lead has no valid phone numbers.")

    # 3. Initialize Twilio
    if not Config.TWILIO_SID or not Config.TWILIO_TOKEN or not Config.TWILIO_PHONE:
        raise ValueError("Twilio credentials are not configured.")

    client = Client(Config.TWILIO_SID, Config.TWILIO_TOKEN)
    
    # 4. Send Message
    status = "failed"
    error_msg = None
    sid = None
    cost = None  # <--- NEW: Initialize cost as None

    try:
        message = client.messages.create(
            body=payload.body,
            from_=Config.TWILIO_PHONE,
            to=target_phone
        )
        
        # Use actual status from Twilio (usually "queued")
        status = message.status 
        sid = message.sid
        
        # <--- NEW: Safe Price Extraction Logic
        # Twilio prices come as strings (e.g. "-0.0075"), so we cast safely.
        if message.price:
            try:
                cost = float(message.price)
            except (ValueError, TypeError):
                cost = None # Keep as None if Twilio sends weird data

    except Exception as e:
        status = "failed"
        error_msg = str(e)

    # 5. Save Record
    new_msg = Message(
        campaign_id=payload.campaign_id, 
        lead_id=lead.radar_id,
        direction="outbound-api",
        body=payload.body,
        status=status,
        twilio_sid=sid,
        to_phone=target_phone,
        error_message=error_msg,
        cost=cost  # <--- NEW: Saving the cost to the DB
    )
    db.add(new_msg)
    
    # 6. Update Campaign Status
    # We accept "queued" OR "sent" as success states
    if payload.campaign_id and status in ["queued", "sent"]:
        roster_item = db.query(CampaignLead).filter(
            CampaignLead.campaign_id == payload.campaign_id,
            CampaignLead.lead_id == lead.radar_id
        ).first()
        if roster_item:
            roster_item.status = "sent"

    db.commit()
    db.refresh(new_msg)
    
    return new_msg
