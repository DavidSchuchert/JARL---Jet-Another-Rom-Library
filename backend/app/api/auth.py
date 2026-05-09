"""Authentication API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import select

from app.auth import create_access_token, get_current_user, get_password_hash, verify_password
from app.config import get_settings
from app.database import get_db_context
from app.models import AppConfig

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()

_PASSWORD_KEY = "auth_password_hash"


async def _check_password(plain: str) -> bool:
    """Verify password against DB override or env var fallback."""
    async with get_db_context() as session:
        result = await session.execute(select(AppConfig).where(AppConfig.key == _PASSWORD_KEY))
        config = result.scalar_one_or_none()
    if config:
        return verify_password(plain, config.value)
    return plain == settings.auth.password


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate a user and return a JWT token."""
    if form_data.username != settings.auth.username or not await _check_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": settings.auth.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
async def get_me():
    """Verify if the current session is valid."""
    return {"status": "authenticated", "username": settings.auth.username}


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


@router.patch("/password", dependencies=[Depends(get_current_user)])
async def change_password(payload: PasswordChange):
    """Change the admin password (persisted to DB, survives restarts)."""
    if not await _check_password(payload.current_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect")
    if len(payload.new_password) < 8:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password must be at least 8 characters")

    new_hash = get_password_hash(payload.new_password)
    async with get_db_context() as session:
        existing = await session.get(AppConfig, _PASSWORD_KEY)
        if existing:
            existing.value = new_hash
        else:
            session.add(AppConfig(key=_PASSWORD_KEY, value=new_hash))
        await session.commit()

    return {"message": "Password updated successfully"}
