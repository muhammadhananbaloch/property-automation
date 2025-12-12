from sqlalchemy.orm import Session
from app.database.models import Lead, SearchHistory, SearchResult
from datetime import datetime
import json

def create_search_record(db: Session, state: str, city: str, strategy: str):
    """
    1. LOGGING THE SEARCH
    Creates a receipt in the 'Search History' table so the Sidebar can see it.
    """
    search = SearchHistory(
        state=state,
        city=city,
        strategy=strategy,
        created_at=datetime.now()
    )
    db.add(search)
    db.commit()
    db.refresh(search) # Refresh to get the new ID (e.g., Search #1)
    return search

def save_lead(db: Session, data: dict, search_id: int):
    """
    2. SAVING THE LEAD
    Now updated to handle inconsistent API capitalization (Value vs value).
    """
    radar_id = data.get('RadarID')
    if not radar_id:
        return # Skip garbage data

    # A. Extract Owner Info (Safely handling the messy list)
    persons = data.get('Persons', [])
    owner_name = "Unknown"
    phones = []
    emails = []

    if persons and isinstance(persons, list):
        # Take the first person as the primary owner
        p1 = persons[0]
        # Handle EntityName vs FirstName/LastName
        owner_name = p1.get('EntityName') or f"{p1.get('FirstName', '')} {p1.get('LastName', '')}".strip()
        
        # Extract Phones (Checking BOTH 'Value' and 'value')
        raw_phones = p1.get('Phone', [])
        if isinstance(raw_phones, list):
            for p in raw_phones:
                if isinstance(p, dict):
                    # The Fix: Check both upper and lowercase keys
                    val = p.get('Value') or p.get('value')
                    if val:
                        phones.append(val)
        
        # Extract Emails (Checking BOTH 'Value' and 'value')
        raw_emails = p1.get('Email', [])
        if isinstance(raw_emails, list):
            for e in raw_emails:
                if isinstance(e, dict):
                    # The Fix: Check both upper and lowercase keys
                    val = e.get('Value') or e.get('value')
                    if val:
                        emails.append(val)

    # B. Check if Lead already exists in the Vault
    lead = db.query(Lead).filter(Lead.radar_id == radar_id).first()

    if not lead:
        # CREATE NEW LEAD
        lead = Lead(radar_id=radar_id)
        db.add(lead)
    
    # C. Update Fields (Whether new or existing, we update the info)
    lead.address = data.get('Address')
    lead.city = data.get('City')
    lead.state = data.get('State')
    lead.zip_code = data.get('Zip') # Sometimes API uses 'Zip', sometimes 'ZipFive'
    if not lead.zip_code:
        lead.zip_code = data.get('ZipFive')
    
    # Real Estate Stats
    lead.beds = data.get('Beds')
    lead.baths = data.get('Baths')
    lead.sq_ft = data.get('SqFt')
    lead.year_built = data.get('Year') or data.get('YearBuilt') # Handle variations
    lead.estimated_value = data.get('AVM')
    lead.estimated_equity = data.get('Equity') or data.get('AvailableEquity') # Handle variations
    
    # Contact Info
    lead.owner_name = owner_name
    lead.phone_numbers = phones  # Saves automatically as JSON
    lead.email_addresses = emails
    
    # The Safety Net (Save the WHOLE raw data blob just in case)
    lead.raw_property_data = data 
    
    db.commit()

    # D. Link this Lead to the Search (The "Bridge")
    # This says: "This lead was found during Search #1"
    # We check if the link exists first to avoid duplicates
    existing_link = db.query(SearchResult).filter(
        SearchResult.search_id == search_id,
        SearchResult.lead_id == radar_id
    ).first()

    if not existing_link:
        link = SearchResult(search_id=search_id, lead_id=radar_id)
        db.add(link)
        db.commit()

    return lead
