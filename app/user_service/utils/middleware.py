from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from time import time
from ..core.logger import setup_logging



# Set up logging
loggers = setup_logging()
logger = loggers["middleware"]

# Basic in-memory store for IP addresses and request counts
request_counts = {}
RATE_LIMIT = 5 # max 5 requests
TIME_WINDOW = 60 # per 60 seconds

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time()

        logger.debug(f"Received request from {client_ip} at {current_time}")

        if client_ip in request_counts:
            request_times = request_counts[client_ip]

            # Remove outdated requests outside the time window
            request_counts[client_ip] = [
                timestamp for timestamp in request_times if current_time - timestamp < TIME_WINDOW
            ]

            if len(request_counts[client_ip]) >= RATE_LIMIT:
                logger.warning(f"Rate limit exceed for {client_ip}")
                raise HTTPException(status_code=429, detail="Too many Requests")
        
        # Add current request timestamp
        request_counts.setdefault(client_ip, []).append(current_time)
        logger.debug(f"Updated request count for {client_ip}: {len(request_counts[client_ip])}")

        # Proceed to the next middleware or endpoint
        response = await call_next(request)
        return response