import pandas as pd
import json
import os
import re

def flatten_leads_with_owners(leads):
    processed = []
    for lead in leads:
        flat_lead = lead.copy()
        persons = flat_lead.pop('Persons', [])
        
        if isinstance(persons, list):
            for i, person in enumerate(persons[:2]):
                prefix = f"Owner {i+1}"
                
                # Name
                name = person.get('EntityName') or f"{person.get('FirstName', '')} {person.get('LastName', '')}".strip()
                flat_lead[f"{prefix} Name"] = name
                
                # Phones (Handle list of dicts)
                phones = person.get('Phone', [])
                phone_strings = []
                if isinstance(phones, list):
                    for p in phones:
                        if isinstance(p, dict):
                            # Check ALL possible keys
                            val = p.get('Value') or p.get('value') or p.get('Linktext')
                            if val: phone_strings.append(val)
                        elif isinstance(p, str):
                            phone_strings.append(p)
                flat_lead[f"{prefix} Phone"] = ", ".join(phone_strings)

                # Emails
                emails = person.get('Email', [])
                email_strings = []
                if isinstance(emails, list):
                    for e in emails:
                        if isinstance(e, dict):
                            val = e.get('Value') or e.get('value') or e.get('Email')
                            if val: email_strings.append(val)
                        elif isinstance(e, str):
                            email_strings.append(e)
                flat_lead[f"{prefix} Email"] = ", ".join(email_strings)
                flat_lead[f"{prefix} Type"] = person.get('OwnershipRole', 'Owner')

        processed.append(flat_lead)
    return processed

def save_leads_locally(leads_list, filename_prefix="Export"):
    if not leads_list: return
    
    # Save JSON
    with open(f"{filename_prefix}.json", "w") as f:
        json.dump(leads_list, f, indent=2)

    # Flatten
    flat_data = flatten_leads_with_owners(leads_list)
    df = pd.DataFrame(flat_data)

    # Cleanup & Formatting
    blacklist = ['Latitude', 'Longitude', 'id', 'GeocodeQuality', 'RadarID', 'PersonKey']
    df.drop(columns=[c for c in blacklist if c in df.columns], inplace=True, errors='ignore')

    money_keywords = ['Value', 'Amount', 'Balance', 'Equity', 'Price', 'Tax', 'AVM']
    ignore = ['Year', 'Beds', 'Baths', 'SqFt', 'Lot', 'Zip', 'isHighEquity', 'inTaxDelinquency']
    
    for col in df.columns:
        if any(k in col for k in money_keywords) and not any(k in col for k in ignore):
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                df[col] = df[col].apply(lambda x: f"${x:,.0f}" if x > 0 else "$0")
            except: pass
        elif col.startswith('is') or col.startswith('in'):
             df[col] = df[col].apply(lambda x: "Yes" if x in [1, True, '1'] else "No")

    # Headers & Sort
    new_headers = {c: re.sub(r'(?<!^)(?=[A-Z])', ' ', c).title().replace("Zip Five", "Zip Code").replace("P Type", "Property Type") for c in df.columns}
    df.rename(columns=new_headers, inplace=True)
    
    priority = ['Owner 1 Name', 'Owner 1 Phone', 'Owner 1 Email', 'Address', 'City', 'State', 'Zip Code', 'Property Type', 'In Tax Delinquency', 'Assessed Value']
    existing = [c for c in priority if c in df.columns]
    rest = sorted([c for c in df.columns if c not in existing])
    df = df[existing + rest]

    try:
        df.to_excel(f"{filename_prefix}.xlsx", index=False)
        print(f"✅ EXCEL SAVED: {filename_prefix}.xlsx")
    except Exception as e:
        print(f"❌ Save Error: {e}")
