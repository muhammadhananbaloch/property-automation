import requests
import json
import time
from app.config import Config

class PropertyRadarClient:
    BASE_URL = "https://api.propertyradar.com/v1"

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {Config.PROPERTY_RADAR_TOKEN}",
            "Content-Type": "application/json"
        }

    # --- 1. SEARCH / LISTS ---
    def get_new_list_items(self, list_id, added_since=None, limit=10):
        url = f"{self.BASE_URL}/lists/{list_id}/items"
        params = {"Limit": str(limit)} 
        if added_since: params["AddedSince"] = added_since

        try:
            print(f"📡 Checking List {list_id}...")
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('results', data)
        except Exception as e:
            print(f"❌ List Error: {e}")
            return []

    # --- 2. GET OWNERS (NAMES ONLY) ---
    def get_property_owners(self, radar_id):
        """
        Fetches the list of owners. 
        CRITICAL FIX: We ONLY ask for 'overview' (Names/IDs). 
        We do NOT ask for 'Phone' here, because that hides the record if unpaid.
        """
        url = f"{self.BASE_URL}/properties/{radar_id}/persons"
        
        # FIX: Removed 'Phone,Email' from fields. This ensures we get the PersonKey.
        params = {"Purchase": "1", "Fields": "overview"} 

        try:
            response = requests.get(url, headers=self.headers, params=params)
            data = response.json()
            return data.get('results', data)
        except:
            return []

    # --- 3. UNLOCK DATA (THE NEW POST METHOD) ---
    def unlock_contact_field(self, person_key, field="Phone"):
        """
        Executes the POST request to buy data for a specific person.
        field: 'Phone' or 'Email'
        """
        # Endpoint: /v1/persons/{Key}/{Field}
        url = f"{self.BASE_URL}/persons/{person_key}/{field}"
        params = {"Purchase": "1"}

        try:
            # POST request is required to unlock
            response = requests.post(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                # Return the list of numbers/emails found
                return data.get('results', data)
            return []
        except Exception as e:
            print(f"⚠️ Unlock Failed for {person_key}: {e}")
            return []
