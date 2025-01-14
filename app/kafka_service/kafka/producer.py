from ...user_service.schemas.user import User
from aiokafka import AIOKafkaProducer
import json
from ..core.logger import setup_logging


# Set up logging
loggers = setup_logging()
logger  = loggers["kafka-producer"]


# Kafka Prodcuer
async def create_producer(user_credentials: User):
    logger.info("Initializing kafka producer")
    try:
        # create a producer instance
        producer = AIOKafkaProducer(
            bootstrap_servers="localhost:9092",
            value_serializer=lambda v: json.dumps(v).encode('utf-8')) # Serialize values to JSON)
        await producer.start()
        logger.debug("Kafka producer started successfully")

        try:
            # Serialize pydantic object into a dictionary
            user_data = user_credentials.model_dump()
            logger.info(f"Sending message for user: {user_data.get("username")}")

            await producer.send_and_wait("twitter_login_requests", user_data)
            logger.debug("Message sent successfully")
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}", exc_info=True)
            raise
        finally:
            await producer.stop()
            logger.info("Kafka producer stopped")
    except Exception as e:
        logger.error(f"Error creating producer: {str(e)}", exc_info=True)
        raise




