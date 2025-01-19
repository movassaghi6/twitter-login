from aiokafka import AIOKafkaConsumer
from ..utils.message_parser import parse_kafka_message
import asyncio
from ...user_service.core.security import password_manager, user_repo
from ...user_service.core.database import mongo_db
from ...user_service.repository.Task import TaskRepo
from ..core.logger import setup_logging



# Set up logging
loggers = setup_logging()
logger  = loggers["kafka-consumer"]

# An event which will be set, when task is ready
task_ready_event = asyncio.Event()

# Kafka Consumer
async def create_consumer():
    consumer = AIOKafkaConsumer(
        "twitter_login_requests",
        #loop=loop,
        bootstrap_servers="localhost:9092",
    )
    await consumer.start()
    logger.info("Kafka consumer started and listening to 'twitter_login_requests' topic")
    try:
        async for msg in consumer:
            try:
                logger.debug(f"Received message: {msg.value}")

                # get username from consumer's message
                parsed_message= parse_kafka_message(msg)
                user = parsed_message.username
                logger.info(f"Processing message for user: {user}")

                if mongo_db.client is None:
                    raise Exception("MongoDB client is not initialized.")
            
                # Fetch user from database 
                user_in_db = await user_repo.get_by_username(username=user)
                logger.debug(f"User fetched from database: {user_in_db}")


                # Check input credentials for login
                if (
                    user_in_db 
                    and password_manager.verify_password(parsed_message.password, user_in_db.hashed_password) 
                    and user_in_db.phone_number == parsed_message.phone_number 
                    and user_in_db.email == parsed_message.email
                ):
                    task_id = await TaskRepo.create(status="success")
                    logger.info(f"Task created with status 'success' for user: {user}")

                else:
                    task_id = await TaskRepo.create(status="failure")
                    logger.info(f"Task created with status 'failure' for user: {user}")

                # Set the event to signal that the task is ready
                task_ready_event.set()
                logger.debug("Task ready event set")

            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
    finally:
        await consumer.stop()
        logger.info("Kafka consumer stopped")
    
