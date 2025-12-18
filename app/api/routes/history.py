from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

# Database & Models
from app.database.database import get_db
from app.database.models import SearchHistory
from app.api.schemas import SearchHistoryResponse, LeadResponse

router = APIRouter(
    prefix="/api/history",
    tags=["History & Leads"]
)

@router.get("/", response_model=List[SearchHistoryResponse])
def get_all_history(db: Session = Depends(get_db)):
    """
    Fetches the list of past searches for the Sidebar.
    Ordered by newest first.
    """
    searches = db.query(SearchHistory).order_by(desc(SearchHistory.created_at)).all()
    return searches

@router.get("/{search_id}", response_model=List[LeadResponse])
def get_leads_for_search(search_id: int, db: Session = Depends(get_db)):
    """
    Fetches all leads associated with a specific search ID.
    """
    # 1. Find the search record
    search = db.query(SearchHistory).filter(SearchHistory.id == search_id).first()
    
    if not search:
        raise HTTPException(status_code=404, detail="Search history not found")
    
    # 2. Extract the leads using the relationship (search.results)
    # The 'results' relationship is the bridge table (SearchResult).
    # We loop through it to get the actual 'Lead' objects.
    leads = [result.lead for result in search.results]
        
    return leads
