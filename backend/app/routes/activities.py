"""Activity-related API endpoints."""

from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.schemas import (
    ActivityCategory,
    ActivityResponse,
    GenerateActivitiesRequest,
    PhotoValidationResponse,
)
from app.services.ai_service import AIService

router = APIRouter(prefix="/activities", tags=["activities"])
ai_service = AIService()


@router.get("/", response_model=list[ActivityResponse])
async def list_activities(
    category: Optional[ActivityCategory] = None,
    age_min: Optional[int] = None,
    age_max: Optional[int] = None,
    location: Optional[str] = None,
):
    """List activities with optional filters (age, category, Sydney location)."""
    # TODO: Query database with filters
    return []


@router.post("/generate")
async def generate_activities(req: GenerateActivitiesRequest):
    """Generate activities via AI (admin/internal use)."""
    try:
        activities = await ai_service.generate_activities(req)
        return {"generated": activities, "message": "TODO: persist to DB"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{activity_id}/submit-photo", response_model=PhotoValidationResponse)
async def submit_photo(
    activity_id: int,
    photo: UploadFile = File(...),
):
    """Submit photo for AI validation. Must be taken at time of completion."""
    # TODO: Load activity from DB
    # TODO: Check EXIF timestamp (reject if too old)
    # TODO: Store photo, call AI validation, award tokens on success
    if not photo.content_type or not photo.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Placeholder - integrate with AI service and DB
    return PhotoValidationResponse(
        valid=False,
        reasoning="Not yet implemented - connect to DB and AI service",
        tokens_awarded=0,
    )
