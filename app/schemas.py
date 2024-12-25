from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    username: str
    password: str
    phone_number: str
    email: str | None = None