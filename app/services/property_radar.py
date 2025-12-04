import requests
import json
from app.config import Config

class PropertyRadarClient:
    BASE_URL = "https://api.propertyradar.com/v1"

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {Config.PROPERTY_RADAR_TOKEN}",
            "Content-Type": "application/json"
        }

    def search_properties(self, criteria, limit=10, purchase=False):
        url = f"{self.BASE_URL}/properties"
        
        # FIX: Removed 'Sort' parameter entirely to avoid 400 Error
        params = {
            "Purchase": "1" if purchase else "0",
            "Fields": "Overview", 
            "Limit": str(limit),
            "Start": "0"
        }

        payload = {
            "Criteria": criteria
        }

        try:
            print(f"📡 DEBUG: Connecting to {url}")
            print(f"📦 DEBUG: Params: {params}")
            
            response = requests.post(url, headers=self.headers, params=params, json=payload)
            
            # Print raw response to confirm data arrival
            if response.text:
                print(f"📩 DEBUG: RAW RESPONSE: {response.text[:200]}...")

            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            return None
