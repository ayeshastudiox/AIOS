from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.meeting_service import generate_meeting_summary


router = APIRouter(
    prefix="/api/meeting",
    tags=["Meeting Summaries"]
)


class MeetingSummaryRequest(BaseModel):
    transcript: str


@router.post("/summarize", summary="Generate Meeting Summary")
def summarize_meeting(payload: MeetingSummaryRequest):
    """
    API endpoint to generate a structured meeting summary.
    """
    try:
        result = generate_meeting_summary(
            transcript=payload.transcript
        )

        return {
            "status": "success",
            "summary": result
        }

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )