import time
import json
from sqlalchemy.orm import Session
from twilio.rest import Client

from app.database.models import Campaign, CampaignLead, Message, Lead
from app.core.config import Config

def launch_campaign_task(campaign_id: int, db: Session):
    """
    Executes a campaign background task.
    Iterates through queued leads, parses templates, and sends SMS via Twilio.
    """
    
    # 1. Fetch Campaign Details
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        print(f"[ERROR] Campaign ID {campaign_id} not found. Aborting task.")
        return

    # 2. Initialize Twilio Client
    client = None
    if Config.TWILIO_SID and Config.TWILIO_TOKEN:
        try:
            client = Client(Config.TWILIO_SID, Config.TWILIO_TOKEN)
        except Exception as e:
            print(f"[ERROR] Twilio initialization failed: {e}")

    # 3. Get 'Queued' Leads
    items = db.query(CampaignLead).filter(
        CampaignLead.campaign_id == campaign_id,
        CampaignLead.status == "queued"
    ).all()

    print(f"[INFO] Starting Campaign '{campaign.name}' (ID: {campaign.id}). Lead count: {len(items)}")

    # 4. Processing Loop
    for item in items:
        lead = item.lead
        
        # --- A. Template Parsing ---
        first_name = "Homeowner"
        if lead.owner_name:
            first_name = lead.owner_name.split(" ")[0].title()

        address_display = lead.address if lead.address else "your property"
        city_display = lead.city if lead.city else "your area"

        msg_body = campaign.template_body\
            .replace("{name}", first_name)\
            .replace("{address}", address_display)\
            .replace("{city}", city_display)

        # --- B. Phone Extraction ---
        target_phone = None
        if lead.phone_numbers:
            phones = lead.phone_numbers
            # Handle potential JSON string format from DB
            if isinstance(phones, str):
                try: 
                    phones = json.loads(phones)
                except json.JSONDecodeError: 
                    phones = []
            
            # Select primary number
            if isinstance(phones, list) and len(phones) > 0:
                target_phone = phones[0] 

        # --- C. Send SMS ---
        status = "failed"
        error_msg = None
        sid = None
        
        if client and target_phone and Config.TWILIO_PHONE:
            try:
                message = client.messages.create(
                    body=msg_body,
                    from_=Config.TWILIO_PHONE,
                    to=target_phone
                )
                status = "queued"
                sid = message.sid
                print(f"[INFO] Sent to lead {lead.radar_id} ({target_phone}). SID: {sid}")
            except Exception as e:
                status = "failed"
                error_msg = str(e)
                print(f"[ERROR] Failed to send to {lead.radar_id}: {e}")
        else:
            if not target_phone: 
                error_msg = "No valid phone number found"
            elif not Config.TWILIO_PHONE: 
                error_msg = "Twilio sender number not configured"
            
            print(f"[WARN] Skipping lead {lead.radar_id}: {error_msg}")

        # --- D. Persist Log ---
        new_msg = Message(
            campaign_id=campaign.id,
            lead_id=lead.radar_id,
            direction="outbound-api",
            body=msg_body,
            status=status,
            twilio_sid=sid,
            to_phone=target_phone,
            error_message=error_msg
        )
        db.add(new_msg)
        
        # --- E. Update Status ---
        # Mark as sent if Twilio accepted the request
        item.status = "sent" if status in ["sent", "queued"] else "failed"
        db.commit()

        # Rate Limiting (0.5s delay)
        time.sleep(0.5)

    print(f"[INFO] Campaign '{campaign.name}' execution completed.")
