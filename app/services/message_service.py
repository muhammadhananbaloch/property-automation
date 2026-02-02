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
    1. Finds ALL leads with this phone number.
    2. Checks message history to find the MOST RECENT conversation context.
    3. Attributes the reply to the correct Campaign and Lead ID.
    """
    
    # 1. Extract Data
    from_number = data.get("From")       
    body = data.get("Body", "")          
    twilio_sid = data.get("MessageSid")  
    
    if not from_number:
        print("Error: No 'From' number in webhook.")
        return

    # 2. Find ALL Leads with this number (not just the first one)
    # We cast to String to allow LIKE search on JSON array
    leads = db.query(Lead).filter(
        cast(Lead.phone_numbers, String).like(f"%{from_number}%")
    ).all()
    
    if not leads:
        print(f"⚠️ Incoming SMS from unknown number: {from_number}")
        return

    # Collect all Lead IDs that match this phone number
    possible_lead_ids = [l.radar_id for l in leads]

    # 3. Find the 'Last Touch' across ALL matching leads
    # We want the most recent OUTBOUND message sent to ANY of these lead IDs.
    last_outbound = db.query(Message).filter(
        Message.lead_id.in_(possible_lead_ids),
        Message.direction.like('outbound%') 
    ).order_by(Message.created_at.desc()).first()
    
    # Defaults
    target_lead_id = leads[0].radar_id # Default to first found if no history
    campaign_id = None

    # If we found a conversation history, stick to that context
    if last_outbound:
        target_lead_id = last_outbound.lead_id
        campaign_id = last_outbound.campaign_id
    else:
        # Fallback: If no messages ever sent, check which Campaign Roster was added to most recently
        last_roster_entry = db.query(CampaignLead).filter(
            CampaignLead.lead_id.in_(possible_lead_ids)
        ).order_by(CampaignLead.created_at.desc()).first()
        
        if last_roster_entry:
            target_lead_id = last_roster_entry.lead_id
            campaign_id = last_roster_entry.campaign_id

    # 4. Save the Message
    new_message = Message(
        campaign_id=campaign_id,
        lead_id=target_lead_id, # <--- Uses the ID from the active conversation
        direction='inbound',
        body=body,
        twilio_sid=twilio_sid,
        status='received',
        to_phone=from_number
    )
    
    try:
        db.add(new_message)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"ℹ️ Message {twilio_sid} already exists. Skipping.")
        return

    # 5. Update Status
    if campaign_id:
        roster_entry = db.query(CampaignLead).filter(
            CampaignLead.campaign_id == campaign_id,
            CampaignLead.lead_id == target_lead_id
        ).first()
        
        if roster_entry:
            roster_entry.status = 'replied'
            db.commit()

    print(f"✅ Inbound SMS linked to Campaign {campaign_id} (Lead: {target_lead_id})")