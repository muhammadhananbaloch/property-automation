import pandas as pd
import json
import os
import re

def save_leads_locally(leads_list, filename_prefix="Virginia_Leads"):
    """
    Takes raw API data, cleans it dynamically, formats money/booleans, 
    and saves to both JSON (backup) and Excel (client report).
    """
    if not leads_list:
        print("⚠️ No data to save.")
        return

    # 1. Save RAW JSON (Always keep a backup for offline use)
    json_filename = f"{filename_prefix}.json"
    with open(json_filename, "w") as f:
        json.dump(leads_list, f, indent=2)
    print(f"💾 BACKUP SAVED: {json_filename}")

    print(f"🧹 Dynamically formatting {len(leads_list)} records...")
    df = pd.DataFrame(leads_list)

    # --- STEP 1: DYNAMIC CLEANUP (Remove "Ghost" Columns) ---
    # Remove columns where ALL values are 0, False, None, or empty.
    # This ensures irrelevant flags like 'inForeclosure' don't show up if no one is in foreclosure.
    for col in df.columns:
        try:
            if pd.api.types.is_numeric_dtype(df[col]):
                if df[col].sum() == 0:
                    df.drop(columns=[col], inplace=True)
                    continue
            
            # Check for empty strings/nulls
            if df[col].astype(str).str.strip().eq("").all():
                df.drop(columns=[col], inplace=True)
        except Exception:
            pass 

    # Explicitly drop technical columns we know the client doesn't need
    blacklist = ['Latitude', 'Longitude', 'id', 'GeocodeQuality', 'RadarID']
    df.drop(columns=[c for c in blacklist if c in df.columns], inplace=True, errors='ignore')


    # --- STEP 2: SMART FORMATTING ---
    
    # A. STRICT MONEY KEYWORDS (Only add $ to these)
    # We avoid generic words to prevent formatting 'YearBuilt' or 'Zip' as money.
    money_keywords = ['Value', 'Amount', 'Balance', 'Equity', 'Price', 'AVM', 'Tax']
    
    # B. COLUMNS TO IGNORE (Never format these as money)
    ignore_keywords = ['Year', 'Beds', 'Baths', 'SqFt', 'Lot', 'Acres', 'Zip']

    for col in df.columns:
        # Check 1: Is it a Boolean? (Starts with 'is' or 'in')
        if col.startswith('is') or col.startswith('in'):
             # Convert 1/0 -> Yes/No
             df[col] = df[col].apply(lambda x: "Yes" if x in [1, True, '1', 'true'] else "No")

        # Check 2: Is it Money?
        elif any(k in col for k in money_keywords) and not any(k in col for k in ignore_keywords):
            try:
                # Convert to numeric first
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                # Format: $150,000
                df[col] = df[col].apply(lambda x: f"${x:,.0f}" if x > 0 else "$0")
            except:
                pass # Skip if it fails


    # --- STEP 3: DYNAMIC HEADER RENAMING ---
    # Convert 'OwnerName' -> 'Owner Name'
    new_headers = {}
    for col in df.columns:
        # Regex adds space before capitals
        friendly_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', col)
        
        # Manual overrides for specific weird API names
        if "Zip" in friendly_name: friendly_name = "Zip Code"
        if "P Type" in friendly_name: friendly_name = "Property Type"
        if "Sq Ft" in friendly_name: friendly_name = "Sq Ft"
        
        new_headers[col] = friendly_name.title()

    df.rename(columns=new_headers, inplace=True)

    # --- STEP 4: SMART SORTING ---
    # Prioritize important columns, let the rest follow alphabetically
    priority_order = [
        'Owner Name', 'Address', 'City', 'State', 'Zip Code', 'Phone',
        'Property Type', 'In Tax Delinquency', 'Assessed Value', 'Estimated Value'
    ]
    
    # Find which priority columns actually exist in this dataset
    existing_priority = [c for c in priority_order if c in df.columns]
    # Get the rest
    remaining_cols = sorted([c for c in df.columns if c not in existing_priority])
    
    # Reorder
    df = df[existing_priority + remaining_cols]

    # --- STEP 5: SAVE EXCEL ---
    excel_filename = f"{filename_prefix}.xlsx"
    try:
        df.to_excel(excel_filename, index=False)
        print(f"✅ EXCEL REPORT SAVED: {os.path.abspath(excel_filename)}")
    except Exception as e:
        print(f"❌ Error saving Excel: {e}")
