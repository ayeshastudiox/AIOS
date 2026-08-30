from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.email_service import generate_business_email


router = APIRouter(
    prefix="/api/email",
    tags=["AI Email Writer"]
)


class EmailRequest(BaseModel):
    recipient: str
    scenario: str
    tone: str


@router.post("/generate", summary="Generate Business Email")
def generate_email(payload: EmailRequest):
    """
    API endpoint to generate a professional business email.
    """
    try:
        result = generate_business_email(
            recipient=payload.recipient,
            scenario=payload.scenario,
            tone=payload.tone
        )

        return {
            "status": "success",
            "email": result
        }

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