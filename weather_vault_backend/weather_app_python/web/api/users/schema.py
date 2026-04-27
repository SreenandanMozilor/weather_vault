from pydantic import BaseModel, Field, EmailStr

class UserCreate(BaseModel):
    """Schema for creating a new user."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    """Schema for logging in (Priority Fix #8)."""
    identifier: str
    password: str

class Token(BaseModel):
    """Schema for the authentication token."""
    access_token: str
    token_type: str