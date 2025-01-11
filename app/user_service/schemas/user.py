from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    username: str
    password: str
    phone_number: str
    email: str | None = None


# Schema for public or dependency use
class UserSafe(BaseModel):
    username: str
    phone_number: str
    email: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    