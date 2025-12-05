import time
from datetime import datetime
from app.services.property_radar import PropertyRadarClient
from app.core.criteria_mapper import CriteriaMapper
from app.utils.file_manager import save_leads_locally

def run_weekly_harvest(state, city, strategy):
    """
    The Core Business Logic:
    1. Checks/Creates the Dynamic List (Trap)
    2. Checks for new items (Harvest)
    3. Enriches them (Skip Trace)
    4. Saves the report
    """
    list_name = f"Auto_Monitor_{city}_{strategy}"
    print(f"🚀 Starting Harvest: {strategy} in {city}, {state}...")
    
    client = PropertyRadarClient()

    # 1. ENSURE TRAP EXISTS
    print("📋 Checking for existing list...")
    existing_lists = client.get_my_lists()
    target_list_id = None
    
    for l in existing_lists:
        if l.get('ListName') == list_name:
            target_list_id = l.get('ListID')
            print(f"   ✅ Found trap: {list_name} (ID: {target_list_id})")
            break
    
    if not target_list_id:
        print("   ⚠️ Trap not found. creating new dynamic list...")
        criteria = CriteriaMapper.build_criteria(state, city, strategy)
        target_list_id = client.create_dynamic_list(list_name, criteria)
        if target_list_id:
            client.set_list_automation(target_list_id)

    if not target_list_id:
        print("❌ Critical Error: Could not get a List ID.")
        return

    # 2. HARVEST NEW LEADS
    print("🚜 Checking for leads...")
    items = client.get_new_list_items(target_list_id, limit=10)
    new_ids = [item.get('RadarID') for item in items if item.get('RadarID')]
    
    if not new_ids:
        print("zzz No leads found in the trap.")
        return

    print(f"⚡ Processing {len(new_ids)} leads...")
    final_leads = []
    
    # 3. ENRICHMENT LOOP
    for i, radar_id in enumerate(new_ids):
        # A. Get Property Details (The House)
        prop_data = client.get_property_data(radar_id) or {"RadarID": radar_id}
        address = prop_data.get('Address', 'Unknown Address')
        
        print(f"   [{i+1}/{len(new_ids)}] Processing {address}...")

        # B. Get Owners (The People)
        persons = client.get_property_owners(radar_id)
        
        # C. Safety Unlock (The Phone)
        if persons:
            persons.sort(key=lambda x: x.get('isPrimaryContact', 0), reverse=True)
            for person in persons[:1]: 
                if not person.get('Phone'): 
                    pkey = person.get('PersonKey')
                    if pkey:
                        print(f"      🔓 Manual Unlock: {person.get('FirstName')}")
                        phones = client.unlock_contact_field(pkey, field="Phone")
                        if phones: person['Phone'] = phones
                        time.sleep(0.5)

        prop_data['Persons'] = persons
        final_leads.append(prop_data)

    # 4. SAVE REPORT
    filename = f"{city}_{strategy}_{datetime.now().strftime('%Y%m%d')}"
    save_leads_locally(final_leads, filename_prefix=filename)
    print(f"\n✅ Harvest Complete. Report: {filename}.xlsx")
