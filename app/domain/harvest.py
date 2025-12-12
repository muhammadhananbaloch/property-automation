import time
from sqlalchemy import desc

# Services (The Tools)
from app.services.property_radar import PropertyRadarClient
from app.core.criteria_mapper import CriteriaMapper

# Database (The Memory)
from app.database.database import get_db
from app.database.models import SearchHistory, Lead
from app.database.repository import create_search_record, save_lead

# --- HELPER: UNLOCK CHECKER ---
def needs_unlocking(data_list):
    """
    Returns True ONLY if we have items that look locked (href) AND we have NO unlocked items.
    """
    if not data_list: return False 
    
    has_unlocked = False
    has_locked = False
    
    for item in data_list:
        if isinstance(item, dict):
            # Check for value (handle capitalization: Value vs value)
            val = item.get('Value') or item.get('value') or item.get('Linktext')
            if val: has_unlocked = True
            
            # Check for lock (href present without value)
            href = item.get('href') or item.get('Href')
            if href and not val: has_locked = True
                
    # If we have at least one unlocked number, we are happy. Don't spend more money.
    if has_unlocked: return False
    # Only unlock if we definitely see a locked item and have no alternative.
    if has_locked: return True
    return False

# --- MODULE 1: THE SCANNER (The Scout) ---
def scan_target_area(state, city, strategy):
    """
    PHASE 1: READ-ONLY
    Scans PropertyRadar for ALL leads in the criteria.
    Returns a summary of what we own vs. what is new.
    Does NOT spend money.
    """
    list_name = f"Auto_Monitor_{city}_{strategy}"
    print(f"📡 Scanning: {list_name}...")

    # Open a temporary DB session just for scanning
    db = next(get_db())
    client = PropertyRadarClient()

    try:
        # 1. Ensure the "Trap" exists (Create list if missing)
        existing_lists = client.get_my_lists()
        target_list_id = next((l['ListID'] for l in existing_lists if l.get('ListName') == list_name), None)
        
        if not target_list_id:
            print("   ⚠️ List not found. Creating it...")
            criteria = CriteriaMapper.build_criteria(state, city, strategy)
            target_list_id = client.create_dynamic_list(list_name, criteria)
            if target_list_id: client.set_list_automation(target_list_id)
            time.sleep(2)
        
        if not target_list_id:
            return {"error": "Could not create/find list."}

        # 2. Fetch IDs (Limit 2000 to catch everything)
        # We use a very old date to ensure we get ALL records, not just new ones.
        print("   📥 Fetching IDs from PropertyRadar...")
        items = client.get_new_list_items(target_list_id, added_since="2020-01-01") # Can add limit=0 param later if needed
        
        # 3. Analyze Data
        all_radar_ids = [item.get('RadarID') for item in items if item.get('RadarID')]
        
        new_leads = []
        already_purchased = []
        
        for rid in all_radar_ids:
            # Ask the Vault: "Do we know this person?"
            exists = db.query(Lead).filter(Lead.radar_id == rid).first()
            if exists and exists.is_purchased:
                already_purchased.append(rid)
            else:
                new_leads.append(rid)

        summary = {
            "list_id": target_list_id,
            "total_in_list": len(all_radar_ids),
            "purchased_count": len(already_purchased),
            "new_count": len(new_leads),
            "new_ids": new_leads, # <--- The Admin will slice this list later!
            "purchased_ids": already_purchased
        }
        
        print(f"   ✅ Scan Complete. Found {len(new_leads)} NEW leads out of {len(all_radar_ids)} total.")
        return summary
    
    finally:
        db.close()

# --- MODULE 2: THE ENRICHER (The Buyer) ---
def enrich_target_leads(radar_ids: list, state: str, city: str, strategy: str):
    """
    PHASE 2: WRITE / SPEND
    Takes a specific list of IDs (selected by Admin).
    Buys them, Unlocks them, Saves them.
    """
    print(f"🚀 Enriching {len(radar_ids)} leads...")
    
    db = next(get_db())
    client = PropertyRadarClient()
    
    try:
        # Create a Receipt for this batch
        current_search = create_search_record(db, state, city, strategy)
        
        leads_saved = 0
        
        for i, radar_id in enumerate(radar_ids):
            try:
                # A. Get Details
                print(f"   [{i+1}/{len(radar_ids)}] Fetching {radar_id}...")
                prop_data = client.get_property_data(radar_id) or {"RadarID": radar_id}
                
                # B. Get Owners
                persons = client.get_property_owners(radar_id)
                
                # C. Unlock Logic (Using the safe 'needs_unlocking' helper)
                if persons:
                    persons.sort(key=lambda x: x.get('isPrimaryContact', 0), reverse=True)
                    for person in persons[:1]: 
                        pkey = person.get('PersonKey')
                        if pkey:
                            if needs_unlocking(person.get('Phone')):
                                print(f"      🔓 Unlocking Phone...")
                                phones = client.unlock_contact_field(pkey, field="Phone")
                                if phones: person['Phone'] = phones
                                time.sleep(0.5)
                            
                            if needs_unlocking(person.get('Email')):
                                print(f"      🔓 Unlocking Email...")
                                emails = client.unlock_contact_field(pkey, field="Email")
                                if emails: person['Email'] = emails
                                time.sleep(0.5)

                prop_data['Persons'] = persons
                
                # D. Save
                save_lead(db, prop_data, current_search.id)
                leads_saved += 1
                
            except Exception as e:
                print(f"   ❌ Error on {radar_id}: {e}")

        # Update stats
        current_search.total_results = leads_saved
        db.commit()
        
        print(f"✅ Batch Complete. {leads_saved} saved.")
        return {"status": "success", "saved": leads_saved}
    
    finally:
        db.close()
