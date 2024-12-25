import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.settings import DATABASE_HOST, DATABASE_NAME
from app.models import User, Task


async def start_mongo_client():
    # create motor client
    client = AsyncIOMotorClient(DATABASE_HOST)

    # Init beanie with user and task document classes.
    await init_beanie(database=client[DATABASE_NAME], document_models=[User, Task])