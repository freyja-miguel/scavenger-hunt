"""Activity-related API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_async_session
from app.models.schemas import (
    ActivityCategory,
    ActivityResponse,
    GenerateActivitiesRequest,
    PhotoValidationResponse,
)
from app.services.activity_service import (
    list_activities,
    persist_generated_activities,
    submit_photo_for_validation,
)
from app.services.ai_service import AIService

router = APIRouter(prefix="/activities", tags=["activities"])
ai_service = AIService()


@router.get("/", response_model=list[ActivityResponse])
async def list_activities_endpoint(
    category: Optional[ActivityCategory] = None,
    age_min: Optional[int] = None,
    age_max: Optional[int] = None,
    location: Optional[str] = None,
    session: AsyncSession = Depends(get_async_session),
):
    """List activities with optional filters (age, category, Sydney location)."""
    activities = await list_activities(
        session,
        category=category,
        age_min=age_min,
        age_max=age_max,
        location=location,
    )
    return [
        ActivityResponse(
            id=a.id,
            title=a.title,
            description=a.description,
            category=ActivityCategory(a.category),
            age_min=a.age_min,
            age_max=a.age_max,
            location_sydney=a.location_sydney,
            tokens_reward=a.tokens_reward,
            ai_validation_prompt=a.ai_validation_prompt,
            created_at=a.created_at,
        )
        for a in activities
    ]


@router.post("/generate")
async def generate_activities_endpoint(
    req: GenerateActivitiesRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """Generate activities via AI (admin/internal use) and persist to DB."""
    try:
        raw = await ai_service.generate_activities(req)
        activities = await persist_generated_activities(session, raw, req)
        return {"generated": len(activities), "activities": activities}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{activity_id}/submit-photo", response_model=PhotoValidationResponse)
async def submit_photo_endpoint(
    activity_id: int,
    child_id: int = Query(..., description="ID of the child submitting the photo"),
    photo: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session),
):
    """Submit photo for AI validation. Must be taken at time of completion."""
    if not photo.content_type or not photo.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    photo_bytes = await photo.read()
    if len(photo_bytes) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large (max 20MB)")

    valid, reasoning, tokens_awarded = await submit_photo_for_validation(
        session=session,
        activity_id=activity_id,
        child_id=child_id,
        photo_bytes=photo_bytes,
        photo_content_type=photo.content_type or "",
    )
    return PhotoValidationResponse(
        valid=valid,
        reasoning=reasoning,
        tokens_awarded=tokens_awarded,
    )
