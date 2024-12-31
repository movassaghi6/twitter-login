import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from settings import DATABASE_HOST, DATABASE_NAME
from models import User, Task
from typing import Callable
from contextlib import asynccontextmanager
from fastapi import FastAPI
from logging

'''
async def start_mongo_client():
    # create motor client
    client = AsyncIOMotorClient(DATABASE_HOST)

    # Init beanie with user and task document classes.
    await init_beanie(database=client[DATABASE_NAME], document_models=[User, Task])'''

# Configure built-in logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    
    # app.state is commonly used to store shared resources (e.g., database clients).
    # Attach the same intance to app.state
    app.state.mongo_client = mongo_db.client

    # Initialize Beanie ODM with your document models
    await init_beanie(
        database=mongo_db.client.get_database(DATABASE_NAME),
        document_models=[User, Task]
    )
    logger.info("MongoDB connection succeeded!")


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



# Context Manager
'''@asynccontextmanager
async def get_mongodb():
    """
    Async context manager to get the shared MongoDB client from the global instance.

    Yields:
        db: The MongoDB database instance for use during the context.
    """
    try:
        if mongo_db.client is None:
            raise Exception("MongoDB client is not initialized.")
        db = mongo_db.client.get_database("clean-database")
        yield db
    except Exception as e:
        logger.error(f'Error: {e}')
        raise'''


    
