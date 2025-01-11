from fastapi import FastAPI, Request, HTTPException
from app.api import user
from app.database import create_start_app_handler, create_stop_app_handler
from app.kafka import create_consumer
import asyncio
from starlette.middleware.base import BaseHTTPMiddleware
from time import time



app = FastAPI()

# Basic in-memory store for IP addresses and request counts
request_counts = {}
RATE_LIMIT = 5 # max 5 requests
TIME_WINDOW = 60 # per 60 seconds

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time()

        if client_ip in request_counts:
            request_times = request_counts[client_ip]

            # Remove outdated requests outside the time window
            request_counts[client_ip] = [
                timestamp for timestamp in request_times if current_time - timestamp < TIME_WINDOW
            ]

            if len(request_counts[client_ip]) >= RATE_LIMIT:
                raise HTTPException(status_code=429, detail="Too many Requests")
        
        # Add current request timestamp
        request_counts.setdefault(client_ip, []).append(current_time)

        # Proceed to the next middleware or endpoint
        response = await call_next(request)
        return response


# Add the middleware to Application
app.add_middleware(RateLimitMiddleware)

app.include_router(user.router)
asyncio.create_task(create_consumer())

# Register startup and shutdown events
app.add_event_handler("startup", create_start_app_handler(app))
app.add_event_handler("shutdown", create_stop_app_handler(app))
