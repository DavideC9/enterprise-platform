from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # Secondi


class AdminOut(BaseModel):
    id: int
    email: str
    is_active: bool

    model_config = {"from_attributes": True}