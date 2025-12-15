import sys

# Import our tools
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

    if "error" in summary:
        print(f"❌ Error: {summary['error']}")
        return

    # STEP 2: THE REPORT
    total = summary['total_in_list']
    new_count = summary['new_count']
    owned_count = summary['purchased_count']
    
    new_ids = summary['new_ids']
    purchased_ids = summary['purchased_ids']

    print(f"\n📊 --- SCAN REPORT ---")
    print(f"   Total Leads in List:        {total}")
    print(f"   [A] Already Owned:          {owned_count}")
    print(f"   [B] NEW Leads:              {new_count}")
    print("------------------------------------------")

    # STEP 3: THE MENU (The "Control Panel")
    print("\n❓ What would you like to do?")
    print(f"   1. Enrich NEW leads ({new_count} available)")
    print(f"   2. Update EXISTING leads ({owned_count} available) -- Force Refresh")
    print(f"   3. Exit")
    
    choice = input("\n👉 Enter choice (1/2/3): ").strip()

    target_ids = []
    
    # --- OPTION 1: NEW LEADS ---
    if choice == '1':
        if new_count == 0:
            print("   ⚠️ No new leads to enrich.")
            return
            
        amount = input(f"   How many new leads? (Enter 1-{new_count}, or 'all'): ").strip().lower()
        if amount == 'all':
            target_ids = new_ids
        elif amount.isdigit():
            target_ids = new_ids[:int(amount)]
        else:
            print("   ❌ Invalid amount.")
            return

    # --- OPTION 2: EXISTING LEADS ---
    elif choice == '2':
        if owned_count == 0:
            print("   ⚠️ No existing leads to update.")
            return

        print(f"   ⚠️ WARNING: This will re-check data for {owned_count} leads you already own.")
        amount = input(f"   How many to update? (Enter 1-{owned_count}, or 'all'): ").strip().lower()
        
        if amount == 'all':
            target_ids = purchased_ids
        elif amount.isdigit():
            target_ids = purchased_ids[:int(amount)]
        else:
            print("   ❌ Invalid amount.")
            return

    # --- OPTION 3: EXIT ---
    else:
        print("👋 Exiting.")
        return

    # STEP 4: EXECUTE
    if target_ids:
        print(f"\n[Phase 2] Processing {len(target_ids)} leads...")
        enrich_target_leads(target_ids, TARGET_STATE, TARGET_CITY, TARGET_STRATEGY)
    else:
        print("No leads selected.")
        
if __name__ == "__main__":
    start_interactive_session()
