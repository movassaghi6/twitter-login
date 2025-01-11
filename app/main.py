from fastapi import FastAPI
from .user_service.api import user
from .user_service.db.database import create_start_app_handler, create_stop_app_handler
from .kafka_service.kafka.consumer import create_consumer
from .user_service.utils.middleware import RateLimitMiddleware
import asyncio



app = FastAPI()

# Add the middleware to Application
app.add_middleware(RateLimitMiddleware)

app.include_router(user.router)
asyncio.create_task(create_consumer())

# Register startup and shutdown events
app.add_event_handler("startup", create_start_app_handler(app))
app.add_event_handler("shutdown", create_stop_app_handler(app))
