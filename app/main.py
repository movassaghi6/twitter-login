from fastapi import FastAPI
from app.api import user
from app.database import create_start_app_handler, create_stop_app_handler
from app.kafka import create_consumer
import asyncio



app = FastAPI()

app.include_router(user.router)
asyncio.create_task(create_consumer())

# Register startup and shutdown events
app.add_event_handler("startup", create_start_app_handler(app))
app.add_event_handler("shutdown", create_stop_app_handler(app))
