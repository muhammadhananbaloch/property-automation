import json
from sqlalchemy.orm import Session
from sqlalchemy import cast, String # <--- NEW IMPORT
from twilio.rest import Client

from app.database.models import Message, Lead, CampaignLead, Campaign
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
    cost = None 

    try:
        message = client.messages.create(
            body=payload.body,
            from_=Config.TWILIO_PHONE,
            to=target_phone
        )
        
        # Use actual status from Twilio (usually "queued")
        status = message.status 
        sid = message.sid
        
        # Safe Price Extraction Logic
        if message.price:
            try:
                cost = float(message.price)
            except (ValueError, TypeError):
                cost = None 

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
        cost=cost 
    )
    db.add(new_msg)
    
    # 6. Update Campaign Status
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

# --- NEW: INBOUND LOGIC ---

def handle_inbound_sms(data: dict, db: Session):
    """
    Processes an incoming SMS webhook from Twilio.
    1. Identifies the Lead by Phone Number.
    2. Attributes the reply to the most recent active Campaign.
    3. Saves the message.
    4. Updates Lead status to 'replied'.
    """
    
    # 1. Extract Data from Twilio Webhook
    from_number = data.get("From")       # e.g., "+15550001234"
    body = data.get("Body", "")          # The actual text
    twilio_sid = data.get("MessageSid")  # Unique ID
    
    if not from_number:
        print("Error: No 'From' number in webhook.")
        return

    # 2. Find the Lead
    # FIX: Cast the JSON column to String so we can search it like text
    # This prevents "operator does not exist: json ~~ text" error
    lead = db.query(Lead).filter(
        cast(Lead.phone_numbers, String).like(f"%{from_number}%")
    ).first()
    
    if not lead:
        print(f"⚠️ Incoming SMS from unknown number: {from_number}")
        return

    # 3. Find the 'Last Touch' Campaign
    # We look for the most recent 'outbound' message sent to this lead 
    # to figure out which campaign they are replying to.
    last_outbound = db.query(Message).filter(
        Message.lead_id == lead.radar_id,
        Message.direction.like('outbound%') # Matches 'outbound-api'
    ).order_by(Message.created_at.desc()).first()
    
    campaign_id = last_outbound.campaign_id if last_outbound else None
    
    # Fallback: If no message history, check if they are in ANY active campaign roster
    if not campaign_id:
        active_roster = db.query(CampaignLead).filter(
            CampaignLead.lead_id == lead.radar_id
        ).order_by(CampaignLead.created_at.desc()).first()
        if active_roster:
            campaign_id = active_roster.campaign_id

    # 4. Save the Message
    new_message = Message(
        campaign_id=campaign_id, # Can be Null if we can't link it
        lead_id=lead.radar_id,
        direction='inbound',
        body=body,
        twilio_sid=twilio_sid,
        status='received',
        to_phone=from_number # We store the sender's number here for reference
    )
    
    try:
        db.add(new_message)
        db.commit()
    except Exception as e:
        # If UNIQUE constraint fails (duplicate webhook from Twilio retry), rollback and ignore
        db.rollback()
        print(f"ℹ️ Message {twilio_sid} already exists. Skipping.")
        return

    # 5. Update Roster Status (Mark as 'replied')
    if campaign_id:
        roster_entry = db.query(CampaignLead).filter(
            CampaignLead.campaign_id == campaign_id,
            CampaignLead.lead_id == lead.radar_id
        ).first()
        
        if roster_entry:
            roster_entry.status = 'replied'
            db.commit()

    print(f"✅ Inbound SMS processed for {lead.owner_name} (Campaign {campaign_id})")