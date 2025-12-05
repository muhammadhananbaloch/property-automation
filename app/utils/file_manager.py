import pandas as pd
import json
import os
import re

def flatten_leads_with_owners(leads):
    processed = []
    
    for lead in leads:
        # Make a copy of the FULL property object (Address, Beds, etc.)
        flat_lead = lead.copy()
        
        # Extract Persons and remove the nested list
        persons = flat_lead.pop('Persons', [])
        
        if isinstance(persons, list):
            for i, person in enumerate(persons[:2]):
                prefix = f"Owner {i+1}"
                
                # Name
                if person.get('EntityName'):
                    name = person.get('EntityName')
                else:
                    fname = person.get('FirstName', '')
                    lname = person.get('LastName', '')
                    name = f"{fname} {lname}".strip()
                flat_lead[f"{prefix} Name"] = name
                
                # Phones
                phones = person.get('Phone', [])
                phone_strings = []
                if isinstance(phones, list):
                    for p in phones:
                        if isinstance(p, dict):
                            # Check all casing variations
                            num = p.get('Value') or p.get('value') or p.get('Linktext')
                            if num: phone_strings.append(num)
                        elif isinstance(p, str):
                            phone_strings.append(p)
                flat_lead[f"{prefix} Phone"] = ", ".join(phone_strings)

                # Emails
                emails = person.get('Email', [])
                email_strings = []
                if isinstance(emails, list):
                    for e in emails:
                        if isinstance(e, dict):
                            addr = e.get('Value') or e.get('value') or e.get('Email') 
                            if addr: email_strings.append(addr)
                        elif isinstance(e, str):
                            email_strings.append(e)
                flat_lead[f"{prefix} Email"] = ", ".join(email_strings)
                
                flat_lead[f"{prefix} Type"] = person.get('OwnershipRole', 'Owner')

        processed.append(flat_lead)
    return processed

def save_leads_locally(leads_list, filename_prefix="Virginia_Leads"):
    if not leads_list: return

    # Save JSON Backup
    with open(f"{filename_prefix}.json", "w") as f:
        json.dump(leads_list, f, indent=2)

    print(f"🧹 Formatting {len(leads_list)} records...")
    flat_data = flatten_leads_with_owners(leads_list)
    df = pd.DataFrame(flat_data)

    # --- 1. DYNAMIC CLEANUP ---
    # Drop columns that are completely empty/null/0 across all rows
    for col in df.columns:
        try:
            if pd.api.types.is_numeric_dtype(df[col]) and df[col].sum() == 0:
                df.drop(columns=[col], inplace=True)
                continue
            if df[col].astype(str).str.strip().eq("").all():
                df.drop(columns=[col], inplace=True)
        except: pass 

    # Drop technical IDs we don't need
    blacklist = ['Latitude', 'Longitude', 'id', 'GeocodeQuality', 'RadarID', 'PersonKey']
    df.drop(columns=[c for c in blacklist if c in df.columns], inplace=True, errors='ignore')

    # --- 2. FORMATTING ---
    # Money: Format any column with these words as Currency
    money_keywords = ['Value', 'Amount', 'Balance', 'Equity', 'Price', 'AVM', 'Tax']
    ignore_money = ['Year', 'Beds', 'Baths', 'SqFt', 'Lot', 'Acres', 'Zip']

    for col in df.columns:
        # Booleans -> Yes/No
        if col.startswith('is') or col.startswith('in'):
             df[col] = df[col].apply(lambda x: "Yes" if x in [1, True, '1', 'true'] else "No")
        
        # Money -> $X,XXX
        elif any(k in col for k in money_keywords) and not any(k in col for k in ignore_money):
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                df[col] = df[col].apply(lambda x: f"${x:,.0f}" if x > 0 else "$0")
            except: pass

    # --- 3. HEADERS ---
    new_headers = {}
    for col in df.columns:
        # Add space before caps (OwnerName -> Owner Name)
        friendly = re.sub(r'(?<!^)(?=[A-Z])', ' ', col).title()
        # Manual fixes for clarity
        friendly = friendly.replace("Zip Five", "Zip Code")
        friendly = friendly.replace("P Type", "Property Type")
        friendly = friendly.replace("Sq Ft", "SqFt")
        new_headers[col] = friendly
    df.rename(columns=new_headers, inplace=True)

    # --- 4. DYNAMIC SORTING ---
    # We want specific important columns first, but we keep EVERYTHING else after them.
    priority_order = [
        'Owner 1 Name', 'Owner 1 Phone', 'Owner 1 Email', 
        'Address', 'City', 'State', 'Zip Code',
        'Property Type', 'Advanced Property Type',
        'Beds', 'Baths', 'Sq Ft', 'Year Built',
        'In Tax Delinquency', 'Assessed Value', 'Estimated Value'
    ]
    
    # Map priority names to actual headers
    clean_priority = [new_headers.get(c, c) for c in priority_order] # This handles renames
    # Find which priority columns actually exist
    existing_priority = [c for c in clean_priority if c in df.columns]
    
    # Collect all other columns (Criteria, Flags, etc.) alphabetically
    remaining_cols = sorted([c for c in df.columns if c not in existing_priority])
    
    # Combine
    df = df[existing_priority + remaining_cols]

    # --- 5. SAVE ---
    try:
        df.to_excel(f"{filename_prefix}.xlsx", index=False)
        print(f"✅ EXCEL SAVED: {filename_prefix}.xlsx")
    except Exception as e:
        print(f"❌ Save Error: {e}")
