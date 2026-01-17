"""Pydantic schemas for authentication."""

from pydantic import BaseModel


class Token(BaseModel):
    """JWT token response schema."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded token data."""

    username: str


class UserResponse(BaseModel):
    """User information response schema."""

    username: str
    is_admin: bool = False
