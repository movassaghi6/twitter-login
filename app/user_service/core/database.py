from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from ..core.settings import DATABASE_HOST, DATABASE_NAME
from ..models.user import User, Task
from typing import Callable
from fastapi import FastAPI
from ..core.logger import setup_logging


# Set up logging
loggers = setup_logging()
logger = loggers["db"]


class MongoDB:
    """
    MongoDB class to hold a single AsyncIOMotorClient instance for the application.
    """
    client: AsyncIOMotorClient = None

# Create a global MongoDB instance
mongo_db= MongoDB()


async def mongodb_startup(app: FastAPI) -> None:
    """
    Establishing a connection to mongodb on application startup.

    Args:
        app (FastAPI): the FastAPI application instance.
    """
    logger.info("Connecting to MongoDB...")
    mongo_db.client = AsyncIOMotorClient(DATABASE_HOST)

    # Log the client instance to ensure it is set
    logger.info(f'MongoDB client initialized: {mongo_db.client}')
    
    # app.state is commonly used to store shared resources (e.g., database clients).
    # Attach the same intance to app.state
    app.state.mongo_client = mongo_db.client

    # Initialize Beanie ODM with your document models
    try:
        await init_beanie(
            database=mongo_db.client.get_database(DATABASE_NAME),
            document_models=[User, Task]
        )
        logger.info("MongoDB connection succeeded!")
    except Exception as e:
        logger.error(f'Error initializing Beanie: {e}', exc_info=True)


async def mongodb_shutdown(app: FastAPI) -> None:
    """
    Closes the MongoDB connection on application shutdown.

    Args:
        app (FastAPI): the FastAPI application instance.
    """
    logger.info("Closing MongoDB connection...")
    if mongo_db.client:
        mongo_db.client.close()
        logger.info("MongoDB connection closed!")
    else:
        logger.warning('MongoDB client was not initialized.')


def create_start_app_handler(app: FastAPI) -> Callable:
    """
    Creates an application startup handler that connects to MongoDB.

    Args:
        app (FastAPI): the FastAPI application instance.

    Returns:
        Callable: A coroutine function that starts the MongoDB connection.
    """
    async def start_app() -> None:
        await mongodb_startup(app)
    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    """
    Creates an application shutdown handler that disconnects from MongoDB.

    Args:
        app (FastAPI): the fastAPI application instance.

    Returns:
        Callable: A coroutine function that stops the MongoDB connection.
    """
    async def stop_app() -> None:
        await mongodb_shutdown(app)
    return stop_app

