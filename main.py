import os
import json
from app.services.property_radar import PropertyRadarClient
from app.utils.export import save_leads_locally

# FILE CONFIGURATION
# We use this filename for both the JSON backup and Excel report
DATA_FILENAME = "Virginia_Tax_Delinquent_Leads" 
JSON_FILE = f"{DATA_FILENAME}.json"

def main():
    print("🚀 Starting Pipeline...\n")

    items = []

    # --- STEP 1: THE "OFFLINE" CHECK (Save Money) ---
    if os.path.exists(JSON_FILE):
        print(f"📂 Found local backup: {JSON_FILE}")
        user_input = input("   ❓ Use local data instead of paying for API? (y/n): ").lower()
        
        if user_input == 'y':
            print("   loading local data...")
            with open(JSON_FILE, "r") as f:
                items = json.load(f)
            print(f"   ✅ Loaded {len(items)} leads from file.")

    # --- STEP 2: THE API CALL (Only if needed) ---
    if not items:
        print("📡 Connecting to PropertyRadar API (Cost will apply)...")
        
        client = PropertyRadarClient()
        
        criteria = [
            {"name": "State", "value": ["VA"]},
            {"name": "City", "value": ["RICHMOND"]},
            {"name": "inTaxDelinquency", "value": [1]}
        ]

        # Fetch 50 records
        results = client.search_properties(criteria, limit=50, purchase=True)

        # Extract list safely
        if results:
            if isinstance(results, list):
                items = results
            elif isinstance(results, dict):
                items = results.get('results', results.get('data', []))
        
        if not items:
            print("❌ Pipeline Failed: No data returned from API.")
            return

    # --- STEP 3: EXPORTING (Uses the new cleaning logic) ---
    print(f"📦 Processing {len(items)} leads...")
    save_leads_locally(items, filename_prefix=DATA_FILENAME)
    
    print("\n🎉 Done! Check your folder.")

if __name__ == "__main__":
    main()