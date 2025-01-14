from pydantic import Field
from typing import Optional
from beanie import Document, Indexed
import datetime



class User(Document):
    username: Indexed(str, unique=True)
    hashed_password: str = Field(min_length=8)
    phone_number: str = Field(unique=True, regex=r'^\+?98?\d{9,15}$')
    email: Optional[str] = None

    class Settings:
        collection = "users"
        use_cache = True
        cache_expiration_time = datetime.timedelta(seconds=100)
        cache_capacity = 5



class Task(Document):
    status: str

    class Settings:
        collection = "tasks"