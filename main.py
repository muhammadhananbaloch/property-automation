from app.domain.harvest import run_weekly_harvest

# --- CONFIGURATION ---
# In the future, these variables will come from a Web Request or CLI Argument
TARGET_STATE = "VA"
TARGET_CITY = "RICHMOND"
TARGET_STRATEGY = "tax_delinquent" 

if __name__ == "__main__":
    # The Controller just triggers the Use Case
    run_weekly_harvest(TARGET_STATE, TARGET_CITY, TARGET_STRATEGY)
