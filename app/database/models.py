from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base


# --- TABLE 1: USERS (Authentication) ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    searches = relationship("SearchHistory", back_populates="user")
    campaigns = relationship("Campaign", back_populates="user") # <--- NEW: Link to Campaigns


# --- TABLE 2: SEARCH HISTORY ---
class SearchHistory(Base):
    __tablename__ = "search_history"

    # Link to User (Nullable for now to support legacy data)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String, nullable=False)
    city = Column(String, nullable=True)
    strategy = Column(String, nullable=False)
    total_results = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    results = relationship("SearchResult", back_populates="search")
    user = relationship("User", back_populates="searches")

# --- TABLE 3: LEADS (Real Estate Data) ---
class Lead(Base):
    __tablename__ = "leads"

    # Identity
    radar_id = Column(String, primary_key=True, index=True)
    
    # Location
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    
    # Property Stats
    beds = Column(Integer, nullable=True)
    baths = Column(Float, nullable=True)
    sq_ft = Column(Integer, nullable=True)
    year_built = Column(Integer, nullable=True)
    lot_sq_ft = Column(Integer, nullable=True)
    property_type = Column(String, nullable=True)
    
    # Financials
    estimated_value = Column(Integer, nullable=True)
    estimated_equity = Column(Integer, nullable=True)
    tax_delinquent = Column(Boolean, default=False)
    
    # Raw Data Safety Net
    raw_property_data = Column(JSON, nullable=True)

    # Owner & Contact
    owner_name = Column(String)
    phone_numbers = Column(JSON) 
    email_addresses = Column(JSON)
    
    # Status
    is_purchased = Column(Boolean, default=False) 
    
    # Relationships
    searches = relationship("SearchResult", back_populates="lead")
    messages = relationship("Message", back_populates="lead") # <--- UPDATED: Points to new Message table

# --- TABLE 4: SEARCH RESULTS (Junction) ---
class SearchResult(Base):
    __tablename__ = "search_results"

    id = Column(Integer, primary_key=True, index=True)
    search_id = Column(Integer, ForeignKey("search_history.id"))
    lead_id = Column(String, ForeignKey("leads.radar_id"))
    
    search = relationship("SearchHistory", back_populates="results")
    lead = relationship("Lead", back_populates="searches")

# --- NEW TABLE 5: CAMPAIGNS (The Folders) ---
class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # Ownership
    
    name = Column(String)  # e.g., "Richmond Pre-Foreclosure - Jan 23"
    template_body = Column(Text)  # The original message you wrote
    
    status = Column(String, default="active") # active, archived
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="campaigns")
    campaign_leads = relationship("CampaignLead", back_populates="campaign")
    messages = relationship("Message", back_populates="campaign")


# --- NEW TABLE 6: CAMPAIGN LEADS (The Roster) ---
# This joins Leads to Campaigns. A lead can be in multiple campaigns.
class CampaignLead(Base):
    __tablename__ = "campaign_leads"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    lead_id = Column(String, ForeignKey("leads.radar_id"))
    
    # Status in this specific campaign
    status = Column(String, default="queued") # queued, sent, replied, stopped
    
    # Relationships
    campaign = relationship("Campaign", back_populates="campaign_leads")
    lead = relationship("Lead") # One-way link to Lead details


# --- TABLE 7: MESSAGES (The Chat Bubbles) ---
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    lead_id = Column(String, ForeignKey("leads.radar_id"))
    
    # Core Data
    direction = Column(String) # "outbound-api", "inbound"
    body = Column(Text)
    
    # Twilio Tech Details
    twilio_sid = Column(String, unique=True, nullable=True) # "sid" from JSON
    status = Column(String) # "queued", "sent", "delivered", "failed", "undelivered"
    
    # Cost & Logging
    cost = Column(Float, nullable=True) # "price" from JSON (Populates later)
    error_message = Column(String, nullable=True) # <--- NEW: captures failure reasons
    to_phone = Column(String, nullable=True)      # <--- NEW: captures specific number used
    
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # "date_created"

    # Relationships
    campaign = relationship("Campaign", back_populates="messages")
    lead = relationship("Lead", back_populates="messages")
