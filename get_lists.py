import requests
import json
from app.config import Config

def get_my_lists():
    print("📋 Fetching your lists...")
    
    url = "https://api.propertyradar.com/v1/lists"
    headers = {"Authorization": f"Bearer {Config.PROPERTY_RADAR_TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        # The API wraps everything in 'results'
        lists = data.get('results', [])
        
        print(f"\n✅ Found {len(lists)} lists:")
        print("-" * 40)
        for l in lists:
            print(f"Name: {l.get('ListName')}")
            print(f"ID:   {l.get('ListID')}  <--- USE THIS")
            print(f"Type: {l.get('ListType')}")
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    get_my_lists()
