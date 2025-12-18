import requests
import json
import sys

# CONFIG
BASE_URL = "http://127.0.0.1:9999"  

def print_pass(message):
    print(f"✅ PASS: {message}")

def print_fail(message, details=None):
    print(f"❌ FAIL: {message}")
    if details:
        print(f"   Details: {details}")

def run_tests():
    print(f"🚀 Starting API System Check against {BASE_URL}...\n")

    # ---------------------------------------------------------
    # TEST 1: HEALTH CHECK
    # ---------------------------------------------------------
    try:
        r = requests.get(f"{BASE_URL}/")
        if r.status_code == 200:
            print_pass("Health Check (Server is online)")
        else:
            print_fail(f"Health Check returned {r.status_code}")
            return
    except Exception as e:
        print_fail("Could not connect to server", e)
        return

    # ---------------------------------------------------------
    # TEST 2: HISTORY (Read)
    # ---------------------------------------------------------
    try:
        r = requests.get(f"{BASE_URL}/api/history")
        if r.status_code == 200:
            history = r.json()
            count = len(history)
            print_pass(f"History Endpoint (Found {count} past searches)")
        else:
            print_fail(f"History Endpoint returned {r.status_code}")
            history = []
    except Exception as e:
        print_fail("History Request failed", e)
        history = []

    # ---------------------------------------------------------
    # TEST 3: SCAN (The Scout)
    # ---------------------------------------------------------
    payload = {
        "state": "VA",
        "city": "RICHMOND",
        "strategy": "pre_foreclosure"
    }
    
    scan_data = None
    try:
        r = requests.post(f"{BASE_URL}/api/search/scan", json=payload)
        if r.status_code == 200:
            scan_data = r.json()
            # Validate Schema
            if "new_ids" in scan_data and "purchased_ids" in scan_data:
                print_pass(f"Scan Endpoint (Found {scan_data['new_count']} new, {scan_data['purchased_count']} owned)")
            else:
                print_fail("Scan Response missing required fields")
        else:
            print_fail(f"Scan Endpoint returned {r.status_code}", r.text)
    except Exception as e:
        print_fail("Scan Request failed", e)

    # ---------------------------------------------------------
    # TEST 4: HISTORY DETAILS (Drill Down)
    # ---------------------------------------------------------
    # We need a search ID to test this. Let's use the first one from history if available.
    if history:
        latest_search_id = history[0]['id']
        try:
            r = requests.get(f"{BASE_URL}/api/history/{latest_search_id}")
            if r.status_code == 200:
                leads = r.json()
                print_pass(f"History Details (Retrieved {len(leads)} leads for Search #{latest_search_id})")
            else:
                print_fail(f"History Details returned {r.status_code}")
        except Exception as e:
            print_fail("History Details failed", e)
    else:
        print("   ⚠️ Skipping History Details test (No history found yet)")

    # ---------------------------------------------------------
    # TEST 5: ENRICH (The Buyer - SAFETY MODE)
    # ---------------------------------------------------------
    # Strategy: Try to 'enrich' a lead we ALREADY own.
    # This proves the API accepts the request, but your Logic Layer should
    # detect it's already unlocked and NOT charge you $1.
    
    target_id = None
    if scan_data and scan_data['purchased_ids']:
        target_id = scan_data['purchased_ids'][0]
        print(f"\n🧪 Safety Test: Re-enriching known lead {target_id}...")
    elif scan_data and scan_data['new_ids']:
        # If we have NO owned leads, we can't do the safety test safely without buying one.
        # So we skip to avoid accidental charges.
        print("\n⚠️ Skipping Enrich Test to save money (No owned leads to re-test).")
        print("   (To test manually, use the Swagger UI to buy 1 new lead)")
        return
    else:
        print("\n⚠️ Skipping Enrich Test (No leads found in scan).")
        return

    if target_id:
        enrich_payload = {
            "state": "VA",
            "city": "RICHMOND",
            "strategy": "pre_foreclosure",
            "radar_ids": [target_id]
        }
        try:
            r = requests.post(f"{BASE_URL}/api/search/enrich", json=enrich_payload)
            if r.status_code == 200:
                result = r.json()
                # If safety works, it should process successfully
                print_pass(f"Enrich Endpoint (Processed {target_id} successfully)")
                print(f"   Response: {result}")
            else:
                print_fail(f"Enrich Endpoint returned {r.status_code}", r.text)
        except Exception as e:
            print_fail("Enrich Request failed", e)

if __name__ == "__main__":
    run_tests()
