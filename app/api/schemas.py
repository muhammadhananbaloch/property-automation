from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

# =======================
# 1. INPUT SCHEMAS (Requests)
# =======================

class ScanRequest(BaseModel):
    """
    What the frontend sends to start a 'Scan' (Phase 1).
    """
    state: str
    city: str
    strategy: str

class EnrichRequest(BaseModel):
    """
    What the frontend sends to start 'Enrichment' (Phase 2).
    Includes the specific list of IDs the user chose to buy.
    """
    state: str
    city: str
    strategy: str
    radar_ids: List[str]  # e.g. ["PDD123", "PDD456"]

# =======================
# 2. OUTPUT SCHEMAS (Responses)
# =======================

class ScanSummary(BaseModel):
    """
    The report we send back after a Scan.
    """
    list_id: Optional[int] = None
    total_in_list: int
    purchased_count: int
    new_count: int
    new_ids: List[str]       # We send these so the frontend can slice them
    purchased_ids: List[str] # We send these so the frontend can re-process them

class EnrichResult(BaseModel):
    """
    The confirmation we send back after buying leads.
    """
    status: str
    saved_count: int

# =======================
# 3. DATABASE MODELS (Reading History)
# =======================

# app/api/schemas.py

# ... keep previous classes the same ...

# app/api/schemas.py

# ... (keep other classes the same) ...

class LeadResponse(BaseModel):
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
    year_built: Optional[int] = 0
    
    # Contact Info
    phone_numbers: List[str] = []
    emails: List[str] = []    
    class Config:
        from_attributes = True
class SearchHistoryResponse(BaseModel):
    """
    Defines how a 'History Item' looks in the Sidebar.
    """
    id: int
    city: str
    strategy: str
    created_at: datetime
    total_results: int
    
    class Config:
        from_attributes = True
