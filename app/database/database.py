from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import Config

# --- 1. THE CONNECTION URL ---
# We build the "phone number" to dial your database using the secrets from Config.
# It looks like: postgresql://admin:secretpassword@localhost:5432/property_db
SQLALCHEMY_DATABASE_URL = f"postgresql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"

# --- 2. THE ENGINE ---
# This is the actual "Cable" connecting Python to the Database.
# It establishes the open line of communication.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# --- 3. THE SESSION MAKER ---
# Think of 'engine' as the building, and 'SessionLocal' as the front desk.
# When our app needs to do work, we don't grab the whole building.
# We ask the front desk for a "Session" (a temporary workspace).
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- 4. THE BASE ---
# This is a "Template" for our tables.
# Later, when we define the 'Leads' table, we will say: "Leads is a kind of Base".
# This tells SQLAlchemy: "Hey, Leads is a table, please track it."
Base = declarative_base()

# --- 5. THE HELPER ---
def get_db():
    """
    This function is used by the API to manage connections safely.
    It ensures that even if your code crashes, the database connection 
    is closed properly so we don't leave the door unlocked.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
