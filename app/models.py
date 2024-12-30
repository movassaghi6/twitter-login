from pydantic import Field
from typing import Optional
from beanie import Document, Indexed



class User(Document):
    username: Indexed(str, unique=True)
    password: str
    phone_number: str = Field(unique=True)
    email: Optional[str] = None

    class Settings:
        collection = "users"


class Task(Document):
    status: str

    class Settings:
        collection = "tasks"