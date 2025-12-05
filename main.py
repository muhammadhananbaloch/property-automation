import os
import time
from datetime import datetime
from app.services.property_radar import PropertyRadarClient
from app.core.criteria_mapper import CriteriaMapper
from app.utils.file_manager import save_leads_locally

# --- CONFIGURATION ---
TARGET_STATE = "VA"
TARGET_CITY = "RICHMOND"
TARGET_STRATEGY = "tax_delinquent" 
LIST_NAME = f"Auto_Monitor_{TARGET_CITY}_{TARGET_STRATEGY}"

def main():
    print(f"🚀 Starting Engine: {TARGET_STRATEGY} in {TARGET_CITY}, {TARGET_STATE}...")
    client = PropertyRadarClient()

    # 1. CHECK / CREATE LIST
    print("📋 Checking for existing list...")
    existing_lists = client.get_my_lists()
    target_list_id = None
    
    for l in existing_lists:
        if l.get('ListName') == LIST_NAME:
            target_list_id = l.get('ListID')
            print(f"   ✅ Found existing list: {LIST_NAME} (ID: {target_list_id})")
            break
    
    if not target_list_id:
        print("   ⚠️ List not found. Creating new dynamic trap...")
        criteria = CriteriaMapper.build_criteria(TARGET_STATE, TARGET_CITY, TARGET_STRATEGY)
        target_list_id = client.create_dynamic_list(LIST_NAME, criteria)
        if target_list_id:
            client.set_list_automation(target_list_id)

    if not target_list_id:
        print("❌ Critical Error: Could not get a List ID.")
        return

    # 2. HARVEST
    print("🚜 Checking for leads...")
    # Limit 10 for safety
    items = client.get_new_list_items(target_list_id, limit=10) 
    
    new_ids = [item.get('RadarID') for item in items if item.get('RadarID')]
    
    if not new_ids:
        print("zzz No leads found in the trap.")
        return

    print(f"⚡ Processing {len(new_ids)} leads...")
    final_leads = []
    
    for i, radar_id in enumerate(new_ids):
        # --- FIX START: Get Full Property Data First ---
        # We need the address, beds, equity, etc.
        # We use a new method 'get_property_data' which calls the main endpoint
        property_data = client.get_property_data(radar_id)
        if not property_data:
             # Fallback to minimal object if fetch fails
             property_data = {"RadarID": radar_id}
        
        address = property_data.get('Address', 'Unknown Address')
        print(f"   [{i+1}/{len(new_ids)}] Processing {address}...")
        # -----------------------------------------------

        # A. Get Owners
        persons = client.get_property_owners(radar_id)
        
        # B. Safety Unlock
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

        # Merge Persons into the FULL Property Data
        property_data['Persons'] = persons
        final_leads.append(property_data)

    # 3. EXPORT
    filename = f"{TARGET_CITY}_{TARGET_STRATEGY}_{datetime.now().strftime('%Y%m%d')}"
    save_leads_locally(final_leads, filename_prefix=filename)
    print(f"\n✅ Done. Report generated: {filename}.xlsx")

if __name__ == "__main__":
    main()
