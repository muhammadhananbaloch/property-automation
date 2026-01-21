import time
import json
import ast
from sqlalchemy import desc

# Services (The Tools)
from app.services.property_radar import PropertyRadarClient
from app.core.criteria_mapper import CriteriaMapper

# Database (The Memory)
from app.database.database import get_db
from app.database.models import SearchHistory, Lead
from app.database.repository import create_search_record, save_lead

# --- HELPER: ROBUST LIST PARSER (Unchanged) ---
def parse_db_list(value):
    if not value: return []
    if isinstance(value, list): return value
    if isinstance(value, str):
        value = value.strip()
        try: return json.loads(value)
        except: pass
        try: return ast.literal_eval(value)
        except: pass
        return [value]
    return []

# --- HELPER: UNLOCK CHECKER (Unchanged) ---
def needs_unlocking(data_list):
    if not data_list: return False 
    
    has_unlocked = False
    has_locked = False
    
    for item in data_list:
        if isinstance(item, dict):
            val = item.get('Value') or item.get('value') or item.get('Linktext')
            if val: has_unlocked = True
            
            href = item.get('href') or item.get('Href')
            if href and not val: has_locked = True
                
    if has_unlocked: return False
    if has_locked: return True
    return False

# --- MODULE 1: THE SCANNER ---
# PATCH 1: Added user=None to prevent crash from search.py
def scan_target_area(state, city, strategy, user=None):
    """
    PHASE 1: READ-ONLY
    """
    list_name = f"Auto_Monitor_{city}_{strategy}"
    print(f"📡 Scanning: {list_name}...")

    db = next(get_db())
    client = PropertyRadarClient()

    try:
        # ... (Your existing Scan logic remains 100% untouched) ...
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

        print("   📥 Fetching IDs from PropertyRadar...")
        items = client.get_new_list_items(target_list_id, added_since="2020-01-01")
        
        existing_ids = {id[0] for id in db.query(Lead.radar_id).all()}
        
        new_leads_list = []
        owned_ids_found = []

        for item in items:
            rid = item.get('RadarID')
            if not rid: continue

            if rid in existing_ids:
                owned_ids_found.append(rid)
            else:
                new_leads_list.append({
                    "id": rid,
                    "address": item.get('Address', 'Address Pending...'),
                    "owner": item.get('Owner', 'Unknown'),
                    "equity": 0.0
                })

        owned_leads_full = []
        if owned_ids_found:
            db_leads = db.query(Lead).filter(Lead.radar_id.in_(owned_ids_found)).all()
            
            for db_lead in db_leads:
                owned_leads_full.append({
                    "radar_id": db_lead.radar_id,
                    "address": db_lead.address if db_lead.address else "N/A",
                    "city": db_lead.city,
                    "state": db_lead.state,
                    "owner_name": db_lead.owner_name,
                    "is_purchased": True,
                    "equity_value": db_lead.estimated_equity,
                    "estimated_value": db_lead.estimated_value,
                    "beds": db_lead.beds,
                    "baths": db_lead.baths,
                    "sq_ft": db_lead.sq_ft,
                    "year_built": db_lead.year_built,
                    "phone_numbers": parse_db_list(db_lead.phone_numbers),
                    "emails": parse_db_list(db_lead.email_addresses)
                })

        summary = {
            "total_found": len(items),
            "new_count": len(new_leads_list),
            "purchased_count": len(owned_leads_full),
            "leads": new_leads_list,
            "purchased_leads": owned_leads_full
        }
        
        print(f"   ✅ Scan Complete. New: {len(new_leads_list)}, Owned: {len(owned_leads_full)}")
        return summary
    
    finally:
        db.close()

# --- MODULE 2: THE ENRICHER ---
# PATCH 2: Added user=None to receive the user object
def enrich_target_leads(radar_ids: list, state: str, city: str, strategy: str, user=None):
    """
    PHASE 2: WRITE / SPEND
    """
    print(f"🚀 Enriching {len(radar_ids)} leads...")
    
    db = next(get_db())
    client = PropertyRadarClient()
    
    try:
        # PATCH 3: Pass user_id to the repository function so the history is owned
        user_id = user.id if user else None
        current_search = create_search_record(db, state, city, strategy, user_id=user_id)
        
        leads_saved = 0
        
        # ... (Your existing Enrich logic remains 100% untouched) ...
        for i, radar_id in enumerate(radar_ids):
            try:
                print(f"   [{i+1}/{len(radar_ids)}] Fetching {radar_id}...")
                prop_data = client.get_property_data(radar_id) or {"RadarID": radar_id}
                
                persons = client.get_property_owners(radar_id)
                
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
                
                save_lead(db, prop_data, current_search.id)
                leads_saved += 1
                
            except Exception as e:
                print(f"   ❌ Error on {radar_id}: {e}")

        current_search.total_results = leads_saved
        db.commit()
        
        print(f"✅ Batch Complete. {leads_saved} saved.")
        return {"status": "success", "saved_count": leads_saved}
    
    finally:
        db.close()
