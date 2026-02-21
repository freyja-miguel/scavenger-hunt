"""SQLAlchemy ORM models."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""

    pass


class Child(Base):
    """Child profile with token balance."""

    __tablename__ = "children"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    token_balance: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    parent_account_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    completions: Mapped[list["ActivityCompletion"]] = relationship(
        "ActivityCompletion", back_populates="child", cascade="all, delete-orphan"
    )


class Activity(Base):
    """Treasure hunt activity."""

    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False)  # city, beach, bush, garden
    age_min: Mapped[int] = mapped_column(Integer, nullable=False)
    age_max: Mapped[int] = mapped_column(Integer, nullable=False)
    location_sydney: Mapped[str] = mapped_column(String(100), nullable=False)
    tokens_reward: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    ai_validation_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    completions: Mapped[list["ActivityCompletion"]] = relationship(
        "ActivityCompletion", back_populates="activity", cascade="all, delete-orphan"
    )


class ActivityCompletion(Base):
    """Record of a child completing an activity with photo validation."""

    __tablename__ = "activity_completions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    child_id: Mapped[int] = mapped_column(ForeignKey("children.id"), nullable=False)
    activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id"), nullable=False)
    photo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    photo_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    validated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    validation_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    tokens_awarded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    child: Mapped["Child"] = relationship("Child", back_populates="completions")
    activity: Mapped["Activity"] = relationship("Activity", back_populates="completions")
