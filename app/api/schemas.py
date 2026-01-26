import json
import ast
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Any
from datetime import datetime


# --- AUTH SCHEMAS ---
class UserCreate(BaseModel):
    email: EmailStr = Field(
        ..., 
        description="Valid email address used for login", 
        examples=["hanan@jbs.com"]
    )

    password: str = Field(
        ..., 
        min_length=6, 
        description="Secure password (min 6 characters)", 
        examples=["Hanan@67"]
    )

    full_name: str = Field(
        ..., 
        min_length=3, 
        max_length=50, 
        description="User's Full name", 
        examples=["Muhammad Hanan Baloch"]
    )
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None


# --- SHARED MODELS ---

class LeadResponse(BaseModel):
    """
    The Full Lead Object (with Phones & Emails).
    Used for History AND "Already Owned" lists.
    """
    radar_id: str
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    owner_name: Optional[str]
    is_purchased: bool
    
    # Real Estate Data
    equity_value: Optional[float] = 0.0
    estimated_value: Optional[float] = 0.0
    beds: Optional[int] = 0
    baths: Optional[float] = 0.0
    sq_ft: Optional[int] = 0       # <--- NEW FIELD ADDED
    year_built: Optional[int] = 0
    
    # Contact Info
    phone_numbers: List[str] = []
    emails: List[str] = []
    
    class Config:
        from_attributes = True

class LeadPreview(BaseModel):
    """
    The 'Lite' version for the "New Leads" table.
    (No contact info, because you haven't bought it yet!)
    """
    id: str
    address: str
    owner: Optional[str] = "Unknown"
    equity: Optional[float] = 0.0

# --- INPUT SCHEMAS (Requests) ---

class ScanRequest(BaseModel):
    state: str
    city: str
    strategy: str

class EnrichRequest(BaseModel):
    state: str
    city: str
    strategy: str
    radar_ids: List[str]

# --- OUTPUT SCHEMAS (Responses) ---

class ScanSummary(BaseModel):
    total_found: int
    new_count: int
    purchased_count: int
    
    # The leads available to buy (Lite Version)
    leads: List[LeadPreview] = [] 
    
    # NEW: The leads you already own (Full Version!)
    purchased_leads: List[LeadResponse] = []

class EnrichResult(BaseModel):
    status: str
    saved_count: int

class SearchHistoryResponse(BaseModel):
    id: int
    city: str
    strategy: str
    created_at: datetime
    total_results: int
    class Config:
        from_attributes = True

# --- NEW: CAMPAIGN SCHEMAS ---

class CampaignCreate(BaseModel):
    """
    What the Frontend sends to start a campaign.
    """
    name: str           # e.g. "Richmond Blast - Jan 24"
    template_body: str  # e.g. "Hi {name}, saw your home at {address}..."
    lead_ids: List[str] # The specific Radar IDs to target

class CampaignResponse(BaseModel):
    """
    What the API returns immediately (before sending finishes).
    """
    id: int
    name: str
    status: str
    total_leads: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- NEW: INDIVIDUAL MESSAGE SCHEMAS ---

class MessageCreate(BaseModel):
    """
    Payload for sending a single, manual message to a lead.
    """
    lead_id: str   # The specific Radar ID (e.g., "b239a0...")
    body: str      # The actual text content
    
    # Optional: If this message belongs to a specific campaign context
    campaign_id: int | None = None 

class MessageResponse(BaseModel):
    """
    The saved message record returned to the UI.
    """
    id: int
    lead_id: str
    direction: str   # "outbound-api", "inbound", etc.
    body: str
    status: str      # "queued", "sent", "failed"
    created_at: datetime
    error_message: str | None = None
    cost: float | None = None  # <--- NEW: Expose cost to UI

    class Config:
        from_attributes = True

# --- NEW: INBOX / CONVERSATION SCHEMAS ---

class InboxMessage(BaseModel):
    """
    Represents a single chat bubble in the UI.
    """
    id: int
    direction: str       # "outbound-api", "inbound", etc.
    body: str
    status: str
    created_at: datetime
    error_message: str | None = None
    cost: float | None = None  # <--- NEW: Expose cost to UI

    class Config:
        from_attributes = True

class InboxConversation(BaseModel):
    """
    Represents one item in the 'Contact List' (Left side of screen).
    Contains the Lead info and their full chat history.
    """
    lead_id: str
    owner_name: str | None = None
    address: str | None = None
    phone_number: str | None = None # The primary number we are texting
    status: str | None = "queued"   # Status in this campaign
    
    # The Chat History
    messages: List[InboxMessage] = []
    
    # Helper for sorting: When was the last activity?
    last_activity_at: datetime | None = None

class InboxResponse(BaseModel):
    """
    The full payload for the Campaign Inbox page.
    """
    campaign_id: int
    campaign_name: str
    conversations: List[InboxConversation]
