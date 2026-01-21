from sqlalchemy.orm import Session
from app.database.models import Lead, SearchHistory, SearchResult
from datetime import datetime
import json

def create_search_record(db: Session, state: str, city: str, strategy: str, user_id: int = None):
    """
    1. LOGGING THE SEARCH
    Creates a receipt in the 'Search History' table.
    """
    search = SearchHistory(
        state=state,
        city=city,
        strategy=strategy,
        user_id=user_id,
        created_at=datetime.now()
    )
    db.add(search)
    db.commit()
    db.refresh(search) 
    return search

def save_lead(db: Session, data: dict, search_id: int):
    """
    2. SAVING THE LEAD
    Updated to mark 'is_purchased = True' so the Scanner knows we own it.
    """
    radar_id = data.get('RadarID')
    if not radar_id:
        return 

    # A. Extract Owner Info
    persons = data.get('Persons', [])
    owner_name = "Unknown"
    phones = []
    emails = []

    if persons and isinstance(persons, list):
        p1 = persons[0]
        owner_name = p1.get('EntityName') or f"{p1.get('FirstName', '')} {p1.get('LastName', '')}".strip()
        
        # Extract Phones (Check both 'Value' and 'value')
        raw_phones = p1.get('Phone', [])
        if isinstance(raw_phones, list):
            for p in raw_phones:
                if isinstance(p, dict):
                    val = p.get('Value') or p.get('value')
                    if val: phones.append(val)
        
        # Extract Emails
        raw_emails = p1.get('Email', [])
        if isinstance(raw_emails, list):
            for e in raw_emails:
                if isinstance(e, dict):
                    val = e.get('Value') or e.get('value')
                    if val: emails.append(val)

    # B. Check/Create Lead
    lead = db.query(Lead).filter(Lead.radar_id == radar_id).first()

    if not lead:
        lead = Lead(radar_id=radar_id)
        db.add(lead)
    
    # --- THE FIX IS HERE ---
    # We explicitly mark this lead as purchased/owned
    lead.is_purchased = True 
    
    # C. Update Fields
    lead.address = data.get('Address')
    lead.city = data.get('City')
    lead.state = data.get('State')
    lead.zip_code = data.get('Zip') or data.get('ZipFive')
    
    lead.beds = data.get('Beds')
    lead.baths = data.get('Baths')
    lead.sq_ft = data.get('SqFt')
    lead.year_built = data.get('Year') or data.get('YearBuilt')
    lead.estimated_value = data.get('AVM')
    lead.estimated_equity = data.get('Equity') or data.get('AvailableEquity')
    
    lead.owner_name = owner_name
    lead.phone_numbers = phones  
    lead.email_addresses = emails
    lead.raw_property_data = data 
    
    db.commit()

    # D. Link to Search
    existing_link = db.query(SearchResult).filter(
        SearchResult.search_id == search_id,
        SearchResult.lead_id == radar_id
    ).first()

    if not existing_link:
        link = SearchResult(search_id=search_id, lead_id=radar_id)
        db.add(link)
        db.commit()

    return lead
