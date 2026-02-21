"""Activity business logic - listing, generation, photo validation."""

import base64
import uuid
from pathlib import Path
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import Activity, ActivityCompletion, Child
from app.models.schemas import (
    ActivityCategory,
    ActivityResponse,
    GenerateActivitiesRequest,
)
from app.services.ai_service import AIService


def _ensure_upload_dir() -> Path:
    path = Path(settings.upload_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


async def list_activities(
    session: AsyncSession,
    category: Optional[ActivityCategory] = None,
    age_min: Optional[int] = None,
    age_max: Optional[int] = None,
    location: Optional[str] = None,
) -> list[Activity]:
    """List activities with optional filters."""
    stmt = select(Activity).order_by(Activity.created_at.desc())
    if category is not None:
        stmt = stmt.where(Activity.category == category.value)
    if age_min is not None:
        stmt = stmt.where(Activity.age_max >= age_min)
    if age_max is not None:
        stmt = stmt.where(Activity.age_min <= age_max)
    if location is not None:
        stmt = stmt.where(Activity.location_sydney.ilike(f"%{location}%"))
    result = await session.execute(stmt)
    return list(result.scalars().all())


def _activity_to_response(a: Activity) -> ActivityResponse:
    return ActivityResponse(
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


async def persist_generated_activities(
    session: AsyncSession,
    raw_activities: list[dict],
    req: GenerateActivitiesRequest,
) -> list[ActivityResponse]:
    """Convert AI output to Activity records and persist."""
    activities: list[Activity] = []
    for item in raw_activities:
        activity = Activity(
            title=item.get("title", "Untitled"),
            description=item.get("description", ""),
            category=req.category.value,
            age_min=req.age_min,
            age_max=req.age_max,
            location_sydney=item.get("location_sydney", req.location_sydney),
            tokens_reward=item.get("tokens_reward", 1),
            ai_validation_prompt=item.get("ai_validation_prompt"),
        )
        session.add(activity)
        activities.append(activity)
    await session.flush()
    for a in activities:
        await session.refresh(a)
    return [_activity_to_response(a) for a in activities]


async def get_activity_by_id(session: AsyncSession, activity_id: int) -> Activity | None:
    """Fetch activity by ID."""
    result = await session.execute(select(Activity).where(Activity.id == activity_id))
    return result.scalar_one_or_none()


async def get_child_by_id(session: AsyncSession, child_id: int) -> Child | None:
    """Fetch child by ID."""
    result = await session.execute(select(Child).where(Child.id == child_id))
    return result.scalar_one_or_none()


async def list_child_completions(
    session: AsyncSession,
    child_id: int,
) -> list[tuple[ActivityCompletion, Activity]]:
    """List completions for a child with activity details."""
    stmt = (
        select(ActivityCompletion, Activity)
        .join(Activity, ActivityCompletion.activity_id == Activity.id)
        .where(ActivityCompletion.child_id == child_id)
        .order_by(ActivityCompletion.completed_at.desc())
    )
    result = await session.execute(stmt)
    return list(result.all())


async def submit_photo_for_validation(
    session: AsyncSession,
    activity_id: int,
    child_id: int,
    photo_bytes: bytes,
    photo_content_type: str,
) -> tuple[bool, str, int]:
    """
    Store photo, run AI validation, create completion, award tokens.
    Returns (valid, reasoning, tokens_awarded).
    """
    activity = await get_activity_by_id(session, activity_id)
    if not activity:
        return False, "Activity not found", 0

    child = await get_child_by_id(session, child_id)
    if not child:
        return False, "Child not found", 0

    ai_service = AIService()
    if not ai_service.client:
        return False, "AI service not configured (GROQ_API_KEY)", 0

    # Store photo
    ext = "jpg" if "jpeg" in (photo_content_type or "") or "jpg" in (photo_content_type or "") else "png"
    upload_dir = _ensure_upload_dir()
    filename = f"{activity_id}_{child_id}_{uuid.uuid4().hex[:12]}.{ext}"
    photo_path = str(upload_dir / filename)
    Path(photo_path).write_bytes(photo_bytes)

    # EXIF check - optional, use upload time if no EXIF
    # For MVP we accept all photos; could add Pillow EXIF parsing here
    image_base64 = base64.b64encode(photo_bytes).decode("utf-8")
    validation_criteria = activity.ai_validation_prompt or "Photo should show completion of the activity."
    try:
        result = await ai_service.validate_photo(
            image_base64=image_base64,
            activity_description=activity.description,
            validation_criteria=validation_criteria,
        )
    except Exception as e:
        return False, f"AI validation failed: {e}", 0

    valid = result.get("valid", False)
    reasoning = result.get("reasoning", "No reasoning provided")

    completion = ActivityCompletion(
        child_id=child_id,
        activity_id=activity_id,
        photo_path=photo_path,
        validated=valid,
        validation_response=reasoning,
        tokens_awarded=activity.tokens_reward if valid else 0,
    )
    session.add(completion)

    if valid:
        child.token_balance = (child.token_balance or 0) + activity.tokens_reward
        await session.flush()

    return valid, reasoning, activity.tokens_reward if valid else 0
