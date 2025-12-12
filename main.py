# app/main.py
import sys

# Import the two new modular tools we created
from app.domain.harvest import scan_target_area, enrich_target_leads

# --- CONFIGURATION ---
TARGET_STATE = "VA"
TARGET_CITY = "RICHMOND"
TARGET_STRATEGY = "pre_foreclosure" 

def start_interactive_session():
    print(f"\n🚀 --- ADMIN DASHBOARD SIMULATOR ---")
    print(f"🎯 Target: {TARGET_STRATEGY} in {TARGET_CITY}, {TARGET_STATE}")
    print("------------------------------------------")

    # STEP 1: THE SCAN (Read-Only)
    print("\n[Phase 1] Scanning for leads (Cost: $0)...")
    summary = scan_target_area(TARGET_STATE, TARGET_CITY, TARGET_STRATEGY)

    # Check for errors
    if "error" in summary:
        print(f"❌ Error: {summary['error']}")
        return

    # STEP 2: THE REPORT
    total = summary['total_in_list']
    new_count = summary['new_count']
    new_ids = summary['new_ids']
    purchased_ids = summary['purchased_ids']

    print(f"\n📊 --- SCAN REPORT ---")
    print(f"   Total Leads found in PropertyRadar: {total}")
    print(f"   Already in Database (Owned):        {summary['purchased_count']}")
    print(f"   NEW Leads available to Buy:         {new_count}")
    print("------------------------------------------")

    # STEP 3: THE DECISION LOOP
    target_ids = []

    if new_count > 0:
        # Scenario A: We have new leads
        print(f"💡 You have {new_count} new leads waiting.")
        choice = input("👉 How many do you want to enrich? (Enter number, 'all', or '0' to skip): ").strip().lower()

        if choice == '0' or choice == 'skip':
            print("👋 Skipping enrichment.")
            return
        elif choice == 'all':
            target_ids = new_ids
        elif choice.isdigit():
            count = int(choice)
            target_ids = new_ids[:count] # Slice the list!
        else:
            print("❌ Invalid input.")
            return

    else:
        # Scenario B: No new leads (The "Force Check" Scenario)
        print("zzz No new leads found.")
        choice = input("👉 Do you want to force-enrich OLD leads? (y/n): ").strip().lower()
        
        if choice == 'y':
             # Logic: Maybe we want to update data for leads we already bought?
             # For now, let's just re-process the 'purchased' ones as a test
             print(f"⚠️  Warning: Re-processing {len(purchased_ids)} existing leads.")
             limit_choice = input("   How many? (Enter number or 'all'): ").strip().lower()
             
             if limit_choice == 'all':
                 target_ids = purchased_ids
             elif limit_choice.isdigit():
                 target_ids = purchased_ids[:int(limit_choice)]
        else:
            print("👋 Okay, exiting.")
            return

    # STEP 4: THE ENRICHMENT (Spending Money)
    if target_ids:
        print(f"\n[Phase 2] Enriching {len(target_ids)} leads (Cost: ~${len(target_ids)})...")
        enrich_target_leads(target_ids, TARGET_STATE, TARGET_CITY, TARGET_STRATEGY)
    else:
        print("No leads selected.")

if __name__ == "__main__":
    start_interactive_session()
