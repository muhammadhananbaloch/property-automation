import time
import json
import os
from datetime import datetime
from app.services.property_radar import PropertyRadarClient
from app.core.criteria_mapper import CriteriaMapper
from app.utils.file_manager import save_leads_locally

# --- HISTORY MANAGER ---
HISTORY_FILE = "purchase_history2.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f: return json.load(f)
        except: pass
    return {"purchased_ids": [], "last_run_date": "2023-01-01"}

def save_history(history_data):
    with open(HISTORY_FILE, 'w') as f: json.dump(history_data, f, indent=2)

# --- HELPER: CHECK IF DATA IS REAL ---
def needs_unlocking(data_list):
    """Returns True if list is empty OR contains only locked 'href' links."""
    if not data_list: return True
    for item in data_list:
        if isinstance(item, dict):
            # If it has 'href' but NO 'Value', it is locked.
            if 'href' in item and not (item.get('Value') or item.get('value') or item.get('Linktext')):
                return True
    return False

def run_weekly_harvest(state, city, strategy):
    list_name = f"Auto_Monitor_{city}_{strategy}"
    print(f"🚀 Starting Harvest: {strategy} in {city}, {state}...")
    
    # 1. LOAD STATE
    history = load_history()
    purchased_set = set(history.get("purchased_ids", []))
    last_run = history.get("last_run_date", "2023-01-01")
    client = PropertyRadarClient()

    # 2. ENSURE TRAP EXISTS
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

    # 3. HARVEST NEW LEADS
    print(f"🚜 Checking for items added since {last_run}...")
    items = client.get_new_list_items(target_list_id, added_since=last_run, limit=2)
    raw_ids = [item.get('RadarID') for item in items if item.get('RadarID')]
    
    # Filter duplicates
    new_ids = [rid for rid in raw_ids if rid not in purchased_set]
    print(f"   🔍 Found {len(new_ids)} new unpurchased leads.")
    
    if not new_ids:
        print("zzz No new leads found.")
        # Update date anyway
        history["last_run_date"] = datetime.now().strftime("%Y-%m-%d")
        save_history(history)
        return

    # 4. ENRICHMENT LOOP
    final_leads = []
    for i, radar_id in enumerate(new_ids):
        # A. Get Property Details
        prop_data = client.get_property_data(radar_id) or {"RadarID": radar_id}
        print(f"   [{i+1}/{len(new_ids)}] Processing {prop_data.get('Address', 'Unknown')}...")

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
        final_leads.append(prop_data)
        purchased_set.add(radar_id)

    # 5. SAVE REPORT
    filename = f"{city}_{strategy}_{datetime.now().strftime('%Y%m%d')}"
    save_leads_locally(final_leads, filename_prefix=filename)
    
    history["purchased_ids"] = list(purchased_set)
    history["last_run_date"] = datetime.now().strftime("%Y-%m-%d")
    save_history(history)
    print(f"\n✅ Harvest Complete. Report: {filename}.xlsx")
