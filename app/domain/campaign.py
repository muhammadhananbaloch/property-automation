import pandas as pd
import time
import os
from datetime import datetime
from app.services.sms_service import SmsService
from app.core.templates import MessageTemplates

def run_campaign(file_path):
    print(f"🚀 Starting Campaign on: {file_path}...")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    # 1. Load Data
    try:
        # Load as string to keep leading zeros in zips/phones
        df = pd.read_excel(file_path, dtype=str)
    except Exception as e:
        print(f"❌ Error reading Excel: {e}")
        return

    # Create status columns if they don't exist
    if 'SMS Status' not in df.columns:
        df['SMS Status'] = 'Pending'
    if 'SMS Content' not in df.columns:
        df['SMS Content'] = ''
    
    sms_engine = SmsService()
    messages_sent = 0
    
    print(f"📋 Loaded {len(df)} rows. Starting batch sending...")

    # 2. Iterate Rows
    for index, row in df.iterrows():
        # Skip if already sent to avoid duplicates
        if row.get('SMS Status') == 'Sent':
            continue

        name = row.get('Owner 1 Name')
        phone_raw = str(row.get('Owner 1 Phone', ''))
        address = row.get('Address')
        
        # Validation
        if not phone_raw or phone_raw.lower() in ['nan', 'none', '']:
            print(f"   ⏭️  Skipping {name}: No phone number.")
            df.at[index, 'SMS Status'] = 'Skipped (No Phone)'
            continue
            
        # Handle multiple numbers (Take first one)
        target_phone = phone_raw.split(',')[0].strip()
        
        # 3. Generate & Save Message (The Audit Trail)
        msg_body = MessageTemplates.get_initial_outreach(name, address)
        df.at[index, 'SMS Content'] = msg_body  # <--- SAVING IT HERE
        
        # 4. Send Message
        print(f"   📨 Sending to {name} ({target_phone})...")
        sid = sms_engine.send_sms(target_phone, msg_body)
        
        if sid:
            print(f"      ✅ Sent! SID: {sid}")
            df.at[index, 'SMS Status'] = 'Sent'
            messages_sent += 1
        else:
            print(f"      ❌ Failed.")
            df.at[index, 'SMS Status'] = 'Failed'

        # 5. Safety Delay (Avoid Carrier Filtering)
        time.sleep(1)

    # 3. Save Updated Report
    new_filename = file_path.replace(".xlsx", "_CAMPAIGN.xlsx")
    df.to_excel(new_filename, index=False)
    
    print(f"\n✅ Campaign Finished. {messages_sent} messages sent.")
    print(f"📂 Updated Report Saved: {new_filename}")
