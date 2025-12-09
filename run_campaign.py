from app.domain.campaign import run_campaign
import os

# --- CONFIGURATION ---
# In a real app, you'd pick this from a list. 
# For now, paste the EXACT name of the Excel file you just generated.
TARGET_FILE = "RICHMOND_pre_foreclosure_20251206.xlsx"

if __name__ == "__main__":
    if os.path.exists(TARGET_FILE):
        # Double check with user before spending money
        confirm = input(f"⚠️  Ready to send SMS to leads in '{TARGET_FILE}'? (yes/no): ")
        if confirm.lower() == "yes":
            run_campaign(TARGET_FILE)
        else:
            print("🚫 Operation cancelled.")
    else:
        print(f"❌ File not found: {TARGET_FILE}")
        print("   (Make sure you generated the Excel file first using main.py)")
