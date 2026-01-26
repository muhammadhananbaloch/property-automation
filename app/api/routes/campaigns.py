from collections import defaultdict
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import json

from app.database.database import get_db
from app.database.models import Campaign, CampaignLead, Lead, User, Message
from app.api.schemas import CampaignCreate, CampaignResponse, InboxResponse
from app.api.dependencies import get_current_user
from app.services.campaign_service import launch_campaign_task

router = APIRouter(prefix="/api/campaigns", tags=["Campaigns"])

@router.post("/start", response_model=CampaignResponse)
def start_campaign(
    payload: CampaignCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Initializes a campaign and triggers background execution.
    """
    
    # 1. Validation
    if not payload.lead_ids:
        raise HTTPException(status_code=400, detail="Lead list cannot be empty.")

    # 2. Create Campaign
    new_campaign = Campaign(
        user_id=current_user.id,
        name=payload.name,
        template_body=payload.template_body,
        status="processing"
    )
    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)

    # 3. Queue Leads
    valid_leads = db.query(Lead).filter(Lead.radar_id.in_(payload.lead_ids)).all()
    
    if not valid_leads:
         raise HTTPException(status_code=404, detail="No valid leads found in database matching provided IDs.")

    for lead in valid_leads:
        roster = CampaignLead(
            campaign_id=new_campaign.id,
            lead_id=lead.radar_id,
            status="queued"
        )
        db.add(roster)
    
    db.commit()

    # 4. Trigger Background Task
    background_tasks.add_task(launch_campaign_task, new_campaign.id, db)

    # 5. Return Response (MANUAL FIX)
    # We construct the dictionary manually to include 'total_leads'
    return {
        "id": new_campaign.id,
        "name": new_campaign.name,
        "status": new_campaign.status,
        "total_leads": len(valid_leads), # <--- The missing piece!
        "created_at": new_campaign.created_at
    }

@router.get("/", response_model=List[CampaignResponse])
def get_user_campaigns(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves all campaigns associated with the current user."""
    campaigns = db.query(Campaign).filter(Campaign.user_id == current_user.id).order_by(Campaign.created_at.desc()).all()
    
    # We must manually count leads for each campaign to satisfy the schema
    results = []
    for c in campaigns:
        count = db.query(CampaignLead).filter(CampaignLead.campaign_id == c.id).count()
        results.append({
            "id": c.id,
            "name": c.name,
            "status": c.status,
            "total_leads": count, # <--- The missing piece!
            "created_at": c.created_at
        })
        
    return results


# --- INBOX / CONVERSATION ENDPOINT ---

@router.get("/{campaign_id}/inbox", response_model=InboxResponse)
def get_campaign_inbox(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetches the full 'Chat Interface' data for a specific campaign.
    Groups messages by lead and sorts by most recent activity.
    """
    
    # 1. Security: Get Campaign & Verify Ownership
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.user_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # 2. Fetch the Roster (The Leads)
    roster_items = db.query(CampaignLead).filter(
        CampaignLead.campaign_id == campaign_id
    ).all()

    # 3. Fetch all Messages for this Campaign
    all_messages = db.query(Message).filter(
        Message.campaign_id == campaign_id
    ).order_by(Message.created_at.asc()).all()

    # 4. Group Messages by Lead
    msg_map = defaultdict(list)
    for msg in all_messages:
        msg_map[msg.lead_id].append(msg)

    # 5. Build Conversation Objects
    conversations = []
    
    for item in roster_items:
        lead = item.lead
        msgs = msg_map.get(lead.radar_id, [])
        
        # Determine Primary Phone
        display_phone = None
        if lead.phone_numbers:
            phones = lead.phone_numbers
            if isinstance(phones, str):
                try: phones = json.loads(phones)
                except: phones = []
            if isinstance(phones, list) and phones:
                display_phone = phones[0]

        # Calculate Last Activity (for sorting)
        last_active = None
        if msgs:
            last_active = msgs[-1].created_at
        else:
            last_active = campaign.created_at

        conversations.append({
            "lead_id": lead.radar_id,
            "owner_name": lead.owner_name,
            "address": lead.address,
            "phone_number": display_phone,
            "status": item.status,
            "messages": msgs,
            "last_activity_at": last_active
        })

    # 6. Sort: Most recent activity first
    conversations.sort(key=lambda x: x["last_activity_at"] or datetime.min, reverse=True)

    return {
        "campaign_id": campaign.id,
        "campaign_name": campaign.name,
        "conversations": conversations
    }
