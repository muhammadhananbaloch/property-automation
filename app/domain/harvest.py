import time
from datetime import datetime
from sqlalchemy import desc

# Services
from app.services.property_radar import PropertyRadarClient
from app.core.criteria_mapper import CriteriaMapper

# Database Imports
from app.database.database import get_db
from app.database.models import SearchHistory, Lead
from app.database.repository import create_search_record, save_lead

# --- HELPER: SMARTER UNLOCK CHECK ---
def needs_unlocking(data_list):
    """
    Returns True ONLY if we have items that look locked (href) AND we have NO unlocked items.
    Prevents '400 Errors' on empty lists and avoids re-purchasing known numbers.
    """
    if not data_list:
        return False # Empty list = nothing to unlock. Stops the "Not available" error.
    
    has_unlocked = False
    has_locked = False
    
    for item in data_list:
        if isinstance(item, dict):
            # Check for value (handle capitalization: Value vs value)
            val = item.get('Value') or item.get('value') or item.get('Linktext')
            if val:
                has_unlocked = True
            
            # Check for lock (href present without value)
            href = item.get('href') or item.get('Href')
            if href and not val:
                has_locked = True
                
    # If we have at least one unlocked number, we are happy. Don't spend more money.
    if has_unlocked:
        return False
        
    # Only unlock if we definitely see a locked item and have no alternative.
    if has_locked:
        return True
        
    return False

def run_weekly_harvest(state, city, strategy):
    list_name = f"Auto_Monitor_{city}_{strategy}"
    print(f"🚀 Starting Harvest: {strategy} in {city}, {state}...")

    # 1. START DATABASE SESSION
    db = next(get_db())
    
    try:
        # 2. GET LAST RUN DATE
        last_search = db.query(SearchHistory)\
            .filter_by(state=state, city=city, strategy=strategy)\
            .order_by(desc(SearchHistory.created_at))\
            .first()
            
        if last_search:
            last_run = last_search.created_at.strftime("%Y-%m-%d")
            print(f"   📅 Last run found in DB: {last_run}")
        else:
            last_run = "2023-01-01"
            print(f"   📅 First time running this search. Defaulting to {last_run}.")

        # 3. CREATE NEW SEARCH RECORD
        current_search = create_search_record(db, state, city, strategy)
        
        # 4. PREPARE CLIENT
        client = PropertyRadarClient()

        # 5. ENSURE TRAP EXISTS
        print("📋 Checking for existing list...")
        existing_lists = client.get_my_lists()
        target_list_id = next((l['ListID'] for l in existing_lists if l.get('ListName') == list_name), None)
        
        if not target_list_id:
            print("   ⚠️ Trap not found. creating new dynamic list...")
            criteria = CriteriaMapper.build_criteria(state, city, strategy)
            target_list_id = client.create_dynamic_list(list_name, criteria)
            if target_list_id: client.set_list_automation(target_list_id)
            time.sleep(5)

        if not target_list_id:
            print("❌ Critical Error: Could not get a List ID.")
            return

        # 6. HARVEST NEW LEADS
        print(f"🚜 Checking for items added since {last_run}...")
        items = client.get_new_list_items(target_list_id, added_since=last_run, limit=10)
        raw_ids = [item.get('RadarID') for item in items[8:10] if item.get('RadarID')]
        
        # 7. FILTER DUPLICATES
        new_ids = []
        for rid in raw_ids:
            exists = db.query(Lead).filter(Lead.radar_id == rid).first()
            if exists and exists.is_purchased:
                print(f"   ⏭️  Skipping {rid} (Already purchased).")
                continue
            new_ids.append(rid)

        print(f"   🔍 Found {len(new_ids)} new unpurchased leads.")
        
        if not new_ids:
            print("zzz No new leads found.")
            return

        # 8. ENRICHMENT LOOP
        leads_processed = 0
        for i, radar_id in enumerate(new_ids):
            # A. Get Property Details
            prop_data = client.get_property_data(radar_id) or {"RadarID": radar_id}
            address_display = prop_data.get('Address', 'Unknown')
            print(f"   [{i+1}/{len(new_ids)}] Processing {address_display}...")

            # B. Get Owners
            persons = client.get_property_owners(radar_id)
            
            # C. Smart Unlock
            if persons:
                persons.sort(key=lambda x: x.get('isPrimaryContact', 0), reverse=True)
                for person in persons[:1]: 
                    pkey = person.get('PersonKey')
                    
                    if pkey:
                        # Check Phones
                        if needs_unlocking(person.get('Phone')):
                            print(f"      🔓 Unlocking Phone...")
                            phones = client.unlock_contact_field(pkey, field="Phone")
                            if phones: person['Phone'] = phones
                            time.sleep(0.5)
                        
                        # Check Emails
                        if needs_unlocking(person.get('Email')):
                            print(f"      🔓 Unlocking Email...")
                            emails = client.unlock_contact_field(pkey, field="Email")
                            if emails: person['Email'] = emails
                            time.sleep(0.5)

            prop_data['Persons'] = persons
            
            # D. SAVE TO DATABASE
            save_lead(db, prop_data, current_search.id)
            leads_processed += 1

        # 9. UPDATE SEARCH STATS
        current_search.total_results = leads_processed
        db.commit()
        
        print(f"\n✅ Harvest Complete. {leads_processed} leads saved to Database.")

    except Exception as e:
        print(f"❌ Error during harvest: {e}")
    finally:
        db.close()
