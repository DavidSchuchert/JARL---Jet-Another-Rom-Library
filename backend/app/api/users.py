"""User management API endpoints (admin-only)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.auth import get_password_hash, require_admin
from app.database import get_db_context
from app.models import User
from app.schemas import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserResponse], dependencies=[Depends(require_admin)])
async def list_users() -> list[UserResponse]:
    """Return all users (admin only)."""
    async with get_db_context() as session:
        result = await session.execute(select(User).order_by(User.created_at))
        return [UserResponse.model_validate(u) for u in result.scalars().all()]


@router.post("", response_model=UserResponse, status_code=201, dependencies=[Depends(require_admin)])
async def create_user(payload: UserCreate) -> UserResponse:
    """Create a new user (admin only)."""
    async with get_db_context() as session:
        existing = await session.execute(select(User).where(User.username == payload.username))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Username already exists")
        user = User(
            username=payload.username,
            password_hash=get_password_hash(payload.password),
            role=payload.role,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, current_user: User = Depends(require_admin)) -> None:
    """Delete a user (admin only). Admins cannot delete their own account."""
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    async with get_db_context() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        await session.delete(user)
        await session.commit()
