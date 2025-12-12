from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base

# --- TABLE 1: SEARCH HISTORY ---
class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String, nullable=False)
    city = Column(String, nullable=True)
    strategy = Column(String, nullable=False)
    total_results = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    results = relationship("SearchResult", back_populates="search")

# --- TABLE 2: LEADS (Updated for Real Estate Investors) ---
class Lead(Base):
    __tablename__ = "leads"

    # Identity
    radar_id = Column(String, primary_key=True, index=True)
    
    # Location
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    
    # --- NEW: Property Stats (The "Good Stuff") ---
    beds = Column(Integer, nullable=True)
    baths = Column(Float, nullable=True)
    sq_ft = Column(Integer, nullable=True)
    year_built = Column(Integer, nullable=True)
    lot_sq_ft = Column(Integer, nullable=True)
    property_type = Column(String, nullable=True) # e.g. "SFR", "Condo"
    
    # --- NEW: Money Fields ---
    estimated_value = Column(Integer, nullable=True) # AVM
    estimated_equity = Column(Integer, nullable=True)
    tax_delinquent = Column(Boolean, default=False)
    
    # --- NEW: The "Safety Net" ---
    # Stores the ENTIRE raw response from PropertyRadar. 
    # If they send "Garage" or "Pool", it gets saved here automatically.
    raw_property_data = Column(JSON, nullable=True)

    # Owner & Contact
    owner_name = Column(String)
    phone_numbers = Column(JSON) 
    email_addresses = Column(JSON)
    
    # Status
    is_purchased = Column(Boolean, default=False) 
    
    # Links
    searches = relationship("SearchResult", back_populates="lead")
    messages = relationship("MessageLog", back_populates="lead")

# --- TABLE 3: SEARCH RESULTS ---
class SearchResult(Base):
    __tablename__ = "search_results"

    id = Column(Integer, primary_key=True, index=True)
    search_id = Column(Integer, ForeignKey("search_history.id"))
    lead_id = Column(String, ForeignKey("leads.radar_id"))
    
    search = relationship("SearchHistory", back_populates="results")
    lead = relationship("Lead", back_populates="searches")

# --- TABLE 4: MESSAGE LOGS ---
class MessageLog(Base):
    __tablename__ = "message_logs"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(String, ForeignKey("leads.radar_id"))
    campaign_id = Column(Integer, ForeignKey("search_history.id"), nullable=True)
    
    to_number = Column(String)
    body = Column(Text)
    status = Column(String)
    sid = Column(String)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    
    lead = relationship("Lead", back_populates="messages")
