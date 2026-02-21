"""Child and rewards API endpoints."""

from fastapi import APIRouter, HTTPException

from app.models.schemas import ChildResponse

router = APIRouter(prefix="/children", tags=["children"])


@router.get("/{child_id}", response_model=ChildResponse)
async def get_child(child_id: int):
    """Get child profile including token balance."""
    # TODO: Load from database
    raise HTTPException(status_code=404, detail="Child not found")


@router.get("/{child_id}/tokens")
async def get_tokens(child_id: int):
    """Get child token balance."""
    # TODO: Load from database
    return {"child_id": child_id, "tokens": 0}


@router.get("/{child_id}/completions")
async def list_completions(child_id: int):
    """List completed activities for a child."""
    # TODO: Query ActivityCompletion table
    return {"child_id": child_id, "completions": []}
