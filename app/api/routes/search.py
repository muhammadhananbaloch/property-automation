from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import User
from app.api.schemas import ScanRequest, ScanSummary, EnrichRequest, EnrichResult
from app.domain.harvest import scan_target_area, enrich_target_leads
from app.api.dependencies import get_current_user # Added Security Dependency

# Create the Router
router = APIRouter(
    prefix="/api/search",
    tags=["Search & Enrichment"]
)

@router.post("/scan", response_model=ScanSummary)
def run_scan_endpoint(
    payload: ScanRequest,
    current_user: User = Depends(get_current_user) # <--- Security Injection
):
    """
    Step 1: The Scout.
    Receives criteria -> Returns a count of available leads.
    """
    try:
        # We pass the USER object down to the domain logic so it can tag the SearchHistory
        result = scan_target_area(
            payload.state, 
            payload.city, 
            payload.strategy,
            user=current_user  # <--- PASS USER HERE
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result['error'])
            
        return result
        
    except Exception as e:
        print(f"Error in /scan: {e}")
        # In production, logging the specific error 'e' is good, but return generic to client
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enrich", response_model=EnrichResult)
def run_enrich_endpoint(
    payload: EnrichRequest,
    current_user: User = Depends(get_current_user) # <--- Security Injection
):
    """
    Step 2: The Buyer.
    Receives a list of IDs -> Buys and Saves them.
    """
    try:
        # Pass user here too, in case enrichment needs to check ownership or log costs
        result = enrich_target_leads(
            payload.radar_ids, 
            payload.state, 
            payload.city, 
            payload.strategy,
            user=current_user # <--- PASS USER HERE
        )
        
        return EnrichResult(
            status="success", 
            saved_count=result.get("saved", 0)
        )
        
    except Exception as e:
        print(f"Error in /enrich: {e}")
        raise HTTPException(status_code=500, detail=str(e))
