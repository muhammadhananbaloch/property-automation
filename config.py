import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class Config:
    PROPERTY_RADAR_TOKEN = os.getenv("PROPERTY_RADAR_API_TOKEN")

    # Twilio (New)
    TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE = os.getenv("TWILIO_PHONE_NUMBER")

    @staticmethod
    def validate():
        if not Config.PROPERTY_RADAR_TOKEN:
            raise ValueError("CRITICAL: PROPERTY_RADAR_API_TOKEN is missing from .env file.")
        
        if not Config.TWILIO_SID or not Config.TWILIO_TOKEN:
            print("⚠️ Warning: Twilio credentials missing. SMS features will be disabled.")

# Check immediately when imported
Config.validate()
