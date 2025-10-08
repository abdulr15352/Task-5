from pydantic import BaseModel, EmailStr, SecretStr
from typing import Optional

class UserSchema(BaseModel):
    name: str
    email: EmailStr
    password: SecretStr
    # hashed_password: Optional[str] = None
    is_active: bool = True


class UserRegisterResponseSchema(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: SecretStr

class CandidateSchema(BaseModel):
    name: str
    party: Optional[str] = "Independent" # Default party is Independent

class VotingSchema(BaseModel):
    candidate_id: int

class UserUpdateSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
