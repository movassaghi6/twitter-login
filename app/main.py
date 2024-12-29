from fastapi import FastAPI
from api import user
import asyncio


app = FastAPI()

app.include_router(user.router)
asyncio.create_task(user.create_consumer())

