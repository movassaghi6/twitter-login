from ...user_service.schemas.user import User
from aiokafka import AIOKafkaProducer
import json


# Kafka Prodcuer
async def create_producer(user_credentials: User):
    
    # create a producer instance
    producer = AIOKafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda v: json.dumps(v).encode('utf-8')) # Serialize values to JSON)
    
    await producer.start()
    try:
        # Serialize pydantic object into a dictionary
        user_data = user_credentials.model_dump()
        ##username = user_data.get("username")

        await producer.send_and_wait("twitter_login_requests", user_data)

    finally:
        await producer.stop()



