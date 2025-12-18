from fastapi import APIRouter, HTTPException
from app.api.schemas import ScanRequest, ScanSummary, EnrichRequest, EnrichResult
from app.domain.harvest import scan_target_area, enrich_target_leads

# Create the Router
# This acts like a mini-app that only handles 'Search' related URLs
router = APIRouter(
    prefix="/api/search",
    tags=["Search & Enrichment"]
)

@router.post("/scan", response_model=ScanSummary)
def run_scan_endpoint(payload: ScanRequest):
    """
    Step 1: The Scout.
    Receives criteria -> Returns a count of available leads.
    """
    try:
        # We pass the data straight from the Schema into our Domain Logic
        result = scan_target_area(payload.state, payload.city, payload.strategy)
        
        # If the domain logic returned an error dict, we catch it here
        if "error" in result:
            raise HTTPException(status_code=400, detail=result['error'])
            
        return result
        
    except Exception as e:
        print(f"Error in /scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enrich", response_model=EnrichResult)
def run_enrich_endpoint(payload: EnrichRequest):
    """
    Step 2: The Buyer.
    Receives a list of IDs -> Buys and Saves them.
    """
    try:
        # Call the enricher with the specific list of IDs the user chose
        result = enrich_target_leads(
            payload.radar_ids, 
            payload.state, 
            payload.city, 
            payload.strategy
        )
        
        # Map the dictionary response to our Pydantic Schema
        return EnrichResult(
            status="success", 
            saved_count=result.get("saved", 0)
        )
        
    except Exception as e:
        print(f"Error in /enrich: {e}")
        raise HTTPException(status_code=500, detail=str(e))
