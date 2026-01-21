import json
import ast
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from app.database.database import get_db
from app.database.models import SearchHistory, User # Added User
from app.api.schemas import SearchHistoryResponse, LeadResponse
from app.api.dependencies import get_current_user # Added Security Dependency

router = APIRouter(
    prefix="/api/history",
    tags=["History & Leads"]
)

@router.get("/", response_model=List[SearchHistoryResponse])
def get_all_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # <--- Security Injection
):
    """
    Fetch search history ONLY for the logged-in user.
    """
    return db.query(SearchHistory)\
        .filter(SearchHistory.user_id == current_user.id)\
        .order_by(desc(SearchHistory.created_at))\
        .all()

@router.get("/{search_id}", response_model=List[LeadResponse])
def get_leads_for_search(
    search_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # <--- Security Injection
):
    # 1. Find the search
    search = db.query(SearchHistory).filter(SearchHistory.id == search_id).first()

    if not search:
        raise HTTPException(status_code=404, detail="Search history not found")

    # 2. Security Check: Does this search belong to the user?
    if search.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You are not authorized to view this search."
        )

    formatted_leads = []

    # Robust parser for mixed data types (JSON string vs Python list vs Text)
    def parse_list(value):
        if not value: return []
        if isinstance(value, list): return value
        if isinstance(value, str):
            value = value.strip()
            try: return json.loads(value)
            except: pass
            try: return ast.literal_eval(value)
            except: pass
            return [value]
        return []

    for result in search.results:
        lead = result.lead
        formatted_leads.append({
            "radar_id": lead.radar_id,
            "address": lead.address if lead.address else "N/A",
            "city": lead.city if lead.city else "",
            "state": lead.state if lead.state else "",
            "owner_name": lead.owner_name,
            "is_purchased": True,
            "equity_value": lead.estimated_equity,
            "estimated_value": lead.estimated_value,
            "beds": lead.beds,
            "baths": lead.baths,
            "sq_ft": lead.sq_ft,
            "year_built": lead.year_built,
            "phone_numbers": parse_list(lead.phone_numbers),
            "emails": parse_list(lead.email_addresses) 
        })

    return formatted_leads
