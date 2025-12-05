import requests
import json
import time
from config import Config

class PropertyRadarClient:
    BASE_URL = "https://api.propertyradar.com/v1"

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {Config.PROPERTY_RADAR_TOKEN}",
            "Content-Type": "application/json"
        }

    # --- 1. LIST MANAGEMENT ---
    def create_dynamic_list(self, name, criteria):
        """Creates a new dynamic list (Trap) for specific criteria."""
        url = f"{self.BASE_URL}/lists"
        payload = {
            "ListName": name,
            "ListType": "dynamic",
            "isMonitored": 1,
            "Criteria": criteria
        }
        try:
            print(f"🔨 Creating List: {name}...")
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get('results', [{}])[0].get('ListID')
        except Exception as e:
            print(f"❌ Create List Error: {e}")
            if hasattr(response, 'text'): print(response.text)
            return None

    def get_my_lists(self):
        """Fetches all lists."""
        url = f"{self.BASE_URL}/lists"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get('results', [])
        except Exception as e:
            print(f"❌ Get Lists Error: {e}")
            return []

    # --- 2. AUTOMATION SETUP ---
    def set_list_automation(self, list_id, purchase_phone=True, purchase_email=True):
        url = f"{self.BASE_URL}/lists/{list_id}/automations"
        payload = {
            "isEnabled": 1,
            "Triggers": "New Matches",
            "PurchasePhone": 1 if purchase_phone else 0,
            "PurchaseEmail": 1 if purchase_email else 0,
            "SetInterestLevel": 0, "SetStatusLevel": 0
        }
        try:
            print(f"⚙️ Configuring Automation for List {list_id}...")
            requests.put(url, headers=self.headers, json=payload).raise_for_status()
            return True
        except Exception as e:
            print(f"❌ Automation Error: {e}")
            return False

    # --- 3. HARVEST ---
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
            print(f"❌ List Fetch Error: {e}")
            return []

    # --- 4. DATA DETAILS & UNLOCK ---
    def get_property_owners(self, radar_id):
        """Get Names & Keys (Purchase=1 required to see them)"""
        url = f"{self.BASE_URL}/properties/{radar_id}/persons"
        params = {"Purchase": "1", "Fields": "overview"} 
        try:
            response = requests.get(url, headers=self.headers, params=params)
            data = response.json()
            return data.get('results', data)
        except: return []

    def unlock_contact_field(self, person_key, field="Phone"):
        """Explicit POST to unlock data if missing"""
        url = f"{self.BASE_URL}/persons/{person_key}/{field}"
        params = {"Purchase": "1"}
        try:
            response = requests.post(url, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get('results', data)
            return []
        except: return []

    # --- 5. PROPERTY DETAILS (The Missing Piece) ---
    def get_property_data(self, radar_id):
        """
        Fetches the full property record (Beds, Baths, Equity, etc.).
        We use Purchase=0 because we just want to view the data we found.
        """
        url = f"{self.BASE_URL}/properties/{radar_id}"
        params = {"Purchase": "1", "Fields": "Overview"} 

        try:
            response = requests.get(url, headers=self.headers, params=params)
            # No raise_for_status() here to avoid crashing the loop on minor errors
            
            data = response.json()
            # Handle API returning a list vs single object
            results = data.get('results', data)
            
            if isinstance(results, list) and len(results) > 0:
                return results[0]
            return results if isinstance(results, dict) else None
            
        except Exception as e:
            print(f"⚠️ Error fetching property details for {radar_id}: {e}")
            return None
