"""Authentication API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import create_access_token, verify_password
from app.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate a user and return a JWT token."""
    print(f"DEBUG: Login attempt for username: '{form_data.username}'")
    print(f"DEBUG: Configured username: '{settings.auth.username}'")
    
    if form_data.username != settings.auth.username:
        print(f"DEBUG: Username mismatch: '{form_data.username}' != '{settings.auth.username}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # We compare with the password from .env
    if form_data.password != settings.auth.password:
        print("DEBUG: Password mismatch")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    print(f"DEBUG: Login successful for {form_data.username}")
    access_token = create_access_token(data={"sub": settings.auth.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
async def get_me():
    """Verify if the current session is valid."""
    # This endpoint is basically a ping to check if the token is still valid
    return {"status": "authenticated", "username": settings.auth.username}
