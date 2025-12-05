import requests
import json
from app.config import Config

def create_dynamic_list():
    print("🚀 Setting up Dynamic List 'Trap'...")
    
    url = "https://api.propertyradar.com/v1/lists"
    
    headers = {
        "Authorization": f"Bearer {Config.PROPERTY_RADAR_TOKEN}",
        "Content-Type": "application/json"
    }

    # CRITERIA: The rules for the trap (Richmond + Tax Delinquent)
    payload = {
        "ListName": "Auto_Monitor_Richmond_Tax_Delinquent",
        "ListType": "dynamic",
        "isMonitored": 1,  # <--- CRITICAL: Updates automatically
        "Criteria": [
            {"name": "State", "value": ["VA"]},
            {"name": "City", "value": ["RICHMOND"]},
            {"name": "inTaxDelinquency", "value": [1]}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ SUCCESS! List Created.")
        print(f"📋 List Name: {data.get('ListName')}")
        print(f"🆔 List ID: {data.get('ListID')} <--- SAVE THIS ID!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if response.text: print(response.text)

if __name__ == "__main__":
    create_dynamic_list()
