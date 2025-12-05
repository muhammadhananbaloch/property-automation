import os
import time
import json
from datetime import datetime
from app.services.property_radar import PropertyRadarClient
from app.utils.export import save_leads_locally

# CONFIGURATION
LIST_ID = "1124721" 
STATE_FILE = "last_run_date.txt"

def is_data_unlocked(data_list):
    """
    Helper to check if the list contains actual data (Values) 
    instead of just 'href' links or empty entries.
    """
    if not data_list or not isinstance(data_list, list):
        return False
        
    for item in data_list:
        # If it's a dictionary, check for the 'Value' or 'value' key (The actual number)
        if isinstance(item, dict):
            if item.get('Value') or item.get('value'):
                return True
        # If it's a raw string (rare), it's unlocked
        elif isinstance(item, str) and len(item) > 5:
            return True
            
    return False

def main():
    print("🚜 Starting Weekly Harvest (Smart Mode)...")
    client = PropertyRadarClient()

    # 1. GET TARGETS
    INPUT_FILE = "Virginia_Tax_Delinquent_Leads.json"
    
    if os.path.exists(INPUT_FILE):
        print(f"📂 Loading {INPUT_FILE}...")
        with open(INPUT_FILE, "r") as f:
            raw_data = json.load(f)
        # Process first 5 for testing
        leads_to_process = raw_data
    else:
        print("❌ JSON file missing.")
        return

    print(f"⚡ Processing {len(leads_to_process)} leads...")

    # 2. ENRICHMENT LOOP
    final_leads = []
    
    for i, prop in enumerate(leads_to_process):
        radar_id = prop.get('RadarID') or prop.get('id')
        address = prop.get('Address', 'Unknown Address')
        
        print(f"\n[{i+1}/{len(leads_to_process)}] Processing {address} ({radar_id})...")
        
        # A. Get Owners
        # We use Purchase=1 here to ensure we see the data if it WAS already bought
        persons = client.get_property_owners(radar_id)
        
        if persons:
            # Sort: Primary Contact first
            persons.sort(key=lambda x: x.get('isPrimaryContact', 0), reverse=True)
            
            for person in persons[:2]: 
                pkey = person.get('PersonKey')
                name = f"{person.get('FirstName', '')} {person.get('LastName', '')}"
                
                if pkey:
                    print(f"   👤 Reviewing: {name}...")
                    
                    # --- SMART CHECK: PHONES ---
                    current_phones = person.get('Phone', [])
                    if is_data_unlocked(current_phones):
                         print(f"      ✅ Phones already unlocked. Skipping purchase.")
                    else:
                         print(f"      🔓 Locked. Buying Phones...")
                         phones = client.unlock_contact_field(pkey, field="Phone")
                         if phones:
                             person['Phone'] = phones
                             print(f"         -> Success! Got {len(phones)} numbers.")
                         else:
                             person['Phone'] = [] # Clear 'href' links if buy failed

                    # --- SMART CHECK: EMAILS ---
                    current_emails = person.get('Email', [])
                    if is_data_unlocked(current_emails):
                         print(f"      ✅ Emails already unlocked. Skipping purchase.")
                    else:
                         print(f"      🔓 Locked. Buying Emails...")
                         emails = client.unlock_contact_field(pkey, field="Email")
                         if emails:
                             person['Email'] = emails
                             print(f"         -> Success! Got {len(emails)} emails.")
                         else:
                             person['Email'] = [] # Clear 'href' links

                    # Polite delay only if we actually hit the API
                    time.sleep(0.2)

        prop['Persons'] = persons
        final_leads.append(prop)

    # 3. SAVE
    filename = f"Final_Smart_Leads_{datetime.now().strftime('%Y%m%d')}"
    save_leads_locally(final_leads, filename_prefix=filename)
    print("\n✅ MISSION ACCOMPLISHED.")

if __name__ == "__main__":
    main()
