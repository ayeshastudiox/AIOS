from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any
from app.services.ai_service import generate_insights_from_metrics

router = APIRouter(
    prefix="/api/ai",
    tags=["AI Engine"]
)

class InsightsRequest(BaseModel):
    metrics: Dict[str, Any]

@router.post("/insights", summary="Generate Insights")
def generate_insights(payload: InsightsRequest):
    """
    API endpoint to receive metrics and return AI business insights.
    """
    try:
        result = generate_insights_from_metrics(payload.metrics)
        return {"status": "success", "data": result}
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )