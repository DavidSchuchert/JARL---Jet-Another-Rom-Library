"""Authentication API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import select

from app.auth import create_access_token, get_current_user, get_password_hash, verify_password
from app.database import get_db_context
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate a user and return a JWT token."""
    async with get_db_context() as session:
        result = await session.execute(
            select(User).where(User.username == form_data.username)
        )
        user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the current authenticated user's info."""
    return {"status": "authenticated", "username": current_user.username, "role": current_user.role}


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


@router.patch("/password")
async def change_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_user),
):
    """Change the current user's password (persisted to DB)."""
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect")
    if len(payload.new_password) < 8:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password must be at least 8 characters")

    async with get_db_context() as session:
        result = await session.execute(select(User).where(User.id == current_user.id))
        user = result.scalar_one()
        user.password_hash = get_password_hash(payload.new_password)
        await session.commit()

    return {"message": "Password updated successfully"}
