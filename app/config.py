import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class Config:
    PROPERTY_RADAR_TOKEN = os.getenv("PROPERTY_RADAR_API_TOKEN")

    @staticmethod
    def validate():
        if not Config.PROPERTY_RADAR_TOKEN:
            raise ValueError("CRITICAL: PROPERTY_RADAR_API_TOKEN is missing from .env file.")

# Check immediately when imported
Config.validate()
