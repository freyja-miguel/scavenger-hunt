"""API request/response schemas."""

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


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


class ChildRegister(BaseModel):
    """Schema for kid registration."""

    name: str = Field(min_length=1, max_length=100)
    date_of_birth: date
    password: Optional[str] = Field(default=None, min_length=6)

    @model_validator(mode="after")
    def age_must_be_5_to_12(self):
        """Ensure child is between 5 and 12 years old."""
        today = date.today()
        age = today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
        if age < 5 or age > 12:
            raise ValueError("Child must be between 5 and 12 years old")
        return self

    @property
    def age(self) -> int:
        """Compute age from date of birth."""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


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
