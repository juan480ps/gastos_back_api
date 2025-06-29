from datetime import datetime  
import re
from pydantic import BaseModel, EmailStr, validator, Field

def strong_password(password: str) -> str:
    """Validador de contraseña fuerte."""
    if len(password) < 8:
        raise ValueError('La contraseña debe tener al menos 8 caracteres')
    if not re.search("[a-z]", password):
        raise ValueError('La contraseña debe contener al menos una letra minúscula')
    if not re.search("[A-Z]", password):
        raise ValueError('La contraseña debe contener al menos una letra mayúscula')
    if not re.search("[0-9]", password):
        raise ValueError('La contraseña debe contener al menos un número')
    return password

class UserCreateSchema(BaseModel):
    full_name: str = Field(..., min_length=3)
    email: EmailStr
    username: str = Field(..., min_length=3)
    password: str

    _validate_password = validator('password', allow_reuse=True)(strong_password)

class UserLoginSchema(BaseModel):
    identifier: str  
    password: str

class UserResponseSchema(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    username: str
    created_at: datetime 
    is_confirmed: bool

    class Config:
        from_attributes = True 