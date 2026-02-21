"""Child and rewards API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_async_session
from app.db.models import Child
from app.models.schemas import ChildCreate, ChildResponse, CompletionResponse
from app.services.activity_service import get_child_by_id, list_child_completions

router = APIRouter(prefix="/children", tags=["children"])


@router.post("/", response_model=ChildResponse)
async def create_child(
    req: ChildCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Create a new child profile."""
    child = Child(name=req.name, age=req.age, token_balance=0)
    session.add(child)
    await session.flush()
    await session.refresh(child)
    return ChildResponse(
        id=child.id,
        name=child.name,
        age=child.age,
        token_balance=child.token_balance,
    )


@router.get("/{child_id}", response_model=ChildResponse)
async def get_child(
    child_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Get child profile including token balance."""
    child = await get_child_by_id(session, child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    return ChildResponse(
        id=child.id,
        name=child.name,
        age=child.age,
        token_balance=child.token_balance or 0,
    )


@router.get("/{child_id}/tokens")
async def get_tokens(
    child_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Get child token balance."""
    child = await get_child_by_id(session, child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    return {"child_id": child_id, "tokens": child.token_balance or 0}


@router.get("/{child_id}/completions")
async def list_completions(
    child_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """List completed activities for a child."""
    child = await get_child_by_id(session, child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    rows = await list_child_completions(session, child_id)
    return {
        "child_id": child_id,
        "completions": [
            CompletionResponse(
                id=c.id,
                activity_id=c.activity_id,
                activity_title=a.title,
                completed_at=c.completed_at,
                tokens_awarded=c.tokens_awarded,
                validated=c.validated,
            )
            for c, a in rows
        ],
    }
