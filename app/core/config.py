import os
from dotenv import load_dotenv
import secrets

# Load variables from .env file
load_dotenv()

class Config:
    # --- External APIs ---
    PROPERTY_RADAR_TOKEN = os.getenv("PROPERTY_RADAR_API_TOKEN")

    # Twilio
    TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE = os.getenv("TWILIO_PHONE_NUMBER")

    # --- Database ---
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "property_db")

    # --- Security ---
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 Hours

    @staticmethod
    def validate():
        if not Config.PROPERTY_RADAR_TOKEN:
            raise ValueError("CRITICAL: PROPERTY_RADAR_API_TOKEN is missing from .env file.")
        
        # Simple warnings for optional services
        if not Config.TWILIO_SID or not Config.TWILIO_TOKEN:
            print("⚠️ Warning: Twilio credentials missing. SMS features will be disabled.")

        if not Config.DB_USER:
             print("⚠️ Warning: Database credentials missing in .env")

# Check immediately when imported
Config.validate()
