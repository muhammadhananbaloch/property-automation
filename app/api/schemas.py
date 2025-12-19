import json
import ast
from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

# =======================
# 1. SHARED MODELS (Must come first!)
# =======================

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

# =======================
# 2. INPUT SCHEMAS (Requests)
# =======================

class ScanRequest(BaseModel):
    state: str
    city: str
    strategy: str

class EnrichRequest(BaseModel):
    state: str
    city: str
    strategy: str
    radar_ids: List[str]

# =======================
# 3. OUTPUT SCHEMAS (Responses)
# =======================

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
