"""API request/response schemas."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ActivityCategory(str, Enum):
    """Activity category for Sydney locations."""

    CITY = "city"
    BEACH = "beach"
    BUSH = "bush"
    GARDEN = "garden"


class ActivityBase(BaseModel):
    """Activity base schema."""

    title: str
    description: str
    category: ActivityCategory
    age_min: int = Field(ge=5, le=12)
    age_max: int = Field(ge=5, le=12)
    location_sydney: str  # Suburb or area name
    tokens_reward: int = Field(default=1, ge=1)


class ActivityCreate(ActivityBase):
    """Schema for creating an activity (admin/internal)."""

    ai_validation_prompt: Optional[str] = None  # What AI should check in photo


class ActivityResponse(ActivityBase):
    """Activity response schema."""

    id: int
    ai_validation_prompt: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChildBase(BaseModel):
    """Child base schema."""

    name: str
    age: int = Field(ge=5, le=12)


class ChildCreate(ChildBase):
    """Schema for creating a child."""

    pass


class ChildResponse(ChildBase):
    """Child response with token balance."""

    id: int
    token_balance: int = 0

    class Config:
        from_attributes = True


class CompletionResponse(BaseModel):
    """Activity completion summary for child profile."""

    id: int
    activity_id: int
    activity_title: str
    completed_at: datetime
    tokens_awarded: int
    validated: bool


class PhotoValidationRequest(BaseModel):
    """Request body for photo submission (if not multipart)."""

    activity_id: int


class PhotoValidationResponse(BaseModel):
    """AI photo validation result."""

    valid: bool
    reasoning: str
    tokens_awarded: int = 0


class GenerateActivitiesRequest(BaseModel):
    """Request for AI activity generation."""

    category: ActivityCategory
    age_min: int = Field(ge=5, le=12)
    age_max: int = Field(ge=5, le=12)
    location_sydney: str
    count: int = Field(default=5, ge=1, le=20)
