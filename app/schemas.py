from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    username: str
    password: str
    phone_number: str
    email: str | None = None


# The role of the dependency get_user_dep is to fetch an
# authenticated user based on a JWT token.
# After verifying the token, there's no need to include the password—the user
# is already authenticated.so we better use a schema without password like below
# for that function.
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
    